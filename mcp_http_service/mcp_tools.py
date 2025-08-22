"""
MCP Tools - Direct Implementation for STDIO Service

Contains all MCP tool implementations that can be called directly without HTTP.
Extracted from the original mcp_service FastAPI implementation and converted
to direct function calls.
"""

import logging
from typing import Dict, Any
from .database import DatabaseManager
from .models import ProjectCreate, TaskCreate, TaskStatus

logger = logging.getLogger(__name__)


class MCPToolsManager:
    """Manager class for all MCP tools with direct database access"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.tools = {
            'create_project': self.create_project,
            'create_task': self.create_task,
            'update_task_status': self.update_task_status,
            'get_tasks_by_status': self.get_tasks_by_status,
            'get_project_tasks': self.get_project_tasks,
            'list_all_projects': self.list_all_projects,
            'get_task_summary': self.get_task_summary
        }
        logger.info("MCP Tools Manager initialized with 7 tools")
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool by name with given arguments
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Dict containing success status and result/error
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
        
        try:
            result = self.tools[tool_name](**arguments)
            return result
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_tools(self) -> list:
        """Get list of available tools with their schemas"""
        return [
            {
                "name": "create_project",
                "description": "Create a new project with name and description",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the project"
                        },
                        "description": {
                            "type": "string", 
                            "description": "Description of the project"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "create_task",
                "description": "Create a new task within a project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Title of the task"
                        },
                        "project_id": {
                            "type": "integer",
                            "description": "ID of the project this task belongs to"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the task"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                            "description": "Priority level of the task"
                        },
                        "assigned_to": {
                            "type": "string",
                            "description": "Person assigned to this task"
                        }
                    },
                    "required": ["title", "project_id"]
                }
            },
            {
                "name": "update_task_status",
                "description": "Update the status of an existing task",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to update"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed", "cancelled"],
                            "description": "New status for the task"
                        }
                    },
                    "required": ["task_id", "status"]
                }
            },
            {
                "name": "get_tasks_by_status",
                "description": "Retrieve all tasks with a specific status",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed", "cancelled"],
                            "description": "Status to filter tasks by"
                        }
                    },
                    "required": ["status"]
                }
            },
            {
                "name": "get_project_tasks",
                "description": "Get all tasks for a specific project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "integer",
                            "description": "ID of the project"
                        }
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "list_all_projects",
                "description": "Get a list of all projects",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_task_summary",
                "description": "Get a summary of task counts by status",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    def create_project(self, name: str, description: str = None) -> Dict[str, Any]:
        """Create a new project"""
        try:
            project_data = ProjectCreate(name=name, description=description)
            project = self.db.create_project(project_data)
            return {
                "success": True,
                "project": {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {"success": False, "error": str(e)}

    def create_task(
        self, 
        title: str, 
        project_id: int, 
        description: str = None, 
        priority: str = "medium", 
        assigned_to: str = None
    ) -> Dict[str, Any]:
        """Create a new task with priority and assignment"""
        try:
            task_data = TaskCreate(
                title=title,
                description=description,
                priority=priority,
                project_id=project_id,
                assigned_to=assigned_to
            )
            task = self.db.create_task(task_data)
            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "project_id": task.project_id,
                    "assigned_to": task.assigned_to,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return {"success": False, "error": str(e)}

    def update_task_status(self, task_id: int, status: str) -> Dict[str, Any]:
        """Update task status (pending → in_progress → completed)"""
        try:
            task_status = TaskStatus(status)
            task = self.db.update_task_status(task_id, task_status)
            if task:
                return {
                    "success": True,
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "status": task.status,
                        "updated_at": task.updated_at.isoformat()
                    }
                }
            else:
                return {"success": False, "error": "Task not found"}
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return {"success": False, "error": str(e)}

    def get_tasks_by_status(self, status: str) -> Dict[str, Any]:
        """Filter tasks by status"""
        try:
            task_status = TaskStatus(status)
            tasks = self.db.get_tasks_by_status(task_status)
            return {
                "success": True,
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "priority": task.priority,
                        "project_id": task.project_id,
                        "assigned_to": task.assigned_to,
                        "created_at": task.created_at.isoformat(),
                        "updated_at": task.updated_at.isoformat()
                    }
                    for task in tasks
                ],
                "count": len(tasks)
            }
        except Exception as e:
            logger.error(f"Error getting tasks by status: {e}")
            return {"success": False, "error": str(e)}

    def get_project_tasks(self, project_id: int) -> Dict[str, Any]:
        """Get all tasks for a project"""
        try:
            project = self.db.get_project(project_id)
            if not project:
                return {"success": False, "error": "Project not found"}
                
            tasks = self.db.get_project_tasks(project_id)
            return {
                "success": True,
                "project": {
                    "id": project.id,
                    "name": project.name
                },
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "priority": task.priority,
                        "assigned_to": task.assigned_to,
                        "created_at": task.created_at.isoformat(),
                        "updated_at": task.updated_at.isoformat()
                    }
                    for task in tasks
                ],
                "count": len(tasks)
            }
        except Exception as e:
            logger.error(f"Error getting project tasks: {e}")
            return {"success": False, "error": str(e)}

    def list_all_projects(self) -> Dict[str, Any]:
        """List all projects"""
        try:
            projects = self.db.get_all_projects()
            return {
                "success": True,
                "projects": [
                    {
                        "id": project.id,
                        "name": project.name,
                        "description": project.description,
                        "created_at": project.created_at.isoformat(),
                        "updated_at": project.updated_at.isoformat()
                    }
                    for project in projects
                ],
                "count": len(projects)
            }
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return {"success": False, "error": str(e)}

    def get_task_summary(self) -> Dict[str, Any]:
        """Get task counts by status"""
        try:
            summary = self.db.get_task_summary()
            return {
                "success": True,
                "summary": {
                    "total_tasks": summary.total_tasks,
                    "pending": summary.pending,
                    "in_progress": summary.in_progress,
                    "completed": summary.completed,
                    "cancelled": summary.cancelled
                }
            }
        except Exception as e:
            logger.error(f"Error getting task summary: {e}")
            return {"success": False, "error": str(e)}