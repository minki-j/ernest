import { nanoid } from '@/lib/utils'
import { Chat } from '@/components/chat'
import { AI } from '@/lib/chat/actions'
import { auth } from '@/auth'
import { Session } from '@/lib/types'
import { getMissingKeys } from '@/app/actions'

export const metadata = {
  title: 'Ernest'
}

export default async function IndexPage() {
  const id = nanoid()
  const session = (await auth()) as Session
  const missingKeys = await getMissingKeys()

  return (
    // AI State being initialized with a new id and an empty array of messages.
    <AI initialAIState={{ reviewId: id, messages: [] }}> 
      <Chat id={id} session={session} missingKeys={missingKeys} />
    </AI>
  )
}
