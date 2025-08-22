"""
Project Manager AI Agent

A CrewAI agent specialized in project management tasks. This agent can:
- Create new projects with proper descriptions
- Create tasks within projects with appropriate priorities and assignments
- Provide guidance on project organization and task management

The agent uses MCP tools to interact with the task management database
through the STDIO wrapper.
"""

import os
import logging
from typing import Optional, Dict, Any
from crewai import Agent, Task, Crew, LLM
from crewai.project import CrewBase, agent, task, crew
from .mcp_tools import CreateProjectTool, CreateTaskTool

logger = logging.getLogger(__name__)

class ProjectManagerCrew(CrewBase):
    """CrewAI project for the Project Manager agent"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self):
        super().__init__()
        
        # Initialize Anthropic Claude LLM
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.llm = LLM(
            model="claude-3-sonnet-20240229",
            api_key=anthropic_api_key
        )
        
        # Initialize MCP tools
        self.create_project_tool = CreateProjectTool()
        self.create_task_tool = CreateTaskTool()
    
    @agent
    def project_manager(self) -> Agent:
        """
        Project Manager Agent
        
        A specialized AI agent focused on project management and task coordination.
        Uses MCP tools to create projects and tasks in the database.
        """
        return Agent(
            role="Senior Project Manager",
            goal="""Efficiently manage projects and tasks by creating well-structured projects 
                   and breaking down work into actionable tasks with appropriate priorities and assignments.""",
            backstory="""You are an experienced project manager with expertise in software development, 
                        task organization, and team coordination. You excel at:
                        
                        - Creating clear, well-defined projects with comprehensive descriptions
                        - Breaking down complex work into manageable tasks
                        - Assigning appropriate priorities based on business impact and urgency
                        - Ensuring tasks are properly assigned to team members
                        - Following project management best practices
                        
                        You use a systematic approach to project organization and always ensure
                        that projects and tasks are created with sufficient detail for team members
                        to understand and execute effectively.""",
            tools=[self.create_project_tool, self.create_task_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
    
    @task  
    def manage_project_request(self) -> Task:
        """
        Task for handling project management requests
        
        This task processes natural language requests for project management
        and executes the appropriate actions using MCP tools.
        """
        return Task(
            description="""Process the user's project management request and take appropriate action.
                         
                         You should:
                         1. Analyze the request to understand what needs to be created
                         2. If a new project is needed, create it with a clear name and description
                         3. If tasks are needed, create them with appropriate details:
                            - Clear, actionable titles
                            - Helpful descriptions when provided
                            - Appropriate priority levels (low, medium, high, critical)
                            - Assignments when specified
                         4. Provide a clear summary of what was accomplished
                         
                         Always ensure that:
                         - Project names are clear and professional
                         - Task titles are specific and actionable
                         - Priorities reflect the actual importance and urgency
                         - All information is captured accurately""",
            agent=self.project_manager(),
            expected_output="""A detailed summary of the project management actions taken,
                             including any projects or tasks created, with their IDs and key details."""
        )
    
    @crew
    def crew(self) -> Crew:
        """Create and return the crew for project management"""
        return Crew(
            agents=[self.project_manager()],
            tasks=[self.manage_project_request()],
            verbose=True,
            process="sequential"
        )

def create_project_manager_agent() -> Agent:
    """
    Factory function to create a standalone Project Manager agent
    
    Returns:
        Configured Project Manager Agent with MCP tools
    """
    # Initialize Anthropic Claude LLM
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    llm = LLM(
        model="claude-3-sonnet-20240229",
        api_key=anthropic_api_key
    )
    
    # Initialize MCP tools
    create_project_tool = CreateProjectTool()
    create_task_tool = CreateTaskTool()
    
    return Agent(
        role="Senior Project Manager",
        goal="""Efficiently manage projects and tasks by creating well-structured projects 
               and breaking down work into actionable tasks with appropriate priorities and assignments.""",
        backstory="""You are an experienced project manager with expertise in software development, 
                    task organization, and team coordination. You excel at:
                    
                    - Creating clear, well-defined projects with comprehensive descriptions
                    - Breaking down complex work into manageable tasks
                    - Assigning appropriate priorities based on business impact and urgency
                    - Ensuring tasks are properly assigned to team members
                    - Following project management best practices
                    
                    You use a systematic approach to project organization and always ensure
                    that projects and tasks are created with sufficient detail for team members
                    to understand and execute effectively.""",
        tools=[create_project_tool, create_task_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )

def execute_project_management_task(request: str) -> Dict[str, Any]:
    """
    Execute a project management task using the CrewAI agent
    
    Args:
        request: Natural language description of what to do
        
    Returns:
        Dictionary containing the execution result
    """
    try:
        logger.info(f"Executing project management request: {request}")
        
        # Create the agent
        agent = create_project_manager_agent()
        
        # Create a task for the request
        task = Task(
            description=f"""Process this project management request: {request}
                         
                         Analyze the request and take appropriate action:
                         - If a new project is needed, create it with a clear name and description
                         - If tasks are needed, create them with appropriate details
                         - Provide a summary of actions taken
                         
                         Request: {request}""",
            agent=agent,
            expected_output="Detailed summary of project management actions completed"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        logger.info(f"Project management task completed: {result}")
        
        return {
            "success": True,
            "result": str(result),
            "request": request
        }
        
    except Exception as e:
        logger.error(f"Error executing project management task: {e}")
        return {
            "success": False,
            "error": str(e),
            "request": request
        }