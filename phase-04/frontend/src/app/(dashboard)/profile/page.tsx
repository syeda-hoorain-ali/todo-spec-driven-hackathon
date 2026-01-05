"use client";

import Loading from "@/app/loading";
import { useUser } from "@/features/auth/hooks";
import { ProfileForm } from "@/components/auth/profile-form";
import { ChangePasswordForm } from "@/components/auth/change-password";
import { ProtectedRoute } from "@/components/protected/protected-route";

export default function DashboarProfilePage() {
  const { user, isLoading } = useUser();

  if (isLoading) return <Loading />;
  if (!user) return null;

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-warm">
        <main className="container mx-auto px-4 py-6 max-w-2xl">
          <div className="mb-8">
            <h1 className="text-3xl font-bold font-display text-foreground">Profile Settings</h1>
            <p className="text-muted-foreground font-sans mt-1">Manage your account information</p>
          </div>

          <div className="space-y-6">
            {/* Profile Info Card */}
            <ProfileForm />

            {/* Password Change Card */}
            <ChangePasswordForm />
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
