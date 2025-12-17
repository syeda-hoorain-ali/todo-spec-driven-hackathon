# Quickstart: Task Management Frontend

## Prerequisites

- Node.js 18+ installed
- The backend API server running and accessible
- Better Auth configured and running
- Environment variables properly set

## Environment Variables

Create a `.env.local` file in the frontend directory with the following variables:

```env
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
NEXT_PUBLIC_BASE_URL=http://localhost:3000
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-secret-key-here
DATABASE_URL=your-database-url
```

## Running the Application

1. **Install dependencies**:
   ```bash
   cd phase-02/frontend
   npm install
   # or
   yarn install
   ```

2. **Run the development server**:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

3. **Access the application**:
   - Open [http://localhost:3000](http://localhost:3000) in your browser
   - Sign in using the authentication system
   - Navigate to the dashboard to access the task management features

## Key Features Overview

### Task List Page
- View all tasks for the authenticated user
- Mark tasks as complete/incomplete with a single click
- Filter tasks by completion status
- Search tasks by title or description

### Create Task Page
- Create new tasks with title and description
- Set optional due dates and reminders
- Configure recurring tasks with various patterns
- Form validation ensures data integrity

### Edit Task Page
- Update existing task details
- Modify completion status, due dates, and recurrence settings
- Save changes and see updates reflected immediately

## Development Guidelines

### Component Structure
- Place new components in `src/features/tasks/components/`
- Use descriptive names for components (e.g., `TaskList.tsx`, `TaskForm.tsx`)
- Follow the existing component architecture patterns

### API Integration
- All API calls should go through the service layer in `src/features/tasks/api/`
- Use React Query hooks for data fetching and mutations
- Implement proper error handling for all API operations

### Form Handling
- Use react-hook-form for form state management
- Implement Zod schemas for validation
- Follow accessibility best practices for form elements

### Testing
- Write unit tests for hooks and utility functions
- Create component tests for UI interactions
- Add integration tests for API service functionality
