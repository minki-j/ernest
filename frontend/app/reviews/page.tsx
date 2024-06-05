import { nanoid } from '@/lib/utils'
import { auth } from '@/auth'
import { Session } from '@/lib/types'
import { getMissingKeys } from '@/app/actions'

export const metadata = {
  title: 'Ernest'
}

export default async function IndexPage() {

  const session = (await auth()) as Session
  const missingKeys = await getMissingKeys()

  return (
    <>
    </>
  )
}
