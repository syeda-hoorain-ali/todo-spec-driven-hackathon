"use client";

import { Button } from "@/components/ui/button";
import { ArrowLeftIcon, HomeIcon } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const NotFound = () => {
  const router = useRouter();

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted">
      <div className="text-center">
        <h1 className="mb-4 text-4xl md:text-6xl font-bold">404</h1>
        <p className="mb-4 text-xl text-muted-foreground">Oops! Page not found</p>
        <div className="flex items-center justify-center gap-3">
          <Button variant="outline" onClick={() => router.back()}>
            <ArrowLeftIcon className="w-4 h-4 mr-2" />
            Go Back
          </Button>
          <Link href="/">
            <Button variant="espresso">
              <HomeIcon className="w-4 h-4 mr-2" />
              Home
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
