# NOTE : Using python-optimized base image to keep it consistent with the server image
FROM python:3.11-slim-bookworm AS builder
ENV AWS_DEFAULT_REGION=us-east-1
ENV PYTHONUNBUFFERED=1
ARG UI_SRC_DIR="ui"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /build
COPY $UI_SRC_DIR/requirements-ui.txt .

# install all dependencies in user's local dir
RUN pip install --user --no-cache-dir -r ./requirements-ui.txt


# --- runtime ----
FROM python:3.11-slim-bookworm

# Create non-root user for security
RUN adduser --disabled-password uiuser 

# Copy only the installed packages from builder
COPY --from=builder /root/.local /home/uiuser/.local

# Set the PATH to include user packages
ENV PATH=/home/uiuser/.local/bin:$PATH

# working dir on docker
WORKDIR /ui

# Copy code
COPY --chown=uiuser:uiuser . .

# Switch to non-root user
USER uiuser

# Expose the port
EXPOSE 8501

# streamlit run src/ui.py
CMD ["streamlit", "run", "ui/src/ui.py"]
