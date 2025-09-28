# fastapi-video-hosting

## Running with Docker

This project uses Python 3.12 and manages dependencies with `uv` in a virtual environment. The application is served via FastAPI and runs on port 80.

### Build and Run

Use Docker Compose to build and start the service:

```bash
docker compose up --build
```

### Service Details
- **Service name:** `python-uv`
- **Exposed port:** `80` (FastAPI default)
- **Container name:** `python-uv`
- **Network:** `backend` (bridge driver)

### Configuration
- No environment variables are required by default. If you need to set any, uncomment the `env_file` line in `docker-compose.yml` and provide a `.env` file.
- All dependencies are managed via `pyproject.toml` and `uv.lock`.

### Notes
- The Dockerfile uses a multi-stage build for efficient dependency management and a minimal final image.
- The application code is located in the `src/` directory and is started with Uvicorn.
