# Task Management Frontend

## Overview
The frontend of our task management application provides a clean, intuitive user interface that allows users to efficiently organize and track their tasks. Built with Next.js, it offers a responsive and fast user experience across all devices.

## Key Features
- **User Authentication**: Secure sign-up, login, and password recovery
- **Task Management**: Create, update, complete, and delete tasks
- **Task Organization**: Filter and sort tasks by status, priority, and date
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Secure Sessions**: Protected user data with secure session management

## Getting Started

### Prerequisites
- Node.js 20+ installed on your system
- A package manager (npm, yarn, pnpm, or bun)

### Environment Setup
Create a `.env.local` file in the root of the `frontend` directory with the following variables:

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

To generate a secure `BETTER_AUTH_SECRET`, use:
```bash
openssl rand -base64 32
```

### Installation
1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## User Experience

The application provides a seamless experience for task management:

- **Registration**: New users can create accounts with name, email, and password
- **Login**: Secure authentication to access personal task lists
- **Dashboard**: Clean interface to view, create, and manage tasks
- **Task Details**: View and update task information including due dates and priority
- **Logout**: Secure session termination

## Security Features
- Strong password requirements during registration
- Secure JWT-based session management
- Protected routes to prevent unauthorized access
- Rate limiting to prevent abuse
- Secure password reset via email
