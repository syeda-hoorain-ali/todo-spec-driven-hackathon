# Quickstart Guide: Authentication System

## Project Setup

### Backend Setup (FastAPI)
1. Initialize the project:
```bash
uv init backend
```

2. Install dependencies:
```bash
uv add fastapi[standard] uvicorn[standard] sqlmodel pydantic python-multipart bcrypt psycopg2-binary python-jose[cryptography] python-dotenv
```

3. Set up the database connection with Neon Postgres using SQLModel

### Frontend Setup (Next.js 16+)
1. Create Next.js app with App Router:
```bash
npx create-next-app@latest frontend --yes --typescript --tailwind --app --src-dir --eslint
```

2. Navigate to the frontend directory and install dependencies:
```bash
cd frontend
npm i better-auth @better-auth/node
```

3. Install additional dependencies for authentication:
```bash
npx shadcn@latest add form button card input label textarea
npm install @tanstack/react-query
```

## Configuration

### Backend Configuration
1. Set up environment variables in `.env`:
```
DATABASE_URL=your_neon_postgres_connection_string
SECRET_KEY=your_secret_key_for_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BETTER_AUTH_SECRET=your_better_auth_secret
```

2. Configure the database models using SQLModel:
- User model with email, hashed password, timestamps
- Session model for JWT token management
- PasswordResetToken model for password recovery

3. Set up authentication service with:
- User registration with email validation
- Secure password hashing using bcrypt
- JWT token generation with refresh token rotation
- Rate limiting implementation

### Frontend Configuration
1. Configure Better Auth in `src/lib/better-auth/`:
- Create client and server configuration files
- Set up JWT integration to work with FastAPI backend

2. Create authentication components in `src/components/auth/`:
- Sign In form with validation
- Sign Up form with password policy enforcement
- Sign Out functionality
- Forgot Password form with email verification

3. Set up protected routes in `src/components/protected/`:
- Route protection middleware
- Redirect to login when not authenticated

## Running the Application

### Backend
```bash
uv run uvicorn src.main:app --port 8000 --reload
```

### Frontend
```bash
npm run dev
```

## API Endpoints

### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password` - Password reset confirmation

### User Endpoints
- `GET /users/me` - Get current user info
- `PUT /users/me` - Update current user
- `DELETE /users/me` - Delete current user account

## Security Features Implemented

1. **Password Security**:
   - bcrypt hashing with salt
   - Moderate password policy enforcement
   - Password reuse prevention

2. **Session Management**:
   - JWT tokens with refresh token rotation
   - Secure token storage
   - Automatic token refresh

3. **Rate Limiting**:
   - Database-based rate limiting
   - Account lockout after 5 failed attempts
   - 30-minute lockout period

4. **User Isolation**:
   - Each user only sees their own data
   - Proper authorization checks on all endpoints
   - Secure API access with JWT verification

## Testing

### Backend Tests
```bash
pytest tests/
```

### Frontend Tests
No tests

## Deployment

1. Set up Neon Postgres production database
2. Configure environment variables for production
3. Build frontend: `npm run build`
4. Deploy backend with FastAPI server
5. Configure domain and SSL certificates
