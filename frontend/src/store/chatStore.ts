import { create } from 'zustand'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  isStreaming?: boolean
}

interface ChatStore {
  messages: Message[]
  emailJson: unknown | null
  isStreaming: boolean
  sendMessage: (text: string) => void
  setEmailJson: (json: unknown) => void
}

// Module-level WebSocket singleton — lives outside Zustand state to avoid
// serialization issues while still being accessible from store actions.
let _ws: WebSocket | null = null
let _pendingAssistantId: string | null = null

export const useChatStore = create<ChatStore>()((set, get) => {
  function handleMessage(raw: string) {
    let msg: { type: string; content?: unknown; tool_name?: string }
    try {
      msg = JSON.parse(raw)
    } catch {
      return
    }

    switch (msg.type) {
      case 'token':
        set((state) => ({
          messages: state.messages.map((m) =>
            m.id === _pendingAssistantId
              ? { ...m, content: m.content + (msg.content as string) }
              : m,
          ),
        }))
        break

      case 'tool_result':
        get().setEmailJson(msg.content)
        break

      case 'done':
        set((state) => ({
          isStreaming: false,
          messages: state.messages.map((m) =>
            m.id === _pendingAssistantId ? { ...m, isStreaming: false } : m,
          ),
        }))
        _pendingAssistantId = null
        break

      case 'error':
        set((state) => ({
          isStreaming: false,
          messages: state.messages.map((m) =>
            m.id === _pendingAssistantId
              ? { ...m, content: `Error: ${msg.content as string}`, isStreaming: false }
              : m,
          ),
        }))
        _pendingAssistantId = null
        break
    }
  }

  function ensureConnected(): Promise<WebSocket> {
    return new Promise((resolve) => {
      if (_ws?.readyState === WebSocket.OPEN) {
        resolve(_ws)
        return
      }
      _ws = new WebSocket('ws://localhost:8000/ws/chat')
      _ws.onmessage = (e) => handleMessage(e.data as string)
      _ws.onerror = () => set({ isStreaming: false })
      _ws.onclose = () => {
        _ws = null
      }
      _ws.onopen = () => resolve(_ws!)
    })
  }

  return {
    messages: [],
    emailJson: null,
    isStreaming: false,

    sendMessage: (text: string) => {
      const userMsg: Message = { id: crypto.randomUUID(), role: 'user', content: text }
      const assistantId = crypto.randomUUID()
      _pendingAssistantId = assistantId

      set((state) => ({
        isStreaming: true,
        messages: [
          ...state.messages,
          userMsg,
          { id: assistantId, role: 'assistant', content: '', isStreaming: true },
        ],
      }))

      ensureConnected().then((ws) => {
        ws.send(JSON.stringify({ message: text }))
      })
    },

    setEmailJson: (json: unknown) => set({ emailJson: json }),
  }
})
