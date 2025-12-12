import { CoffeeIcon } from "lucide-react";

export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-warm">
      <div className="animate-pulse-soft">
        <CoffeeIcon className="w-12 h-12 text-accent" />
      </div>
    </div>
  );
}
