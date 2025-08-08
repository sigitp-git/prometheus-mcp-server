#!/usr/bin/env python3
"""
Tests for the simple Amazon Managed Prometheus server.
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from prometheus_mcp_server.simple_server import (
    PrometheusClient,
    PrometheusTestServer,
    WorkspaceInfo,
)


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
            alias=None,
            arn="arn:aws:aps:us-east-1:123456789012:workspace/ws-12345",
            status="ACTIVE",
            prometheus_endpoint=None,
            created_at="2023-01-01T00:00:00Z",
        )

        assert workspace.workspace_id == "ws-12345"
        assert workspace.alias is None
        assert workspace.prometheus_endpoint is None
        assert workspace.tags == {}


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

        # Mock response with status as dict (like real AWS API)
        mock_response = {
            "workspaces": [
                {
                    "workspaceId": "ws-12345",
                    "alias": "test-workspace",
                    "arn": "arn:aws:aps:us-east-1:123456789012:workspace/ws-12345",
                    "status": {"statusCode": "ACTIVE"},
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
        assert workspace.status == "ACTIVE"  # Should extract statusCode
        assert workspace.tags == {"Environment": "test"}

    @patch("boto3.client")
    def test_get_workspace(self, mock_boto_client):
        """Test getting a specific workspace"""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        # Mock response with status as dict
        mock_response = {
            "workspace": {
                "workspaceId": "ws-12345",
                "alias": "test-workspace",
                "arn": "arn:aws:aps:us-east-1:123456789012:workspace/ws-12345",
                "status": {"statusCode": "ACTIVE"},
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


class TestPrometheusTestServer:
    """Test cases for PrometheusTestServer"""

    @patch("prometheus_mcp_server.simple_server.PrometheusClient")
    def test_test_connection_success(self, mock_client_class):
        """Test successful connection test"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.aps_client.list_workspaces.return_value = {
            "workspaces": [{"workspaceId": "ws-123"}]
        }

        server = PrometheusTestServer("us-east-1")
        result = server.test_connection()

        assert result["status"] == "success"
        assert result["region"] == "us-east-1"
        assert result["workspace_count"] == 1

    @patch("prometheus_mcp_server.simple_server.PrometheusClient")
    def test_test_list_workspaces_success(self, mock_client_class):
        """Test successful workspace listing"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_workspace = WorkspaceInfo(
            workspace_id="ws-12345",
            alias=None,
            arn="arn:aws:aps:us-east-1:123456789012:workspace/ws-12345",
            status="ACTIVE",
            prometheus_endpoint=None,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_client.list_workspaces.return_value = [mock_workspace]

        server = PrometheusTestServer("us-east-1")
        result = server.test_list_workspaces()

        assert result["status"] == "success"
        assert result["count"] == 1
        assert len(result["workspaces"]) == 1
        assert result["workspaces"][0]["workspace_id"] == "ws-12345"

    @patch("prometheus_mcp_server.simple_server.PrometheusClient")
    def test_test_get_workspace_success(self, mock_client_class):
        """Test successful workspace retrieval"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_workspace = WorkspaceInfo(
            workspace_id="ws-12345",
            alias=None,
            arn="arn:aws:aps:us-east-1:123456789012:workspace/ws-12345",
            status="ACTIVE",
            prometheus_endpoint=None,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_client.get_workspace.return_value = mock_workspace

        server = PrometheusTestServer("us-east-1")
        result = server.test_get_workspace("ws-12345")

        assert result["status"] == "success"
        assert result["workspace_id"] == "ws-12345"
        assert result["workspace"]["workspace_id"] == "ws-12345"


if __name__ == "__main__":
    pytest.main([__file__])
