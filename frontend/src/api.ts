import type { Product, User } from './types'

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
  }
}

async function getJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init)
  if (!res.ok) {
    // FastAPI sends { detail: "message" } for errors we raise on purpose.
    const body = await res.json().catch(() => null)
    const detail = typeof body?.detail === 'string' ? body.detail : null
    throw new ApiError(res.status, detail ?? (res.status === 404 ? 'Not found' : `Server error (${res.status})`))
  }
  return res.json() as Promise<T>
}

export const fetchProducts = () => getJson<Product[]>('/api/products')

export const fetchSimilar = (id: string) => getJson<Product[]>(`/api/products/${encodeURIComponent(id)}/similar`)

export const fetchProduct = (id: string) => getJson<Product>(`/api/products/${encodeURIComponent(id)}`)

const postJson = <T,>(url: string, body: unknown) =>
  getJson<T>(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })

export interface ChatResult {
  reply: string
  products: Product[]
  results_title: string | null
  conversation_id: string
  model: string | null
}

export interface PageContext {
  path: string
  product_id: string | null
}

export const sendChat = (message: string, conversationId: string | null, page: PageContext) =>
  postJson<ChatResult>('/api/chat', { message, conversation_id: conversationId, page })

export interface SavedMessage {
  role: string
  content: string
  products: Product[]
  created_at: string
}

export const fetchChatHistory = () => getJson<SavedMessage[]>('/api/chat/history')

export const fetchMe = () => getJson<User>('/api/me')

export const login = (email: string, password: string) => postJson<User>('/api/login', { email, password })

export const signup = (form: {
  first_name: string
  last_name: string
  email: string
  password: string
  confirm_password: string
}) => postJson<User>('/api/signup', form)

export const logout = () => postJson<{ ok: boolean }>('/api/logout', {})

export const money = (n: number) => n.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
