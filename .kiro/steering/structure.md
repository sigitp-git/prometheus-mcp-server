# Project Structure & Organization

## Directory Layout

```
prometheus-mcp-server/
├── src/prometheus_mcp_server/     # Main source package
│   ├── __init__.py               # Package initialization & metadata
│   ├── main.py                   # FastMCP server with MCP tools
│   ├── client.py                 # Enhanced authenticated Prometheus client
│   ├── auth.py                   # AWS SigV4 authentication utilities
│   └── simple_server.py          # Simple test server implementation
├── tests/                        # Unit tests
│   ├── test_prometheus_server.py # Core functionality tests
│   └── test_simple_server.py     # Simple server tests
├── examples/                     # Usage examples & demos
│   ├── example_usage.py          # Programmatic usage examples
│   └── mcp_config.json           # MCP client configuration example
├── scripts/                      # Development scripts
│   ├── setup-dev.sh              # Unix development setup
│   └── setup-dev.ps1             # Windows development setup
├── .kiro/steering/               # AI assistant steering rules
├── pyproject.toml                # Modern Python project configuration
├── uv.lock                       # Dependency lock file
├── Makefile                      # Development automation
├── test_demo.py                  # Comprehensive integration test
└── README.md                     # Project documentation
```

## Architecture Patterns

### Core Components
- **main.py**: FastMCP server entry point with MCP tool definitions
- **client.py**: Enhanced client with AWS authentication for actual Prometheus queries
- **auth.py**: AWS SigV4 authentication utilities for secure API access
- **simple_server.py**: Lightweight test server for development

### Data Models
- **WorkspaceInfo**: Pydantic model for workspace metadata
- Type-safe data validation using Pydantic v2
- JSON serialization for MCP protocol responses

### Error Handling
- Comprehensive exception handling with proper logging
- AWS ClientError handling for API failures
- Graceful degradation for missing workspace endpoints

## Code Organization Principles

### Module Responsibilities
- **main.py**: MCP protocol implementation, tool definitions, high-level orchestration
- **client.py**: Low-level Prometheus API interactions, authentication
- **auth.py**: AWS-specific authentication logic
- **models**: Data validation and serialization (embedded in main.py)

### Import Patterns
- Relative imports within package (`from .auth import PrometheusAuth`)
- Lazy imports for optional dependencies to avoid circular imports
- Standard library imports first, then third-party, then local

### Testing Structure
- Unit tests in `tests/` directory mirror source structure
- Integration tests as standalone scripts (`test_demo.py`)
- Examples serve as both documentation and integration tests

## Configuration Management
- **pyproject.toml**: Single source of truth for project metadata
- **uv.lock**: Reproducible dependency resolution
- Environment variables for AWS configuration
- No hardcoded configuration values in source code

## Entry Points
- **CLI**: `prometheus-mcp-server` command via `project.scripts`
- **Programmatic**: Import from `prometheus_mcp_server.main`
- **Development**: Direct execution of modules for testing