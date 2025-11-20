# Docker Setup for Piper TTS

This guide explains how to run the Piper TTS application using Docker.

## Prerequisites

- Docker installed on your system ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Install Docker Compose](https://docs.docker.com/compose/install/))
- Model files downloaded and placed in the `models/` directory

## Quick Start

### 1. Download Model Files

Before building the Docker image, ensure you have the Malayalam voice model files:

1. Visit: https://huggingface.co/rhasspy/piper-voices/tree/main/ml/ml_IN/arjun/medium
2. Download:
   - `ml_IN-arjun-medium.onnx`
   - `ml_IN-arjun-medium.onnx.json`
3. Place them in the `models/` directory

### 2. Build and Run with Docker Compose

The easiest way to run the application:

```bash
docker-compose up --build
```

This command will:
- Build the Docker image
- Start the container
- Expose the API on `http://localhost:8000`

### 3. Access the API

Once running, you can access:
- **API Root**: http://localhost:8000/
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example API Call

```bash
curl "http://localhost:8000/tts?text=നിങ്ങൾ%20എങ്ങനെയുണ്ട്"
```

## Docker Commands

### Build the Image

```bash
docker build -t piper-tts:latest .
```

### Run Container Directly

```bash
docker run -p 8000:8000 -v $(pwd)/models:/app/models piper-tts:latest
```

### Stop Running Container

```bash
docker-compose down
```

### View Logs

```bash
docker-compose logs -f piper-tts
```

### Remove Image and Containers

```bash
docker-compose down --rmi all
```

## Project Structure

```
project/
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Docker Compose configuration
├── .dockerignore                 # Files to exclude from Docker build
├── main.py                       # FastAPI application
├── requirements.txt              # Python dependencies
├── models/                       # Directory for model files
│   ├── ml_IN-arjun-medium.onnx
│   └── ml_IN-arjun-medium.onnx.json
├── README.md                     # Original setup instructions
└── DOCKER_SETUP.md              # This file
```

## Environment Variables

The Docker setup uses the following environment variable:

- `PYTHONUNBUFFERED=1`: Ensures Python output is sent straight to logs without buffering

## Health Check

The container includes a health check that verifies the API is running every 30 seconds. You can check the container health status with:

```bash
docker ps
```

Look for the `(healthy)` status indicator.

## Troubleshooting

### Model Files Not Found

**Error**: `⚠️ Model file not found at models/ml_IN-arjun-medium.onnx`

**Solution**: Ensure model files are downloaded and placed in the `models/` directory before building the image.

### Port Already in Use

**Error**: `bind: address already in use`

**Solution**: Change the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

### Container Exits Immediately

**Solution**: Check logs with:
```bash
docker-compose logs piper-tts
```

### Permission Issues

**Solution**: Ensure the `models/` directory has proper permissions:
```bash
chmod 755 models/
```

## Performance Notes

- First startup may take longer as the model is loaded into memory
- The container requires sufficient RAM (at least 2GB recommended)
- Audio processing is CPU-intensive; more CPU cores will improve performance

## Additional Resources

- [Piper TTS Documentation](https://github.com/rhasspy/piper)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
