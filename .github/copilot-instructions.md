# Copilot Instructions for MCP Deployment Manager

## Project Overview
This is a Python-based Model Context Protocol (MCP) server specialized in deployment and version management for .NET Core + Angular applications. The project provides a comprehensive system for tracking deployments, managing versions across environments, and automating deployment documentation.

## Development Patterns

### MCP Deployment Manager Architecture
- **Server Core**: Main MCP server in `src/mcp_server/server.py` implementing MCP protocol
- **Deployment Tools**: Tools in `src/tools/deployment/` for version and deployment management
- **Git Integration**: Tools in `src/tools/git/` for commit tracking and change analysis
- **Documentation Generator**: Automated wiki/markdown generation in `src/tools/documentation/`
- **Incident Management**: Post-deployment issue tracking in `src/tools/incidents/`
- **Streamlit Dashboard**: Web UI in `src/frontend/` specialized for deployment visualization
- **Data Models**: Deployment and version models in `src/models/`
- **Configuration**: Environment configs in `config/environments/`

### Code Organization
```
src/
├── mcp_server/          # Core MCP server implementation
├── tools/               # MCP tools organized by domain
│   ├── deployment/      # Deployment management tools
│   ├── git/            # Git integration tools
│   ├── documentation/  # Documentation generation tools
│   └── incidents/      # Incident tracking tools
├── models/             # Data models for deployments and versions
├── frontend/           # Streamlit deployment dashboard
├── schemas/            # MCP protocol schemas and validators
└── utils/              # Shared utilities and helpers
```

### Key Conventions
- **MCP Protocol Compliance**: Follow MCP specification for tool registration and client communication
- **Async First**: All server operations use `async/await` patterns
- **Type Hints**: Mandatory for all function signatures and class attributes
- **Error Handling**: Use MCP-compliant error responses in `src/exceptions.py`
- **Logging**: Structured logging with request context using `src/utils/logging.py`

### Tool Development
- Implement MCP tool interface with proper JSON schemas
- Include tool metadata: name, description, input/output schemas
- Add comprehensive docstrings with usage examples
- Register tools in `src/tools/registry.py` with MCP manifest generation
- Validate tool inputs/outputs against schemas

### Testing Strategy
- Unit tests in `tests/unit/` mirror `src/` structure
- Integration tests in `tests/integration/` for MCP protocol compliance
- Streamlit app tests in `tests/frontend/`
- Use `pytest-asyncio` for async test support
- Mock MCP clients using `tests/fixtures/`

### Environment Setup
- Python 3.10+ required
- Virtual environment: `python -m venv venv`
- Dependencies: `pip install -r requirements.txt`
- Development setup: `pip install -r requirements-dev.txt`

### Configuration Management
- Environment variables in `.env` (not committed)
- Agent configurations in `config/agents/*.yaml`
- Model settings in `config/models.yaml`
- Use `src/config/loader.py` for configuration access

### Environment Setup
- Python 3.10+ required
- Virtual environment: `python -m venv venv`
- Dependencies: `pip install -r requirements.txt` (includes mcp, streamlit, pydantic)
- Development setup: `pip install -r requirements-dev.txt`
- Start MCP server: `python -m src.mcp_server.main`
- Run Streamlit frontend: `streamlit run src/frontend/app.py`

### Configuration Management
- Environment variables in `.env` (not committed)
- MCP server config in `config/server.yaml`
- Tool configurations in `config/tools/`
- Use `src/config/loader.py` for configuration access

### Cloud Deployment Patterns
- **Containerization**: Dockerfile for MCP server and Streamlit app
- **Cloud Platforms**: Deploy to Railway, Render, or Heroku
- **Environment Variables**: Use platform-specific env var management
- **Health Checks**: Implement `/health` endpoint for monitoring
- **Logging**: Cloud-compatible structured logging

### MCP Protocol Implementation
- **Server Registration**: Implement proper MCP server discovery
- **Tool Registration**: Dynamic tool registration with schema validation
- **Message Handling**: Async request/response patterns
- **Error Handling**: MCP-compliant error codes and messages
- **Streaming**: Support for streaming responses when applicable

### Development Workflow
- Run tests: `pytest tests/`
- Code formatting: `black src/ tests/`
- Type checking: `mypy src/`
- Linting: `flake8 src/`
- Start MCP server: `python -m src.mcp_server.main`
- Launch Streamlit UI: `streamlit run src/frontend/app.py`
- Build for deployment: `docker build -t mcp-server .`

## Important Notes
- Always validate MCP protocol compliance for tool definitions
- Implement proper error handling for client disconnections
- Use structured logging for debugging MCP message flows
- Test tool registration and discovery thoroughly
- Handle graceful server shutdown and cleanup
- Monitor server performance and tool execution metrics