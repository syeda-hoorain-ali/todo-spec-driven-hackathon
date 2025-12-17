import axios from 'axios';
import { getSessionToken } from '@/lib/auth/client';
import { env } from '@/utils/env';

const API_BASE_URL = env.NEXT_PUBLIC_API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    // For Better Auth, we may need to include credentials (cookies) instead of Bearer token
    // Better Auth typically handles auth via cookies by default
    config.withCredentials = true;

    // We can still try to get the token if needed
    const token = await getSessionToken();
    console.log("Token: ", token)

    // Only add Authorization header if we have a token and the backend specifically requires it
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access - maybe redirect to login
      console.error('Unauthorized access - token may have expired');
    }
    return Promise.reject(error);
  }
);

// Function to create API instance with user ID in the path
export const createApiWithUserId = (userId: string) => {
  const apiWithUserId = axios.create({
    baseURL: `${API_BASE_URL}/${userId}`,
  });

  // Add the same interceptors to the user-specific API instance
  apiWithUserId.interceptors.request.use(
    async (config) => {
      // Include credentials for Better Auth cookie-based auth
      config.withCredentials = true;
      const token = await getSessionToken();

      // Only add Authorization header if we have a token
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  apiWithUserId.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        // Handle unauthorized access - maybe redirect to login
        console.error('Unauthorized access - token may have expired');
      }
      return Promise.reject(error);
    }
  );

  return apiWithUserId;
};

export default api;
