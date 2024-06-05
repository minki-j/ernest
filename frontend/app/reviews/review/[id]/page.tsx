import { type Metadata } from 'next'
import { notFound, redirect } from 'next/navigation'

import { auth } from '@/auth'
import { Session } from '@/lib/types'

// export async function generateMetadata({
//   params
// }: ChatPageProps): Promise<Metadata> {
//   const session = await auth()

//   if (!session?.user) {
//     return {}
//   }

//   const chat = await getReview(params.id, session.user.id)
//   return {
//     title: chat?.title.toString().slice(0, 50) ?? 'Chat'
//   }
// }

export default async function ReviewPage({ params }) {
  console.log('ReviewPage: ', params)

  const session = (await auth()) as Session

  if (!session?.user) {
    redirect(`/login?next=/chat/${params.id}`)
  }

  return (
    <>
    </>
  )
}
