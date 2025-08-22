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

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
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
        agent_type="Project Manager (CrewAI + MCP)",
        tools_available=["create_project", "create_task"],
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
        
        # Execute the task using Simple Project Agent
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

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "CrewAI Project Manager",
        "version": "1.0.0",
        "description": "AI-powered project management agent using CrewAI and MCP",
        "endpoints": {
            "execute": "/agent/execute",
            "status": "/agent/status", 
            "health": "/health",
            "metrics": "/agent/metrics"
        },
        "agent_capabilities": [
            "Create projects with detailed descriptions",
            "Create tasks with priorities and assignments",
            "Natural language processing for project management requests"
        ]
    }

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