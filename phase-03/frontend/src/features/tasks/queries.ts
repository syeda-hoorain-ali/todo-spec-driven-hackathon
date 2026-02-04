"use client";

import { createApiWithUserId } from "./api";
import { Task, CreateTaskData, UpdateTaskData } from "./types";

// Define filter parameters type
export interface GetTasksFilters {
  keyword?: string;
  completed?: boolean;
  priority?: string;
  category?: string;
  date_from?: string;
  date_to?: string;
  skip?: number;
  limit?: number;
}

// Fetch all tasks for the specified user with optional filters
export const getTasks = async (userId: string, filters?: GetTasksFilters): Promise<{tasks: Task[], count: number}> => {
  const userApi = createApiWithUserId(userId);
  const params = new URLSearchParams();

  if (filters) {
    if (filters.keyword) params.append('keyword', filters.keyword);
    if (filters.completed !== undefined) params.append('completed', String(filters.completed));
    if (filters.priority && filters.priority !== "all") params.append('priority', filters.priority);
    if (filters.category && filters.category !== "all") params.append('category', filters.category);
    if (filters.date_from) params.append('date_from', filters.date_from);
    if (filters.date_to) params.append('date_to', filters.date_to);
    if (filters.skip !== undefined) params.append('skip', String(filters.skip));
    if (filters.limit !== undefined) params.append('limit', String(filters.limit));
  }

  const queryString = params.toString();
  const url = queryString ? `/tasks?${queryString}` : '/tasks';

  const response = await userApi.get(url);
  return response.data;
};

// Fetch a single task by ID for the specified user
export const getTask = async (userId: string, id: string): Promise<Task> => {
  const userApi = createApiWithUserId(userId);
  const response = await userApi.get(`/tasks/${id}`);
  return response.data;
};

// Create a new task for the specified user
export const createTask = async (userId: string, taskData: CreateTaskData): Promise<Task> => {
  const userApi = createApiWithUserId(userId);
  const response = await userApi.post("/tasks", taskData);
  return response.data;
};

// Update an existing task for the specified user
export const updateTask = async (userId: string, id: string, taskData: Partial<UpdateTaskData>): Promise<Task> => {
  const userApi = createApiWithUserId(userId);
  const response = await userApi.put(`/tasks/${id}`, taskData);
  return response.data;
};

// Delete a task for the specified user
export const deleteTask = async (userId: string, id: string): Promise<void> => {
  const userApi = createApiWithUserId(userId);
  await userApi.delete(`/tasks/${id}`);
};

// Toggle task completion status for the specified user
export const toggleTaskCompletion = async (userId: string, id: string, completed: boolean): Promise<Task> => {
  const userApi = createApiWithUserId(userId);
  const response = await userApi.patch(`/tasks/${id}/complete`, { completed });
  return response.data;
};
