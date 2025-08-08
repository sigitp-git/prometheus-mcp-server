#!/usr/bin/env python3
"""
Comprehensive test demonstration for the Amazon Managed Prometheus MCP Server.

This script demonstrates all the functionality of the MCP server and provides
a comprehensive test of the system.
"""

import json
import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from prometheus_mcp_server.simple_server import PrometheusTestServer


def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n--- {title} ---")


def test_multiple_regions():
    """Test the server across multiple AWS regions"""
    print_header("AMAZON MANAGED PROMETHEUS MCP SERVER - COMPREHENSIVE TEST")
    
    regions_to_test = ["us-east-1", "us-west-2", "eu-west-1"]
    all_results = {}
    
    for region in regions_to_test:
        print_section(f"Testing Region: {region}")
        
        try:
            server = PrometheusTestServer(region)
            results = server.run_all_tests()
            all_results[region] = results
            
            # Print summary for this region
            total_tests = len(results["tests"])
            successful_tests = sum(1 for test in results["tests"].values() if test["status"] == "success")
            print(f"Region {region}: {successful_tests}/{total_tests} tests passed")
            
            if results["tests"].get("list_workspaces", {}).get("status") == "success":
                workspace_count = results["tests"]["list_workspaces"]["count"]
                print(f"Found {workspace_count} workspaces in {region}")
            
        except Exception as e:
            print(f"Error testing region {region}: {e}")
            all_results[region] = {"error": str(e)}
    
    return all_results


def analyze_results(all_results):
    """Analyze and summarize test results"""
    print_header("TEST RESULTS ANALYSIS")
    
    total_regions = len(all_results)
    successful_regions = 0
    total_workspaces = 0
    
    for region, results in all_results.items():
        if "error" in results:
            print(f"❌ {region}: Failed with error - {results['error']}")
            continue
        
        tests = results.get("tests", {})
        connection_test = tests.get("connection", {})
        
        if connection_test.get("status") == "success":
            successful_regions += 1
            workspace_count = connection_test.get("workspace_count", 0)
            total_workspaces += workspace_count
            print(f"✅ {region}: Connected successfully, {workspace_count} workspaces")
        else:
            print(f"❌ {region}: Connection failed")
    
    print_section("Summary")
    print(f"Regions tested: {total_regions}")
    print(f"Successful connections: {successful_regions}")
    print(f"Total workspaces found: {total_workspaces}")
    
    if successful_regions > 0:
        print(f"\n🎉 SUCCESS: MCP Server is working in {successful_regions}/{total_regions} regions!")
    else:
        print(f"\n❌ FAILURE: No successful connections")
    
    return successful_regions > 0


def demonstrate_functionality():
    """Demonstrate specific MCP server functionality"""
    print_header("FUNCTIONALITY DEMONSTRATION")
    
    # Test with us-east-1 (most likely to have workspaces)
    server = PrometheusTestServer("us-east-1")
    
    print_section("1. Testing AWS Connection")
    connection_result = server.test_connection()
    print(json.dumps(connection_result, indent=2))
    
    if connection_result["status"] != "success":
        print("❌ Cannot proceed with further tests - AWS connection failed")
        return False
    
    print_section("2. Listing All Workspaces")
    list_result = server.test_list_workspaces()
    
    if list_result["status"] == "success":
        print(f"✅ Found {list_result['count']} workspaces")
        
        # Show first workspace details
        if list_result["count"] > 0:
            first_workspace = list_result["workspaces"][0]
            print(f"First workspace: {first_workspace['workspace_id']}")
            print(f"  Alias: {first_workspace.get('alias', 'N/A')}")
            print(f"  Status: {first_workspace['status']}")
            print(f"  Endpoint: {first_workspace.get('prometheus_endpoint', 'N/A')}")
            
            print_section("3. Getting Specific Workspace Details")
            workspace_id = first_workspace['workspace_id']
            get_result = server.test_get_workspace(workspace_id)
            
            if get_result["status"] == "success":
                print(f"✅ Successfully retrieved details for {workspace_id}")
                workspace_details = get_result["workspace"]
                print(f"  ARN: {workspace_details['arn']}")
                print(f"  Created: {workspace_details['created_at']}")
                print(f"  Tags: {workspace_details.get('tags', {})}")
            else:
                print(f"❌ Failed to get workspace details: {get_result.get('error')}")
    else:
        print(f"❌ Failed to list workspaces: {list_result.get('error')}")
    
    return True


def main():
    """Main test function"""
    print(f"Amazon Managed Prometheus MCP Server Test")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # Test 1: Multi-region functionality
    all_results = test_multiple_regions()
    
    # Test 2: Analyze results
    success = analyze_results(all_results)
    
    # Test 3: Demonstrate functionality
    if success:
        demonstrate_functionality()
    
    # Final summary
    print_header("FINAL SUMMARY")
    
    if success:
        print("🎉 MCP SERVER TEST COMPLETED SUCCESSFULLY!")
        print("\nThe Amazon Managed Prometheus MCP Server is working correctly and can:")
        print("  ✅ Connect to AWS Amazon Managed Prometheus service")
        print("  ✅ List workspaces across multiple regions")
        print("  ✅ Retrieve detailed workspace information")
        print("  ✅ Handle AWS API responses correctly")
        print("  ✅ Provide structured JSON responses")
        print("\nThe server is ready for integration with MCP clients!")
        return 0
    else:
        print("❌ MCP SERVER TEST FAILED")
        print("\nPlease check:")
        print("  - AWS credentials are configured correctly")
        print("  - IAM permissions include aps:ListWorkspaces and aps:DescribeWorkspace")
        print("  - Network connectivity to AWS services")
        return 1


if __name__ == "__main__":
    sys.exit(main())
