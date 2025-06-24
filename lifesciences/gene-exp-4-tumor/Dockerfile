#FROM alpine:latest
# RUN apk add --no-cache build-base gcc musl-dev

# NOTE : Using python-optimized base image (debian os) given the challenges of getting matplotlib installed on an alpine version.
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install matplotlib
RUN pip install matplotlib

# FROM python:3.13.0-alpine
WORKDIR /src

#COPY --exclude=data/*.csv --exclude=models/*.pkl . .
COPY src /app/src/
COPY models/xgb_GridSearch_Pipeline.pkl /app/models/
COPY ./pyproject.toml /app/.
# COPY ui.py /app/.

COPY requirements.txt .
RUN pip install -r requirements.txt

# Expose the port
EXPOSE 5000

CMD ["python", "main.py"]