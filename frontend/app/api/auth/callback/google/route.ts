import { handlers } from '@/auth'
import { NextRequest } from 'next/server'

export async function GET(req: NextRequest) {
  console.log('GET /api/auth/callback/google')

  return handlers.GET(req)
}

export async function POST(req: NextRequest) {
  console.log('POST /api/auth/callback/google')

  return handlers.POST(req)
}
