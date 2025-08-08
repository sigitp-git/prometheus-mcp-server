"""
Enhanced Prometheus client with authentication support.

This module provides a more complete implementation of the Prometheus client
with proper AWS SigV4 authentication for querying metrics.
"""

import logging
from typing import Any
from urllib.parse import urljoin

import requests
from botocore.exceptions import ClientError

from .auth import PrometheusAuth
from .main import PrometheusClient

logger = logging.getLogger(__name__)


class AuthenticatedPrometheusClient(PrometheusClient):
    """Enhanced Prometheus client with authentication support"""

    def __init__(self, region_name: str = "us-east-1"):
        """Initialize the authenticated Prometheus client"""
        super().__init__(region_name)
        self.auth = PrometheusAuth(region_name)

    def execute_query(
        self,
        workspace_id: str,
        query: str,
        start_time: str | None = None,
        end_time: str | None = None,
        step: str | None = None,
        timeout: int = 30,
    ) -> dict[str, Any]:
        """
        Execute a PromQL query against a workspace with proper authentication.

        Args:
            workspace_id: The workspace ID to query
            query: PromQL query string
            start_time: Start time for range queries (RFC3339 format)
            end_time: End time for range queries (RFC3339 format)
            step: Query resolution step for range queries
            timeout: Request timeout in seconds

        Returns:
            Dictionary containing query results
        """
        try:
            # Get workspace details
            workspace = self.get_workspace(workspace_id)

            if not workspace.prometheus_endpoint:
                raise ValueError(
                    f"Workspace {workspace_id} does not have a Prometheus endpoint"
                )

            # Determine query type and endpoint
            base_url = workspace.prometheus_endpoint.rstrip('/')
            if start_time and end_time:
                # Range query
                endpoint = f"{base_url}/api/v1/query_range"
                params = {
                    "query": query,
                    "start": start_time,
                    "end": end_time,
                    "step": step or "15s",
                }
            else:
                # Instant query
                endpoint = f"{base_url}/api/v1/query"
                params = {"query": query}

            # Get authenticated headers
            headers = self.auth.get_signed_headers("GET", endpoint, params)
            headers["Content-Type"] = "application/json"

            # Execute the request
            response = requests.get(
                endpoint, params=params, headers=headers, timeout=timeout
            )

            response.raise_for_status()

            result = response.json()

            logger.info(f"Successfully executed query on workspace: {workspace_id}")

            return {
                "workspace_id": workspace_id,
                "query": query,
                "status": result.get("status"),
                "data": result.get("data"),
                "error": result.get("error"),
                "warnings": result.get("warnings"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request error: {e}")
            raise
        except ClientError as e:
            logger.error(f"AWS client error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            raise

    def get_label_values(
        self, workspace_id: str, label_name: str, timeout: int = 30
    ) -> list[str]:
        """
        Get all label values for a specific label name.

        Args:
            workspace_id: The workspace ID to query
            label_name: Name of the label
            timeout: Request timeout in seconds

        Returns:
            List of label values
        """
        try:
            workspace = self.get_workspace(workspace_id)

            if not workspace.prometheus_endpoint:
                raise ValueError(
                    f"Workspace {workspace_id} does not have a Prometheus endpoint"
                )

            base_url = workspace.prometheus_endpoint.rstrip('/')
            endpoint = f"{base_url}/api/v1/label/{label_name}/values"

            headers = self.auth.get_signed_headers("GET", endpoint)
            headers["Content-Type"] = "application/json"

            response = requests.get(endpoint, headers=headers, timeout=timeout)
            response.raise_for_status()

            result = response.json()

            if result.get("status") == "success":
                return result.get("data", [])
            else:
                raise ValueError(f"Query failed: {result.get('error')}")

        except Exception as e:
            logger.error(f"Error getting label values: {e}")
            raise

    def get_series(
        self,
        workspace_id: str,
        match: list[str],
        start_time: str | None = None,
        end_time: str | None = None,
        timeout: int = 30,
    ) -> list[dict[str, str]]:
        """
        Get series that match the given label matchers.

        Args:
            workspace_id: The workspace ID to query
            match: List of series selector patterns
            start_time: Start time (RFC3339 format)
            end_time: End time (RFC3339 format)
            timeout: Request timeout in seconds

        Returns:
            List of series metadata
        """
        try:
            workspace = self.get_workspace(workspace_id)

            if not workspace.prometheus_endpoint:
                raise ValueError(
                    f"Workspace {workspace_id} does not have a Prometheus endpoint"
                )

            base_url = workspace.prometheus_endpoint.rstrip('/')
            endpoint = f"{base_url}/api/v1/series"

            params = {"match[]": match}
            if start_time:
                params["start"] = start_time
            if end_time:
                params["end"] = end_time

            headers = self.auth.get_signed_headers("GET", endpoint, params)
            headers["Content-Type"] = "application/json"

            response = requests.get(
                endpoint, params=params, headers=headers, timeout=timeout
            )
            response.raise_for_status()

            result = response.json()

            if result.get("status") == "success":
                return result.get("data", [])
            else:
                raise ValueError(f"Query failed: {result.get('error')}")

        except Exception as e:
            logger.error(f"Error getting series: {e}")
            raise
