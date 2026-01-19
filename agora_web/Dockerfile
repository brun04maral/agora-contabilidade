FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY agora_web/requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn psycopg2-binary

# Copy Django project
COPY agora_web/ .

# Copy documentation from project root
COPY CHANGELOG.md /app/CHANGELOG.md
COPY README.md /app/README.md
COPY README-DEV.md /app/README-DEV.md
COPY docs/ /app/docs/
COPY .claude/claude.md /app/claude.md

# Create static and media directories
RUN mkdir -p /app/static /app/media

# Collect static files (will be run during deployment)
# RUN python manage.py collectstatic --noinput

# Create non-root user
RUN useradd -m -u 1000 agora && \
    chown -R agora:agora /app

USER agora

# Expose port
EXPOSE 8000

# Health check (usando urllib nativa do Python)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/admin/login/', timeout=5)"

# Run gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
