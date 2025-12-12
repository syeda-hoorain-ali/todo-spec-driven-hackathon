"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useSession } from "@/lib/auth/client";
import { toast } from "sonner";
import { useEffect, useState } from "react";
import { User } from "./types";
import { useRouter } from "next/navigation";
import {
  changePasswordQuery,
  forgotPasswordQuery,
  resetPasswordQuery,
  signInQuery,
  signOutQuery,
  signUpQuery,
  updateUserQuery
} from "./queries";


export const useAuth = () => {
  const router = useRouter();

  const signUp = useMutation({
    mutationFn: signUpQuery,
    onSuccess: () => {
      toast.success("Registration successful! Redirecting...");
      router.push("/dashboard");
    },
    onError: (error) => {
      console.error("Registration error:", error);
      toast.error(error.message || "Registration failed");
    }
  });


  const signIn = useMutation({
    mutationFn: signInQuery,
    onSuccess: () => {
      toast.success("Sign in successful! Redirecting...");
      router.push("/dashboard");
    },
    onError: (error) => {
      console.error("Sign in error:", error);
      toast.error("An unexpected error occurred during sign in");
    },
  });


  const signOut = useMutation({
    mutationFn: signOutQuery,
    onSuccess: () => {
      toast.success("Successfully signed out");
      router.push("/sign-in"); // Redirect to sign-in page after sign-out
    },
    onError: (error) => {
      console.error("Sign out error:", error);
      toast.error(error.message || "Sign out failed");
    },
  });


  const forgotPassword = useMutation({
    mutationFn: forgotPasswordQuery,
    onError: ({ message }) => {
      console.error("Forgot password error:", message);
      if (message?.includes('rate limit')) {
        toast.error("Too many requests. Please try again later.");
      } else {
        toast.error("An unexpected error occurred. Please try again.");
      }
    },
    onSuccess: () => {
      toast.success("If an account with this email exists, a password reset link has been sent.");
    }
  });


  const resetPassword = useMutation({
    mutationFn: resetPasswordQuery,
    onSuccess: () => {
      toast.success("Password reset successful! Redirecting to sign in...");
      router.push("/sign-in");
    },
    onError: (error) => {
      console.error("Password reset failed: ", error);
      toast.error(error.message || "Password reset failed");
    }
  });


  const changePassword = useMutation({
    mutationFn: changePasswordQuery,
    onSuccess: () => {
      toast.success("Password changed successfully!");
    },
    onError: (error) => {
      console.error("Change password error:", error);
      toast.error(error.message || "Failed to change password");
    },
  });

  return {
    signUp,
    signIn,
    signOut,
    forgotPassword,
    resetPassword,
    changePassword,
  }
}


export const useUser = () => {

  const { data: session, isPending: isLoading, error, refetch } = useSession();
  const queryClient = useQueryClient();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    if (session) {
      setUser(session.user);
    } else {
      setUser(null);
    }
    console.log(user);
    console.log(session);
    console.log(isLoading);
  }, [session]);

  const updateUserMutation = useMutation({
    mutationFn: updateUserQuery,
    onSuccess: () => {
      toast.success("Profile updated successfully!");
      // Refetch user data to update context
      refetch();
      // Invalidate and refetch user query to update dashboard/profile page
      queryClient.invalidateQueries({ queryKey: ["user"] });
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to update profile");
    },
  });


  return {
    updateUser: updateUserMutation,
    user,
    isLoading,
    error,
    refetch
  }
};

