"use client";

import { SignInButton, UserButton } from "@clerk/clerk-react";
import Link from "next/link";

import { useScrollTop } from "@/hooks/use-scroll-top";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/spinner";
import { cn } from "@/lib/utils";

import { Logo } from "./logo";

export const Navbar = () => {

  const scrolled = useScrollTop();
  const isLoading = false;
  const isLogged = true;

  return (
    <div
      className={cn(
        "z-50 bg-background dark:bg-[#1F1F1F] fixed top-0 flex items-center w-full p-6",
        scrolled && "border-b shadow-sm"
      )}
    >
      <Logo />
      <div className="md:ml-auto md:justify-end justify-between w-full flex items-center gap-x-2">
        {isLoading && <Spinner />}
        {!isLoading && !isLogged  && (
          <>
            <SignInButton mode="modal">
              <Button variant="ghost" size="sm">
                Log in
              </Button>
            </SignInButton>
            <SignInButton mode="modal">
              <Button size="sm">Get Survey Buddy free</Button>
            </SignInButton>
          </>
        )}
        {!isLoading && isLogged && (
          <>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/dashboard">Enter Dashboard</Link>
            </Button>
            <UserButton afterSignOutUrl="/" />
          </>
        )}
        {/* Don't use night mode yet */}
        {/* <ModeToggle /> */}
      </div>
    </div>
  );
}