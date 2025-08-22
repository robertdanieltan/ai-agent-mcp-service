"""
Simple Project Management Agent

A lightweight alternative that demonstrates the MCP integration concept
without the complex CrewAI dependencies. This agent directly calls the
MCP service via HTTP to manage projects and tasks.
"""

import os
import json
import logging
from typing import Dict, Any
import requests
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class SimpleProjectAgent:
    def __init__(self):
        # Initialize Anthropic client
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.anthropic = Anthropic(api_key=self.anthropic_api_key)
        
        # MCP service configuration
        self.mcp_service_url = os.getenv("MCP_SERVICE_URL", "http://mcp-service:8000")
        self.tools_url = f"{self.mcp_service_url}/tools/call"
        
        logger.info(f"Simple Project Agent initialized with MCP URL: {self.mcp_service_url}")
    
    def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool via HTTP"""
        payload = {
            "name": tool_name,
            "arguments": arguments
        }
        
        try:
            logger.info(f"Calling MCP tool: {tool_name} with args: {arguments}")
            
            response = requests.post(
                self.tools_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"MCP tool {tool_name} response: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_request_with_claude(self, user_request: str) -> Dict[str, Any]:
        """Use Claude to analyze the user request and determine actions"""
        system_prompt = """You are a project management AI assistant. Analyze user requests and determine what actions to take.

You have access to these MCP tools:
1. create_project(name, description) - Creates a new project
2. create_task(title, project_id, description, priority, assigned_to) - Creates a task

Respond with a JSON object containing:
{
    "actions": [
        {
            "tool": "create_project" or "create_task",
            "arguments": {...}
        }
    ],
    "explanation": "What you're going to do and why"
}

Priority levels: low, medium, high, critical
"""
        
        try:
            message = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_request
                    }
                ]
            )
            
            response_text = message.content[0].text
            logger.info(f"Claude response: {response_text}")
            
            # Try to extract JSON from Claude's response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {
                    "actions": [],
                    "explanation": "Could not parse Claude's response into actions",
                    "raw_response": response_text
                }
                
        except Exception as e:
            logger.error(f"Error calling Claude: {e}")
            return {
                "actions": [],
                "explanation": f"Error analyzing request: {e}"
            }
    
    def execute_project_management_task(self, user_request: str) -> Dict[str, Any]:
        """Execute a project management task based on user request"""
        try:
            logger.info(f"Processing request: {user_request}")
            
            # Use Claude to analyze the request
            analysis = self.analyze_request_with_claude(user_request)
            
            results = []
            
            # Execute the planned actions
            for action in analysis.get("actions", []):
                tool_name = action.get("tool")
                arguments = action.get("arguments", {})
                
                if tool_name in ["create_project", "create_task"]:
                    result = self.call_mcp_tool(tool_name, arguments)
                    results.append({
                        "tool": tool_name,
                        "arguments": arguments,
                        "result": result
                    })
                else:
                    logger.warning(f"Unknown tool: {tool_name}")
            
            # Format the response
            response = {
                "success": True,
                "request": user_request,
                "analysis": analysis.get("explanation", ""),
                "actions_executed": len(results),
                "results": results
            }
            
            # Create a human-readable summary
            summary_parts = [analysis.get("explanation", "")]
            
            for i, result in enumerate(results, 1):
                tool = result["tool"]
                success = result["result"].get("success", False)
                if success:
                    if tool == "create_project":
                        project = result["result"].get("project", {})
                        summary_parts.append(f"{i}. ✅ Created project '{project.get('name')}' (ID: {project.get('id')})")
                    elif tool == "create_task":
                        task = result["result"].get("task", {})
                        summary_parts.append(f"{i}. ✅ Created task '{task.get('title')}' (ID: {task.get('id')}, Priority: {task.get('priority')})")
                else:
                    error = result["result"].get("error", "Unknown error")
                    summary_parts.append(f"{i}. ❌ Failed to execute {tool}: {error}")
            
            response["summary"] = "\n".join(summary_parts)
            
            logger.info(f"Task execution completed: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error executing project management task: {e}")
            return {
                "success": False,
                "error": str(e),
                "request": user_request
            }