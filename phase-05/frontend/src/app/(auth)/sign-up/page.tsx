import { SignUpForm } from "@/components/auth/sign-up";
import { AuthRedirect } from "@/components/shared/auth-redirect";
import { CoffeeIcon } from "lucide-react";

export default function SignUpPage() {
  return (
    <AuthRedirect requireAuth={false} redirectTo="/dashboard">
      <div className="min-h-screen flex items-center justify-center bg-gradient-warm p-4">
        <div className="w-full max-w-md animate-scale-in">
          {/* Logo Section */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-espresso shadow-elevated mb-4">
              <CoffeeIcon className="w-8 h-8 text-primary-foreground" />
            </div>
            <h1 className="text-4xl font-bold font-display text-foreground">TaskFlow</h1>
            <p className="text-muted-foreground mt-2 font-sans">Your AI-powered productivity companion</p>
          </div>
          <SignUpForm />
          {/* Features list */}
          <div className="mt-8 grid grid-cols-3 gap-4 text-center animate-slide-up delay-300">
            {[
              { icon: "🎯", label: "Smart Tasks" },
              { icon: "🤖", label: "AI Assistant" },
              { icon: "🎙️", label: "Voice Input" },
            ].map((feature) => (
              <div key={feature.label} className="p-3 rounded-xl bg-card/50 shadow-soft">
                <span className="text-2xl">{feature.icon}</span>
                <p className="text-xs text-muted-foreground mt-1 font-sans">{feature.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AuthRedirect>
  );
}
