"""
MCP Tools for CrewAI Integration

Custom CrewAI tools that communicate with our MCP service via HTTP.
These tools enable CrewAI agents to create projects and tasks through direct
HTTP communication with the MCP service.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
import requests

logger = logging.getLogger(__name__)

class MCPTool(BaseTool):
    """Base class for MCP tools that communicate via HTTP"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mcp_service_url = os.getenv("MCP_SERVICE_URL", "http://mcp-service:8000")
        self.tools_url = f"{self.mcp_service_url}/tools/call"
        self.session = requests.Session()
        self.session.timeout = 30
    
    def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool via HTTP
        
        Args:
            tool_name: Name of the MCP tool
            arguments: Tool arguments
            
        Returns:
            Tool response dictionary
        """
        payload = {
            "name": tool_name,
            "arguments": arguments
        }
        
        try:
            logger.info(f"Calling MCP tool: {tool_name} with args: {arguments}")
            
            response = self.session.post(
                self.tools_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"MCP tool {tool_name} response: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"HTTP request failed for tool {tool_name}: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error calling tool {tool_name}: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

class CreateProjectArgs(BaseModel):
    """Arguments for the create_project tool"""
    name: str = Field(..., description="Name of the project")
    description: Optional[str] = Field(None, description="Description of the project")

class CreateProjectTool(MCPTool):
    """Tool for creating projects via MCP service"""
    
    name: str = "create_project"
    description: str = "Create a new project with name and optional description"
    args_schema: type[BaseModel] = CreateProjectArgs
    
    def _run(self, name: str, description: Optional[str] = None) -> str:
        """
        Create a new project
        
        Args:
            name: Name of the project
            description: Optional description
            
        Returns:
            String representation of the result
        """
        arguments = {"name": name}
        if description:
            arguments["description"] = description
            
        result = self._call_mcp_tool("create_project", arguments)
        
        if result.get("success", False):
            project = result.get("project", {})
            project_id = project.get("id")
            project_name = project.get("name")
            created_at = project.get("created_at")
            
            return f"""✅ Project created successfully!
📋 Project Details:
- ID: {project_id}
- Name: {project_name}
- Description: {project.get('description', 'No description')}
- Created: {created_at}

The project is now ready for task creation."""
        else:
            error = result.get("error", "Unknown error")
            return f"❌ Failed to create project: {error}"

class CreateTaskArgs(BaseModel):
    """Arguments for the create_task tool"""
    title: str = Field(..., description="Title of the task")
    project_id: int = Field(..., description="ID of the project this task belongs to")
    description: Optional[str] = Field(None, description="Description of the task")
    priority: Optional[str] = Field("medium", description="Priority: low, medium, high, critical")
    assigned_to: Optional[str] = Field(None, description="Person assigned to this task")

class CreateTaskTool(MCPTool):
    """Tool for creating tasks via MCP service"""
    
    name: str = "create_task"
    description: str = "Create a new task within a project with priority and assignment"
    args_schema: type[BaseModel] = CreateTaskArgs
    
    def _run(
        self, 
        title: str, 
        project_id: int, 
        description: Optional[str] = None,
        priority: Optional[str] = "medium",
        assigned_to: Optional[str] = None
    ) -> str:
        """
        Create a new task
        
        Args:
            title: Title of the task
            project_id: ID of the project
            description: Optional description
            priority: Priority level (low, medium, high, critical)
            assigned_to: Optional assignee
            
        Returns:
            String representation of the result
        """
        arguments = {
            "title": title,
            "project_id": project_id
        }
        
        if description:
            arguments["description"] = description
        if priority:
            arguments["priority"] = priority
        if assigned_to:
            arguments["assigned_to"] = assigned_to
            
        result = self._call_mcp_tool("create_task", arguments)
        
        if result.get("success", False):
            task = result.get("task", {})
            task_id = task.get("id")
            task_title = task.get("title")
            task_status = task.get("status")
            task_priority = task.get("priority")
            task_assigned = task.get("assigned_to")
            created_at = task.get("created_at")
            
            return f"""✅ Task created successfully!
📋 Task Details:
- ID: {task_id}
- Title: {task_title}
- Description: {task.get('description', 'No description')}
- Project ID: {project_id}
- Status: {task_status}
- Priority: {task_priority}
- Assigned to: {task_assigned or 'Unassigned'}
- Created: {created_at}

The task is now ready and can be worked on."""
        else:
            error = result.get("error", "Unknown error")
            return f"❌ Failed to create task: {error}"