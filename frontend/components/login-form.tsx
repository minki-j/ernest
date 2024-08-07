'use client'

import { signIn } from '@/auth'
import { Toaster, toast } from 'react-hot-toast'
import { useFormState, useFormStatus } from 'react-dom'
import { useEffect } from 'react'
import { loginAction, loginGoogleAction } from '@/app/login/actions'

export default function LoginForm() {
  const [state, formAction] = useFormState(loginAction, null)

  useEffect(() => {
    if (state) {
      if (state.status !== 201) {
        toast.error(state.message)
      } else {
        toast.success('Welcome back! You have successfully logged in.')
        window.location.href = '/'
      }
    }
  }, [state])

  return (
    <div className="space-y-3">
      <Toaster position="top-right" reverseOrder={false} />
      <form
        action={formAction}
        className="flex flex-col items-center mx-auto gap-4 space-y-3 max-w-md"
      >
        <input
          className="flex h-10 w-full flex-row items-center justify-center rounded-md p-2 text-sm font-semibold"
          type="email"
          name="email"
          placeholder="Email"
          required
        />
        <input
          className="flex h-10 w-full flex-row items-center justify-center rounded-md p-2 text-sm font-semibold"
          type="password"
          name="password"
          placeholder="Password"
          required
        />
        <LoginButton button_text="Log In" />
      </form>
      <form
        action={loginGoogleAction}
        className="flex flex-col items-center mx-auto gap-4 space-y-3 max-w-md"
      >
        <LoginButton button_text="Log In with Google" />
      </form>
    </div>
  )
}

function LoginButton({ button_text }: { button_text: string }) {
  const { pending } = useFormStatus()

  return (
    <button
      className="flex h-10 w-full flex-row items-center justify-center rounded-md bg-zinc-900 p-2 text-sm font-semibold text-zinc-100 hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
      disabled={pending}
    >
      {pending ? (
        <div className="size-6 border-y-2 border-zinc-100 rounded-full animate-spin"></div>
      ) : (
        button_text
      )}
    </button>
  )
}
