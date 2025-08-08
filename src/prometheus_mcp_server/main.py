#!/usr/bin/env python3
"""
Amazon Managed Prometheus MCP Server

This server provides access to Amazon Managed Prometheus workspaces
through the Model Context Protocol (MCP) using FastMCP SDK.
"""

import json
import logging
from typing import Any

import boto3
from botocore.exceptions import ClientError
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Amazon Managed Prometheus MCP Server")


class WorkspaceInfo(BaseModel):
    """Model for workspace information"""

    workspace_id: str = Field(description="Workspace ID")
    alias: str | None = Field(description="Workspace alias")
    arn: str = Field(description="Workspace ARN")
    status: str = Field(description="Workspace status")
    prometheus_endpoint: str | None = Field(description="Prometheus endpoint URL")
    created_at: str = Field(description="Creation timestamp")
    tags: dict[str, str] = Field(default_factory=dict, description="Workspace tags")


class PrometheusClient:
    """Client for interacting with Amazon Managed Prometheus"""

    def __init__(self, region_name: str = "us-east-1"):
        """Initialize the Prometheus client"""
        try:
            self.aps_client = boto3.client("amp", region_name=region_name)
            self.region = region_name
            logger.info(f"Initialized Prometheus client for region: {region_name}")
        except Exception as e:
            logger.error(f"Failed to initialize AWS client: {e}")
            raise

    def list_workspaces(self) -> list[WorkspaceInfo]:
        """List all Prometheus workspaces"""
        try:
            response = self.aps_client.list_workspaces()
            workspaces = []

            for workspace in response.get("workspaces", []):
                # Handle different status formats
                status = workspace.get("status")
                if isinstance(status, dict):
                    status = status.get("statusCode", "UNKNOWN")

                # Handle datetime conversion
                created_at = workspace.get("createdAt")
                if hasattr(created_at, "isoformat"):
                    created_at = created_at.isoformat()
                else:
                    created_at = str(created_at)

                workspace_info = WorkspaceInfo(
                    workspace_id=workspace["workspaceId"],
                    alias=workspace.get("alias"),
                    arn=workspace["arn"],
                    status=status,
                    prometheus_endpoint=workspace.get("prometheusEndpoint"),
                    created_at=created_at,
                    tags=workspace.get("tags", {}),
                )
                workspaces.append(workspace_info)

            logger.info(f"Found {len(workspaces)} workspaces")
            return workspaces

        except ClientError as e:
            logger.error(f"AWS client error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error listing workspaces: {e}")
            raise

    def get_workspace(self, workspace_id: str) -> WorkspaceInfo:
        """Get detailed information about a specific workspace"""
        try:
            response = self.aps_client.describe_workspace(workspaceId=workspace_id)
            workspace = response["workspace"]

            # Handle different status formats
            status = workspace.get("status")
            if isinstance(status, dict):
                status = status.get("statusCode", "UNKNOWN")

            # Handle datetime conversion
            created_at = workspace.get("createdAt")
            if hasattr(created_at, "isoformat"):
                created_at = created_at.isoformat()
            else:
                created_at = str(created_at)

            workspace_info = WorkspaceInfo(
                workspace_id=workspace["workspaceId"],
                alias=workspace.get("alias"),
                arn=workspace["arn"],
                status=status,
                prometheus_endpoint=workspace.get("prometheusEndpoint"),
                created_at=created_at,
                tags=workspace.get("tags", {}),
            )

            logger.info(f"Retrieved workspace: {workspace_id}")
            return workspace_info

        except ClientError as e:
            logger.error(f"AWS client error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting workspace: {e}")
            raise

    def query_metrics(
        self,
        workspace_id: str,
        query: str,
        start_time: str | None = None,
        end_time: str | None = None,
        step: str | None = None,
    ) -> dict[str, Any]:
        """Execute a PromQL query against a workspace"""
        try:
            # Import here to avoid circular imports
            from .client import AuthenticatedPrometheusClient
            
            # Use authenticated client for actual queries
            auth_client = AuthenticatedPrometheusClient(self.region)
            result = auth_client.execute_query(
                workspace_id=workspace_id,
                query=query,
                start_time=start_time,
                end_time=end_time,
                step=step,
            )

            logger.info(f"Successfully executed query for workspace: {workspace_id}")
            return result

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise


# Initialize the Prometheus client
prometheus_client = PrometheusClient()


@mcp.tool()
def list_workspaces(region: str = "us-east-1") -> str:
    """
    List all Amazon Managed Prometheus workspaces in the specified region.

    Args:
        region: AWS region to query (default: us-east-1)

    Returns:
        JSON string containing list of workspaces with their details
    """
    try:
        # Create client for the specified region if different
        if region != prometheus_client.region:
            client = PrometheusClient(region)
        else:
            client = prometheus_client

        workspaces = client.list_workspaces()

        # Convert to dict for JSON serialization
        workspaces_dict = [workspace.model_dump() for workspace in workspaces]

        return json.dumps(
            {
                "region": region,
                "count": len(workspaces_dict),
                "workspaces": workspaces_dict,
            },
            indent=2,
        )

    except Exception as e:
        error_msg = f"Failed to list workspaces: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


@mcp.tool()
def get_workspace(workspace_id: str, region: str = "us-east-1") -> str:
    """
    Get detailed information about a specific Amazon Managed Prometheus workspace.

    Args:
        workspace_id: The ID of the workspace to retrieve
        region: AWS region where the workspace is located (default: us-east-1)

    Returns:
        JSON string containing workspace details
    """
    try:
        # Create client for the specified region if different
        if region != prometheus_client.region:
            client = PrometheusClient(region)
        else:
            client = prometheus_client

        workspace = client.get_workspace(workspace_id)

        return json.dumps({"workspace": workspace.model_dump()}, indent=2)

    except Exception as e:
        error_msg = f"Failed to get workspace {workspace_id}: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


@mcp.tool()
def query_metrics(
    workspace_id: str,
    query: str,
    region: str = "us-east-1",
    start_time: str | None = None,
    end_time: str | None = None,
    step: str | None = None,
) -> str:
    """
    Execute a PromQL query against an Amazon Managed Prometheus workspace.

    Args:
        workspace_id: The ID of the workspace to query
        query: PromQL query string
        region: AWS region where the workspace is located (default: us-east-1)
        start_time: Start time for range queries (RFC3339 format)
        end_time: End time for range queries (RFC3339 format)
        step: Query resolution step for range queries (e.g., "15s", "1m")

    Returns:
        JSON string containing query results or preparation details
    """
    try:
        # Create client for the specified region if different
        if region != prometheus_client.region:
            client = PrometheusClient(region)
        else:
            client = prometheus_client

        result = client.query_metrics(
            workspace_id=workspace_id,
            query=query,
            start_time=start_time,
            end_time=end_time,
            step=step,
        )

        return json.dumps(result, indent=2)

    except Exception as e:
        error_msg = f"Failed to query metrics: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


@mcp.tool()
def get_workspace_status(workspace_id: str, region: str = "us-east-1") -> str:
    """
    Get the current status of an Amazon Managed Prometheus workspace.

    Args:
        workspace_id: The ID of the workspace
        region: AWS region where the workspace is located (default: us-east-1)

    Returns:
        JSON string containing workspace status information
    """
    try:
        # Create client for the specified region if different
        if region != prometheus_client.region:
            client = PrometheusClient(region)
        else:
            client = prometheus_client

        workspace = client.get_workspace(workspace_id)

        status_info = {
            "workspace_id": workspace.workspace_id,
            "status": workspace.status,
            "alias": workspace.alias,
            "prometheus_endpoint": workspace.prometheus_endpoint,
            "created_at": workspace.created_at,
            "has_endpoint": workspace.prometheus_endpoint is not None,
        }

        return json.dumps(status_info, indent=2)

    except Exception as e:
        error_msg = f"Failed to get workspace status: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


def main() -> None:
    """Main entry point for the MCP server"""
    logger.info("Starting Amazon Managed Prometheus MCP Server")
    mcp.run()


if __name__ == "__main__":
    main()
