"use client";

import { ArrowRight } from "lucide-react";
import { SignInButton } from "@clerk/clerk-react";
// import { auth, currentUser } from "@clerk/nextjs";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/spinner";

export const Heading = () => {
  const isLoading = false;
  const loggedIn = true;

  return (
    <div className="max-w-3xl space-y-4">
      <h1 className="text-3xl sm:text-5xl md:text-6xl font-bold">
        No more shallow customer insights.
        <br />
        <span className="underline">AI survey buddy</span>
      </h1>
      <h3 className="text-base sm:text-xl md:text-2xl font-medium">
        With a smart AI survey buddy, <br />
        get your customers&apos; pain points accurately.
      </h3>
      {isLoading && (
        <div className="w-full flex items-center justify-center">
          <Spinner size="lg" />
        </div>
      )}
      {loggedIn && !isLoading && (
        <Button asChild>
          <Link href="/home">
            Enter AI Survey Buddy
            <ArrowRight className="h-4 w-4 ml-2" />
          </Link>
        </Button>
      )}
      {!loggedIn && !isLoading && (
        <SignInButton mode="modal">
          <Button>
            Get Survey Buddy free
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        </SignInButton>
      )}
    </div>
  );
}