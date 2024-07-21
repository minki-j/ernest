import NextAuth from 'next-auth'
import { authConfig } from './auth.config'
import Google from 'next-auth/providers/google'
import CredentialsProvider from 'next-auth/providers/credentials'
import type { Adapter } from '@auth/core/adapters'
import { MongoDBAdapter } from '@auth/mongodb-adapter'
import clientPromise from './lib/mongodb'

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
  authorize: async (
    credentials: Partial<Record<'email' | 'password', unknown>>,
    request: Request
  ): Promise<User | null> => {
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
      console.log('log in successful from backend. Sending user')
      const res = await response.json()
      console.log('======= user_id =======\n', res)
      const user: User = {
        id: res._id,
        email: res.email,
        name: res.name
      }
      return user
    }
  }
})

export const { handlers, auth, signIn, signOut } = NextAuth({
  ...authConfig,
  adapter: <Adapter>MongoDBAdapter(clientPromise, {
    databaseName: 'ernest',
    collections: { Users: 'users' }
  }),
  providers: [Google, customProvider],
  session: { strategy: 'jwt' }
})
