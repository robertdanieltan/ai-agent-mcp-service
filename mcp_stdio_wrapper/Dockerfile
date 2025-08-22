# Dockerfile for MCP STDIO Wrapper
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy wrapper code
COPY mcp_stdio_wrapper/ .

# Create non-root user
RUN groupadd -r mcpwrapper && useradd -r -g mcpwrapper mcpwrapper
RUN chown -R mcpwrapper:mcpwrapper /app

# Switch to non-root user
USER mcpwrapper

# Set environment variables
ENV PYTHONPATH=/app
ENV MCP_SERVICE_URL=http://mcp-service:8000

# Default command - can be overridden
CMD ["python", "mcp_stdio_wrapper.py"]