# NOTE : Using python-optimized base image to keep it consistent with the server image
FROM python:3.13-slim
ENV AWS_DEFAULT_REGION=us-east-1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# define working dir
WORKDIR /ui

COPY src /ui/src

COPY ./pyproject.toml /ui/.

COPY requirements.txt /ui/.
RUN pip install --no-cache-dir -r /ui/requirements.txt

# Expose the port
# EXPOSE 8000
# streamlit run src/ui.py
CMD ["streamlit", "run", "src/ui.py"]
