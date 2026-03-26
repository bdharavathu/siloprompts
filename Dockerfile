# Multi-stage build for smaller image size
FROM python:3.11-slim as builder

WORKDIR /build

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Final stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000 \
    FLASK_ENV=production

# Create non-root user for security
RUN useradd -m -u 1000 siloprompts && \
    mkdir -p /app /app/data /app/prompts && \
    chown -R siloprompts:siloprompts /app

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/siloprompts/.local

# Copy application files
COPY --chown=siloprompts:siloprompts app.py .
COPY --chown=siloprompts:siloprompts html_templates ./html_templates
COPY --chown=siloprompts:siloprompts static ./static

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
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
