FROM python:3.13-slim

# Install system dependencies, TeX Live for pdflatex, and utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    git \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency configuration
COPY pyproject.toml README.md ./

# Install python dependencies and project
COPY src/ ./src/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Install Playwright Chromium and required OS shared libraries
RUN playwright install --with-deps chromium

# Copy application assets, templates, migrations, and seed configs
COPY templates/ ./templates/
COPY data/config/ ./data/config/
COPY data/config/ /app/seed_config/
COPY migrations/ ./migrations/

# Create runtime directories for data volume
RUN mkdir -p /app/data/output /app/data/notifications

# Configure environment defaults
ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/app/data
ENV TZ="Asia/Kolkata"

# Continuous 4-slot IST scheduler daemon entrypoint
CMD ["resume-agent", "daemon"]
