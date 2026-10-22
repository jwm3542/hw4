import { Link } from 'react-router-dom'
import { money } from '../api'
import type { Product } from '../types'

// Honest urgency: badges come straight from inventory counts in the DB.
function StockBadge({ product }: { product: Product }) {
  const inStock = product.sizes_in_stock
  if (product.total_stock === 0) return <span className="badge">Sold out</span>
  if (product.total_stock <= 12) return <span className="badge badge-low">Only {product.total_stock} left</span>
  if (inStock && inStock.length <= 3) return <span className="badge badge-limited">Only {inStock.length} sizes left</span>
  return null
}

export default function ProductCard({ product }: { product: Product }) {
  return (
    <Link to={`/products/${product.product_id}`} className="card">
      <div className="card-img">
        <img src={product.image_url} alt={product.name} loading="lazy" />
        <StockBadge product={product} />
      </div>
      <div className="card-body">
        <h3>{product.name}</h3>
        <p className="card-desc">{product.description}</p>
        <p className="price hang-tag">
          <span className="sr-only">Price: </span>
          {money(product.price)}
        </p>
        {product.sizes_in_stock && product.sizes_in_stock.length > 0 && product.sizes_in_stock.length < 6 && (
          <p className="card-sizes">In stock: {product.sizes_in_stock.join(' · ')}</p>
        )}
      </div>
    </Link>
  )
}
