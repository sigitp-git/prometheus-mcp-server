#!/usr/bin/env python3
"""
Example usage of the Amazon Managed Prometheus MCP Server.

This script demonstrates how to use the MCP server tools programmatically.
"""

import json
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from prometheus_mcp_server.main import prometheus_client
from prometheus_mcp_server.client import AuthenticatedPrometheusClient


def example_list_workspaces():
    """Example: List all workspaces"""
    print("=== Listing Workspaces ===")
    try:
        workspaces = prometheus_client.list_workspaces()
        for workspace in workspaces:
            print(f"Workspace: {workspace.workspace_id}")
            print(f"  Alias: {workspace.alias}")
            print(f"  Status: {workspace.status}")
            print(f"  Endpoint: {workspace.prometheus_endpoint}")
            print(f"  Created: {workspace.created_at}")
            print()
    except Exception as e:
        print(f"Error: {e}")


def example_get_workspace(workspace_id: str):
    """Example: Get specific workspace details"""
    print(f"=== Getting Workspace {workspace_id} ===")
    try:
        workspace = prometheus_client.get_workspace(workspace_id)
        print(f"Workspace Details:")
        print(f"  ID: {workspace.workspace_id}")
        print(f"  Alias: {workspace.alias}")
        print(f"  ARN: {workspace.arn}")
        print(f"  Status: {workspace.status}")
        print(f"  Endpoint: {workspace.prometheus_endpoint}")
        print(f"  Created: {workspace.created_at}")
        print(f"  Tags: {workspace.tags}")
        print()
    except Exception as e:
        print(f"Error: {e}")


def example_query_metrics(workspace_id: str):
    """Example: Query metrics from a workspace"""
    print(f"=== Querying Metrics from {workspace_id} ===")
    
    # Use the authenticated client for actual queries
    auth_client = AuthenticatedPrometheusClient()
    
    try:
        # Example instant query
        result = auth_client.execute_query(
            workspace_id=workspace_id,
            query="up"
        )
        print("Instant Query Result:")
        print(json.dumps(result, indent=2))
        print()
        
        # Example range query (last hour)
        from datetime import datetime, timedelta
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        result = auth_client.execute_query(
            workspace_id=workspace_id,
            query="rate(http_requests_total[5m])",
            start_time=start_time.isoformat() + "Z",
            end_time=end_time.isoformat() + "Z",
            step="1m"
        )
        print("Range Query Result:")
        print(json.dumps(result, indent=2))
        print()
        
    except Exception as e:
        print(f"Error: {e}")


def example_get_label_values(workspace_id: str):
    """Example: Get label values"""
    print(f"=== Getting Label Values from {workspace_id} ===")
    
    auth_client = AuthenticatedPrometheusClient()
    
    try:
        # Get all job label values
        job_values = auth_client.get_label_values(workspace_id, "job")
        print(f"Job label values: {job_values}")
        
        # Get all instance label values
        instance_values = auth_client.get_label_values(workspace_id, "instance")
        print(f"Instance label values: {instance_values}")
        print()
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main example function"""
    print("Amazon Managed Prometheus MCP Server Examples")
    print("=" * 50)
    
    # List all workspaces
    example_list_workspaces()
    
    # If you have a specific workspace ID, uncomment and modify these:
    # workspace_id = "ws-12345678-1234-1234-1234-123456789012"
    # example_get_workspace(workspace_id)
    # example_query_metrics(workspace_id)
    # example_get_label_values(workspace_id)
    
    print("Examples completed!")


if __name__ == "__main__":
    main()
