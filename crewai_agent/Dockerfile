# Multi-stage build for CrewAI Agent Service
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY crewai_agent/requirements.txt .
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
RUN groupadd -r crewaiuser && useradd -r -g crewaiuser crewaiuser

# Copy Python packages from builder stage to crewaiuser home
COPY --from=builder /root/.local /home/crewaiuser/.local
RUN chown -R crewaiuser:crewaiuser /home/crewaiuser/.local

# Make sure scripts in .local are usable for crewaiuser
ENV PATH=/home/crewaiuser/.local/bin:$PATH

# Copy application code
COPY crewai_agent/ ./crewai_agent/

# Set permissions
RUN chown -R crewaiuser:crewaiuser /app

# Switch to non-root user
USER crewaiuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8001
ENV HOST=0.0.0.0

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["python", "-m", "crewai_agent.main"]