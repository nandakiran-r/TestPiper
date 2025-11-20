# Pushing Piper TTS to Docker Hub

This guide explains how to push your Docker image to Docker Hub.

## Prerequisites

1. **Docker Hub Account**: Create one at https://hub.docker.com/ (free)
2. **Docker installed**: Already verified on your system
3. **Docker daemon running**: Ensure Docker is running

## Step-by-Step Instructions

### 1. Login to Docker Hub

First, authenticate with Docker Hub:

```bash
docker login
```

You'll be prompted to enter:
- **Username**: Your Docker Hub username
- **Password**: Your Docker Hub password (or personal access token)

**Note**: For security, use a Personal Access Token instead of your password:
1. Go to https://hub.docker.com/settings/security
2. Create a new access token
3. Use the token as your password when prompted

### 2. Build the Image (if not already built)

```bash
docker build -t piper-tts:latest .
```

### 3. Tag the Image for Docker Hub

Replace `nandakiranr` with your Docker Hub username:

```bash
docker tag piper-tts:latest nandakiranr/piper-tts:latest
```

**Example**:
```bash
docker tag piper-tts:latest nandakiran/piper-tts:latest
```

You can also add a version tag:

```bash
docker tag piper-tts:latest nandakiranr/piper-tts:1.0.0
```

### 4. Push to Docker Hub

Push the tagged image:

```bash
docker push nandakiranr/piper-tts:latest
```

**Example**:
```bash
docker push nandakiran/piper-tts:latest
```

To push multiple tags:

```bash
docker push nandakiranr/piper-tts:1.0.0
```

### 5. Verify on Docker Hub

1. Go to https://hub.docker.com/
2. Login to your account
3. Navigate to **Repositories**
4. You should see `piper-tts` listed

## Complete Workflow

Here's the complete set of commands:

```bash
# 1. Login
docker login

# 2. Build the image
docker build -t piper-tts:latest .

# 3. Tag for Docker Hub (replace nandakiranr)
docker tag piper-tts:latest nandakiranr/piper-tts:latest
docker tag piper-tts:latest nandakiranr/piper-tts:1.0.0

# 4. Push to Docker Hub
docker push nandakiranr/piper-tts:latest
docker push nandakiranr/piper-tts:1.0.0
```

## Using the Image from Docker Hub

Once pushed, anyone can pull and run your image:

```bash
docker pull nandakiranr/piper-tts:latest
docker run -p 8000:8000 -v $(pwd)/models:/app/models nandakiranr/piper-tts:latest
```

Or with docker-compose:

```yaml
version: '3.8'
services:
  piper-tts:
    image: nandakiranr/piper-tts:latest
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
```

## Useful Docker Commands

### View Local Images

```bash
docker images | grep piper-tts
```

### View Image Details

```bash
docker inspect nandakiranr/piper-tts:latest
```

### Check Image Size

```bash
docker images nandakiranr/piper-tts
```

### Remove Local Image

```bash
docker rmi nandakiranr/piper-tts:latest
```

### View Push History

```bash
docker image history nandakiranr/piper-tts:latest
```

## Troubleshooting

### "unauthorized: authentication required"

**Solution**: Run `docker login` again and verify credentials

### "denied: requested access to the resource is denied"

**Solution**: Ensure the repository name matches your username:
```bash
docker tag piper-tts:latest nandakiranr/piper-tts:latest
```

### "image not found"

**Solution**: Build the image first:
```bash
docker build -t piper-tts:latest .
```

### Large Image Size

**Solution**: The image may be large due to system dependencies. To reduce size:
- Use multi-stage builds
- Remove unnecessary packages
- Use `.dockerignore` to exclude files

### Push is Slow

**Solution**: 
- Check your internet connection
- Use a smaller tag or version number
- Consider using Docker Hub's build feature for automated builds

## Docker Hub Repository Settings

After pushing, you can configure your repository:

1. Go to https://hub.docker.com/repositories
2. Click on your repository
3. Configure:
   - **Description**: Add a description
   - **README**: Upload a README.md
   - **Visibility**: Make it public or private
   - **Collaborators**: Add team members

## Automated Builds (Optional)

For automatic builds when you push to GitHub:

1. Connect your GitHub account to Docker Hub
2. Go to Repository Settings → Builds
3. Configure build rules
4. Docker Hub will automatically build when you push code

## Security Best Practices

- ✅ Use Personal Access Tokens instead of passwords
- ✅ Keep your credentials secure
- ✅ Don't commit `.docker/config.json` to version control
- ✅ Use private repositories for sensitive images
- ✅ Regularly update base images (python:3.10-slim)
- ✅ Scan images for vulnerabilities

## Additional Resources

- [Docker Hub Documentation](https://docs.docker.com/docker-hub/)
- [Docker Push Documentation](https://docs.docker.com/engine/reference/commandline/push/)
- [Docker Login Documentation](https://docs.docker.com/engine/reference/commandline/login/)
