#!/usr/bin/env python3
"""
Tests for the Amazon Managed Prometheus MCP Server.
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from prometheus_mcp_server.client import AuthenticatedPrometheusClient
from prometheus_mcp_server.main import PrometheusClient, WorkspaceInfo


class TestPrometheusClient:
    """Test cases for PrometheusClient"""

    @patch("boto3.client")
    def test_init(self, mock_boto_client):
        """Test client initialization"""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        client = PrometheusClient("us-west-2")

        assert client.region == "us-west-2"
        mock_boto_client.assert_called_once_with("amp", region_name="us-west-2")

    @patch("boto3.client")
    def test_list_workspaces(self, mock_boto_client):
        """Test listing workspaces"""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        # Mock response
        mock_response = {
            "workspaces": [
                {
                    "workspaceId": "ws-12345",
                    "alias": "test-workspace",
                    "arn": "arn:aws:aps:us-east-1:123456789012:workspace/ws-12345",
                    "status": "ACTIVE",
                    "prometheusEndpoint": "https://aps-workspaces.us-east-1.amazonaws.com/workspaces/ws-12345",
                    "createdAt": "2023-01-01T00:00:00Z",
                    "tags": {"Environment": "test"},
                }
            ]
        }
        mock_client.list_workspaces.return_value = mock_response

        client = PrometheusClient()
        workspaces = client.list_workspaces()

        assert len(workspaces) == 1
        workspace = workspaces[0]
        assert workspace.workspace_id == "ws-12345"
        assert workspace.alias == "test-workspace"
        assert workspace.status == "ACTIVE"
        assert workspace.tags == {"Environment": "test"}

    @patch("boto3.client")
    def test_get_workspace(self, mock_boto_client):
        """Test getting a specific workspace"""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        # Mock response
        mock_response = {
            "workspace": {
                "workspaceId": "ws-12345",
                "alias": "test-workspace",
                "arn": "arn:aws:aps:us-east-1:123456789012:workspace/ws-12345",
                "status": "ACTIVE",
                "prometheusEndpoint": "https://aps-workspaces.us-east-1.amazonaws.com/workspaces/ws-12345",
                "createdAt": "2023-01-01T00:00:00Z",
                "tags": {"Environment": "test"},
            }
        }
        mock_client.describe_workspace.return_value = mock_response

        client = PrometheusClient()
        workspace = client.get_workspace("ws-12345")

        assert workspace.workspace_id == "ws-12345"
        assert workspace.alias == "test-workspace"
        assert workspace.status == "ACTIVE"
        mock_client.describe_workspace.assert_called_once_with(workspaceId="ws-12345")


class TestWorkspaceInfo:
    """Test cases for WorkspaceInfo model"""

    def test_workspace_info_creation(self):
        """Test creating a WorkspaceInfo instance"""
        workspace = WorkspaceInfo(
            workspace_id="ws-12345",
            alias="test-workspace",
            arn="arn:aws:aps:us-east-1:123456789012:workspace/ws-12345",
            status="ACTIVE",
            prometheus_endpoint="https://aps-workspaces.us-east-1.amazonaws.com/workspaces/ws-12345",
            created_at="2023-01-01T00:00:00Z",
            tags={"Environment": "test"},
        )

        assert workspace.workspace_id == "ws-12345"
        assert workspace.alias == "test-workspace"
        assert workspace.status == "ACTIVE"
        assert workspace.tags == {"Environment": "test"}

    def test_workspace_info_optional_fields(self):
        """Test WorkspaceInfo with optional fields"""
        workspace = WorkspaceInfo(
            workspace_id="ws-12345",
            arn="arn:aws:aps:us-east-1:123456789012:workspace/ws-12345",
            status="ACTIVE",
            created_at="2023-01-01T00:00:00Z",
        )

        assert workspace.workspace_id == "ws-12345"
        assert workspace.alias is None
        assert workspace.prometheus_endpoint is None
        assert workspace.tags == {}


class TestAuthenticatedPrometheusClient:
    """Test cases for AuthenticatedPrometheusClient"""

    @patch("prometheus_mcp_server.client.PrometheusAuth")
    @patch("boto3.client")
    def test_init(self, mock_boto_client, mock_auth):
        """Test authenticated client initialization"""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        mock_auth_instance = Mock()
        mock_auth.return_value = mock_auth_instance

        client = AuthenticatedPrometheusClient("us-west-2")

        assert client.region == "us-west-2"
        mock_auth.assert_called_once_with("us-west-2")

    @patch("requests.get")
    @patch("prometheus_mcp_server.client.PrometheusAuth")
    @patch("boto3.client")
    def test_execute_query_instant(
        self, mock_boto_client, mock_auth, mock_requests_get
    ):
        """Test executing an instant query"""
        # Setup mocks
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        mock_auth_instance = Mock()
        mock_auth.return_value = mock_auth_instance
        mock_auth_instance.get_signed_headers.return_value = {
            "Authorization": "AWS4-HMAC-SHA256 ..."
        }

        # Mock workspace response
        mock_workspace_response = {
            "workspace": {
                "workspaceId": "ws-12345",
                "arn": "arn:aws:aps:us-east-1:123456789012:workspace/ws-12345",
                "status": "ACTIVE",
                "prometheusEndpoint": "https://aps-workspaces.us-east-1.amazonaws.com/workspaces/ws-12345",
                "createdAt": "2023-01-01T00:00:00Z",
            }
        }
        mock_client.describe_workspace.return_value = mock_workspace_response

        # Mock HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "data": {"resultType": "vector", "result": []},
        }
        mock_requests_get.return_value = mock_response

        client = AuthenticatedPrometheusClient()
        result = client.execute_query("ws-12345", "up")

        assert result["workspace_id"] == "ws-12345"
        assert result["query"] == "up"
        assert result["status"] == "success"
        mock_requests_get.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
