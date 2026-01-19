import { ResetPasswordForm } from "@/components/auth/reset-password";
import { CoffeeIcon } from "lucide-react";

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-warm p-4">
      <div className="w-full max-w-md animate-scale-in">
        {/* Logo Section */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-espresso shadow-elevated mb-4">
            <CoffeeIcon className="w-8 h-8 text-primary-foreground" />
          </div>
          <h1 className="text-4xl font-bold font-display text-foreground">TaskFlow</h1>
          <p className="text-muted-foreground mt-2 font-sans">Create a new password</p>
        </div>
        <ResetPasswordForm />
      </div>
    </div>
  );
}
