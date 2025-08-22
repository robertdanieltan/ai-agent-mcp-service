# Development Guide

## Overview

This guide provides comprehensive instructions for developers who want to contribute to, extend, or learn from the AI Agent MCP Service Learning Project. It covers development setup, architecture patterns, testing strategies, and best practices.

## Development Environment Setup

### Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose**
- **Git**
- **Code Editor** (VS Code recommended with Python extension)
- **Anthropic API Key**

### Local Development Setup

#### 1. Repository Setup
```bash
# Clone repository
git clone <repository-url>
cd mcp_proj1

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r crewai_agent/requirements.txt

# Install development tools
pip install pytest black flake8 mypy pre-commit
```

#### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your development configuration
# Required: ANTHROPIC_API_KEY=your_key_here
```

#### 3. Development Database
```bash
# Start only database services for local development
docker-compose up postgres pgadmin -d

# Verify database connection
psql postgresql://postgres:postgres@localhost:5432/task_management
```

#### 4. IDE Configuration

**VS Code Settings** (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.associations": {
        "*.md": "markdown"
    }
}
```

## Project Architecture

### Service Architecture

```
mcp_proj1/
├── crewai_agent/           # AI Agent Service (Port 8001)
│   ├── main.py            # FastAPI web service
│   ├── simple_agent.py    # Agent implementation with Claude
│   └── requirements.txt   # Service dependencies
├── mcp_service/           # MCP Service (Port 8000)
│   ├── main.py           # FastAPI MCP server
│   ├── tools.py          # MCP tool implementations
│   ├── models.py         # Pydantic data models
│   ├── database.py       # Database operations
│   └── requirements.txt  # Service dependencies
├── database/             # Database Schema & Data
│   ├── init.sql         # Complete schema
│   └── sample_data.sql  # Sample projects/tasks
└── tests/               # Test Suites
    ├── test_mcp_tools.sh # Bash integration tests
    └── test_mcp_tools.py # Python unit tests
```

### Design Patterns

#### 1. FastAPI Application Pattern
```python
# Standard FastAPI structure
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Service Name",
    description="Service description",
    version="1.0.0"
)

# Pydantic models for request/response
class RequestModel(BaseModel):
    field: str

class ResponseModel(BaseModel):
    success: bool
    result: str = None
    error: str = None

# Health check endpoint (required)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Main endpoint
@app.post("/endpoint", response_model=ResponseModel)
async def endpoint_handler(request: RequestModel):
    try:
        # Business logic here
        result = process_request(request)
        return ResponseModel(success=True, result=result)
    except Exception as e:
        logger.error(f"Error: {e}")
        return ResponseModel(success=False, error=str(e))
```

#### 2. Database Operations Pattern
```python
# database.py pattern
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)

def get_database_connection():
    """Get database connection with error handling"""
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="task_management", 
            user="postgres",
            password="postgres"
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def execute_query(query: str, params: tuple = None, fetch: bool = True):
    """Execute database query with connection management"""
    conn = None
    try:
        conn = get_database_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            
            if fetch:
                return cur.fetchall()
            else:
                conn.commit()
                return cur.rowcount
                
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Query execution failed: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Usage example
def create_project(name: str, description: str = None):
    """Create a new project"""
    query = """
        INSERT INTO projects (name, description) 
        VALUES (%s, %s) 
        RETURNING *
    """
    result = execute_query(query, (name, description), fetch=True)
    return result[0] if result else None
```

#### 3. MCP Tool Implementation Pattern
```python
# tools.py pattern
def mcp_tool_template(argument1: str, argument2: int = None):
    """
    MCP Tool Template
    
    Args:
        argument1: Required string argument
        argument2: Optional integer argument
        
    Returns:
        dict: Standard MCP response format
    """
    try:
        # Validate arguments
        if not argument1:
            return {
                "success": False,
                "error": "argument1 is required"
            }
        
        # Business logic
        result = perform_operation(argument1, argument2)
        
        # Return success response
        return {
            "success": True,
            "data": result,
            "message": f"Operation completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Register tool in main.py
@app.post("/tools/call")
async def call_tool(request: dict):
    tool_name = request.get("name")
    arguments = request.get("arguments", {})
    
    if tool_name == "tool_template":
        return mcp_tool_template(**arguments)
    
    return {"success": False, "error": f"Unknown tool: {tool_name}"}
```

#### 4. AI Agent Integration Pattern
```python
# simple_agent.py pattern
class SimpleProjectAgent:
    def __init__(self):
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.mcp_service_url = os.getenv("MCP_SERVICE_URL")
        
    def call_mcp_tool(self, tool_name: str, arguments: dict):
        """Call MCP tool via HTTP"""
        response = requests.post(
            f"{self.mcp_service_url}/tools/call",
            json={"name": tool_name, "arguments": arguments},
            timeout=30
        )
        return response.json()
    
    def analyze_request_with_claude(self, user_request: str):
        """Use Claude to analyze request and plan actions"""
        system_prompt = """You are a project management AI. 
        Analyze requests and return JSON with actions to take."""
        
        message = self.anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_request}]
        )
        
        # Parse Claude's response and extract JSON
        return self.parse_claude_response(message.content[0].text)
    
    def execute_project_management_task(self, user_request: str):
        """Main execution method"""
        # 1. Analyze request with Claude
        analysis = self.analyze_request_with_claude(user_request)
        
        # 2. Execute planned actions
        results = []
        for action in analysis.get("actions", []):
            result = self.call_mcp_tool(action["tool"], action["arguments"])
            results.append(result)
        
        # 3. Format response
        return self.format_response(analysis, results)
```

## Development Workflows

### Adding New MCP Tools

#### 1. Define Tool Function
```python
# Add to mcp_service/tools.py
def new_tool_name(param1: str, param2: int = None):
    """
    Tool description
    
    Args:
        param1: Parameter description
        param2: Optional parameter description
        
    Returns:
        dict: Success/error response with data
    """
    try:
        # Validate inputs
        if not param1:
            return {"success": False, "error": "param1 is required"}
        
        # Database operations
        query = "SELECT * FROM table WHERE column = %s"
        result = execute_query(query, (param1,))
        
        return {
            "success": True,
            "data": result,
            "count": len(result)
        }
        
    except Exception as e:
        logger.error(f"Tool {tool_name} failed: {e}")
        return {"success": False, "error": str(e)}
```

#### 2. Register Tool in Main App
```python
# Add to mcp_service/main.py call_tool function
elif tool_name == "new_tool_name":
    return new_tool_name(**arguments)
```

#### 3. Add Database Schema Changes
```sql
-- Add to database/init.sql if needed
ALTER TABLE existing_table ADD COLUMN new_column VARCHAR(255);
CREATE INDEX idx_new_column ON existing_table(new_column);
```

#### 4. Update AI Agent (Optional)
```python
# Add to crewai_agent/simple_agent.py system prompt
"""
Available tools:
- new_tool_name(param1, param2) - Tool description
"""
```

#### 5. Add Tests
```python
# Add to tests/test_mcp_tools.py
def test_new_tool():
    """Test new MCP tool"""
    response = requests.post(
        f"{MCP_URL}/tools/call",
        json={
            "name": "new_tool_name",
            "arguments": {"param1": "test_value"}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "data" in data
```

### Extending AI Agent Capabilities

#### 1. Add New Natural Language Patterns
```python
# Update system prompt in simple_agent.py
system_prompt = """You are a project management AI assistant.

You have access to these MCP tools:
1. create_project(name, description) - Creates a new project
2. create_task(title, project_id, description, priority, assigned_to) - Creates a task
3. new_tool_name(param1, param2) - New tool description

Common request patterns:
- "Create project X with tasks A, B, C"
- "Add high priority task Y to project Z"
- "New pattern for new tool"

Respond with JSON:
{
    "actions": [
        {"tool": "tool_name", "arguments": {...}}
    ],
    "explanation": "What you're going to do"
}
"""
```

#### 2. Handle New Response Formats
```python
# Update execute_project_management_task in simple_agent.py
def format_response(self, analysis, results):
    """Create human-readable summary"""
    summary_parts = [analysis.get("explanation", "")]
    
    for i, result in enumerate(results, 1):
        tool = result["tool"]
        success = result["result"].get("success", False)
        
        if success:
            if tool == "create_project":
                # Existing formatting
                pass
            elif tool == "new_tool_name":
                # New tool formatting
                data = result["result"].get("data", {})
                summary_parts.append(f"{i}. ✅ New tool executed: {data}")
        else:
            error = result["result"].get("error", "Unknown error")
            summary_parts.append(f"{i}. ❌ Failed: {error}")
    
    return "\n".join(summary_parts)
```

### Database Development

#### 1. Schema Modifications
```sql
-- Create migration script: migrations/001_add_users.sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add foreign key to existing tables
ALTER TABLE projects ADD COLUMN user_id INTEGER REFERENCES users(id);
ALTER TABLE tasks ADD COLUMN user_id INTEGER REFERENCES users(id);

-- Create indexes
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
```

#### 2. Migration Strategy
```python
# migrations/migrate.py
import psycopg2
import os

def run_migration(migration_file):
    """Run SQL migration file"""
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    try:
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        with conn.cursor() as cur:
            cur.execute(migration_sql)
        
        conn.commit()
        print(f"Migration {migration_file} completed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()

# Usage
if __name__ == "__main__":
    run_migration("migrations/001_add_users.sql")
```

#### 3. Data Access Layer Enhancement
```python
# Add to database.py
class DatabaseManager:
    """Enhanced database manager with connection pooling"""
    
    def __init__(self):
        self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            host="postgres",
            database="task_management",
            user="postgres", 
            password="postgres"
        )
    
    def get_connection(self):
        """Get connection from pool"""
        return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        """Return connection to pool"""
        self.connection_pool.putconn(conn)
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """Execute query with connection pooling"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                
                if fetch:
                    return cur.fetchall()
                else:
                    conn.commit()
                    return cur.rowcount
        finally:
            self.return_connection(conn)

# Singleton instance
db_manager = DatabaseManager()
```

## Testing Strategy

### Unit Testing

#### 1. Test Structure
```python
# tests/test_unit.py
import pytest
import requests
from unittest.mock import Mock, patch
from mcp_service.tools import create_project
from crewai_agent.simple_agent import SimpleProjectAgent

class TestMCPTools:
    """Unit tests for MCP tools"""
    
    @patch('mcp_service.tools.execute_query')
    def test_create_project_success(self, mock_query):
        """Test successful project creation"""
        # Mock database response
        mock_query.return_value = [{
            'id': 1,
            'name': 'Test Project',
            'description': 'Test Description'
        }]
        
        # Test tool
        result = create_project("Test Project", "Test Description")
        
        # Assertions
        assert result["success"] == True
        assert result["project"]["name"] == "Test Project"
        mock_query.assert_called_once()
    
    @patch('mcp_service.tools.execute_query')
    def test_create_project_failure(self, mock_query):
        """Test project creation failure"""
        # Mock database error
        mock_query.side_effect = Exception("Database error")
        
        # Test tool
        result = create_project("Test Project")
        
        # Assertions
        assert result["success"] == False
        assert "Database error" in result["error"]

class TestSimpleAgent:
    """Unit tests for AI agent"""
    
    @patch('crewai_agent.simple_agent.Anthropic')
    def test_analyze_request(self, mock_anthropic):
        """Test request analysis with Claude"""
        # Mock Claude response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '''
        {
            "actions": [
                {"tool": "create_project", "arguments": {"name": "Test"}}
            ],
            "explanation": "Creating test project"
        }
        '''
        mock_anthropic.return_value.messages.create.return_value = mock_response
        
        # Test agent
        agent = SimpleProjectAgent()
        result = agent.analyze_request_with_claude("Create a test project")
        
        # Assertions
        assert len(result["actions"]) == 1
        assert result["actions"][0]["tool"] == "create_project"
```

#### 2. Integration Testing
```python
# tests/test_integration.py
import pytest
import requests
import time

class TestIntegration:
    """Integration tests for full system"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        # Wait for services to be ready
        cls.wait_for_service("http://localhost:8000/health")
        cls.wait_for_service("http://localhost:8001/health")
    
    @staticmethod
    def wait_for_service(url, timeout=30):
        """Wait for service to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    return
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(1)
        raise Exception(f"Service at {url} not ready after {timeout}s")
    
    def test_end_to_end_workflow(self):
        """Test complete workflow: AI Agent -> MCP Service -> Database"""
        # 1. Create project via AI agent
        response = requests.post(
            "http://localhost:8001/agent/execute",
            json={"request": "Create a test project for integration testing"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        # 2. Verify project exists in MCP service
        response = requests.post(
            "http://localhost:8000/tools/call",
            json={"name": "list_all_projects", "arguments": {}}
        )
        
        assert response.status_code == 200
        projects = response.json()
        assert projects["success"] == True
        assert any("integration testing" in p["name"].lower() 
                  for p in projects["projects"])
```

#### 3. Performance Testing
```python
# tests/test_performance.py
import time
import statistics
import requests
import concurrent.futures

class TestPerformance:
    """Performance tests"""
    
    def test_mcp_tool_response_time(self):
        """Test MCP tool response times"""
        url = "http://localhost:8000/tools/call"
        payload = {"name": "list_all_projects", "arguments": {}}
        
        response_times = []
        for _ in range(10):
            start_time = time.time()
            response = requests.post(url, json=payload)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_time = statistics.mean(response_times)
        assert avg_time < 0.5  # Should respond within 500ms
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        url = "http://localhost:8001/agent/execute" 
        payload = {"request": "Create a test project"}
        
        def make_request():
            return requests.post(url, json=payload)
        
        # Test 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        for response in results:
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
```

### Testing Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_unit.py -v

# Run with coverage
pip install pytest-cov
python -m pytest tests/ --cov=mcp_service --cov=crewai_agent --cov-report=html

# Run performance tests
python -m pytest tests/test_performance.py -v

# Run integration tests
docker-compose up -d
python -m pytest tests/test_integration.py -v
```

## Code Quality and Standards

### Code Formatting

#### 1. Black Configuration
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.venv
  | build
  | dist
)/
'''
```

#### 2. Flake8 Configuration
```ini
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,venv,.venv,build,dist
```

#### 3. MyPy Configuration
```ini
# mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True

[mypy-psycopg2.*]
ignore_missing_imports = True

[mypy-anthropic.*]
ignore_missing_imports = True
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
      
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
      
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

Setup:
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

### Documentation Standards

#### 1. Docstring Format
```python
def create_project(name: str, description: str = None) -> dict:
    """
    Create a new project in the database.
    
    Args:
        name: Project name (required, max 255 characters)
        description: Optional project description
        
    Returns:
        dict: Success response with project data or error message
        
    Raises:
        DatabaseError: If database operation fails
        ValidationError: If name is empty or too long
        
    Example:
        >>> result = create_project("My Project", "A test project")
        >>> print(result["success"])
        True
    """
```

#### 2. API Documentation
```python
# FastAPI automatic documentation via Pydantic models
class CreateProjectRequest(BaseModel):
    """Request model for creating a project"""
    name: str = Field(..., max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")

class ProjectResponse(BaseModel):
    """Response model for project operations"""
    success: bool = Field(..., description="Whether operation succeeded")
    project: Optional[dict] = Field(None, description="Project data if successful")
    error: Optional[str] = Field(None, description="Error message if failed")

@app.post("/projects", response_model=ProjectResponse)
async def create_project_endpoint(request: CreateProjectRequest):
    """
    Create a new project
    
    - **name**: Project name (required)
    - **description**: Optional project description
    
    Returns the created project data or error message.
    """
```

## Debugging and Troubleshooting

### Local Debugging

#### 1. VS Code Debug Configuration
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug MCP Service",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/mcp_service/main.py",
            "env": {
                "DATABASE_URL": "postgresql://postgres:postgres@localhost:5432/task_management"
            },
            "console": "integratedTerminal"
        },
        {
            "name": "Debug AI Agent",
            "type": "python", 
            "request": "launch",
            "program": "${workspaceFolder}/crewai_agent/main.py",
            "env": {
                "ANTHROPIC_API_KEY": "your_key_here",
                "MCP_SERVICE_URL": "http://localhost:8000"
            },
            "console": "integratedTerminal"
        }
    ]
}
```

#### 2. Debug Logging
```python
# Add to any module for detailed debugging
import logging

# Configure debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

logger = logging.getLogger(__name__)

# Use throughout code
logger.debug(f"Processing request: {request_data}")
logger.info(f"Successfully created project: {project_id}")
logger.warning(f"Unusual response time: {duration}s")
logger.error(f"Database error: {error_message}")
```

#### 3. Interactive Debugging
```python
# Add breakpoints with pdb
import pdb

def create_project(name: str, description: str = None):
    pdb.set_trace()  # Debugger will stop here
    
    # Inspect variables
    print(f"name: {name}")
    print(f"description: {description}")
    
    # Continue execution
    result = database_operation(name, description)
    return result
```

### Container Debugging

#### 1. Service Logs
```bash
# View live logs
docker-compose logs -f crewai-agent
docker-compose logs -f mcp-service

# Search logs
docker-compose logs mcp-service | grep ERROR
docker-compose logs crewai-agent | grep "Claude"

# Export logs
docker-compose logs > debug_logs.txt
```

#### 2. Container Inspection
```bash
# Shell into container
docker-compose exec mcp-service bash
docker-compose exec crewai-agent bash

# Check environment variables
docker-compose exec crewai-agent env

# Check file system
docker-compose exec mcp-service ls -la
docker-compose exec mcp-service cat /app/mcp_service/main.py
```

#### 3. Database Debugging
```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d task_management

# Check database status
\l                    # List databases
\dt                   # List tables
\d projects          # Describe projects table
SELECT * FROM projects LIMIT 5;

# Check connections
SELECT * FROM pg_stat_activity;
```

### Common Issues and Solutions

#### 1. Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000
netstat -tulpn | grep :8001

# Kill process using port
sudo kill -9 $(lsof -t -i:8000)

# Use different ports
PORT=8002 docker-compose up mcp-service
```

#### 2. Database Connection Issues
```python
# Test database connection
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="task_management",
        user="postgres", 
        password="postgres",
        port="5432"
    )
    print("Database connection successful")
    conn.close()
except Exception as e:
    print(f"Database connection failed: {e}")
```

#### 3. API Key Issues
```python
# Test Anthropic API key
import anthropic

client = anthropic.Anthropic(api_key="your_key_here")

try:
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=10,
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("API key valid")
except Exception as e:
    print(f"API key error: {e}")
```

## Performance Optimization

### Database Optimization

#### 1. Query Optimization
```sql
-- Add indexes for common queries
CREATE INDEX CONCURRENTLY idx_tasks_status_priority ON tasks(status, priority);
CREATE INDEX CONCURRENTLY idx_projects_name_lower ON projects(LOWER(name));

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM tasks WHERE status = 'pending' AND priority = 'high';

-- Update table statistics
ANALYZE tasks;
ANALYZE projects;
```

#### 2. Connection Pooling
```python
# Implement connection pooling
from psycopg2 import pool
import threading

class DatabasePool:
    def __init__(self):
        self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=20,
            host="postgres",
            database="task_management",
            user="postgres",
            password="postgres"
        )
        self.lock = threading.Lock()
    
    def get_connection(self):
        with self.lock:
            return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        with self.lock:
            self.connection_pool.putconn(conn)

# Singleton instance
db_pool = DatabasePool()
```

### Application Optimization

#### 1. Caching
```python
# Add Redis caching
import redis
from functools import wraps
import json

redis_client = redis.Redis(host='redis', port=6379, db=0)

def cache_result(expiry=300):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiry, json.dumps(result))
            return result
        return wrapper
    return decorator

# Usage
@cache_result(expiry=600)  # Cache for 10 minutes
def get_project_tasks(project_id: int):
    """Get tasks for project with caching"""
    return execute_query(
        "SELECT * FROM tasks WHERE project_id = %s",
        (project_id,)
    )
```

#### 2. Async Operations
```python
# Convert to async for better performance
import asyncio
import asyncpg
from fastapi import FastAPI

app = FastAPI()

# Async database operations
async def get_database_connection():
    return await asyncpg.connect(
        host="postgres",
        database="task_management",
        user="postgres",
        password="postgres"
    )

async def create_project_async(name: str, description: str = None):
    """Async project creation"""
    conn = await get_database_connection()
    try:
        result = await conn.fetchrow(
            "INSERT INTO projects (name, description) VALUES ($1, $2) RETURNING *",
            name, description
        )
        return dict(result)
    finally:
        await conn.close()

# Async endpoint
@app.post("/projects/async")
async def create_project_endpoint(request: CreateProjectRequest):
    result = await create_project_async(request.name, request.description)
    return {"success": True, "project": result}
```

## Contributing Guidelines

### Git Workflow

#### 1. Branch Strategy
```bash
# Feature development
git checkout -b feature/add-user-authentication
git checkout -b feature/new-mcp-tool
git checkout -b bugfix/database-connection

# Make changes and commit
git add .
git commit -m "feat: add user authentication system"

# Push and create PR
git push origin feature/add-user-authentication
```

#### 2. Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(mcp): add user authentication tool
fix(agent): resolve Claude API timeout issue
docs(api): update endpoint documentation
test(integration): add end-to-end workflow tests
```

#### 3. Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

### Code Review Guidelines

#### 1. Review Checklist
- **Functionality**: Does the code work as intended?
- **Style**: Does it follow project conventions?
- **Performance**: Are there any performance concerns?
- **Security**: Are there any security vulnerabilities?
- **Testing**: Are there adequate tests?
- **Documentation**: Is documentation updated?

#### 2. Review Process
1. **Automated Checks**: Ensure CI/CD passes
2. **Code Review**: At least one team member review
3. **Testing**: Verify tests pass locally
4. **Documentation**: Check for documentation updates
5. **Merge**: Squash and merge to main branch

## Deployment for Development

### Local Development Environment

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Development with auto-reload
uvicorn mcp_service.main:app --reload --host 0.0.0.0 --port 8000
uvicorn crewai_agent.main:app --reload --host 0.0.0.0 --port 8001
```

### Staging Environment

```yaml
# docker-compose.staging.yml
version: '3.8'
services:
  mcp-service:
    build: ./mcp_service
    environment:
      - DATABASE_URL=postgresql://user:pass@staging-db:5432/staging_db
    ports:
      - "8000:8000"
      
  crewai-agent:
    build: ./crewai_agent
    environment:
      - ANTHROPIC_API_KEY=${STAGING_ANTHROPIC_API_KEY}
      - MCP_SERVICE_URL=http://mcp-service:8000
    ports:
      - "8001:8001"
```

This development guide provides comprehensive coverage for contributing to and extending the AI Agent MCP Service Learning Project.