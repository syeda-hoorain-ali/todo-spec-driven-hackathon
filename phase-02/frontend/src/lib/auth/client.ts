import { env } from "@/utils/env";
import { createAuthClient } from "better-auth/react";
import { toast } from "sonner";

export const { useSession, ...authClient } = createAuthClient({
  baseURL: env.NEXT_PUBLIC_BASE_URL,
  fetchOptions: {
    onError: (error) => {
      console.error("Auth error:", error);
      toast.error(error.error.message || "An authentication error occurred");
    },
  },
});
