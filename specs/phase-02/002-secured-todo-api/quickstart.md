# Quickstart Guide: Secured Todo API

## Overview
This guide provides instructions for setting up and running the secured todo API backend that integrates with Better Auth for JWT token verification.

## Prerequisites
- Python 3.12 or higher
- uv (Python package manager)
- Access to Neon Postgres database
- Better Auth secret key (BETTER_AUTH_SECRET)

## Setup Instructions

### 1. Initialize project with uv
```bash
cd phase-02
uv init backend
```

### 2. Install Dependencies with uv
```bash
uv add fastapi[standard] uvicorn[standard] sqlmodel python-jose[cryptography] psycopg2-binary python-dotenv pytest
```

### 2. Create Backend Directory Structure
```bash
mkdir -p backend/{src,tests}
mkdir -p backend/src/{models,database,auth,api,schemas,config}
mkdir -p backend/src/api/routes
mkdir -p backend/tests/{unit,integration,contract}
```

### 4. Environment Configuration
Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://username:password@host:port/database
BETTER_AUTH_SECRET=your-better-auth-secret-key
JWT_ALGORITHM=HS256
ENVIRONMENT=development
```

### 5. Run the Application
```bash
cd backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Usage

### Authentication
All API endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Example Requests
1. Get user's tasks:
   ```bash
   curl -H "Authorization: Bearer <token>" http://localhost:8000/api/123/tasks
   ```

2. Create a new task:
   ```bash
   curl -X POST -H "Authorization: Bearer <token>" \
        -H "Content-Type: application/json" \
        -d '{"title":"New task","description":"Task description"}' \
        http://localhost:8000/api/123/tasks
   ```

## Testing
Run the test suite:
```bash
cd backend
uv run pytest
```

## Configuration Notes
- The API verifies JWT tokens using the same secret as Better Auth
- User ID in the URL must match the user ID in the JWT token
- The system ensures data isolation by filtering results by user_id
