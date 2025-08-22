"""
MCP STDIO Service - Combined MCP Service with STDIO Communication

This module combines the MCP service functionality with STDIO wrapper communication
for direct CrewAI integration without the need for separate HTTP communication.

Architecture:
CrewAI Agent ←→ STDIO ←→ This Combined Service ←→ PostgreSQL Database
"""

__version__ = "1.0.0"
__author__ = "AI Agent MCP Service Project"