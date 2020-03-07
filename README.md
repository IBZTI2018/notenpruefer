# Notenpruefer - Gradebot
Periodically checks grade list on the IBZ website and sends a notification when something has changed.

## Docker setup
```bash
# Build container from local Dockerfile
docker build -t notenpruefer .

# Run docker container with shared data directory
# For running on Windows, the full local Path must be
# provided to mount the volume. E,g, C:\...\shared
docker run -v ./shared:/shared notenpruefer
```

## Configuration
For configuration, create the file `shared/credentials.txt` and fill it with `username::password`.
