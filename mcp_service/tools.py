from fastmcp import FastMCP
from .database import DatabaseManager
from .models import ProjectCreate, TaskCreate, TaskStatus
import json


def setup_mcp_tools(mcp: FastMCP):
    db = DatabaseManager()

    @mcp.tool()
    def create_project(name: str, description: str = None) -> str:
        """Create a new project"""
        try:
            project_data = ProjectCreate(name=name, description=description)
            project = db.create_project(project_data)
            return json.dumps({
                "success": True,
                "project": {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "created_at": project.created_at.isoformat()
                }
            })
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    def create_task(
        title: str, 
        project_id: int, 
        description: str = None, 
        priority: str = "medium", 
        assigned_to: str = None
    ) -> str:
        """Create a new task with priority and assignment"""
        try:
            task_data = TaskCreate(
                title=title,
                description=description,
                priority=priority,
                project_id=project_id,
                assigned_to=assigned_to
            )
            task = db.create_task(task_data)
            return json.dumps({
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "project_id": task.project_id,
                    "assigned_to": task.assigned_to,
                    "created_at": task.created_at.isoformat()
                }
            })
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    def update_task_status(task_id: int, status: str) -> str:
        """Update task status (pending → in_progress → completed)"""
        try:
            task_status = TaskStatus(status)
            task = db.update_task_status(task_id, task_status)
            if task:
                return json.dumps({
                    "success": True,
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "status": task.status,
                        "updated_at": task.updated_at.isoformat()
                    }
                })
            else:
                return json.dumps({"success": False, "error": "Task not found"})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    def get_tasks_by_status(status: str) -> str:
        """Filter tasks by status"""
        try:
            task_status = TaskStatus(status)
            tasks = db.get_tasks_by_status(task_status)
            return json.dumps({
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
                        "created_at": task.created_at.isoformat()
                    }
                    for task in tasks
                ]
            })
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    def get_project_tasks(project_id: int) -> str:
        """Get all tasks for a project"""
        try:
            tasks = db.get_project_tasks(project_id)
            return json.dumps({
                "success": True,
                "project_id": project_id,
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "priority": task.priority,
                        "assigned_to": task.assigned_to,
                        "created_at": task.created_at.isoformat()
                    }
                    for task in tasks
                ]
            })
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    def list_all_projects() -> str:
        """List all projects"""
        try:
            projects = db.get_all_projects()
            return json.dumps({
                "success": True,
                "projects": [
                    {
                        "id": project.id,
                        "name": project.name,
                        "description": project.description,
                        "created_at": project.created_at.isoformat()
                    }
                    for project in projects
                ]
            })
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    def get_task_summary() -> str:
        """Get task counts by status"""
        try:
            summary = db.get_task_summary()
            return json.dumps({
                "success": True,
                "summary": {
                    "total_tasks": summary.total_tasks,
                    "pending": summary.pending,
                    "in_progress": summary.in_progress,
                    "completed": summary.completed,
                    "cancelled": summary.cancelled
                }
            })
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})