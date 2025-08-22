# Multi-stage build for MCP HTTP Service
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY mcp_http_service/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user first
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

# Copy Python packages from builder stage to mcpuser home
COPY --from=builder /root/.local /home/mcpuser/.local
RUN chown -R mcpuser:mcpuser /home/mcpuser/.local

# Make sure scripts in .local are usable for mcpuser
ENV PATH=/home/mcpuser/.local/bin:$PATH

# Copy application code
COPY mcp_http_service/ ./mcp_http_service/

# Set permissions
RUN chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Set environment variables
ENV PYTHONPATH=/app
ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV DB_NAME=task_management
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres
ENV PORT=8000
ENV HOST=0.0.0.0

# Expose port for HTTP mode
EXPOSE 8000

# Set default command to HTTP mode
# Use --stdio flag to run experimental STDIO server if needed
CMD ["python", "-m", "mcp_http_service.main"]