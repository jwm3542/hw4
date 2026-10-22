import { useEffect, useMemo, useState } from 'react'
import { fetchProducts } from '../api'
import ProductCard from '../components/ProductCard'
import { ErrorBox, Loading } from '../components/Status'
import type { Product } from '../types'

export default function Products() {
  const [products, setProducts] = useState<Product[] | null>(null)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')

  useEffect(() => {
    fetchProducts()
      .then(setProducts)
      .catch(() => setError('Could not load products. Make sure the backend is running.'))
  }, [])

  const shown = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!products || !q) return products
    return products.filter(p =>
      [p.name, p.garment_type, p.description, ...p.colors, ...p.search_tags].join(' ').toLowerCase().includes(q),
    )
  }, [products, query])

  return (
    <section className="container">
      <div className="section-head">
        <h1>All Products</h1>
        <label className="search">
          <span className="sr-only">Search products</span>
          <input
            type="search"
            placeholder="Search hoodies, colleges, colors…"
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
        </label>
      </div>
      {error && <ErrorBox message={error} />}
      {!error && !shown && <Loading label="Loading products…" />}
      {shown && (
        <>
          <p className="muted">
            {shown.length} item{shown.length === 1 ? '' : 's'}
          </p>
          {shown.length === 0 ? (
            <p>Nothing matches “{query}”. Try another word.</p>
          ) : (
            <div className="grid">
              {shown.map(p => (
                <ProductCard key={p.product_id} product={p} />
              ))}
            </div>
          )}
        </>
      )}
    </section>
  )
}
