import { useMemo, type ReactNode } from 'react'
import { useChatStore } from '../store/chatStore'

// ---------------------------------------------------------------------------
// JSON tokenizer - returns React spans, no dangerouslySetInnerHTML
// ---------------------------------------------------------------------------

type TokenType = 'key' | 'string' | 'number' | 'boolean' | 'null' | 'punctuation'

interface Token {
  type: TokenType
  value: string
}

const TOKEN_PATTERN =
  /("(?:\\u[\da-fA-F]{4}|\\[^u]|[^\\"])*"(?:\s*:)?)|\b(true|false|null)\b|(-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)|([{}[\],:])/g

function tokenize(json: string): Token[] {
  const tokens: Token[] = []
  let lastIndex = 0

  for (const match of json.matchAll(TOKEN_PATTERN)) {
    if (match.index! > lastIndex) {
      tokens.push({ type: 'punctuation', value: json.slice(lastIndex, match.index) })
    }
    const [full, strOrKey, boolOrNull, num] = match
    if (strOrKey !== undefined) {
      tokens.push({ type: full.trimEnd().endsWith(':') ? 'key' : 'string', value: full })
    } else if (boolOrNull !== undefined) {
      tokens.push({ type: boolOrNull === 'null' ? 'null' : 'boolean', value: full })
    } else if (num !== undefined) {
      tokens.push({ type: 'number', value: full })
    } else {
      tokens.push({ type: 'punctuation', value: full })
    }
    lastIndex = match.index! + full.length
  }

  if (lastIndex < json.length) {
    tokens.push({ type: 'punctuation', value: json.slice(lastIndex) })
  }
  return tokens
}

const TOKEN_CLASSES: Record<TokenType, string> = {
  key: 'text-sky-300',
  string: 'text-emerald-300',
  number: 'text-amber-300',
  boolean: 'text-violet-300',
  null: 'text-rose-300',
  punctuation: 'text-default-400',
}

function ColorizedJson({ json }: { json: string }): ReactNode {
  const tokens = useMemo(() => tokenize(json), [json])
  return (
    <pre className="p-4 text-xs leading-relaxed font-mono min-h-full">
      {tokens.map((tok, i) => (
        <span key={i} className={TOKEN_CLASSES[tok.type]}>
          {tok.value}
        </span>
      ))}
    </pre>
  )
}

// ---------------------------------------------------------------------------
// Panel
// ---------------------------------------------------------------------------

export default function JsonPreviewPanel() {
  const emailJson = useChatStore((s) => s.emailJson)

  const { jsonStr, charCount } = useMemo(() => {
    if (!emailJson) return { jsonStr: null, charCount: 0 }
    const str = JSON.stringify(emailJson, null, 2)
    return { jsonStr: str, charCount: str.length }
  }, [emailJson])

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-divider shrink-0">
        <h2 className="font-semibold text-sm">BEE JSON</h2>
        {charCount > 0 && (
          <span className="text-xs text-default-400 font-mono tabular-nums">
            {charCount.toLocaleString()} chars
          </span>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto" style={{ background: '#0d1117' }}>
        {jsonStr ? (
          <ColorizedJson json={jsonStr} />
        ) : (
          <div className="flex flex-col items-center justify-center h-full gap-3 text-default-500 select-none">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.2}
              stroke="currentColor"
              className="w-12 h-12 opacity-20"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5"
              />
            </svg>
            <p className="text-sm">Email JSON will appear here</p>
            <p className="text-xs opacity-50">Ask the agent to create or fetch a template</p>
          </div>
        )}
      </div>
    </div>
  )
}
