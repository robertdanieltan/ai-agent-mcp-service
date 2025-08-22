#!/usr/bin/env python3
"""
Simple Web Interface for CrewAI Project Manager
A standalone web server that provides a simple HTML interface for testing
"""
import os
import requests
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="Simple Web Interface", version="1.0.0")

# Configuration
AGENT_URL = "http://localhost:8001"
MCP_URL = "http://localhost:8000"

@app.get("/", response_class=HTMLResponse)
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
                <form action="/create-project" method="post">
                    <label for="project_name">Project Name:</label>
                    <input type="text" id="project_name" name="project_name" required placeholder="e.g., Website Redesign">
                    
                    <label for="project_description">Project Description:</label>
                    <textarea id="project_description" name="project_description" rows="3" required placeholder="Describe what this project is about..."></textarea>
                    
                    <button type="submit">Create Project</button>
                </form>
            </div>
            
            <div class="form-section">
                <h3>✅ Create New Task</h3>
                <form action="/create-task" method="post">
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
                <a href="/projects"><button type="button">View All Projects</button></a>
                <a href="/tasks"><button type="button">View All Tasks</button></a>
                <a href="/status"><button type="button">Agent Status</button></a>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.post("/create-project", response_class=HTMLResponse)
async def create_project(
    project_name: str = Form(...),
    project_description: str = Form(...)
):
    """Create a new project via web form"""
    try:
        # Call the AI agent
        response = requests.post(f"{AGENT_URL}/agent/execute", json={
            "request": f"Create a new project called {project_name} for {project_description}"
        }, timeout=30)
        
        result = response.json()
        
        if result.get("success"):
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
                        <a href="/projects"><button>View All Projects</button></a>
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
            <head><title>Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .error {{ background: #f8d7da; padding: 15px; border-radius: 4px; border-left: 4px solid #dc3545; }}
                button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; }}
            </style></head>
            <body><h1>❌ Error</h1><div class="error"><p>{error_msg}</p></div><a href="/"><button>Back</button></a></body></html>
            """
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p><a href='/'>Back</a>"

@app.post("/create-task", response_class=HTMLResponse)
async def create_task(
    task_title: str = Form(...),
    project_id: int = Form(...),
    task_description: str = Form(""),
    priority: str = Form("medium"),
    assigned_to: str = Form("")
):
    """Create a new task via web form"""
    try:
        # Call MCP service directly
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
        
        response = requests.post(f"{MCP_URL}/tools/call", json=payload, timeout=30)
        result = response.json()
        
        if result.get("success"):
            task = result.get("task", {})
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>Task Created Successfully</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .success {{ background: #d4edda; padding: 15px; border-radius: 4px; border-left: 4px solid #28a745; margin: 20px 0; }}
                .task-id {{ font-size: 20px; font-weight: bold; color: #28a745; }}
                button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }}
            </style></head>
            <body>
                <h1>✅ Task Created Successfully!</h1>
                <div class="success">
                    <p><strong>Title:</strong> {task.get('title', task_title)}</p>
                    <p><strong>Priority:</strong> {task.get('priority', priority)}</p>
                    <p><strong>Project ID:</strong> {task.get('project_id', project_id)}</p>
                    <p><strong>Task ID:</strong> <span class="task-id">{task.get('id', 'Unknown')}</span></p>
                </div>
                <a href="/"><button>Back to Main Page</button></a>
                <a href="/tasks"><button>View All Tasks</button></a>
            </body>
            </html>
            """
        else:
            return f"<h1>❌ Task Creation Failed</h1><p>{result.get('error', 'Unknown error')}</p><a href='/'>Back</a>"
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p><a href='/'>Back</a>"

@app.get("/projects", response_class=HTMLResponse)
async def view_projects():
    """View all projects"""
    try:
        response = requests.post(f"{MCP_URL}/tools/call", json={
            "name": "list_all_projects",
            "arguments": {}
        }, timeout=30)
        
        result = response.json()
        if result.get("success"):
            projects = result.get("projects", [])
            projects_html = ""
            for project in projects:
                projects_html += f"""
                <div style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff;">
                    <h4>📁 {project.get('name', 'Unnamed')} (ID: {project.get('id')})</h4>
                    <p><strong>Description:</strong> {project.get('description', 'No description')}</p>
                    <p><strong>Created:</strong> {project.get('created_at', 'Unknown')}</p>
                </div>
                """
            
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>All Projects</title>
            <style>body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }}</style></head>
            <body>
                <h1>📁 All Projects ({len(projects)} total)</h1>
                {projects_html}
                <a href="/"><button>Back to Main Page</button></a>
            </body>
            </html>
            """
        else:
            return "<h1>Error loading projects</h1><a href='/'>Back</a>"
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p><a href='/'>Back</a>"

@app.get("/tasks", response_class=HTMLResponse) 
async def view_tasks():
    """View all tasks"""
    try:
        response = requests.post(f"{MCP_URL}/tools/call", json={
            "name": "get_tasks_by_status",
            "arguments": {"status": "pending"}
        }, timeout=30)
        
        result = response.json()
        if result.get("success"):
            tasks = result.get("tasks", [])
            tasks_html = ""
            for task in tasks:
                priority_color = {"critical": "#dc3545", "high": "#fd7e14", "medium": "#007bff", "low": "#28a745"}.get(task.get('priority', 'medium'), "#007bff")
                tasks_html += f"""
                <div style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid {priority_color};">
                    <h4>✅ {task.get('title', 'Unnamed')} (ID: {task.get('id')})</h4>
                    <p><strong>Priority:</strong> <span style="color: {priority_color}; font-weight: bold;">{task.get('priority', 'medium').upper()}</span></p>
                    <p><strong>Project ID:</strong> {task.get('project_id')}</p>
                    <p><strong>Assigned To:</strong> {task.get('assigned_to', 'Unassigned')}</p>
                </div>
                """
            
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>All Tasks</title>
            <style>body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }}</style></head>
            <body>
                <h1>✅ All Pending Tasks ({len(tasks)} total)</h1>
                {tasks_html}
                <a href="/"><button>Back to Main Page</button></a>
            </body>
            </html>
            """
        else:
            return "<h1>Error loading tasks</h1><a href='/'>Back</a>"
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p><a href='/'>Back</a>"

@app.get("/status", response_class=HTMLResponse)
async def agent_status():
    """Check agent status"""
    try:
        response = requests.get(f"{AGENT_URL}/agent/status", timeout=10)
        status = response.json()
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Agent Status</title>
        <style>body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        button {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }}</style></head>
        <body>
            <h1>🤖 Agent Status</h1>
            <div style="background: #e9ecef; padding: 15px; border-radius: 4px;">
                <p><strong>Status:</strong> {status.get('status')}</p>
                <p><strong>Type:</strong> {status.get('agent_type')}</p>
                <p><strong>Tools Available:</strong> {len(status.get('tools_available', []))}</p>
                <p><strong>API Configured:</strong> {status.get('anthropic_api_configured')}</p>
            </div>
            <a href="/"><button>Back to Main Page</button></a>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>Status Check Failed</h1><p>{str(e)}</p><a href='/'>Back</a>"

if __name__ == "__main__":
    print("🚀 Starting Simple Web Interface on http://localhost:9000")
    print("   Make sure CrewAI agent is running on port 8001")
    print("   Make sure MCP service is running on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=9000)