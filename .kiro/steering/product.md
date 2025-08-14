# Product Overview

## Amazon Managed Prometheus MCP Server

A Model Context Protocol (MCP) server that provides programmatic access to Amazon Managed Prometheus workspaces. This server enables AI assistants and other MCP clients to interact with AWS Prometheus workspaces through a standardized interface.

### Core Functionality
- List and discover Amazon Managed Prometheus workspaces across AWS regions
- Retrieve detailed workspace information and metadata
- Execute PromQL queries against Prometheus workspaces with proper AWS SigV4 authentication
- Get workspace status and health information
- Support for both instant and range queries

### Key Features
- Multi-region support (us-east-1, us-west-2, eu-west-1, etc.)
- AWS SigV4 authentication for secure API access
- FastMCP SDK integration for efficient MCP protocol handling
- Comprehensive error handling and logging
- Support for workspace aliases, tags, and metadata

### Target Use Cases
- Monitoring and observability automation
- Prometheus workspace management through AI assistants
- Integration with MCP-compatible clients and tools
- Automated metric querying and analysis