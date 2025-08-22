# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **AI Agent MCP Service Learning Project** that demonstrates Model Context Protocol (MCP) service development using **HTTP-based MCP service** with **Simple AI Agent** integration. The project runs in a **Docker multi-container environment with PostgreSQL** for data persistence.

**Architecture**: Simple AI Agent (FastAPI + Anthropic Claude) ← HTTP → MCP HTTP Service (FastAPI) ← PostgreSQL Database

**Key Features**:
- Natural language project management via Anthropic Claude
- HTTP-based MCP service with 7 tools
- Multi-container Docker deployment with health monitoring
- PostgreSQL database with sample data
- REST API for agent interaction

## Project Structure

```
mcp_proj1/
├── mcp_http_service/        # HTTP-based MCP service (renamed from mcp_stdio_service)
│   ├── __init__.py
│   ├── main.py              # FastAPI HTTP MCP server with experimental STDIO support
│   ├── models.py            # Pydantic models for Project and Task
│   ├── database.py          # PostgreSQL connection and operations
│   ├── mcp_tools.py         # All 7 MCP tool implementations
│   ├── requirements.txt     # HTTP service dependencies
│   └── Dockerfile           # HTTP MCP service container
├── crewai_agent/
│   ├── __init__.py
│   ├── main.py              # FastAPI web service for AI agent
│   ├── simple_agent.py      # Simple Project Agent with Anthropic Claude
│   ├── project_manager_agent.py # Experimental CrewAI agent (dependency conflicts)
│   ├── mcp_tools.py         # Custom CrewAI MCP tools (unused)
│   ├── requirements.txt     # Agent dependencies
│   └── Dockerfile           # AI agent container
├── mcp_service/             # Original MCP service (commented out in docker-compose)
├── mcp_stdio_wrapper/       # Original STDIO wrapper (commented out in docker-compose)
├── database/
│   ├── init.sql             # Complete database schema
│   └── sample_data.sql      # Sample projects and tasks
├── tests/
│   ├── test_mcp_tools.sh    # Bash test suite for MCP service
│   └── test_mcp_tools.py    # Python test suite for MCP service
├── docker-compose.yml       # 3-service orchestration (mcp-http-service, crewai-agent, postgres, pgadmin)
├── requirements.txt         # Legacy requirements (for MCP service)
├── .env                     # Environment variables
├── .dockerignore           # Docker build exclusions
└── README.md               # Comprehensive project documentation
```

## Implementation Status

### ✅ Completed Components

1. **MCP HTTP Service** (FastAPI-based)
   - ✅ 7 MCP tools: create_project, create_task, update_task_status, get_tasks_by_status, get_project_tasks, list_all_projects, get_task_summary
   - ✅ PostgreSQL integration with direct database access
   - ✅ HTTP communication (port 8000) + experimental STDIO support
   - ✅ Health check endpoint at /health
   - ✅ Pydantic models with validation
   - ✅ Container consolidation (reduced from 4 to 3 services)

2. **Simple AI Agent** (HTTP-based MCP integration)
   - ✅ Project Manager agent with natural language processing
   - ✅ HTTP-based MCP tool calls (working)
   - ✅ FastAPI web service on port 8001
   - ✅ Health check and status endpoints
   - ✅ End-to-end project creation workflow
   - ⚠️ Simplified request parsing (Anthropic Claude bypassed due to proxy issues)

3. **Database Infrastructure**
   - ✅ Complete PostgreSQL schema with constraints and indexes
   - ✅ Sample data with multiple projects created via API
   - ✅ Automatic timestamp triggers
   - ✅ Task status and priority validation

4. **Optimized Docker Infrastructure**
   - ✅ Container consolidation: 4 → 3 services
   - ✅ Multi-stage Dockerfiles for both active services
   - ✅ Health checks and restart policies
   - ✅ Persistent volumes for data
   - ✅ Network isolation and service dependencies

5. **Testing & Validation**
   - ✅ Combined MCP service testing (all 7 tools verified)
   - ✅ AI agent integration testing via HTTP
   - ✅ End-to-end project creation workflow
   - ✅ Database operations verification
   - ✅ Container health monitoring

### 🔄 Experimental Components (Available but deferred)

1. **Native CrewAI MCP Integration**
   - ✅ MCPServerAdapter implementation with StdioServerParameters
   - ✅ Native STDIO MCP protocol support
   - ❌ Dependency conflicts (CrewAI MCP requires anyio>=4.5, FastAPI requires anyio<4.0.0)
   - ⚠️ Deferred until dependency conflicts resolved

2. **Original Separate Services** (commented out in docker-compose.yml)
   - ✅ Original mcp-service (FastAPI HTTP-only)
   - ✅ Original mcp-stdio-wrapper (STDIO ↔ HTTP bridge)
   - ⚠️ Replaced by combined mcp-stdio-service for optimization

## Quick Start

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs mcp-http-service
```

## Access Points

- **AI Agent Service**: http://localhost:8001
- **AI Agent Health**: http://localhost:8001/health
- **AI Agent Status**: http://localhost:8001/agent/status
- **AI Agent Execute**: http://localhost:8001/agent/execute
- **MCP Service**: http://localhost:8000
- **MCP Health Check**: http://localhost:8000/health
- **pgAdmin**: http://localhost:8080 (admin@example.com / admin123)
- **PostgreSQL**: localhost:5432 (postgres / postgres)

## Current Implementation Architecture

**Data Flow**: User Request → AI Agent (Claude API) → HTTP → MCP Service → PostgreSQL

**Services**:
1. **crewai-agent**: AI agent with natural language processing (port 8001)
2. **mcp-http-service**: HTTP MCP service with 7 tools (port 8000)
3. **postgres**: PostgreSQL database (port 5432)
4. **pgadmin**: Database management UI (port 8080)

## Future Enhancement Opportunities

1. **Advanced AI Agents**: Replace simple agent with full CrewAI implementation
2. **Additional MCP Tools**: Expand beyond create_project/create_task
3. **STDIO Integration**: Activate STDIO wrapper for CrewAI compatibility
4. **Authentication**: Add user management and API authentication
5. **Monitoring**: Add comprehensive logging and metrics
6. **UI Frontend**: Create web interface for project management

## Important Instructions

- Current implementation uses HTTP-based MCP integration (not native CrewAI MCP)
- Simple AI agent handles natural language processing
- All services are containerized and health-monitored
- Database includes sample data for immediate testing
- Environment variables configured in .env file
- Experimental STDIO support available but not used due to dependency conflicts

