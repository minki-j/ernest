import NextAuth from 'next-auth'
import { authConfig } from './auth.config'
import Google from 'next-auth/providers/google'
import CredentialsProvider from 'next-auth/providers/credentials'

interface User {
  id: string
  name?: string | null
  email?: string | null
  image?: string | null
}

const customProvider = CredentialsProvider({
  name: 'Credentials',
  credentials: {
    email: { label: 'Email', type: 'text' },
    password: { label: 'Password', type: 'password' }
  },
  authorize: async (credentials: Partial<Record<"email" | "password", unknown>>, request: Request): Promise<User | null> => {
    const api_base = process.env.API_URL
    const endpoint = 'db/loginByEmail'
    const url = new URL(endpoint, api_base).toString()

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.API_TOKEN}`
      },
      body: JSON.stringify({
        email: credentials.email,
        password: credentials.password
      })
    })

    if (!response.ok) {
      return null
    } else {
      console.log("log in successful from backend. Sending user")
      const user: User = {
        id: 'some-unique-id', 
        email: credentials.email as string,
      }
      return user
    }
  }
})

export const { handlers, auth, signIn, signOut } = NextAuth({
  ...authConfig,
  providers: [Google, customProvider],
  callbacks: {
    async signIn({ user, account, profile }) {
      if (!account) {
        return false
      }
      if (account.provider === 'google') {
        await addUserToBackend(user)
      }
      return true
    }
  }
})


async function addUserToBackend(user: User) {
  const api_base = process.env.API_URL
  const endpoint = 'db/addNewUser'
  const url = new URL(endpoint, api_base).toString()
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${process.env.API_TOKEN}`
    },
    body: JSON.stringify({
      user_id: user.id,
      name: user.name,
      email: user.email
    })
  })

  if (!response.ok) {
    console.error('Failed to add user to backend')
  }
}
