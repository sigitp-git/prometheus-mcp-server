# Technology Stack

## Build System & Package Management
- **Primary**: `uv` - Fast Python package manager (10-100x faster than pip)
- **Build Backend**: Hatchling (modern Python packaging)
- **Configuration**: `pyproject.toml` (modern Python project configuration)
- **Legacy Support**: `setup.py` (deprecated, use `uv sync` instead)

## Core Dependencies
- **FastMCP SDK**: MCP protocol implementation (`fastmcp>=0.2.0`)
- **AWS SDK**: `boto3>=1.26.0` for AWS API interactions
- **HTTP Client**: `requests>=2.28.0` for Prometheus API calls
- **Data Validation**: `pydantic>=2.0.0` for type-safe data models

## Development Tools
- **Testing**: pytest with coverage support
- **Code Formatting**: black (line length: 88)
- **Import Sorting**: isort (black-compatible profile)
- **Linting**: ruff (fast Python linter)
- **Type Checking**: mypy with strict configuration

## Python Requirements
- **Minimum Version**: Python 3.10+
- **Supported Versions**: 3.10, 3.11, 3.12
- **Virtual Environment**: Managed by `uv`

## Common Commands

### Installation & Setup
```bash
# Install dependencies
uv sync

# Install with development dependencies
uv sync --extra dev --extra test

# Install all optional dependencies
uv sync --all-extras
```

### Development Workflow
```bash
# Run the MCP server
uv run prometheus-mcp-server

# Run tests
uv run pytest
uv run pytest --cov=prometheus_mcp_server

# Code quality checks
uv run black src/ tests/           # Format code
uv run isort src/ tests/           # Sort imports
uv run ruff check src/ tests/      # Lint code
uv run mypy src/                   # Type check

# Combined quality check
make check
```

### Testing & Validation
```bash
# Run comprehensive test demo
uv run python test_demo.py

# Run simple server test
uv run python src/prometheus_mcp_server/simple_server.py

# Integration tests
uv run python examples/example_usage.py
```

### Build & Distribution
```bash
# Build package
uv build

# Clean build artifacts
make clean
```

## AWS Configuration
- **Authentication**: AWS credentials via CLI, environment variables, or IAM roles
- **Required Permissions**: `aps:ListWorkspaces`, `aps:DescribeWorkspace`, `aps:QueryMetrics`
- **Regions**: Multi-region support with configurable default (us-east-1)