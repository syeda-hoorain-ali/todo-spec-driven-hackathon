# Docker Containerization Commands for Todo Chatbot Application

## Docker Installation Verification Commands

1. **Check Docker version:**
   ```bash
   docker --version
   ```

2. **Check Docker daemon status:**
   ```bash
   docker info
   ```

3. **Test Docker with hello-world:**
   ```bash
   docker run hello-world
   ```

## Docker AI Agent (Gordon) Setup Commands

1. **Enable Docker AI Agent in Docker Desktop:**
   - Open Docker Desktop
   - Go to Settings > Features in development
   - Enable "Docker AI Agent (Gordon)"
   - Restart Docker Desktop if prompted

2. **Verify Docker AI Agent is enabled:**
   ```bash
   docker ai --version
   ```

3. **Configure Docker AI Agent settings:**
   - In Docker Desktop, go to Settings > AI settings
   - Configure API key for chosen LLM provider (OpenAI, Anthropic, etc.)
   - Set up preferences for Dockerfile generation

## Docker AI Agent (Gordon) Containerization Commands

### For frontend specifically:
1. **Navigate to frontend directory:**
   ```bash
   cd phase-04/frontend
   ```

2. **Generate Dockerfile for frontend using Docker AI Agent:**
   ```bash
   docker ai create Dockerfile --description "Next.js frontend for Todo Chatbot application"
   ```

3. **Optimize the generated Dockerfile using Docker AI Agent:**
   ```bash
   docker ai optimize Dockerfile --target-size 200MB
   ```

4. **Build frontend Docker image:**
   ```bash
   docker build -t todo-frontend:latest .
   ```

5. **Run frontend container:**
   ```bash
   docker run -p 3000:3000 todo-frontend:latest
   ```

### For backend specifically:
1. **Navigate to backend directory:**
   ```bash
   cd phase-04/backend
   ```

2. **Generate Dockerfile for backend using Docker AI Agent:**
   ```bash
   docker ai create Dockerfile --description "FastAPI backend for Todo Chatbot application"
   ```

3. **Optimize the generated Dockerfile using Docker AI Agent:**
   ```bash
   docker ai optimize Dockerfile --target-size 150MB
   ```

4. **Build backend Docker image:**
   ```bash
   docker build -t todo-backend:latest .
   ```

5. **Run backend container:**
   ```bash
   docker run -p 8000:8000 todo-backend:latest
   ```

### For MCP server specifically:
1. **Navigate to MCP server directory:**
   ```bash
   cd phase-04/mcp_server
   ```

2. **Generate Dockerfile for MCP server using Docker AI Agent:**
   ```bash
   docker ai create Dockerfile --description "Python MCP server for Todo Chatbot application"
   ```

3. **Optimize the generated Dockerfile using Docker AI Agent:**
   ```bash
   docker ai optimize Dockerfile --security-focused
   ```

4. **Build MCP server Docker image:**
   ```bash
   docker build -t todo-mcp-server:latest .
   ```

5. **Run MCP server container:**
   ```bash
   docker run -p 8080:8080 todo-mcp-server:latest
   ```

## Python Environment Setup Commands

### For both MCP server and backend directories:
1. **Create virtual environment:**
   ```bash
   uv venv
   ```

2. **Activate virtual environment:**
   ```bash
   # On Linux/macOS:
   source .venv/bin/activate
   # On Windows:
   source .venv/Scripts/activate
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```

### For backend specifically:
1. **Navigate to backend directory:**
   ```bash
   cd phase-04/backend
   ```

2. **Create virtual environment & activate it:**
   ```bash
   uv venv
   source .venv/Scripts/activate
   ```

3. **Install backend dependencies from pyproject.toml:**
   ```bash
   uv sync
   ```

### For MCP server specifically:
1. **Navigate to MCP server directory:**
   ```bash
   cd phase-04/mcp_server
   ```

2. **Create virtual environment & activate it:**
   ```bash
   uv venv
   source .venv/Scripts/activate
   ```

3. **Install MCP server dependencies from pyproject.toml:**
   ```bash
   uv sync
   ```

## Frontend Dependencies Setup Commands

1. **Navigate to frontend directory:**
   ```bash
   cd phase-04/frontend
   ```

2. **Install frontend dependencies from package.json:**
   ```bash
   npm install
   ```

3. **Verify installation and check for any issues:**
   ```bash
   npm audit
   ```

4. **Build the frontend application (optional, for verification):**
   ```bash
   npm run build
   ```

## Docker Compose Configuration Commands

1. **Create docker-compose.yml for local development:**
   ```yaml
   version: '3.8'

   services:
     frontend:
       build:
         context: ./frontend
         dockerfile: Dockerfile
       ports:
         - "3000:3000"
       environment:
         - NEXT_PUBLIC_API_URL=http://localhost:8000
       depends_on:
         - backend
       restart: unless-stopped

     backend:
       build:
         context: ./backend
         dockerfile: Dockerfile
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql://user:password@db:5432/todoapp
         - AUTH_SECRET=your-auth-secret
       depends_on:
         - db
       restart: unless-stopped

     mcp_server:
       build:
         context: ./mcp_server
         dockerfile: Dockerfile
       ports:
         - "8080:8080"
       restart: unless-stopped

     db:
       image: postgres:15-alpine
       environment:
         POSTGRES_DB: todoapp
         POSTGRES_USER: user
         POSTGRES_PASSWORD: password
       ports:
         - "5432:5432"
       volumes:
         - postgres_data:/var/lib/postgresql/data
       restart: unless-stopped

   volumes:
     postgres_data:
   ```

2. **Build and start all services with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Start services in detached mode:**
   ```bash
   docker-compose up -d
   ```

4. **Stop all services:**
   ```bash
   docker-compose down
   ```

5. **View service logs:**
   ```bash
   docker-compose logs -f
   ```

## Basic Docker Containerization Commands

1. **Build Docker image:**
   ```bash
   docker build -t <image-name>:<tag> .
   ```

2. **Run Docker container:**
   ```bash
   docker run -p <host-port>:<container-port> <image-name>:<tag>
   ```
