import { createContext, ReactNode, useContext, useState } from 'react'
import type { Product } from './types'

// Products the chat agent just found. The chat panel writes here; the on-page shelf reads from here.
export interface ChatResults {
  title: string
  query: string
  products: Product[]
  id: number // bumps on every new result set so the shelf re-animates
}

interface ChatResultsState {
  results: ChatResults | null
  show: (r: Omit<ChatResults, 'id'>) => void
  clear: () => void
}

const Ctx = createContext<ChatResultsState | null>(null)

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [results, setResults] = useState<ChatResults | null>(null)
  const show = (r: Omit<ChatResults, 'id'>) => setResults({ ...r, id: Date.now() })
  return <Ctx.Provider value={{ results, show, clear: () => setResults(null) }}>{children}</Ctx.Provider>
}

export function useChatResults() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useChatResults must be used inside ChatResultsProvider')
  return ctx
}
