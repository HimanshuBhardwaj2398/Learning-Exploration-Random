#!/bin/bash

GITHUB_REPO=$1
DOCKERHUB_REPO=$2
# DOCKER_USER=$3
# DOCKER_PWD=$4

if [ $# -ne 2 ]; then
   echo "Error Incorrect number of arguments"
   echo "Usage: $0 <github_repo> <dockerhub_repo>"
   exit 1 
fi 


# Validate credentials
if [ -z "$DOCKER_USER" ] || [ -z "$DOCKER_PWD" ]; then
    echo "Error: DOCKER_USER and DOCKER_PWD environment variables must be set"
    exit 1
fi


REPO_NAME="${GITHUB_REPO##*/}"


# Create a temp directory name
CLONE_DIR="temp_$REPO_NAME"


# Clone the repository
git clone "https://github.com/$GITHUB_REPO.git" "$CLONE_DIR"


if [ $? -ne 0 ]; then
    echo "Error: Failed to clone repository!"
    exit 1
fi


cd "$CLONE_DIR"

# Use docker.exe explicitly on Windows to avoid shell issues
if command -v docker.exe &> /dev/null; then
    DOCKER_CMD="docker.exe"
else
    DOCKER_CMD="docker"
fi

$DOCKER_CMD build -t "$DOCKERHUB_REPO" .


if [ $? -ne 0 ]; then
    echo "Error: Docker build failed!"
    exit 1
fi

## Adding docker hub login
echo "$DOCKER_PWD" | $DOCKER_CMD login -u "$DOCKER_USER" --password-stdin

if [ $? -ne 0 ]; then
    echo "Error: Docker Hub login failed! Check your credentials."
    echo "Tip: Use a Personal Access Token instead of your password"
    exit 1
fi

echo "Successfully logged in to Docker Hub"

$DOCKER_CMD push "$DOCKERHUB_REPO"


if [ $? -ne 0 ]; then
    echo "Error: Docker push failed!"
    exit 1
fi
