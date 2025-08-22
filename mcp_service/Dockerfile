# Multi-stage build for MCP Service
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
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
COPY mcp_service/ ./mcp_service/
RUN chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "-m", "mcp_service.main"]