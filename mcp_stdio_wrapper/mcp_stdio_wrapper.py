#!/usr/bin/env python3
"""
MCP STDIO Wrapper for CrewAI Integration

This wrapper translates between CrewAI's expected STDIO MCP communication
and our HTTP-based MCP service. It acts as a bridge allowing CrewAI agents
to use MCP tools via standard input/output while communicating with the
HTTP MCP service running on port 8000.

Architecture:
CrewAI Agent ←→ STDIO ←→ This Wrapper ←→ HTTP ←→ MCP Service ←→ PostgreSQL
"""

import json
import sys
import requests
import logging
from typing import Dict, Any, Optional
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/mcp_stdio_wrapper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MCPStdioWrapper:
    def __init__(self, http_url: str = "http://mcp-service:8000"):
        """
        Initialize the MCP STDIO wrapper
        
        Args:
            http_url: URL of the HTTP MCP service (default uses Docker service name)
        """
        self.http_url = http_url
        self.tools_url = f"{http_url}/tools/call"
        self.health_url = f"{http_url}/health"
        self.session = requests.Session()
        self.session.timeout = 30
        
        logger.info(f"MCP STDIO Wrapper initialized with HTTP URL: {http_url}")
        
        # Wait for MCP service to be ready
        self._wait_for_service()
    
    def _wait_for_service(self, max_retries: int = 30, delay: float = 2.0):
        """Wait for the MCP HTTP service to be available"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(self.health_url, timeout=5)
                if response.status_code == 200:
                    logger.info("MCP HTTP service is ready")
                    return
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}: MCP service not ready - {e}")
                time.sleep(delay)
        
        logger.error("MCP HTTP service failed to become ready")
        raise RuntimeError("MCP HTTP service is not available")
    
    def _call_http_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool via HTTP and return the response
        
        Args:
            tool_name: Name of the MCP tool to call
            arguments: Arguments for the tool
            
        Returns:
            Dict containing the tool response
        """
        payload = {
            "name": tool_name,
            "arguments": arguments
        }
        
        try:
            logger.info(f"Calling HTTP tool: {tool_name} with args: {arguments}")
            response = self.session.post(
                self.tools_url, 
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Tool {tool_name} returned: {result}")
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
    
    def _handle_tools_list_request(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle MCP tools/list request - return available tools
        
        Returns:
            MCP-formatted response with available tools
        """
        tools = [
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
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
    
    def _handle_tools_call_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP tools/call request
        
        Args:
            request_data: MCP request data
            
        Returns:
            MCP-formatted response
        """
        request_id = request_data.get("id")
        params = request_data.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": "Tool name is required"
                }
            }
        
        # Call the HTTP MCP service
        http_result = self._call_http_tool(tool_name, arguments)
        
        if http_result.get("success", False):
            # Success - return the result in MCP format
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(http_result, indent=2)
                        }
                    ]
                }
            }
        else:
            # Error - return error in MCP format
            error_message = http_result.get("error", "Unknown error")
            return {
                "jsonrpc": "2.0", 
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {error_message}"
                }
            }
    
    def _handle_initialize_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        request_id = request_data.get("id")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "mcp-stdio-wrapper",
                    "version": "1.0.0"
                }
            }
        }
    
    def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an MCP request and return the appropriate response
        
        Args:
            request_data: Parsed MCP request
            
        Returns:
            MCP response dictionary
        """
        method = request_data.get("method")
        request_id = request_data.get("id")
        
        logger.info(f"Handling MCP request: {method}")
        
        if method == "initialize":
            return self._handle_initialize_request(request_data)
        elif method == "tools/list":
            return self._handle_tools_list_request(request_id)
        elif method == "tools/call":
            return self._handle_tools_call_request(request_data)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    def run(self):
        """
        Main STDIO loop for CrewAI communication
        
        Reads JSON-RPC requests from stdin and writes responses to stdout
        """
        logger.info("Starting MCP STDIO wrapper main loop")
        
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    # Parse the incoming MCP request
                    request_data = json.loads(line)
                    logger.info(f"Received request: {request_data}")
                    
                    # Handle the request
                    response = self.handle_request(request_data)
                    
                    # Send response back to CrewAI
                    response_json = json.dumps(response)
                    print(response_json)
                    sys.stdout.flush()
                    logger.info(f"Sent response: {response}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {line} - Error: {e}")
                    # Send error response for invalid JSON
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                    
                except Exception as e:
                    logger.error(f"Error processing request: {e}")
                    error_response = {
                        "jsonrpc": "2.0", 
                        "id": None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {e}"
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                    
        except KeyboardInterrupt:
            logger.info("MCP STDIO wrapper interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error in main loop: {e}")
            raise

def main():
    """Entry point for the MCP STDIO wrapper"""
    import os
    
    # Allow override of MCP service URL via environment variable
    mcp_url = os.getenv("MCP_SERVICE_URL", "http://mcp-service:8000")
    
    wrapper = MCPStdioWrapper(mcp_url)
    wrapper.run()

if __name__ == "__main__":
    main()