import { useChatStore } from '../store/chatStore'

/**
 * Thin hook over the chat store. Components should use this rather than
 * importing useChatStore directly so we have one place to add connection
 * lifecycle logic (e.g. reconnect on focus, presence indicators) later.
 */
export function useChat() {
  const messages = useChatStore((s) => s.messages)
  const emailJson = useChatStore((s) => s.emailJson)
  const isStreaming = useChatStore((s) => s.isStreaming)
  const sendMessage = useChatStore((s) => s.sendMessage)

  return { messages, emailJson, isStreaming, sendMessage }
}
