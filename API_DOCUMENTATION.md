# API Documentation

## Overview

This document provides comprehensive API documentation for the AI Agent MCP Service Learning Project. The project consists of two main services that communicate via HTTP:

1. **AI Agent Service** (port 8001) - Natural language interface
2. **MCP Service** (port 8000) - Project management tools

## AI Agent Service API

**Base URL**: `http://localhost:8001`

### Endpoints

#### POST /agent/execute
Execute a project management task using natural language.

**Request Body**:
```json
{
  "request": "string (required) - Natural language description of the task",
  "user_id": "string (optional) - User identifier", 
  "priority": "string (optional) - Overall priority: low|medium|high|critical"
}
```

**Response**:
```json
{
  "success": "boolean - Whether the request was successful",
  "result": "string (optional) - Human-readable result summary",
  "error": "string (optional) - Error message if failed",
  "request": "string - Original request text",
  "timestamp": "datetime - When the request was processed",
  "execution_time_seconds": "float (optional) - How long execution took"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8001/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Create a new project called Website Redesign for improving our company website",
    "priority": "high"
  }'
```

**Example Response**:
```json
{
  "success": true,
  "result": "I'll help you create a new project for website redesign.\n\n1. ✅ Created project 'Website Redesign' (ID: 4)",
  "request": "Create a new project called Website Redesign for improving our company website",
  "timestamp": "2024-01-15T10:30:45.123456",
  "execution_time_seconds": 2.45
}
```

#### GET /agent/status
Get the current status of the AI agent.

**Response**:
```json
{
  "status": "string - Current agent status (ready|busy|error)",
  "agent_type": "string - Type of agent",
  "tools_available": ["string"] - List of available MCP tools,
  "last_execution": "datetime (optional) - When agent last executed a task",
  "anthropic_api_configured": "boolean - Whether Anthropic API is properly configured"
}
```

#### GET /health
Health check endpoint.

**Response**:
```json
{
  "status": "string - Service health status",
  "timestamp": "datetime - Current timestamp",
  "service": "string - Service name",
  "version": "string - Service version"
}
```

#### GET /agent/metrics
Get basic metrics about agent usage.

**Response**:
```json
{
  "total_executions": "integer - Total number of executions",
  "last_execution": "datetime (optional) - Last execution timestamp",
  "status": "string - Operational status"
}
```

### Natural Language Examples

The AI agent can process various types of natural language requests:

**Project Creation**:
- "Create a new project called 'Mobile App Development'"
- "Start a project for redesigning our website"
- "I need a project for the Q1 marketing campaign"

**Task Creation**:
- "Add a high priority task 'Setup development environment' to project 1"
- "Create a task for user authentication in the mobile app project"
- "Add tasks for testing and deployment to project 2"

**Combined Operations**:
- "Create a project 'E-commerce Platform' and add tasks for user registration, product catalog, and payment processing"
- "Start a new AI project with tasks for data collection, model training, and deployment"

## MCP Service API

**Base URL**: `http://localhost:8000`

### Tool Execution Endpoint

#### POST /tools/call
Execute an MCP tool with specified arguments.

**Request Body**:
```json
{
  "name": "string (required) - Tool name",
  "arguments": "object (required) - Tool-specific arguments"
}
```

**Response**:
```json
{
  "success": "boolean - Whether the tool execution was successful",
  "error": "string (optional) - Error message if failed",
  "[tool-specific-data]": "various - Tool-specific response data"
}
```

### Available MCP Tools

#### 1. create_project

Create a new project.

**Arguments**:
```json
{
  "name": "string (required) - Project name",
  "description": "string (optional) - Project description"
}
```

**Response**:
```json
{
  "success": true,
  "project": {
    "id": "integer - Project ID",
    "name": "string - Project name", 
    "description": "string - Project description",
    "created_at": "datetime - Creation timestamp",
    "updated_at": "datetime - Last update timestamp"
  }
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_project",
    "arguments": {
      "name": "Website Redesign",
      "description": "Modernize company website with new design and features"
    }
  }'
```

#### 2. create_task

Create a new task within a project.

**Arguments**:
```json
{
  "title": "string (required) - Task title",
  "project_id": "integer (required) - Project ID",
  "description": "string (optional) - Task description",
  "priority": "string (optional) - Priority level: low|medium|high|critical",
  "assigned_to": "string (optional) - Person assigned to task"
}
```

**Response**:
```json
{
  "success": true,
  "task": {
    "id": "integer - Task ID",
    "title": "string - Task title",
    "description": "string - Task description",
    "project_id": "integer - Associated project ID",
    "status": "string - Task status (pending)",
    "priority": "string - Priority level",
    "assigned_to": "string - Assigned person",
    "created_at": "datetime - Creation timestamp",
    "updated_at": "datetime - Last update timestamp"
  }
}
```

#### 3. update_task_status

Update the status of an existing task.

**Arguments**:
```json
{
  "task_id": "integer (required) - Task ID",
  "status": "string (required) - New status: pending|in_progress|completed|cancelled"
}
```

**Response**:
```json
{
  "success": true,
  "task": {
    "id": "integer - Task ID",
    "title": "string - Task title",
    "status": "string - Updated status",
    "updated_at": "datetime - Update timestamp"
  }
}
```

#### 4. get_tasks_by_status

Retrieve all tasks with a specific status.

**Arguments**:
```json
{
  "status": "string (required) - Status to filter by: pending|in_progress|completed|cancelled"
}
```

**Response**:
```json
{
  "success": true,
  "tasks": [
    {
      "id": "integer - Task ID",
      "title": "string - Task title",
      "description": "string - Task description",
      "project_id": "integer - Associated project ID",
      "status": "string - Task status",
      "priority": "string - Priority level",
      "assigned_to": "string - Assigned person",
      "created_at": "datetime - Creation timestamp",
      "updated_at": "datetime - Last update timestamp"
    }
  ],
  "count": "integer - Number of tasks returned"
}
```

#### 5. get_project_tasks

Get all tasks for a specific project.

**Arguments**:
```json
{
  "project_id": "integer (required) - Project ID"
}
```

**Response**:
```json
{
  "success": true,
  "project": {
    "id": "integer - Project ID",
    "name": "string - Project name"
  },
  "tasks": [
    {
      "id": "integer - Task ID",
      "title": "string - Task title",
      "description": "string - Task description",
      "status": "string - Task status",
      "priority": "string - Priority level",
      "assigned_to": "string - Assigned person",
      "created_at": "datetime - Creation timestamp",
      "updated_at": "datetime - Last update timestamp"
    }
  ],
  "count": "integer - Number of tasks in project"
}
```

#### 6. list_all_projects

Get a list of all projects.

**Arguments**:
```json
{}
```

**Response**:
```json
{
  "success": true,
  "projects": [
    {
      "id": "integer - Project ID",
      "name": "string - Project name",
      "description": "string - Project description",
      "created_at": "datetime - Creation timestamp",
      "updated_at": "datetime - Last update timestamp"
    }
  ],
  "count": "integer - Number of projects"
}
```

#### 7. get_task_summary

Get a summary of task counts by status.

**Arguments**:
```json
{}
```

**Response**:
```json
{
  "success": true,
  "summary": {
    "total_tasks": "integer - Total number of tasks",
    "pending": "integer - Number of pending tasks",
    "in_progress": "integer - Number of in-progress tasks", 
    "completed": "integer - Number of completed tasks",
    "cancelled": "integer - Number of cancelled tasks"
  }
}
```

### Health Check

#### GET /health

Check service health.

**Response**:
```json
{
  "status": "healthy",
  "service": "Task Management MCP Service", 
  "version": "1.0.0",
  "database": "connected"
}
```

## Data Models

### Project
```json
{
  "id": "integer - Unique project identifier",
  "name": "string - Project name (max 255 chars)",
  "description": "string - Project description",
  "created_at": "datetime - Creation timestamp", 
  "updated_at": "datetime - Last update timestamp"
}
```

### Task
```json
{
  "id": "integer - Unique task identifier",
  "title": "string - Task title (max 255 chars)",
  "description": "string - Task description",
  "project_id": "integer - Associated project ID",
  "status": "enum - pending|in_progress|completed|cancelled",
  "priority": "enum - low|medium|high|critical", 
  "assigned_to": "string - Person assigned to task",
  "created_at": "datetime - Creation timestamp",
  "updated_at": "datetime - Last update timestamp"
}
```

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "success": false,
  "error": "Invalid request: missing required field 'name'"
}
```

#### 404 Not Found
```json
{
  "success": false,
  "error": "Project with ID 999 not found"
}
```

#### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Database connection failed"
}
```

### MCP Tool Errors

When an MCP tool fails, the response includes error details:

```json
{
  "success": false,
  "error": "Task with ID 999 not found"
}
```

## Authentication

**Current Status**: No authentication required

**Future Enhancement**: JWT-based authentication planned for production deployment.

## Rate Limiting

**Current Status**: No rate limiting implemented

**Recommendation**: Implement rate limiting for production use.

## Testing

### Health Checks
```bash
# Check AI Agent service
curl http://localhost:8001/health

# Check MCP service  
curl http://localhost:8000/health
```

### Test Suites

The project includes comprehensive test suites:

- **Bash Test Suite**: `tests/test_mcp_tools.sh` - 8 automated tests
- **Python Test Suite**: `tests/test_mcp_tools.py` - 8 detailed tests

Run tests:
```bash
# Bash tests
./tests/test_mcp_tools.sh

# Python tests
python3 tests/test_mcp_tools.py
```

## Database Schema

### Projects Table
```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tasks Table
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    assigned_to VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Sample Data

The database includes sample data:
- **3 projects**: E-commerce Platform, Mobile App, Data Analytics Dashboard
- **14 tasks**: Distributed across projects with various statuses and priorities

Access via pgAdmin at http://localhost:8080 (admin@example.com / admin123)