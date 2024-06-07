

interface ChatLayoutProps {
  children: React.ReactNode
}

export default async function ReviewsLayout({ children }: ChatLayoutProps) {
  return (
    <div className="relative flex h-[calc(100vh_-_theme(spacing.16))] overflow-y-auto p-3">
      {children}
    </div>
  )
}
