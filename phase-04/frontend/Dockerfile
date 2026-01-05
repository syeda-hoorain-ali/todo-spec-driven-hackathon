# ========================================
# Production-Ready Multi-Stage Dockerfile
# Next.js Frontend Application
# ========================================

# --- Base stage ---
FROM node:24.11.1-alpine AS base

# Set working directory
WORKDIR /app

# Install system dependencies needed for building
RUN apk add --no-cache libc6-compat

# --- Dependencies stage ---
FROM base AS dependencies

# Copy package files
COPY package.json package-lock.json ./

# Install production dependencies only
RUN npm ci --only=production --omit=dev

# --- Builder stage ---
FROM base AS builder

# Install build dependencies
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package.json package-lock.json ./

# Install all dependencies (including dev dependencies) for building
RUN npm ci

# Copy application source code
COPY . .

# Build the Next.js application with environment variables provided at build time
# Use a PostgreSQL URL format that neon driver can accept during build time
ENV NODE_ENV=production
ENV NEXT_PUBLIC_BASE_URL=${NEXT_PUBLIC_BASE_URL:-http://localhost:3000}
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL:-http://localhost:8000}
ENV NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=${NEXT_PUBLIC_CHATKIT_DOMAIN_KEY:-dummy-key}
ENV BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET:-dummy-secret}
ENV DATABASE_URL=${DATABASE_URL:-postgresql://user:password@localhost:5432/dbname}
ENV SMTP_USER=${SMTP_USER:-dummy@example.com}
ENV SMTP_PASS=${SMTP_PASS:-dummy}

RUN npm run build

# Clean up build dependencies
RUN apk del python3 make g++

# --- Final stage ---
FROM node:24.11.1-alpine AS final

# Install minimal runtime dependencies and create non-root user in one layer
RUN apk add --no-cache libc6-compat && \
    adduser --disabled-password --gecos '' appuser

# Set working directory
WORKDIR /app

# Copy only necessary files from previous stages
COPY --from=dependencies --chown=appuser:appuser /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appuser /app/.next/standalone ./
COPY --from=builder --chown=appuser:appuser /app/.next/static ./.next/static
COPY --from=builder --chown=appuser:appuser /app/public ./public

# Switch to non-root user
USER appuser

# Expose port 3000
EXPOSE 3000

# Set environment variables for Next.js standalone output
ENV PORT=3000
ENV NODE_ENV=production

# Run the Next.js application
CMD ["node", "server.js"]