import { auth } from '@/auth'
import LoginForm from '@/components/login-form'
import { Session } from '@/lib/types'
import { redirect } from 'next/navigation'

export default async function LoginPage() {
  console.log('LoginPage called');
  
  const session = (await auth()) as Session

  if (session) {
    console.log('redirect to home since a session already exists:', session);
    redirect('/')
  }

  return (
    <main className="flex flex-col p-4">
      <LoginForm />
    </main>
  )
}
