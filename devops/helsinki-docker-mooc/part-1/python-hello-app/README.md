# Python Hello App

A simple Flask web application demonstrating Docker containerization. This app provides a REST API with basic endpoints for health checks and information display.

## Features

- Simple REST API built with Flask
- Health check endpoint for container monitoring
- JSON responses with timestamp and hostname information
- Optimized Docker image using Python slim base
- Non-root user for enhanced security
- Built-in health checks

## Endpoints

- `GET /` - Home endpoint with basic information
- `GET /health` - Health check endpoint
- `GET /info` - Application information and available endpoints

## Running with Docker

### Pull from Docker Hub

```bash
docker pull himanshubhardwaj23/python-hello-app
```

### Run the container

```bash
docker run -p 5000:5000 himanshubhardwaj23/python-hello-app
```

The application will be available at `http://localhost:5000`

### Test the application

```bash
# Home endpoint
curl http://localhost:5000/

# Health check
curl http://localhost:5000/health

# Application info
curl http://localhost:5000/info
```

## Building from Source

### Build the Docker image

```bash
docker build -t himanshubhardwaj23/python-hello-app .
```

### Run locally

```bash
docker run -p 5000:5000 himanshubhardwaj23/python-hello-app
```

## Running without Docker

### Prerequisites

- Python 3.11 or higher
- pip

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python app.py
```

## Docker Image Details

- Base Image: `python:3.11-slim`
- Exposed Port: 5000
- Working Directory: `/app`
- User: Non-root user (appuser)
- Health Check: Enabled (checks `/health` endpoint every 30s)

## Project Structure

```
python-hello-app/
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker image definition
├── .dockerignore      # Docker ignore patterns
└── README.md          # This file
```

## License

MIT License
