# Amazon Managed Prometheus MCP Server

An MCP (Model Context Protocol) server that provides access to Amazon Managed Prometheus workspaces using the FastMCP SDK and `uv` for fast Python package management.

<a href="https://glama.ai/mcp/servers/@sigitp-git/prometheus-mcp-server">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@sigitp-git/prometheus-mcp-server/badge" alt="Amazon Managed Prometheus Server MCP server" />
</a>

## Features

- List Amazon Managed Prometheus workspaces
- Get workspace details and configuration
- Query metrics from Prometheus workspaces
- Execute PromQL queries
- Get workspace status and metadata
- Fast dependency management with `uv`

## Prerequisites

1. **Install uv** (if not already installed):
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Or with pip
   pip install uv
   ```

2. **AWS Credentials**: Configure AWS credentials (one of the following):
   - AWS CLI: `aws configure`
   - Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
   - IAM roles (if running on EC2)

## Installation

### Quick Start with uv

```bash
# Clone or navigate to the project directory
cd prometheus-mcp-server

# Create virtual environment and install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows

# Run the server
uv run prometheus-mcp-server
```

### Development Installation

```bash
# Install with development dependencies
uv sync --extra dev

# Install with test dependencies
uv sync --extra test

# Install all optional dependencies
uv sync --all-extras
```

### Alternative Installation Methods

```bash
# Install in editable mode
uv pip install -e .

# Install from PyPI (when published)
uv pip install prometheus-mcp-server

# Install specific version
uv pip install prometheus-mcp-server==0.1.0
```

## Usage

### Running the MCP Server

```bash
# Using uv run (recommended)
uv run prometheus-mcp-server

# Or after activating virtual environment
prometheus-mcp-server

# Run with specific region
AWS_REGION=us-west-2 uv run prometheus-mcp-server
```

### Testing the Server

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=prometheus_mcp_server

# Run integration tests
uv run python test_demo.py

# Run simple server test
uv run python src/prometheus_mcp_server/simple_server.py
```

### Development Commands

```bash
# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type checking
uv run mypy src/

# Run all quality checks
uv run black --check src/ tests/
uv run isort --check-only src/ tests/
uv run ruff check src/ tests/
uv run mypy src/
uv run pytest
```

## Required AWS Permissions

The server requires the following AWS permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "aps:ListWorkspaces",
                "aps:DescribeWorkspace",
                "aps:QueryMetrics"
            ],
            "Resource": "*"
        }
    ]
}
```

## Available Tools

- `list_workspaces`: List all Amazon Managed Prometheus workspaces
- `get_workspace`: Get detailed information about a specific workspace
- `query_metrics`: Execute PromQL queries against a workspace
- `get_workspace_status`: Get the current status of a workspace

## Configuration

### Environment Variables

```bash
# AWS Configuration
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key

# Optional: Enable debug logging
export LOG_LEVEL=DEBUG
```

### MCP Client Configuration

Example configuration for MCP clients:

```json
{
  "mcpServers": {
    "prometheus": {
      "command": "uv",
      "args": [
        "run", 
        "--directory", 
        "/path/to/prometheus-mcp-server",
        "prometheus-mcp-server"
      ],
      "env": {
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

## Development with uv

### Adding Dependencies

```bash
# Add runtime dependency
uv add boto3

# Add development dependency
uv add --dev pytest

# Add optional dependency
uv add --optional test pytest-mock
```

### Managing Python Versions

```bash
# Use specific Python version
uv python install 3.11
uv sync --python 3.11

# List available Python versions
uv python list
```

### Virtual Environment Management

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Deactivate
deactivate

# Remove virtual environment
rm -rf .venv
```

## Project Structure

```
prometheus-mcp-server/
├── src/prometheus_mcp_server/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # Main MCP server with FastMCP tools
│   ├── auth.py              # AWS SigV4 authentication utilities
│   ├── client.py            # Enhanced client with authentication
│   └── simple_server.py     # Simple test server
├── tests/
│   ├── test_prometheus_server.py  # Original unit tests
│   └── test_simple_server.py      # Simple server tests
├── examples/
│   ├── example_usage.py     # Usage examples
│   └── mcp_config.json      # MCP client configuration
├── pyproject.toml           # Project configuration with uv support
├── .python-version          # Python version specification
├── README.md                # This file
├── test_demo.py            # Comprehensive test demonstration
└── TEST_RESULTS.md         # Test results documentation
```

## Performance Benefits with uv

- **Fast Installation**: Up to 10-100x faster than pip
- **Reliable Resolution**: Better dependency resolution
- **Disk Efficient**: Shared package cache
- **Reproducible Builds**: Lock file ensures consistency
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Troubleshooting

### Common Issues

1. **FastMCP not found**: 
   ```bash
   # Install FastMCP from GitHub
   uv add git+https://github.com/jlowin/fastmcp.git
   ```

2. **AWS Credentials Error**:
   ```bash
   # Configure AWS credentials
   aws configure
   # or set environment variables
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   ```

3. **Permission Denied**:
   - Ensure IAM user/role has required AMP permissions
   - Check AWS region configuration

### Debug Mode

```bash
# Enable verbose logging
LOG_LEVEL=DEBUG uv run prometheus-mcp-server

# Run with AWS debug
AWS_DEBUG=1 uv run prometheus-mcp-server
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Install development dependencies: `uv sync --extra dev`
4. Make your changes
5. Run tests: `uv run pytest`
6. Run quality checks: `uv run black src/ && uv run ruff check src/`
7. Commit your changes: `git commit -am 'Add feature'`
8. Push to the branch: `git push origin feature-name`
9. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### v0.1.0
- Initial release
- Basic workspace listing and querying
- AWS authentication support
- Multi-region support
- uv package management integration