// 'use client'

import { signIn } from '@/auth'

export default function LoginForm() {

  return (
    <form
      action={async () => {
        'use server'
        await signIn('google')
      }}
      className="flex flex-col items-center mx-auto gap-4 space-y-3 max-w-md"
    >
      <GoogleButton />
    </form>
  )
}

function GoogleButton() {

  return (
    <button
      className="flex h-10 w-full flex-row items-center justify-center rounded-md bg-zinc-900 p-2 text-sm font-semibold text-zinc-100 hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
    >
      {"Sign up with Google"}
    </button>
  )
}
