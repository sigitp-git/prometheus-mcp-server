# Development setup script for Amazon Managed Prometheus MCP Server (Windows)

Write-Host "🚀 Setting up Amazon Managed Prometheus MCP Server development environment" -ForegroundColor Green

# Check if uv is installed
try {
    $uvVersion = uv --version
    Write-Host "✅ uv is already installed: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ uv is not installed. Installing uv..." -ForegroundColor Yellow
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    Write-Host "✅ uv installed successfully" -ForegroundColor Green
}

# Install Python if needed
Write-Host "🐍 Setting up Python..." -ForegroundColor Blue
uv python install 3.9

# Create virtual environment and install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Blue
uv sync --all-extras

# Show virtual environment info
Write-Host "🔧 Virtual environment created at: .venv" -ForegroundColor Blue

# Run initial tests to verify setup
Write-Host "🧪 Running initial tests..." -ForegroundColor Blue
try {
    uv run pytest tests/test_simple_server.py -v
    Write-Host "✅ Tests passed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Some tests failed, but setup is complete" -ForegroundColor Yellow
}

# Show next steps
Write-Host ""
Write-Host "🎉 Development environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Activate the virtual environment:" -ForegroundColor White
Write-Host "     .venv\Scripts\activate" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Configure AWS credentials:" -ForegroundColor White
Write-Host "     aws configure" -ForegroundColor Gray
Write-Host "     # or set environment variables:" -ForegroundColor Gray
Write-Host "     `$env:AWS_ACCESS_KEY_ID='your_key'" -ForegroundColor Gray
Write-Host "     `$env:AWS_SECRET_ACCESS_KEY='your_secret'" -ForegroundColor Gray
Write-Host "     `$env:AWS_REGION='us-east-1'" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Test the server:" -ForegroundColor White
Write-Host "     uv run python src/prometheus_mcp_server/simple_server.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Run comprehensive tests:" -ForegroundColor White
Write-Host "     uv run python test_demo.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  5. Start development:" -ForegroundColor White
Write-Host "     uv run prometheus-mcp-server" -ForegroundColor Gray
Write-Host ""
Write-Host "Available make commands (if you have make installed):" -ForegroundColor Cyan
Write-Host "  make help        - Show all available commands" -ForegroundColor Gray
Write-Host "  make test        - Run tests" -ForegroundColor Gray
Write-Host "  make format      - Format code" -ForegroundColor Gray
Write-Host "  make lint        - Run linting" -ForegroundColor Gray
Write-Host "  make run         - Run the server" -ForegroundColor Gray
Write-Host "  make demo        - Run test demonstration" -ForegroundColor Gray
Write-Host ""
