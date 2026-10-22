export interface SizeStock {
  size: string
  quantity: number
}

export interface Product {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  search_tags: string[]
  price: number
  image_url: string
  total_stock: number
  sizes_in_stock?: string[]
  inventory?: SizeStock[]
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  products?: Product[]
  resultsTitle?: string
  query?: string
}

export interface User {
  id: number
  first_name: string | null
  last_name: string | null
  name: string
  email: string
}
