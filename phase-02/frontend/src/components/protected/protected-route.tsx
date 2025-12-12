"use client";

import { useSession } from "@/lib/auth/client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import Loading from "@/app/loading";

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

export function ProtectedRoute({
  children,
  redirectTo = "/sign-in"
}: ProtectedRouteProps) {
  const { data: session, isPending: isLoading } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !session) {
      toast.info("Please sign in to access this page");
      router.push(redirectTo);
    }
  }, [session, isLoading, router, redirectTo]);

  // Show loading state while checking session
  if (isLoading) {
    return <Loading />;
  }

  // If user is authenticated, render the protected content
  if (session) {
    return <>{children}</>;
  }

  // If not authenticated and not loading, return null (as redirect effect will handle navigation)
  return null;
}
