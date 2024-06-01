import { clearChats, getReviewsByUser } from '@/app/actions'
import { ClearHistory } from '@/components/clear-history'
import { SidebarItems } from '@/components/sidebar-items'
import { ThemeToggle } from '@/components/theme-toggle'
import { cache } from 'react'
import { auth } from '@/auth'



const loadChats = cache(async (userId?: string) => {
  // console.log("calling loadChats (not using cache) ")
  const result = await getReviewsByUser(userId)

  return result
})

export async function SidebarList() {
  const session = await auth()
  let chats = []

  if (!session?.user?.id) {
    return null
  } else {
    // console.log('session.user.id: ', session.user.id)
    chats = await loadChats(session?.user?.id)
    // console.log("loaded chats: ", chats?.length);
  }
    

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <div className="flex-1 overflow-auto">
        {chats?.length ? (
          <div className="space-y-2 px-2">
            <SidebarItems chats={chats} />
          </div>
        ) : (
          <div className="p-8 text-center">
            <p className="text-sm text-muted-foreground">No chat history...</p>
          </div>
        )}
      </div>
      <div className="flex items-center justify-between p-4">
        <ThemeToggle />
        <ClearHistory clearChats={clearChats} isEnabled={chats?.length > 0} />
      </div>
    </div>
  )
}
