#!/bin/bash
# Development setup script for Amazon Managed Prometheus MCP Server

set -e

echo "🚀 Setting up Amazon Managed Prometheus MCP Server development environment"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed"
fi

# Check uv version
echo "📦 uv version: $(uv --version)"

# Install Python if needed
echo "🐍 Setting up Python..."
uv python install 3.9

# Create virtual environment and install dependencies
echo "📦 Installing dependencies..."
uv sync --all-extras

# Activate virtual environment and show info
echo "🔧 Virtual environment created at: .venv"

# Run initial tests to verify setup
echo "🧪 Running initial tests..."
if uv run pytest tests/test_simple_server.py -v; then
    echo "✅ Tests passed successfully"
else
    echo "❌ Some tests failed, but setup is complete"
fi

# Show next steps
echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Configure AWS credentials:"
echo "     aws configure"
echo "     # or set environment variables:"
echo "     export AWS_ACCESS_KEY_ID=your_key"
echo "     export AWS_SECRET_ACCESS_KEY=your_secret"
echo "     export AWS_REGION=us-east-1"
echo ""
echo "  3. Test the server:"
echo "     uv run python src/prometheus_mcp_server/simple_server.py"
echo ""
echo "  4. Run comprehensive tests:"
echo "     uv run python test_demo.py"
echo ""
echo "  5. Start development:"
echo "     uv run prometheus-mcp-server"
echo ""
echo "Available make commands:"
echo "  make help        - Show all available commands"
echo "  make test        - Run tests"
echo "  make format      - Format code"
echo "  make lint        - Run linting"
echo "  make run         - Run the server"
echo "  make demo        - Run test demonstration"
echo ""
