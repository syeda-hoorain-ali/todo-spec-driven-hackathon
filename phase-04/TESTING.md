# Testing Containerized Applications

This document explains how to build and test the containerized applications to verify they maintain full functionality when running in containers as compared to local development.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose installed
- Access to the database (PostgreSQL)

## Building and Running the Applications

### Option 1: Using Docker Compose (Recommended for local development)

```bash
# Navigate to the phase-04 directory
cd phase-04

# Build and run all services
docker-compose -f compose.yaml up --build

# Or run in detached mode
docker-compose -f compose.yaml up --build -d
```

### Option 2: Individual Container Testing

```bash
# Build the frontend container
cd phase-04\frontend
docker build -t taskflow-frontend:latest .

# Build the backend container
cd phase-04\backend
docker build -t taskflow-backend:latest .

# Build the MCP server container
cd phase-04\mcp_server
docker build -t taskflow-mcp-server:latest .

# Run the containers with Docker Compose
cd phase-04
docker-compose -f compose.yaml up
```

## Testing Functionality

### Frontend (Next.js)
1. Open browser to http://localhost:3000
2. Verify the application loads correctly
3. Check that authentication works (sign-in/sign-up pages)
4. Verify API calls to the backend are working
5. Check that environment variables are properly loaded

### Backend (FastAPI)
1. Open browser to http://localhost:8000/docs
2. Verify the API documentation loads
3. Test the health endpoint at http://localhost:8000/health
4. Verify database connections work
5. Test API endpoints to ensure they function as expected

### MCP Server
1. Check that the MCP server is accessible at http://localhost:8080
2. Verify it can connect to the database
3. Test any MCP-specific endpoints

## Environment Configuration

The application uses .env files for configuration:

- Each service has an `.env.example` file showing required variables
- Copy the example files to `.env` and fill in your actual values
- The compose file will automatically load these environment variables

## Verification Checklist

- [ ] All containers start without errors
- [ ] Frontend application is accessible on port 3000
- [ ] Backend API is accessible on port 8000
- [ ] MCP server is accessible on port 8080
- [ ] Database connections work properly
- [ ] Health checks pass for all services
- [ ] Inter-service communication works (frontend to backend)
- [ ] Environment variables are properly configured
- [ ] Authentication and authorization work correctly
- [ ] Application functionality matches local development behavior

## Troubleshooting

1. **Container fails to start**: Check logs with `docker logs <container-name>`
2. **Database connection errors**: Verify the database service is running and accessible
3. **Environment variables not loading**: Check that .env files are properly configured
4. **Port conflicts**: Ensure ports 3000, 8000, 8080, and 5432 are available

## Image Sizes

After building, verify image sizes meet the requirements:
- Frontend: Should be under 200MB
- Backend: Should be under 150MB
- MCP Server: Should be optimized as well

Check sizes with: `docker images | grep taskflow-`
