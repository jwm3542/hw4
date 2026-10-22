import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, fetchSimilar, money } from '../api'
import ProductCard from '../components/ProductCard'
import RecentlyViewed from '../components/RecentlyViewed'
import SizeGuide from '../components/SizeGuide'
import { addRecent } from '../recentlyViewed'
import { ErrorBox, Loading } from '../components/Status'
import type { Product } from '../types'

// At or below this many units, a size gets an "N left" badge.
const LOW_STOCK = 3

export default function ProductDetail() {
  const { id = '' } = useParams()
  const [product, setProduct] = useState<Product | null>(null)
  const [error, setError] = useState('')
  const [size, setSize] = useState('')
  const topRef = useRef<HTMLElement>(null)
  const [similar, setSimilar] = useState<Product[] | null>(null)

  useEffect(() => {
    setProduct(null)
    setError('')
    setSize('')
    setSimilar(null)
    fetchSimilar(id)
      .then(setSimilar)
      .catch(() => setSimilar([]))
    fetchProduct(id)
      .then(p => {
        setProduct(p)
        addRecent(p)
        // If the chat shelf sits above us, jump past it so the item opens in view.
        requestAnimationFrame(() => topRef.current?.scrollIntoView({ block: 'start' }))
      })
      .catch(e => setError(e.message === 'Not found' ? 'We couldn’t find that product.' : 'Could not load this product.'))
  }, [id])

  if (error)
    return (
      <section className="container">
        <ErrorBox message={error} />
        <Link to="/products">← Back to products</Link>
      </section>
    )
  if (!product)
    return (
      <section className="container">
        <Loading label="Loading product…" />
      </section>
    )

  const chosen = product.inventory?.find(s => s.size === size)

  return (
    <section className="container detail-page" ref={topRef}>
      <Link to="/products" className="back">
        ← All products
      </Link>
      <div className="detail">
        <div className="detail-img">
          <img src={product.image_url} alt={product.name} />
        </div>
        <div className="detail-info">
          <p className="eyebrow">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <p className="price price-lg">{money(product.price)}</p>
          <p>{product.description}</p>

          {product.colors.length > 0 && (
            <p>
              <strong>Colors:</strong> {product.colors.join(', ')}
            </p>
          )}

          <fieldset className="sizes">
            <legend>
              Size <SizeGuide />
            </legend>
            {product.inventory?.map(s => (
              <span key={s.size} className="size-wrap">
                <button
                  type="button"
                  className={`size ${size === s.size ? 'selected' : ''}`}
                  disabled={s.quantity === 0}
                  aria-pressed={size === s.size}
                  onClick={() => setSize(s.size)}
                  aria-label={`${s.size}, ${s.quantity === 0 ? 'sold out' : `${s.quantity} in stock`}`}
                >
                  {s.size}
                </button>
                {s.quantity === 0 ? (
                  <span className="size-tag size-tag-out">Sold out</span>
                ) : s.quantity <= LOW_STOCK ? (
                  <span className="size-tag size-tag-low">{s.quantity} left</span>
                ) : null}
              </span>
            ))}
          </fieldset>

          <p className={`stock ${chosen && chosen.quantity <= LOW_STOCK ? 'stock-low' : ''}`} aria-live="polite">
            {chosen
              ? chosen.quantity <= LOW_STOCK
                ? `Hurry, only ${chosen.quantity} left in size ${chosen.size}!`
                : `${chosen.quantity} in stock in size ${chosen.size}`
              : product.total_stock > 0
                ? `${product.total_stock} in stock across all sizes. Pick a size to check it.`
                : 'Sold out in every size.'}
          </p>

          <table className="stock-table">
            <caption className="sr-only">Stock by size</caption>
            <thead>
              <tr>
                <th scope="col">Size</th>
                <th scope="col">In stock</th>
              </tr>
            </thead>
            <tbody>
              {product.inventory?.map(s => (
                <tr key={s.size} className={s.quantity === 0 ? 'out' : ''}>
                  <td>{s.size}</td>
                  <td>{s.quantity === 0 ? 'Sold out' : s.quantity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <section className="also" aria-labelledby="also-title">
        <h2 id="also-title">You may also like</h2>
        <p className="muted">Similar styles that are in stock right now.</p>
        {similar === null ? (
          <Loading label="Finding similar items…" />
        ) : similar.length === 0 ? (
          <p className="muted">No similar items in stock right now.</p>
        ) : (
          <div className="grid">
            {similar.map(p => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
        )}
      </section>

      <RecentlyViewed key={product.product_id} excludeId={product.product_id} />
    </section>
  )
}
