'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { kv } from '@vercel/kv'

import { auth } from '@/auth'
import { type Review } from '@/lib/types'

let api_url =process.env['API_URL']

export async function getReviewsByUser(userId?: string | null){
  console.log('getReviewsByUser', userId);  
  if (!userId) {
    console.error('getReviewsByUser error: userId is undefined')
    return []
  }
  const url = api_url + "db/getReviewsByUser" + '?user_id=' + userId
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + process.env['API_TOKEN']
      }
    }).then(res => {
      if (res.status==404){
        console.log("No reviews found for user", userId)
        return []
      }
      if (!res.ok) {
        console.error('getReviewsByUser error:\n', res)
        return []
      }
      return res.json()
    })
    
    const reviews: Review[] = res.map((review: any) => {
      return {
        id: review._id,
        title: review.title,
        createdAt: review.created_at,
        userId: review.user_id,
        path: `/chat/${review._id}`,
        messages: review.messages,
        story: review.story
      }
    })
    // console.log('reviews: ', reviews);
    
    return reviews

  } catch (error) {
    console.error('getReviewsByUser error:\n', error)
    return []
  }
}

export async function getReview(param_id?: string) {
  console.log('getReview', param_id)

  const url = api_url + 'db/getReview' + '?review_id=' + param_id

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + process.env['API_TOKEN']
      },
    }).then(res => res.json())

    // console.log('res: ', res);

    const review: Review = {
      id: res._id,
      title: res.story,
      createdAt: res.created_at,
      userId: res.user_id,
      path: `/chat/${res._id}`,
      messages: res.messages
    }

    return review
      
  } catch (error) {
    console.error('getReview error:\n', error)
    return null
  }
}


export async function saveReview(chat: Review) {
  console.log('saveReview');
  
  const session = await auth()

  if (session && session.user) {    
    const url = api_url + 'db/saveReview'

    const body = JSON.stringify(chat)
    console.log("======= body =======\n", body);

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer ' + process.env['API_TOKEN'],
          body: body
        },
      }).then(res => res.json())
    } catch (error) {
      console.error('saveReview error:\n', error)
      return []
    }

  } else {
    return
  }
}

export async function removeChat({ id, path }: { id: string; path: string }) {
  console.log('removeChat');
  
  const session = await auth()

  if (!session) {
    return {
      error: 'Unauthorized'
    }
  }

  //Convert uid to string for consistent comparison with session.user.id
  const uid = String(await kv.hget(`chat:${id}`, 'userId'))

  if (uid !== session?.user?.id) {
    return {
      error: 'Unauthorized'
    }
  }

  await kv.del(`chat:${id}`)
  await kv.zrem(`user:chat:${session.user.id}`, `chat:${id}`)

  revalidatePath('/')
  return revalidatePath(path)
}

export async function clearChats() {
  console.log('clearChats');
  
  const session = await auth()

  if (!session?.user?.id) {
    return {
      error: 'Unauthorized'
    }
  }

  const url = api_url + 'db/deleteReviewsByUser' + '?user_id=' + session.user.id

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + process.env['API_TOKEN']
      }
    }).then(res => res.json())

    console.log('deleteReviewsByUser res: ', res)
    
  } catch (error) {
    console.error('deleteReviewsByUser error:\n', error)
    return 
  }

  revalidatePath('/')
  redirect('/')  
}

export async function getSharedChat(id: string) {
  console.log('getSharedChat');
  
  const chat = await kv.hgetall<Review>(`chat:${id}`)

  if (!chat || !chat.sharePath) {
    return null
  }

  return chat
}

export async function shareChat(id: string) {
  const session = await auth()

  if (!session?.user?.id) {
    return {
      error: 'Unauthorized'
    }
  }

  const chat = await kv.hgetall<Review>(`chat:${id}`)

  if (!chat || chat.userId !== session.user.id) {
    return {
      error: 'Something went wrong'
    }
  }

  const payload = {
    ...chat,
    sharePath: `/share/${chat.id}`
  }

  await kv.hmset(`chat:${chat.id}`, payload)

  return payload
}


export async function refreshHistory(path: string) {
  redirect(path)
}

export async function getMissingKeys() {
  const keysRequired = ['OPENAI_API_KEY']
  return keysRequired
    .map(key => (process.env[key] ? '' : key))
    .filter(key => key !== '')
}


export async function add_vendor(name: string, address: string, reviewID: string) {
  console.log('add_vendor');

  const session = await auth()

  if (session && session.user) {

    const url = api_url + 'db/addVendor'
    const body = JSON.stringify({ name, address, reviewID})

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer ' + process.env['API_TOKEN']
        },
        body: body
      }).then(res => res.json())

      return res
    } catch (error) {
      console.error('add_vendor error:\n', error)
      return []
    }
    
  } else {
    return
  }
}