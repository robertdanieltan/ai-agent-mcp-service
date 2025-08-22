"""
Project Manager AI Agent - DEPRECATED

This module contains experimental native CrewAI MCP integration code
that has dependency conflicts (CrewAI requires anyio>=4.5 while FastAPI requires anyio<4.0.0).

The project now uses HTTP-based MCP integration via the Simple Agent instead.
This file is retained for reference but is not actively used.
"""

# This module is deprecated and not currently used due to dependency conflicts.
# Please use SimpleProjectAgent from simple_agent.py instead.