# Deployment Script for Todo App with Better Auth

This script automates the deployment of the Next.js application with Better Auth to production.

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Access to production environment variables
- Database (Neon Postgres) connection ready

## Environment Variables

Before deployment, ensure the following environment variables are set in your production environment:

```bash
NEXT_PUBLIC_BASE_URL="https://yourdomain.com"

# Better Auth Configuration
AUTH_SECRET=your-production-jwt-secret-here-make-sure-it-is-at-least-32-characters-long
BETTER_AUTH_URL=https://yourdomain.com

# Neon Database Configuration
DATABASE_URL=your-production-neon-database-connection-string

# Email Configuration (for password reset)
SMTP_HOST=your-production-smtp-host
SMTP_PORT=587
SMTP_USER=your-production-smtp-username
SMTP_PASSWORD=your-production-smtp-password
SMTP_FROM=your-app-name <noreply@yourdomain.com>

# Node Environment
NODE_ENV=production
```

## Deployment Steps

### 1. Install Dependencies

```bash
npm install
# or
yarn install
```

### 2. Build the Application

```bash
npm run build
# or
yarn build
```

### 3. Start the Production Server

```bash
npm start
# or
yarn start
```

## Docker Deployment (Optional)

If you prefer to deploy using Docker, create a `Dockerfile`:

```Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
```

And a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_BASE_URL=${NEXT_PUBLIC_BASE_URL}
      - BETTER_AUTH_URL=${BETTER_AUTH_URL}
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - DATABASE_URL=${DATABASE_URL}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - SMTP_FROM=${SMTP_FROM}
    restart: unless-stopped
```

To deploy with Docker:

```bash
# Build and start the container
docker-compose up -d

# To stop the container
docker-compose down
```

## Vercel Deployment

For deployment to Vercel (recommended for Next.js apps):

1. Install the Vercel CLI:
```bash
npm i -g vercel
```

2. Link your project:
```bash
vercel
```

3. Set environment variables in the Vercel dashboard or using the CLI:
```bash
vercel env add
```

4. Deploy:
```bash
vercel --prod
```

## Post-Deployment Tasks

1. Verify the application is running at your domain
2. Test registration and sign-in functionality
3. Verify password reset emails are working
4. Check that protected routes are properly secured
5. Monitor logs for any errors

## Rollback Procedure

If issues occur after deployment:

1. Keep the previous version running
2. Identify the issue and fix it in a development branch
3. Test the fix thoroughly
4. Deploy the fix as a new version
5. If needed, temporarily rollback to the previous version

## Health Checks

The application includes basic health checks:

- `/api/health` - Returns 200 OK if the app is running
- Monitor authentication endpoints for functionality
- Check database connectivity
- Verify email service configuration

## Monitoring

Set up monitoring for:

- Application uptime
- Authentication success/failure rates
- Database connection health
- Error logs
- Performance metrics
