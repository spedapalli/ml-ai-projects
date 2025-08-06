#FROM alpine:latest
# Using python-optimized base image (debian bookworm aka v12 os)
# NOTE: as of Jul 21, all slim bookworm versions hv critical CVEs. For this POC sticking to 3.11
FROM python:3.11-slim-bookworm AS builder

# Use when running docker cmd from root dir - Need to standardize with below
# ARG APP_SRC_DIR="app"
# Use when running using Ansible scripts or when building locally
ARG APP_SRC_DIR="."

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /build
COPY $APP_SRC_DIR/requirements-fastapi.txt .
# COPY requirements-fastapi.txt .
# Dont see need for below file given we are using requirements file
# COPY ./../pyproject.toml /app/.

# install all dependencies in user's local dir
RUN pip install --user --no-cache-dir -r ./requirements-fastapi.txt


# --- runtime ----
FROM python:3.11-slim-bookworm

# Create non-root user for security
RUN adduser --disabled-password appuser 

# Copy only the installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local


# Set the PATH to include user packages
ENV PATH=/home/appuser/.local/bin:$PATH

# RUN nltk.path.append("/root/nltk_data")
RUN pip install --upgrade nltk
# RUN python -m nltk.downloader punkt
RUN python -c "import nltk; \
            nltk.download('punkt_tab', download_dir='/home/appuser/nltk_data'); \
            nltk.download('wordnet', download_dir='/home/appuser/nltk_data'); \
            nltk.download('averaged_perceptron_tagger', download_dir='/home/appuser/nltk_data'); \
            nltk.download('averaged_perceptron_tagger_eng', download_dir='/home/appuser/nltk_data'); \
            nltk.download('stopwords', download_dir='/home/appuser/nltk_data');"

# working dir on docker
WORKDIR /app

# Copy application code
# COPY --chown=appuser:appuser app/ .
COPY --chown=appuser:appuser $APP_SRC_DIR .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    # CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1
    CMD curl -f http://localhost:8000/health || exit 1


# Expose the port
EXPOSE 8000
# --app-dir ./app api.health_conversation_model_api:app
CMD ["uvicorn", "api.health_conversation_model_api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
