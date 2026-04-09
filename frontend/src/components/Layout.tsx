import ChatPanel from './ChatPanel'
import JsonPreviewPanel from './JsonPreviewPanel'

export default function Layout() {
  return (
    <div className="flex h-dvh overflow-hidden bg-background text-foreground">
      <div className="flex flex-col w-1/2 min-w-0 border-r border-divider">
        <ChatPanel />
      </div>
      <div className="flex flex-col w-1/2 min-w-0">
        <JsonPreviewPanel />
      </div>
    </div>
  )
}
