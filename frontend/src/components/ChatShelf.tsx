import { CSSProperties, useEffect, useRef } from 'react'
import { useChatResults } from '../chatResults'
import ProductCard from './ProductCard'

// The "neat" part: whatever the chat agent finds drops onto the page as real product cards.
export default function ChatShelf() {
  const { results, clear } = useChatResults()
  const ref = useRef<HTMLElement>(null)

  useEffect(() => {
    if (results) ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [results?.id])

  if (!results) return null

  return (
    <section key={results.id} ref={ref} className="shelf" aria-labelledby="shelf-title" aria-live="polite">
      <div className="shelf-inner">
        <div className="shelf-head">
          <div>
            <p className="shelf-eyebrow">
              <span className="shelf-dot" aria-hidden="true" /> The clerk pulled these from the back room · “{results.query}”
            </p>
            <h2 id="shelf-title">{results.title}</h2>
          </div>
          <div className="shelf-meta">
            <span>
              {results.products.length} match{results.products.length === 1 ? '' : 'es'}
            </span>
            <button className="shelf-close" onClick={clear} aria-label="Hide chat results">
              ×
            </button>
          </div>
        </div>
        <div className="shelf-grid">
          {results.products.map((p, i) => (
            <div key={p.product_id} className="shelf-item" style={{ '--i': i } as CSSProperties}>
              <ProductCard product={p} />
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
