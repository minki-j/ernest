import 'server-only'

import {
  createAI,
  createStreamableUI,
  getMutableAIState,
  getAIState,
  streamUI,
  createStreamableValue
} from 'ai/rsc'

import { z } from 'zod'
import { EventsSkeleton } from '@/components/stocks/events-skeleton'
import { Events } from '@/components/stocks/events'

import {
  formatNumber,
  runAsyncFnWithoutBlocking,
  sleep,
  nanoid
} from '@/lib/utils'
import { saveReview } from '@/app/actions'
import {
  SpinnerMessage,
  UserMessage,
  BotMessage
} from '@/components/stocks/message'
import { PickVendor } from '@/components/stocks/pick-vendor'
import { Review, Message } from '@/lib/types'
import { auth } from '@/auth'

let api_url = process.env['API_URL']

async function submitFirstAIMessage(reviewId: string, message: string) {
  // Add the first AI message to the backend
  const session = await auth()
  console.log('submitFirstAIMessage session: ', session)

  if (!session || !session.user) return

  if (!session.user.email) {
    throw new Error('User email is not found in the session')
  }

  const formData = new FormData()
  formData.append('user_email', session.user.email)
  formData.append('review_id', reviewId)
  formData.append('message', message)

  const url = api_url + 'chat/add_ai_first_message'

  const res = await fetch(url, {
    method: 'POST',
    body: formData
  })
  console.log('submitFirstAIMessage res: ', res)

  if (!res.ok) {
    throw new Error(`HTTP error! status: ${res.status}`)
  }
  return
}

async function submitUserMessage(message: string, reviewId: string) {
  'use server'

  const aiState = getMutableAIState<typeof AI>()

  aiState.update({
    ...aiState.get(),
    messages: [
      ...aiState.get().messages,
      {
        id: nanoid(),
        role: 'user',
        content: message
      }
    ]
  })

  const session = await auth()

  if (!session || !session.user) return
  const formData = new FormData()
  formData.append('user_id', session.user.id)
  formData.append('review_id', reviewId)
  formData.append('user_msg', message)

  const url = api_url + 'chat/invoke'

  // ! I need to use tool to use StreamUI function from Vercel AI SDK.. But I couldn't since I'm not calling LLM call here. I'm using FastAPI endpoints that calls LLMs.
  const res = await fetch(url, {
    method: 'POST',
    body: formData
  })
  // console.log('res: ', res);

  if (!res.ok) {
    throw new Error(`HTTP error! status: ${res.status}`)
  }

  const data = await res.json()
  // console.log("======= data =======\n", data);

  type ComponentMapType = {
    [key: string]: JSX.Element
  }

  const componentMap: ComponentMapType = {
    message: <BotMessage content={data.message} />,
    pick_vendor: <PickVendor />
  }

  const display = componentMap[data.uiType]

  return {
    id: nanoid(),
    role: 'ai',
    display: display
  }
}

//AI State refers to the state of the application in a serialisable format that will be used on the server and can be shared with the language model.
export type AIState = {
  reviewId: string
  messages: Message[]
}

export type UIState = {
  id: string
  role: 'user' | 'assistant' | 'system' | 'tool'
  display: React.ReactNode
}[]

export const AI = createAI<AIState, UIState>({
  actions: {
    submitUserMessage
  },
  initialUIState: [],
  initialAIState: {
    reviewId: nanoid(),
    messages: []
  },
  // onGetUIState runs when?
  onGetUIState: async () => {
    'use server'
    console.log('onGetUIState')

    const session = await auth()

    if (session && session.user) {
      const aiState = getAIState()

      if (aiState.messages.length != 0) {
        const uiState = convertSateAI2UI(aiState)
        return uiState
      } else {
        let message_content: string
        if (session.user?.name) {
          message_content = `Hi ${session.user.name}! Which company of product do you want to talk about today?`
        } else {
          message_content = "Hi I'm Ernest! What's your name?"
        }
        submitFirstAIMessage(aiState.reviewId, message_content)
        return [
          {
            id: `${aiState.reviewId}-0`,
            role: 'assistant',
            display: <BotMessage key={nanoid()} content={message_content} />
          }
        ]
      }
    } else {
      return
    }
  },
  // runs whenever the AI state is updated
  onSetAIState: async ({ state }) => {
    'use server'
    console.log('onSetAIState')
  }
})

export const convertSateAI2UI = (aiState: Review) => {
  return aiState.messages
    .filter(message => message.role !== 'system')
    .map((message, index) => ({
      id: `${aiState.reviewId}-${index}`,
      role: message.role,
      display:
        message.role === 'tool' ? (
          message.content.map(tool => {
            console.log('tool in messages: ', tool)
            // TODO: Implement ToolMessage component
            return <BotMessage key={nanoid()} content={message.content} />
          })
        ) : message.role === 'user' ? (
          <UserMessage>{message.content as string}</UserMessage>
        ) : message.role === 'assistant' &&
          typeof message.content === 'string' ? (
          <BotMessage content={message.content} />
        ) : null
    }))
}
