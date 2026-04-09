import { useRef, useEffect, useState, type KeyboardEvent } from 'react'
import { Button, Textarea, Spinner, ScrollShadow } from '@heroui/react'
import { useChat } from '../api/useChat'

export default function ChatPanel() {
  const { messages, isStreaming, sendMessage } = useChat()
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = () => {
    const text = input.trim()
    if (!text || isStreaming) return
    sendMessage(text)
    setInput('')
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-divider shrink-0">
        <h2 className="font-semibold text-sm">Chat</h2>
        {isStreaming && (
          <div className="flex items-center gap-1.5 ml-1">
            <Spinner size="sm" color="primary" />
            <span className="text-xs text-default-400">thinking...</span>
          </div>
        )}
      </div>

      {/* Message list */}
      <ScrollShadow className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-2 select-none">
            <p className="text-default-400 text-sm">Ask the agent to create an email template</p>
            <p className="text-default-300 text-xs">
              Try: "Create a bold product launch email"
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={[
                    'max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed',
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground rounded-br-sm'
                      : 'bg-default-100 text-foreground rounded-bl-sm',
                  ].join(' ')}
                >
                  {msg.content ? (
                    <span className="whitespace-pre-wrap">{msg.content}</span>
                  ) : msg.isStreaming ? (
                    <span className="flex gap-1 items-center h-4">
                      <span className="w-1.5 h-1.5 rounded-full bg-current animate-bounce [animation-delay:0ms]" />
                      <span className="w-1.5 h-1.5 rounded-full bg-current animate-bounce [animation-delay:150ms]" />
                      <span className="w-1.5 h-1.5 rounded-full bg-current animate-bounce [animation-delay:300ms]" />
                    </span>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        )}
        <div ref={bottomRef} />
      </ScrollShadow>

      {/* Input */}
      <div className="p-4 border-t border-divider shrink-0">
        <div className="flex gap-2 items-end">
          <Textarea
            value={input}
            onValueChange={setInput}
            onKeyDown={handleKeyDown}
            placeholder="Message the agent... (Enter to send, Shift+Enter for newline)"
            minRows={1}
            maxRows={5}
            className="flex-1"
            isDisabled={isStreaming}
            variant="bordered"
            size="sm"
          />
          <Button
            color="primary"
            onPress={handleSend}
            isDisabled={!input.trim() || isStreaming}
            isIconOnly
            size="sm"
            className="shrink-0 mb-0.5"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="w-4 h-4"
            >
              <path d="M3.105 2.289a.75.75 0 00-.826.95l1.414 4.925A1.5 1.5 0 005.135 9.25h6.115a.75.75 0 010 1.5H5.135a1.5 1.5 0 00-1.442 1.086l-1.414 4.926a.75.75 0 00.826.95 28.896 28.896 0 0015.293-7.154.75.75 0 000-1.115A28.897 28.897 0 003.105 2.289z" />
            </svg>
          </Button>
        </div>
      </div>
    </div>
  )
}
