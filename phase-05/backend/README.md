## Running the Application with Docker

This project provides a Docker-based setup for easy local development and deployment. The included `Dockerfile` and `docker-compose.yml` files handle all dependencies and service orchestration.

### Requirements
- **Docker** and **Docker Compose** installed on your system.
- The application uses **Python 3.12** (as specified in the Dockerfile).
- All dependencies are managed via `pyproject.toml` and installed using [uv](https://github.com/astral-sh/uv) for fast, reproducible builds.

### Environment Variables
The following environment variables are required for the application to start (see `docker-compose.yml`):

- `DATABASE_URL`: Database connection string (default: `postgresql://postgres:postgres@python-db:5432/postgres`)
- `JWT_ALGORITHM`: Algorithm used for JWT tokens (default: `HS256`)
- (Recommended) Place secrets such as `BETTER_AUTH_SECRET` in a `.env` file and uncomment the `env_file` line in `docker-compose.yml` for secure configuration.

### Build and Run Instructions

1. **Build and start all services:**

   ```bash
   docker compose up --build
   ```

   This will build the API backend and start both the API server and the Postgres database.

2. **Accessing the services:**
   - **API Server:** http://localhost:8000
     - The main FastAPI server is exposed on port **8000**.
   - **Postgres Database:** localhost:5432 (if you need to connect from your host)
     - The database is exposed on port **5432** (can be disabled in `docker-compose.yml` if not needed).

3. **Stopping the services:**

   ```bash
   docker compose down
   ```

### Special Configuration
- The Docker setup uses a multi-stage build for a minimal, secure runtime image.
- The application runs as a non-root user inside the container for improved security.
- Database data is not persisted by default. To persist Postgres data, uncomment the `volumes` section for `python-db` in `docker-compose.yml`.
- If you have a `.env` file with secrets, uncomment the `env_file` line in `docker-compose.yml` to load it automatically.

### Exposed Ports
- **8000**: FastAPI main API server (container: `python-api`)
- **5432**: Postgres database (container: `python-db`)

For more details on API endpoints and advanced features, see the sections above and the included `API_DOCS.md` file.
