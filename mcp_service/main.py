import uvicorn
from fastapi import FastAPI
from .database import DatabaseManager
from .models import ProjectCreate, TaskCreate, TaskStatus


app = FastAPI(title="Task Management MCP Service", version="1.0.0")
db = DatabaseManager()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Task Management MCP Service"}


@app.post("/tools/call")
async def call_tool(request: dict):
    """Call an MCP tool"""
    tool_name = request.get("name")
    arguments = request.get("arguments", {})
    
    try:
        if tool_name == "create_project":
            project_data = ProjectCreate(**arguments)
            project = db.create_project(project_data)
            return {
                "success": True,
                "project": {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "created_at": project.created_at.isoformat()
                }
            }
        
        elif tool_name == "create_task":
            task_data = TaskCreate(**arguments)
            task = db.create_task(task_data)
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
                    "created_at": task.created_at.isoformat()
                }
            }
        
        elif tool_name == "update_task_status":
            task_id = arguments.get("task_id")
            status = TaskStatus(arguments.get("status"))
            task = db.update_task_status(task_id, status)
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
        
        elif tool_name == "get_tasks_by_status":
            status = TaskStatus(arguments.get("status"))
            tasks = db.get_tasks_by_status(status)
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
                        "created_at": task.created_at.isoformat()
                    }
                    for task in tasks
                ]
            }
        
        elif tool_name == "get_project_tasks":
            project_id = arguments.get("project_id")
            tasks = db.get_project_tasks(project_id)
            return {
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
            }
        
        elif tool_name == "list_all_projects":
            projects = db.get_all_projects()
            return {
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
            }
        
        elif tool_name == "get_task_summary":
            summary = db.get_task_summary()
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
        
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """Main entry point for the MCP service"""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()