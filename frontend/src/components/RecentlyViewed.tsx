import { useState } from 'react'
import { Link } from 'react-router-dom'
import { money } from '../api'
import { clearRecent, getRecent } from '../recentlyViewed'

// Horizontal strip of products this shopper opened recently (stored in their browser).
export default function RecentlyViewed({ excludeId }: { excludeId?: string }) {
  const [items, setItems] = useState(() => getRecent().filter(i => i.product_id !== excludeId))
  if (items.length === 0) return null
  return (
    <section className="recent" aria-labelledby="recent-title">
      <div className="section-head">
        <h2 id="recent-title">Recently viewed</h2>
        <button
          className="link-btn"
          onClick={() => {
            clearRecent()
            setItems([])
          }}
        >
          Clear
        </button>
      </div>
      <ul className="recent-strip">
        {items.map(i => (
          <li key={i.product_id}>
            <Link to={`/products/${i.product_id}`} className="recent-item">
              <img src={i.image_url} alt="" loading="lazy" />
              <span className="recent-name">{i.name}</span>
              <span className="recent-price">{money(i.price)}</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
