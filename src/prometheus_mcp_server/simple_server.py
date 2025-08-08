#!/usr/bin/env python3
"""
Simple Amazon Managed Prometheus Server for Testing

This is a simplified version that can be tested without external MCP dependencies.
It implements the core functionality for interacting with Amazon Managed Prometheus.
"""

import json
import logging
import sys
from typing import Any

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


class PrometheusTestServer:
    """Test server for Amazon Managed Prometheus functionality"""

    def __init__(self, region: str = "us-east-1"):
        """Initialize the test server"""
        self.client = PrometheusClient(region)
        self.region = region

    def test_list_workspaces(self) -> dict[str, Any]:
        """Test listing workspaces"""
        try:
            workspaces = self.client.list_workspaces()
            workspaces_dict = [workspace.model_dump() for workspace in workspaces]

            return {
                "test": "list_workspaces",
                "status": "success",
                "region": self.region,
                "count": len(workspaces_dict),
                "workspaces": workspaces_dict,
            }
        except Exception as e:
            return {"test": "list_workspaces", "status": "error", "error": str(e)}

    def test_get_workspace(self, workspace_id: str) -> dict[str, Any]:
        """Test getting a specific workspace"""
        try:
            workspace = self.client.get_workspace(workspace_id)

            return {
                "test": "get_workspace",
                "status": "success",
                "workspace_id": workspace_id,
                "workspace": workspace.model_dump(),
            }
        except Exception as e:
            return {
                "test": "get_workspace",
                "status": "error",
                "workspace_id": workspace_id,
                "error": str(e),
            }

    def test_connection(self) -> dict[str, Any]:
        """Test AWS connection and permissions"""
        try:
            # Try to list workspaces to test connection
            response = self.client.aps_client.list_workspaces()

            return {
                "test": "connection",
                "status": "success",
                "region": self.region,
                "message": "Successfully connected to Amazon Managed Prometheus",
                "workspace_count": len(response.get("workspaces", [])),
            }
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))

            return {
                "test": "connection",
                "status": "error",
                "region": self.region,
                "error_code": error_code,
                "error_message": error_message,
                "suggestion": self._get_error_suggestion(error_code),
            }
        except Exception as e:
            return {
                "test": "connection",
                "status": "error",
                "region": self.region,
                "error": str(e),
            }

    def _get_error_suggestion(self, error_code: str) -> str:
        """Get suggestion based on error code"""
        suggestions = {
            "UnauthorizedOperation": "Check AWS credentials and IAM permissions for AMP",
            "AccessDenied": "Ensure IAM user/role has aps:ListWorkspaces permission",
            "InvalidUserID.NotFound": "Check AWS credentials configuration",
            "NoCredentialsError": "Configure AWS credentials using 'aws configure' or environment variables",
        }
        return suggestions.get(error_code, "Check AWS credentials and permissions")

    def run_all_tests(self) -> dict[str, Any]:
        """Run all available tests"""
        results = {
            "test_suite": "Amazon Managed Prometheus MCP Server",
            "region": self.region,
            "tests": {},
        }

        # Test connection
        print("Testing AWS connection...")
        connection_result = self.test_connection()
        results["tests"]["connection"] = connection_result
        print(f"Connection test: {connection_result['status']}")

        if connection_result["status"] == "success":
            # Test listing workspaces
            print("Testing workspace listing...")
            list_result = self.test_list_workspaces()
            results["tests"]["list_workspaces"] = list_result
            print(f"List workspaces test: {list_result['status']}")

            # If we have workspaces, test getting one
            if list_result["status"] == "success" and list_result["count"] > 0:
                workspace_id = list_result["workspaces"][0]["workspace_id"]
                print(f"Testing workspace details for: {workspace_id}")
                get_result = self.test_get_workspace(workspace_id)
                results["tests"]["get_workspace"] = get_result
                print(f"Get workspace test: {get_result['status']}")

        return results


def main():
    """Main function for testing"""
    print("Amazon Managed Prometheus MCP Server - Test Mode")
    print("=" * 60)

    # Check for region argument
    region = "us-east-1"
    if len(sys.argv) > 1:
        region = sys.argv[1]

    print(f"Testing in region: {region}")
    print()

    # Create test server
    test_server = PrometheusTestServer(region)

    # Run tests
    results = test_server.run_all_tests()

    # Print results
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(json.dumps(results, indent=2))

    # Summary
    total_tests = len(results["tests"])
    successful_tests = sum(
        1 for test in results["tests"].values() if test["status"] == "success"
    )

    print(f"\nSummary: {successful_tests}/{total_tests} tests passed")

    if successful_tests == total_tests:
        print("✅ All tests passed! The MCP server is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the results above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
