import type { Product } from './types'

// Recently viewed products, kept in this browser only (localStorage), newest first.
const KEY = 'cc_recently_viewed'
const MAX = 8

export type RecentItem = Pick<Product, 'product_id' | 'name' | 'price' | 'image_url'>

export function getRecent(): RecentItem[] {
  try {
    const items = JSON.parse(localStorage.getItem(KEY) ?? '[]')
    return Array.isArray(items) ? items.filter(i => typeof i?.product_id === 'string') : []
  } catch {
    return []
  }
}

export function addRecent(p: Product) {
  const item: RecentItem = { product_id: p.product_id, name: p.name, price: p.price, image_url: p.image_url }
  const next = [item, ...getRecent().filter(i => i.product_id !== p.product_id)].slice(0, MAX)
  localStorage.setItem(KEY, JSON.stringify(next))
}

export function clearRecent() {
  localStorage.removeItem(KEY)
}
