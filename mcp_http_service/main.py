#!/usr/bin/env python3
"""
MCP HTTP Service - HTTP-based MCP Service Implementation

This service provides HTTP endpoints for MCP tools, enabling communication
between AI agents and PostgreSQL database through REST API calls.

Architecture:
CrewAI Agent ←→ HTTP API ←→ This HTTP Service ←→ PostgreSQL Database

Usage:
    python -m mcp_http_service.main [--http]  # For HTTP mode (default)
    python -m mcp_http_service.main --stdio   # For STDIO mode (experimental)
"""

import json
import sys
import os
import logging
import time
import argparse
from typing import Dict, Any, Optional

from .mcp_tools import MCPToolsManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/mcp_http_service.log'),
        logging.StreamHandler(sys.stderr)  # Use stderr to avoid mixing with STDIO protocol
    ]
)
logger = logging.getLogger(__name__)


class MCPStdioService:
    """
    MCP STDIO Service - experimental STDIO protocol support
    
    This service implements the JSON-RPC 2.0 protocol over STDIO for potential
    future CrewAI integration. Currently not used due to dependency conflicts.
    """
    
    def __init__(self):
        """Initialize the MCP STDIO service"""
        self.tools_manager = MCPToolsManager()
        self.initialized = False
        
        logger.info("MCP STDIO Service initialized")
        
        # Wait for database to be ready
        self._wait_for_database()
    
    def _wait_for_database(self, max_retries: int = 30, delay: float = 2.0):
        """Wait for the database to be available"""
        for attempt in range(max_retries):
            try:
                # Test database connection by trying to get task summary
                result = self.tools_manager.get_task_summary()
                if result.get("success", False):
                    logger.info("Database connection verified")
                    return
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}: Database not ready - {e}")
                time.sleep(delay)
        
        logger.error("Database failed to become ready")
        raise RuntimeError("Database is not available")
    
    def _handle_initialize_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        request_id = request_data.get("id")
        
        self.initialized = True
        logger.info("MCP service initialized")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "mcp-http-service",
                    "version": "1.0.0"
                }
            }
        }
    
    def _handle_tools_list_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP tools/list request - return available tools
        
        Returns:
            MCP-formatted response with available tools
        """
        request_id = request_data.get("id")
        tools = self.tools_manager.get_available_tools()
        
        logger.info(f"Returning {len(tools)} available tools")
        
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
        
        logger.info(f"Calling tool: {tool_name} with args: {arguments}")
        
        # Call the tool directly (no HTTP)
        tool_result = self.tools_manager.call_tool(tool_name, arguments)
        
        if tool_result.get("success", False):
            # Success - return the result in MCP format
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(tool_result, indent=2)
                        }
                    ]
                }
            }
        else:
            # Error - return error in MCP format
            error_message = tool_result.get("error", "Unknown error")
            logger.error(f"Tool {tool_name} failed: {error_message}")
            return {
                "jsonrpc": "2.0", 
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {error_message}"
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
            return self._handle_tools_list_request(request_data)
        elif method == "tools/call":
            return self._handle_tools_call_request(request_data)
        else:
            logger.warning(f"Unknown method: {method}")
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
        logger.info("Starting MCP STDIO Service main loop (experimental)")
        
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    # Parse the incoming MCP request
                    request_data = json.loads(line)
                    logger.debug(f"Received request: {request_data}")
                    
                    # Handle the request
                    response = self.handle_request(request_data)
                    
                    # Send response back to CrewAI
                    response_json = json.dumps(response)
                    print(response_json)
                    sys.stdout.flush()
                    logger.debug(f"Sent response: {response}")
                    
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
            logger.info("MCP STDIO Service interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error in main loop: {e}")
            raise
        finally:
            logger.info("MCP STDIO Service shutting down")


def run_http_server():
    """Run HTTP server for backward compatibility"""
    try:
        from fastapi import FastAPI
        import uvicorn
        
        logger.info("Starting MCP HTTP Server")
        
        app = FastAPI(title="MCP HTTP Service", version="1.0.0")
        tools_manager = MCPToolsManager()
        
        @app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "MCP HTTP Service", "version": "1.0.0"}
        
        @app.post("/tools/call")
        async def call_tool(request: dict):
            """Call an MCP tool via HTTP"""
            tool_name = request.get("name")
            arguments = request.get("arguments", {})
            
            logger.info(f"HTTP call to tool: {tool_name} with args: {arguments}")
            result = tools_manager.call_tool(tool_name, arguments)
            return result
        
        # Start the HTTP server
        port = int(os.environ.get('PORT', 8000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        uvicorn.run(app, host=host, port=port, log_level="info")
        
    except ImportError:
        logger.error("FastAPI not available. Install with: pip install fastapi uvicorn")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start HTTP server: {e}")
        sys.exit(1)


def main():
    """Entry point for the MCP HTTP Service"""
    parser = argparse.ArgumentParser(description="MCP HTTP Service")
    parser.add_argument('--stdio', action='store_true', 
                       help='Run in experimental STDIO mode')
    parser.add_argument('--http', action='store_true', 
                       help='Run in HTTP mode (default)')
    args = parser.parse_args()
    
    # Set environment variables for database connection
    os.environ.setdefault('DB_HOST', 'postgres')
    os.environ.setdefault('DB_PORT', '5432')
    os.environ.setdefault('DB_NAME', 'task_management')
    os.environ.setdefault('DB_USER', 'postgres')
    os.environ.setdefault('DB_PASSWORD', 'postgres')
    
    # Also support DATABASE_URL format
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Parse DATABASE_URL if provided
        # Format: postgresql://user:password@host:port/database
        import urllib.parse
        result = urllib.parse.urlparse(database_url)
        if result.hostname:
            os.environ['DB_HOST'] = result.hostname
        if result.port:
            os.environ['DB_PORT'] = str(result.port)
        if result.username:
            os.environ['DB_USER'] = result.username
        if result.password:
            os.environ['DB_PASSWORD'] = result.password
        if result.path and len(result.path) > 1:
            os.environ['DB_NAME'] = result.path[1:]  # Remove leading '/'
    
    if args.stdio:
        logger.info("Starting MCP STDIO Service (experimental)")
        try:
            service = MCPStdioService()
            service.run()
        except Exception as e:
            logger.error(f"Failed to start MCP STDIO Service: {e}")
            sys.exit(1)
    else:
        # Default to HTTP mode
        run_http_server()


if __name__ == "__main__":
    main()