import * as React from 'react'
import Link from 'next/link'

import { cn } from '@/lib/utils'
import { auth } from '@/auth'
import { Button, buttonVariants } from '@/components/ui/button'
import {
  IconSeparator,
} from '@/components/ui/icons'
import { UserMenu } from '@/components/user-menu'
import { SidebarMobile } from './sidebar-mobile'
import { ChatHistory } from './chat-history'
import { Session } from '@/lib/types'

async function UserOrLogin() {
  const session = (await auth()) as Session

  return (
    <>
      {session?.user ? (
        <SidebarMobile>
          <ChatHistory />
        </SidebarMobile>
      ) : (
        <Link href="/new" rel="nofollow">
          {/* TODO: Add an Icon */}
          {/* <IconNextChat className="size-6 mr-2 dark:hidden" inverted /> */}
        </Link>
      )}
      <div className="flex items-center">
        <IconSeparator className="size-6 text-muted-foreground/50" />
        {session?.user ? (
          <UserMenu user={session.user} />
        ) : (
          <Button variant="link" asChild className="-ml-2">
            <Link href="/login">Login</Link>
          </Button>
        )}
      </div>
      <div className="flex items-center">
        <Button variant="link" asChild className="-ml-2">
          <Link href="/">Home</Link>
        </Button>
        <Button variant="link" asChild className="-ml-2">
          <Link href="/reviews">Reviews</Link>
        </Button>
      </div>
    </>
  )
}

export function Header() {
  return (
    <header className="sticky top-0 z-50 flex items-center justify-between w-full h-16 px-4 border-b shrink-0 bg-gradient-to-b from-background/10 via-background/50 to-background/80 backdrop-blur-xl">
      <div className="flex items-center">
        <React.Suspense fallback={<div className="flex-1 overflow-auto" />}>
          <UserOrLogin />
        </React.Suspense>
      </div>
      <div className="flex items-center justify-end space-x-2"></div>
    </header>
  )
}
