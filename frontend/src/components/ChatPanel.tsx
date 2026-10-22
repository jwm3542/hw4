import { FormEvent, useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { fetchChatHistory, sendChat } from '../api'
import { useAuth } from '../auth'
import { useChatResults } from '../chatResults'
import type { ChatMessage } from '../types'
import Markdown from './Markdown'

const GREETING: ChatMessage = {
  role: 'assistant',
  content: "Hey there, welcome to the shop! I'm the clerk behind the counter. Ask me about hoodies, sizes, prices, or what's in stock.",
}

export default function ChatPanel() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING])
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [draft, setDraft] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const listRef = useRef<HTMLDivElement>(null)
  const { show } = useChatResults()
  const { user, checking } = useAuth()
  const location = useLocation()
  const [historyNote, setHistoryNote] = useState('')

  // When the shopper changes (page load, login, logout), start fresh and reload their saved chat if logged in.
  useEffect(() => {
    if (checking) return
    setConversationId(null)
    setError('')
    setHistoryNote('')
    if (!user) {
      setMessages([GREETING])
      return
    }
    const hello: ChatMessage = { role: 'assistant', content: `Welcome back, ${user.first_name || user.name}! What can I find for you?` }
    setMessages([hello])
    fetchChatHistory()
      .then(saved => {
        if (saved.length === 0) return
        setMessages([
          ...saved.map(m => ({
            role: m.role as ChatMessage['role'],
            content: m.content,
            products: m.products,
            resultsTitle: 'From your earlier chat',
            query: '',
          })),
          hello,
        ])
        setHistoryNote(`Loaded ${saved.length} saved messages`)
      })
      .catch(() => setHistoryNote('Couldn’t load your saved chat.'))
  }, [user?.id, checking])

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight })
  }, [messages, busy, open])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    const text = draft.trim()
    if (!text || busy) return
    setMessages(m => [...m, { role: 'user', content: text }])
    setDraft('')
    setBusy(true)
    setError('')
    try {
      // Page context: the agent knows which product "this" means when the shopper is on a product page.
      const productId = location.pathname.match(/^\/products\/([^/]+)$/)?.[1] ?? null
      const res = await sendChat(text, conversationId, { path: location.pathname, product_id: productId })
      setConversationId(res.conversation_id)
      const title = res.results_title ?? 'Picked for you'
      setMessages(m => [
        ...m,
        { role: 'assistant', content: res.reply, products: res.products, resultsTitle: title, query: text },
      ])
      // The API contract: structured matches from the agent go straight onto the page as product cards.
      if (res.products.length > 0) show({ title, query: text, products: res.products })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't reach the shop assistant.")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="chat">
      {open && (
        <section className="chat-panel" aria-label="Shopping assistant chat">
          <header className="chat-head">
            <span>
              Ask the Clerk
              <small className="chat-sub">
                {user ? `Signed in as ${user.email} · chat is saved` : 'Guest · log in to save your chat'}
              </small>
            </span>
            <button className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">
              ×
            </button>
          </header>
          <div className="chat-list" ref={listRef} aria-live="polite">
            {historyNote && <p className="chat-note">{historyNote}</p>}
            {messages.map((m, i) => (
              <div key={i} className={`msg msg-${m.role}`}>
                <div className={`bubble bubble-${m.role}`}>
                  {m.role === 'assistant' ? <Markdown text={m.content} /> : m.content}
                </div>
                {m.products && m.products.length > 0 && (
                  <button
                    className="chat-shown"
                    onClick={() => show({ title: m.resultsTitle ?? 'Picked for you', query: m.query ?? '', products: m.products! })}
                  >
                    ✨ {m.products.length} match{m.products.length === 1 ? '' : 'es'} on the page · show again
                  </button>
                )}
              </div>
            ))}
            {busy && (
              <div className="bubble bubble-assistant typing" role="status">
                <span className="spinner" aria-hidden="true" /> Thinking…
              </div>
            )}
            {error && (
              <div className="chat-error" role="alert">
                {error}
              </div>
            )}
          </div>
          <form className="chat-form" onSubmit={onSubmit}>
            <label htmlFor="chat-input" className="sr-only">
              Message
            </label>
            <input
              id="chat-input"
              value={draft}
              onChange={e => setDraft(e.target.value)}
              placeholder="Ask about merch…"
              maxLength={2000}
              autoComplete="off"
            />
            <button className="btn" disabled={busy || !draft.trim()}>
              Send
            </button>
          </form>
        </section>
      )}
      <button
        className="chat-fab"
        onClick={() => setOpen(o => !o)}
        aria-expanded={open}
        aria-label={open ? 'Close chat' : 'Open chat'}
      >
        {open ? '×' : <span className="bell" aria-hidden="true">🛎️</span>}
      </button>
    </div>
  )
}
