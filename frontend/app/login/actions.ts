'use server'

import { signIn } from '@/auth'


export async function loginAction(prevState: any, formData: FormData) {
  const email = formData.get('email') as string
  const password = formData.get('password') as string

  try {
    const res = await signIn('credentials', {
      redirect: false,
      email: email,
      password: password
    })
      return { status: 201, message: 'Login succeeded' }
  } catch (error) {
    console.error('Login error:', error)
    return { status: 500, message: 'Username or Password didn\'t match' }
  }
}

export async function loginGoogleAction(formData: FormData) {
  await signIn('google')
}