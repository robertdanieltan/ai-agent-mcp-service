"""
CrewAI Project Manager Web Service

FastAPI web service that hosts the CrewAI Project Manager agent.
Provides REST API endpoints for project management requests using
natural language processing and AI agent execution.

Endpoints:
- POST /agent/execute - Execute project management tasks
- GET /agent/status - Agent health and status
- GET /health - Service health check
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn

from .simple_agent import SimpleProjectAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Request/Response Models
class ProjectManagementRequest(BaseModel):
    """Request model for project management tasks"""
    request: str = Field(..., description="Natural language description of the project management task")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    priority: Optional[str] = Field("medium", description="Overall priority for the request")

class ProjectManagementResponse(BaseModel):
    """Response model for project management task execution"""
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    request: str
    timestamp: datetime
    execution_time_seconds: Optional[float] = None

class AgentStatus(BaseModel):
    """Status model for the AI agent"""
    status: str
    agent_type: str
    tools_available: list[str]
    last_execution: Optional[datetime] = None
    anthropic_api_configured: bool

class HealthCheck(BaseModel):
    """Health check model"""
    status: str
    timestamp: datetime
    service: str
    version: str

# Global state
app_state = {
    "last_execution": None,
    "execution_count": 0
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("Starting CrewAI Project Manager Service")
    
    # Verify required environment variables
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY environment variable is required")
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    logger.info("CrewAI Project Manager Service started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down CrewAI Project Manager Service")

# Create FastAPI app
app = FastAPI(
    title="CrewAI Project Manager Service",
    description="AI-powered project management agent using CrewAI and MCP",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        service="crewai-project-manager",
        version="1.0.0"
    )

@app.get("/agent/status", response_model=AgentStatus)
async def agent_status():
    """Get the current status of the AI agent"""
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    return AgentStatus(
        status="ready",
        agent_type="Simple Project Manager (HTTP + MCP)",
        tools_available=["create_project", "create_task", "update_task_status", "get_tasks_by_status", "get_project_tasks", "list_all_projects", "get_task_summary"],
        last_execution=app_state["last_execution"],
        anthropic_api_configured=bool(anthropic_api_key)
    )

@app.post("/agent/execute", response_model=ProjectManagementResponse)
async def execute_project_management(
    request: ProjectManagementRequest,
    background_tasks: BackgroundTasks
) -> ProjectManagementResponse:
    """
    Execute a project management task using the CrewAI agent
    
    This endpoint accepts natural language requests for project management
    and uses the AI agent to execute the appropriate actions.
    
    Examples:
    - "Create a new project called 'Website Redesign' for improving our company website"
    - "Add a high priority task 'Set up development environment' to project 1"
    - "Create project 'Mobile App' and add tasks for user authentication and data sync"
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Executing project management request: {request.request}")
        
        # Validate request
        if not request.request.strip():
            raise HTTPException(
                status_code=400, 
                detail="Request cannot be empty"
            )
        
        # Execute the task using Simple Project Agent (HTTP-based approach)
        agent = SimpleProjectAgent()
        result = agent.execute_project_management_task(request.request)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Update global state
        app_state["last_execution"] = end_time
        app_state["execution_count"] += 1
        
        response = ProjectManagementResponse(
            success=result["success"],
            result=result.get("result"),
            error=result.get("error"),
            request=request.request,
            timestamp=end_time,
            execution_time_seconds=execution_time
        )
        
        logger.info(f"Request completed in {execution_time:.2f}s")
        return response
        
    except Exception as e:
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        logger.error(f"Error executing project management request: {e}")
        
        return ProjectManagementResponse(
            success=False,
            error=str(e),
            request=request.request,
            timestamp=end_time,
            execution_time_seconds=execution_time
        )

@app.get("/agent/metrics")
async def agent_metrics():
    """Get basic metrics about agent usage"""
    return {
        "total_executions": app_state["execution_count"],
        "last_execution": app_state["last_execution"],
        "status": "operational"
    }

@app.get("/web", response_class=HTMLResponse)
async def web_interface():
    """Simple web interface for testing the AI agent"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CrewAI Project Manager - Web Interface</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px; 
                background-color: #f5f5f5; 
            }
            .container { 
                background: white; 
                padding: 30px; 
                border-radius: 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
            }
            h1 { 
                color: #333; 
                text-align: center; 
                margin-bottom: 30px; 
            }
            .form-section { 
                margin: 30px 0; 
                padding: 20px; 
                border: 1px solid #ddd; 
                border-radius: 5px; 
                background: #fafafa; 
            }
            label { 
                display: block; 
                margin: 10px 0 5px 0; 
                font-weight: bold; 
            }
            input, textarea, select { 
                width: 100%; 
                padding: 10px; 
                border: 1px solid #ccc; 
                border-radius: 4px; 
                box-sizing: border-box; 
            }
            button { 
                background: #007bff; 
                color: white; 
                padding: 12px 30px; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 16px; 
                margin: 10px 0; 
            }
            button:hover { 
                background: #0056b3; 
            }
            .result { 
                margin: 20px 0; 
                padding: 15px; 
                border-radius: 4px; 
                background: #e9ecef; 
                border-left: 4px solid #007bff; 
            }
            .success { 
                background: #d4edda; 
                border-left-color: #28a745; 
            }
            .error { 
                background: #f8d7da; 
                border-left-color: #dc3545; 
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 CrewAI Project Manager</h1>
            <p style="text-align: center; color: #666;">Simple web interface for creating projects and tasks</p>
            
            <div class="form-section">
                <h3>📁 Create New Project</h3>
                <form action="/web/create-project" method="post">
                    <label for="project_name">Project Name:</label>
                    <input type="text" id="project_name" name="project_name" required placeholder="e.g., Website Redesign">
                    
                    <label for="project_description">Project Description:</label>
                    <textarea id="project_description" name="project_description" rows="3" required placeholder="Describe what this project is about..."></textarea>
                    
                    <button type="submit">Create Project</button>
                </form>
            </div>
            
            <div class="form-section">
                <h3>✅ Create New Task</h3>
                <form action="/web/create-task" method="post">
                    <label for="task_title">Task Title:</label>
                    <input type="text" id="task_title" name="task_title" required placeholder="e.g., Design homepage mockup">
                    
                    <label for="project_id">Project ID:</label>
                    <input type="number" id="project_id" name="project_id" required placeholder="Enter project ID (from project creation above)">
                    
                    <label for="task_description">Task Description:</label>
                    <textarea id="task_description" name="task_description" rows="3" placeholder="Describe what needs to be done..."></textarea>
                    
                    <label for="priority">Priority:</label>
                    <select id="priority" name="priority" required>
                        <option value="low">Low</option>
                        <option value="medium" selected>Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                    </select>
                    
                    <label for="assigned_to">Assigned To:</label>
                    <input type="text" id="assigned_to" name="assigned_to" placeholder="e.g., john.doe">
                    
                    <button type="submit">Create Task</button>
                </form>
            </div>
            
            <div class="form-section">
                <h3>📊 Quick Actions</h3>
                <a href="/web/projects"><button type="button">View All Projects</button></a>
                <a href="/web/tasks"><button type="button">View All Tasks</button></a>
                <a href="/agent/status"><button type="button">Agent Status</button></a>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/")
async def root():
    """Root endpoint with service information and web interface link"""
    return {
        "service": "Simple Project Manager",
        "version": "1.0.0", 
        "description": "HTTP-based project management agent using MCP tools",
        "implementation": "Simple Agent (HTTP + MCP)",
        "web_interface": "http://localhost:8001/web",
        "endpoints": {
            "web_interface": "/web",
            "execute": "/agent/execute",
            "status": "/agent/status",
            "health": "/health", 
            "metrics": "/agent/metrics"
        },
        "agent_capabilities": [
            "Create projects with detailed descriptions",
            "Create tasks with priorities and assignments", 
            "Natural language processing for project management requests",
            "HTTP-based MCP tool integration"
        ]
    }

@app.post("/web/create-project", response_class=HTMLResponse)
async def web_create_project(
    project_name: str = Form(...),
    project_description: str = Form(...)
):
    """Create a new project via web form"""
    try:
        # Use the AI agent to create the project
        agent = SimpleProjectAgent()
        request_text = f"Create a new project called {project_name} for {project_description}"
        result = agent.execute_project_management_task(request_text)
        
        if result["success"]:
            # Extract project ID from result
            project_id = "Unknown"
            if "result" in result and result["result"]:
                import re
                match = re.search(r'ID: (\d+)', result["result"])
                if match:
                    project_id = match.group(1)
            
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Project Created Successfully</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .success {{ background: #d4edda; padding: 15px; border-radius: 4px; border-left: 4px solid #28a745; margin: 20px 0; }}
                    .project-id {{ font-size: 24px; font-weight: bold; color: #28a745; }}
                    button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; margin: 10px 5px; }}
                    button:hover {{ background: #0056b3; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>✅ Project Created Successfully!</h1>
                    <div class="success">
                        <h3>Project Details:</h3>
                        <p><strong>Name:</strong> {project_name}</p>
                        <p><strong>Description:</strong> {project_description}</p>
                        <p><strong>Project ID:</strong> <span class="project-id">{project_id}</span></p>
                        <p><em>Remember this Project ID to create tasks for this project!</em></p>
                    </div>
                    <div>
                        <a href="/"><button>Back to Main Page</button></a>
                        <a href="/web/projects"><button>View All Projects</button></a>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            error_msg = result.get("error", "Unknown error occurred")
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Project Creation Failed</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .error {{ background: #f8d7da; padding: 15px; border-radius: 4px; border-left: 4px solid #dc3545; }}
                    button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>❌ Project Creation Failed</h1>
                    <div class="error">
                        <p><strong>Error:</strong> {error_msg}</p>
                    </div>
                    <a href="/"><button>Back to Main Page</button></a>
                </div>
            </body>
            </html>
            """
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .error {{ background: #f8d7da; padding: 15px; border-radius: 4px; border-left: 4px solid #dc3545; }}
                button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ System Error</h1>
                <div class="error">
                    <p><strong>Error:</strong> {str(e)}</p>
                </div>
                <a href="/"><button>Back to Main Page</button></a>
            </div>
        </body>
        </html>
        """

@app.post("/web/create-task", response_class=HTMLResponse)
async def web_create_task(
    task_title: str = Form(...),
    project_id: int = Form(...),
    task_description: str = Form(""),
    priority: str = Form("medium"),
    assigned_to: str = Form("")
):
    """Create a new task via web form"""
    try:
        import requests
        
        # Call MCP service directly to create task
        mcp_url = os.getenv("MCP_SERVICE_URL", "http://mcp-http-service:8000")
        
        payload = {
            "name": "create_task",
            "arguments": {
                "title": task_title,
                "project_id": project_id,
                "description": task_description or f"Task: {task_title}",
                "priority": priority,
                "assigned_to": assigned_to or "web-user"
            }
        }
        
        response = requests.post(f"{mcp_url}/tools/call", json=payload, timeout=30)
        result = response.json()
        
        if result.get("success"):
            task = result.get("task", {})
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Task Created Successfully</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .success {{ background: #d4edda; padding: 15px; border-radius: 4px; border-left: 4px solid #28a745; margin: 20px 0; }}
                    .task-id {{ font-size: 24px; font-weight: bold; color: #28a745; }}
                    button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; margin: 10px 5px; }}
                    button:hover {{ background: #0056b3; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>✅ Task Created Successfully!</h1>
                    <div class="success">
                        <h3>Task Details:</h3>
                        <p><strong>Title:</strong> {task.get('title', task_title)}</p>
                        <p><strong>Description:</strong> {task.get('description', task_description)}</p>
                        <p><strong>Priority:</strong> {task.get('priority', priority)}</p>
                        <p><strong>Assigned To:</strong> {task.get('assigned_to', assigned_to)}</p>
                        <p><strong>Project ID:</strong> {task.get('project_id', project_id)}</p>
                        <p><strong>Task ID:</strong> <span class="task-id">{task.get('id', 'Unknown')}</span></p>
                        <p><strong>Status:</strong> {task.get('status', 'pending')}</p>
                    </div>
                    <div>
                        <a href="/"><button>Back to Main Page</button></a>
                        <a href="/web/tasks"><button>View All Tasks</button></a>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            error_msg = result.get("error", "Unknown error occurred")
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Task Creation Failed</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .error {{ background: #f8d7da; padding: 15px; border-radius: 4px; border-left: 4px solid #dc3545; }}
                    button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>❌ Task Creation Failed</h1>
                    <div class="error">
                        <p><strong>Error:</strong> {error_msg}</p>
                    </div>
                    <a href="/"><button>Back to Main Page</button></a>
                </div>
            </body>
            </html>
            """
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .error {{ background: #f8d7da; padding: 15px; border-radius: 4px; border-left: 4px solid #dc3545; }}
                button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ System Error</h1>
                <div class="error">
                    <p><strong>Error:</strong> {str(e)}</p>
                </div>
                <a href="/"><button>Back to Main Page</button></a>
            </div>
        </body>
        </html>
        """

@app.get("/web/projects", response_class=HTMLResponse)
async def web_view_projects():
    """View all projects via web interface"""
    try:
        import requests
        
        # Get all projects from MCP service
        mcp_url = os.getenv("MCP_SERVICE_URL", "http://mcp-http-service:8000")
        
        payload = {
            "name": "list_all_projects",
            "arguments": {}
        }
        
        response = requests.post(f"{mcp_url}/tools/call", json=payload, timeout=30)
        result = response.json()
        
        if result.get("success"):
            projects = result.get("projects", [])
            
            projects_html = ""
            for project in projects:
                projects_html += f"""
                <div class="project-item">
                    <h4>📁 {project.get('name', 'Unnamed Project')} (ID: {project.get('id')})</h4>
                    <p><strong>Description:</strong> {project.get('description', 'No description')}</p>
                    <p><strong>Created:</strong> {project.get('created_at', 'Unknown')}</p>
                </div>
                """
            
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>All Projects</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .project-item {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }}
                    button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; margin: 10px 5px; }}
                    button:hover {{ background: #0056b3; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📁 All Projects ({len(projects)} total)</h1>
                    {projects_html}
                    <div>
                        <a href="/"><button>Back to Main Page</button></a>
                        <a href="/web/tasks"><button>View All Tasks</button></a>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .error {{ background: #f8d7da; padding: 15px; border-radius: 4px; border-left: 4px solid #dc3545; }}
                    button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>❌ Error Loading Projects</h1>
                    <div class="error">
                        <p>Could not load projects from the MCP service.</p>
                    </div>
                    <a href="/"><button>Back to Main Page</button></a>
                </div>
            </body>
            </html>
            """
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .error {{ background: #f8d7da; padding: 15px; border-radius: 4px; border-left: 4px solid #dc3545; }}
                button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ System Error</h1>
                <div class="error">
                    <p><strong>Error:</strong> {str(e)}</p>
                </div>
                <a href="/"><button>Back to Main Page</button></a>
            </div>
        </body>
        </html>
        """

@app.get("/web/tasks", response_class=HTMLResponse)
async def web_view_tasks():
    """View all tasks via web interface"""
    try:
        import requests
        
        # Get all pending tasks from MCP service
        mcp_url = os.getenv("MCP_SERVICE_URL", "http://mcp-http-service:8000")
        
        payload = {
            "name": "get_tasks_by_status",
            "arguments": {"status": "pending"}
        }
        
        response = requests.post(f"{mcp_url}/tools/call", json=payload, timeout=30)
        result = response.json()
        
        if result.get("success"):
            tasks = result.get("tasks", [])
            
            tasks_html = ""
            for task in tasks:
                priority_color = {
                    "critical": "#dc3545",
                    "high": "#fd7e14", 
                    "medium": "#007bff",
                    "low": "#28a745"
                }.get(task.get('priority', 'medium'), "#007bff")
                
                tasks_html += f"""
                <div class="task-item" style="border-left-color: {priority_color}">
                    <h4>✅ {task.get('title', 'Unnamed Task')} (ID: {task.get('id')})</h4>
                    <p><strong>Description:</strong> {task.get('description', 'No description')}</p>
                    <p><strong>Priority:</strong> <span style="color: {priority_color}; font-weight: bold;">{task.get('priority', 'medium').upper()}</span></p>
                    <p><strong>Project ID:</strong> {task.get('project_id')}</p>
                    <p><strong>Assigned To:</strong> {task.get('assigned_to', 'Unassigned')}</p>
                    <p><strong>Status:</strong> {task.get('status', 'pending')}</p>
                </div>
                """
            
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>All Tasks</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .task-item {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }}
                    button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; margin: 10px 5px; }}
                    button:hover {{ background: #0056b3; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>✅ All Pending Tasks ({len(tasks)} total)</h1>
                    {tasks_html}
                    <div>
                        <a href="/"><button>Back to Main Page</button></a>
                        <a href="/web/projects"><button>View All Projects</button></a>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .error {{ background: #f8d7da; padding: 15px; border-radius: 4px; border-left: 4px solid #dc3545; }}
                    button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>❌ Error Loading Tasks</h1>
                    <div class="error">
                        <p>Could not load tasks from the MCP service.</p>
                    </div>
                    <a href="/"><button>Back to Main Page</button></a>
                </div>
            </body>
            </html>
            """
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .error {{ background: #f8d7da; padding: 15px; border-radius: 4px; border-left: 4px solid #dc3545; }}
                button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ System Error</h1>
                <div class="error">
                    <p><strong>Error:</strong> {str(e)}</p>
                </div>
                <a href="/"><button>Back to Main Page</button></a>
            </div>
        </body>
        </html>
        """

def main():
    """Main entry point for running the service"""
    port = int(os.getenv("PORT", 8001))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting CrewAI Project Manager Service on {host}:{port}")
    
    uvicorn.run(
        "crewai_agent.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()