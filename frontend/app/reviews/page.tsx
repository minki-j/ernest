import { nanoid } from '@/lib/utils'
import { auth } from '@/auth'
import { Session } from '@/lib/types'
import { getMissingKeys } from '@/app/actions'
import { cache } from 'react'
import { getReviewsByUser } from '@/app/actions'

import {ReviewCard} from '@/components/review-card'

export const metadata = {
  title: 'Ernest'
}


const loadChats = cache(async (userId?: string) => {
  console.log("calling loadChats (not using cache) ")
  const result = await getReviewsByUser(userId)

  return result
})

export default async function ReviewsPage() {
  const session = await auth()
  let chats = []

  if (!session?.user?.id) {
    return null
  } else {
    console.log('loadChats runs')
    chats = await loadChats(session?.user?.id)
    // console.log("loaded chats: ", chats?.length);
  }
  


  return (
    <>
    {chats?.length ? (
      <div className="space-y-2 px-2">
        {chats.map((chat) => (
          <ReviewCard key={nanoid()} title={chat.title} description={chat.description} content={chat.story} created_at={chat.createdAt} />
        ))}
      </div>
    ) : (
      <div className="p-8 text-center">
        <p className="text-sm text-muted-foreground">No chat history...</p>
      </div>
    )}
    </>
  )
}
