# Todo App with Authentication

This is a [Next.js](https://nextjs.org) project with a complete authentication system implemented using [Better Auth](https://www.better-auth.com). The application supports user registration, sign in, sign out, and password recovery functionality.

## Features

- User registration with email and password
- Secure sign in and sign out
- Password reset via email
- Protected routes and user profiles
- Session management with JWT tokens
- Comprehensive security measures (rate limiting, password policies, etc.)

## Getting Started

### Prerequisites

- Node.js 18+
- npm, yarn, pnpm, or bun

### Environment Setup

First, create a `.env.local` file in the root of the `frontend` directory with the following variables:

```env
NEXT_PUBLIC_BASE_URL="http://localhost:3000"

# Better Auth Configuration
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-super-secret-jwt-token-here-make-sure-it-is-at-least-32-characters-long

# Neon Database Configuration
DATABASE_URL=your-neon-database-connection-string

# Email Configuration (for password reset)
SMTP_HOST=your-smtp-host
SMTP_PORT=587
SMTP_USER=your-smtp-username
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=your-app-name <noreply@yourdomain.com>
```

To generate a secure `BETTER_AUTH_SECRET`, you can use the following command:
```bash
openssl rand -base64 32
```

### Installation

1. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
# or
bun install
```

2. Run the development server:
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Authentication System

The authentication system is built with Better Auth and includes:

- **Registration**: Users can create accounts with name, email, and password
- **Sign In**: Secure login with email and password
- **Sign Out**: Secure logout functionality
- **Password Reset**: Password recovery via email
- **Protected Routes**: Access control for authenticated users only
- **Profile Management**: Update user profile information

### API Endpoints

- `POST /api/auth/sign-up` - Create a new user account
- `POST /api/auth/sign-in` - Authenticate user and create session
- `POST /api/auth/sign-out` - End user session
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset user password

## Project Structure

```
frontend/
├── better-auth_migrations/     # Database migrations for Better Auth
├── emails/                     # Email templates for authentication 
├── src/
│   ├── app/                    # Next.js app router pages
│   │   ├── api/auth/[...all]/  # Better Auth API routes
│   │   ├── (auth)/             # Authentication pages
│   │   └── (dashboard)/        # Protected dashboard pages
│   ├── components/auth/        # Authentication UI components
│   ├── features/auth/          # Authentication logic and hooks
│   └── lib/auth/               # Better Auth client/server configuration
```

## Security Measures

The authentication system implements several security measures:

- **Rate Limiting**: Prevents brute force attacks
- **Password Policy**: Enforces strong passwords (8+ characters, mixed case, numbers, special chars)
- **Account Enumeration Prevention**: Generic error messages
- **Secure Token Handling**: HTTP-only, secure cookies with SameSite attribute
- **Password Reuse Prevention**: Prevents users from reusing old passwords
- **Database Error Handling**: Graceful failure for database issues
