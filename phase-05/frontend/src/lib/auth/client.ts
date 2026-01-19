"use client";

import { env } from "@/utils/env";
import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";
import { toast } from "react-hot-toast";

export const authClient = createAuthClient({
  baseURL: env.NEXT_PUBLIC_BASE_URL,
  plugins: [
    jwtClient()
  ],
  fetchOptions: {
    onError: (error) => {
      console.error("Auth error:", error);
      toast.error(error.error.message || "An authentication error occurred");
    },
  },
});

export const getAuthClient = () => authClient;

// Extend the authClient with a method to get the session token
export const getSessionToken = async (): Promise<string | null> => {
  try {
    // Use the JWT token method as per the documentation
    const tokenResponse = await authClient.token();

    if (tokenResponse?.data?.token) {
      return tokenResponse.data.token;
    }

    // Fallback to session token if JWT is not available
    const { data, error } = await authClient.getSession();
    if (error) throw error;

    return data?.session?.token || null;
  } catch (error) {
    console.error("Error getting session token:", error);
    return null;
  }
};
