# Multi-stage build for smaller image size
FROM python:3.14-slim AS builder

WORKDIR /build

# Install package and production dependencies
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir --user . && \
    pip install --no-cache-dir --user gunicorn==25.3.0


# Final stage
FROM python:3.14-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000 \
    FLASK_ENV=production \
    PROMPTS_DIR=/app/prompts \
    DATA_DIR=/app/data

# Create non-root user for security
RUN useradd -m -u 1000 siloprompts && \
    mkdir -p /app /app/data /app/prompts && \
    chown -R siloprompts:siloprompts /app

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/siloprompts/.local

# Copy default prompts
COPY --chown=siloprompts:siloprompts prompts ./prompts

# Switch to non-root user
USER siloprompts

# Add local bin to PATH
ENV PATH=/home/siloprompts/.local/bin:$PATH

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "siloprompts.web:app"]
