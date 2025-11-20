#!/bin/bash

# Docker Hub Push Script for Piper TTS
# Usage: ./push-to-docker-hub.sh <docker_username> [version]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}Error: Docker Hub username required${NC}"
    echo "Usage: $0 <docker_username> [version]"
    echo "Example: $0 nandakiran 1.0.0"
    exit 1
fi

DOCKER_USERNAME=$1
VERSION=${2:-latest}
IMAGE_NAME="piper-tts"
FULL_IMAGE_NAME="$DOCKER_USERNAME/$IMAGE_NAME"

echo -e "${YELLOW}=== Docker Hub Push Script ===${NC}"
echo "Username: $DOCKER_USERNAME"
echo "Image: $FULL_IMAGE_NAME"
echo "Version: $VERSION"
echo ""

# Step 1: Check if logged in
echo -e "${YELLOW}[1/5] Checking Docker login...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker daemon is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker daemon is running${NC}"

# Step 2: Build the image
echo -e "${YELLOW}[2/5] Building Docker image...${NC}"
docker build -t $IMAGE_NAME:latest .
echo -e "${GREEN}✓ Image built successfully${NC}"

# Step 3: Tag the image
echo -e "${YELLOW}[3/5] Tagging image for Docker Hub...${NC}"
docker tag $IMAGE_NAME:latest $FULL_IMAGE_NAME:latest
if [ "$VERSION" != "latest" ]; then
    docker tag $IMAGE_NAME:latest $FULL_IMAGE_NAME:$VERSION
    echo -e "${GREEN}✓ Tagged as: $FULL_IMAGE_NAME:latest and $FULL_IMAGE_NAME:$VERSION${NC}"
else
    echo -e "${GREEN}✓ Tagged as: $FULL_IMAGE_NAME:latest${NC}"
fi

# Step 4: Login to Docker Hub
echo -e "${YELLOW}[4/5] Logging in to Docker Hub...${NC}"
docker login
echo -e "${GREEN}✓ Logged in successfully${NC}"

# Step 5: Push to Docker Hub
echo -e "${YELLOW}[5/5] Pushing to Docker Hub...${NC}"
docker push $FULL_IMAGE_NAME:latest
if [ "$VERSION" != "latest" ]; then
    docker push $FULL_IMAGE_NAME:$VERSION
    echo -e "${GREEN}✓ Pushed: $FULL_IMAGE_NAME:latest and $FULL_IMAGE_NAME:$VERSION${NC}"
else
    echo -e "${GREEN}✓ Pushed: $FULL_IMAGE_NAME:latest${NC}"
fi

echo ""
echo -e "${GREEN}=== Push Complete ===${NC}"
echo "Your image is now available at:"
echo "  https://hub.docker.com/r/$FULL_IMAGE_NAME"
echo ""
echo "To pull and run:"
echo "  docker pull $FULL_IMAGE_NAME:latest"
echo "  docker run -p 8000:8000 -v \$(pwd)/models:/app/models $FULL_IMAGE_NAME:latest"
