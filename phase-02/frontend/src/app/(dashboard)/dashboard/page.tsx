"use client";

import Loading from "@/app/loading";
import { useUser } from "@/features/auth/hooks";
import { ProtectedRoute } from "@/components/protected/protected-route";
import { CoffeeIcon } from "lucide-react";

export default function DashboardPage() {
  const { user, isLoading } = useUser();

  if (isLoading) return <Loading />
  if (!user) return null;

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-warm">
        <main className="container mx-auto px-4 py-6">
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <div className="text-center mb-4">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-espresso shadow-elevated mb-4">
                <CoffeeIcon className="w-8 h-8 text-primary-foreground" />
              </div>
              <h1 className="text-4xl font-bold font-display text-foreground">TaskFlow</h1>
              <p className="text-muted-foreground mt-2 font-sans">Dashboard Comming Soon</p>
            </div>
            <p className="text-muted-foreground text-center max-w-md">
              We're working hard to bring you an amazing dashboard experience. Stay tuned!
            </p>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
