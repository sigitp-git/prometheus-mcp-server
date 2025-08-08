#!/usr/bin/env python3
"""
Test script to verify MCP server can be started with the configuration
"""

import subprocess
import sys
import json
import os

def test_mcp_server():
    """Test if the MCP server can be started"""
    print("🧪 Testing MCP Server Configuration...")
    
    # Change to project directory
    project_dir = "/Users/sigitp/Library/CloudStorage/OneDrive-amazon.com/TIBU/CSE/environment/mcp/fastmcp-starter/prometheus-mcp-server"
    os.chdir(project_dir)
    
    try:
        # Test if we can import the module
        print("1. Testing module import...")
        result = subprocess.run([
            "uv", "run", "python", "-c", 
            "import prometheus_mcp_server.main; print('✅ Module import successful')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Module import test passed")
        else:
            print(f"❌ Module import failed: {result.stderr}")
            return False
            
        # Test if server can start (just check help)
        print("2. Testing server startup...")
        result = subprocess.run([
            "uv", "run", "python", "-m", "prometheus_mcp_server.main", "--help"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Server startup test passed")
            print("🎉 MCP Server is ready to use with Amazon Q!")
            return True
        else:
            print(f"❌ Server startup failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)
