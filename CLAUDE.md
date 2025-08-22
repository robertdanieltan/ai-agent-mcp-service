# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **AI Agent MCP Service Learning Project** that demonstrates Model Context Protocol (MCP) service development using **FastAPI HTTP MCP service** with **Simple AI Agent** integration. The project runs in a **Docker multi-container environment with PostgreSQL** for data persistence.

**Architecture**: Simple AI Agent (FastAPI + Anthropic Claude) ← HTTP → MCP Service (FastAPI) ← PostgreSQL Database

**Key Features**:
- Natural language project management via Anthropic Claude
- HTTP-based MCP service with 7 tools
- Multi-container Docker deployment with health monitoring
- PostgreSQL database with sample data
- REST API for agent interaction

## Project Structure

```
mcp_proj1/
├── mcp_service/
│   ├── __init__.py
│   ├── main.py              # FastAPI HTTP MCP server
│   ├── models.py            # Pydantic models for Project and Task
│   ├── database.py          # PostgreSQL connection and operations
│   ├── tools.py             # All 7 MCP tool implementations
│   └── Dockerfile           # MCP service container
├── crewai_agent/
│   ├── __init__.py
│   ├── main.py              # FastAPI web service for AI agent
│   ├── simple_agent.py      # Simple Project Agent with Anthropic Claude
│   ├── requirements.txt     # Agent dependencies
│   └── Dockerfile           # AI agent container
├── mcp_stdio_wrapper/
│   ├── __init__.py
│   ├── mcp_stdio_wrapper.py # STDIO ↔ HTTP bridge (unused in current impl)
│   ├── requirements.txt     # Wrapper dependencies
│   └── Dockerfile           # STDIO wrapper container
├── database/
│   ├── init.sql             # Complete database schema
│   └── sample_data.sql      # Sample projects and tasks
├── tests/
│   ├── test_mcp_tools.sh    # Bash test suite for MCP service
│   └── test_mcp_tools.py    # Python test suite for MCP service
├── docker-compose.yml       # Multi-service orchestration
├── requirements.txt         # Legacy requirements (for MCP service)
├── .env                     # Environment variables
├── .dockerignore           # Docker build exclusions
└── README.md               # Comprehensive project documentation
```

## Implementation Status

### ✅ Completed Components

1. **MCP Service** (FastAPI HTTP-based)
   - ✅ 7 MCP tools: create_project, create_task, update_task_status, get_tasks_by_status, get_project_tasks, list_all_projects, get_task_summary
   - ✅ PostgreSQL integration with psycopg2
   - ✅ HTTP communication on port 8000
   - ✅ Health check endpoint at /health
   - ✅ Pydantic models with validation
   - ✅ Comprehensive testing (Bash and Python test suites)

2. **Simple AI Agent** (Lightweight alternative to CrewAI)
   - ✅ Project Manager agent with Anthropic Claude integration
   - ✅ Natural language processing for project management requests
   - ✅ HTTP calls to MCP service (create_project, create_task)
   - ✅ FastAPI web service on port 8001
   - ✅ Health check and status endpoints
   - ✅ End-to-end testing completed

3. **Database Infrastructure**
   - ✅ Complete PostgreSQL schema with constraints and indexes
   - ✅ Sample data with 3 projects and 14 tasks
   - ✅ Automatic timestamp triggers
   - ✅ Task status and priority validation

4. **Docker Infrastructure**
   - ✅ Multi-stage Dockerfiles for all services
   - ✅ Docker Compose with 4 services: mcp-service, crewai-agent, postgres, pgadmin
   - ✅ Health checks and restart policies
   - ✅ Persistent volumes for data
   - ✅ Network isolation and service dependencies

5. **Testing & Validation**
   - ✅ MCP service testing (all 7 tools verified)
   - ✅ AI agent integration testing
   - ✅ End-to-end workflow validation
   - ✅ Natural language request processing
   - ✅ Database operations verification

### 🔄 Optional Components (Available but unused)

1. **STDIO Wrapper**
   - ✅ Bridge between STDIO and HTTP MCP service
   - ✅ JSON-RPC 2.0 protocol implementation
   - ⚠️ Not used in current implementation (direct HTTP used instead)

## Quick Start

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs mcp-service
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
2. **mcp-service**: HTTP MCP service with 7 tools (port 8000)
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

- Current implementation uses simple AI agent (not full CrewAI)
- STDIO wrapper exists but is unused (direct HTTP communication)
- All services are containerized and health-monitored
- Database includes sample data for immediate testing
- Environment variables configured in .env file

