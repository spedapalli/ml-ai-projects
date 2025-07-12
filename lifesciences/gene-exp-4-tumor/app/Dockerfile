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
WORKDIR /app

#COPY --exclude=data/*.csv --exclude=models/*.pkl . .
COPY src /app/src

COPY resources /app/resources/
COPY ./pyproject.toml /app/.
# COPY .env /app/.

COPY requirements.txt /app/.
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose the port
EXPOSE 8000

CMD ["uvicorn", "--app-dir", "src", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# CMD ["python", "src/main.py"]