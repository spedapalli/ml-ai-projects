#FROM alpine:latest
# RUN apk add --no-cache build-base gcc musl-dev

# NOTE : Using python-optimized base image (debian os) given the challenges of getting matplotlib installed on an alpine version.
FROM python:3.13-slim
ENV AWS_DEFAULT_REGION=us-east-1


# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install matplotlib
RUN pip install matplotlib

# FROM python:3.13.0-alpine
WORKDIR /app/src

#COPY --exclude=data/*.csv --exclude=models/*.pkl . .
COPY src /app/src/
COPY resources /app/.
COPY ./pyproject.toml /app/.
# COPY .env /app/.

COPY requirements.txt /app/.
RUN pip install -r /app/requirements.txt

# Expose the port
EXPOSE 5000

CMD ["python", "main.py"]