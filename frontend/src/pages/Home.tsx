import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchProducts } from '../api'
import { HOME } from '../content'
import ProductCard from '../components/ProductCard'
import RecentlyViewed from '../components/RecentlyViewed'
import { ErrorBox, Loading } from '../components/Status'
import type { Product } from '../types'

export default function Home() {
  const [featured, setFeatured] = useState<Product[] | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchProducts()
      .then(all => setFeatured(all.filter(p => p.total_stock > 0).slice(0, 4)))
      .catch(() => setError('Could not load featured gear right now.'))
  }, [])

  return (
    <>
      <section className="hero">
        <div className="hero-sunset" aria-hidden="true" />
        <div className="hero-inner">
          <div className="window">
            <span className="neon" aria-hidden="true">
              Open
            </span>
            <p className="window-arch">Campus Customs · Est. 1975</p>
            <h1>{HOME.heroTitle}</h1>
            <p className="window-copy">{HOME.heroText}</p>
            <Link to="/products" className="btn btn-brass">
              {HOME.heroCta}
            </Link>
            <p className="window-small">Officially licensed · Yale Bulldog Blue · 57 Broadway</p>
          </div>
        </div>
      </section>

      <section className="container tiles" aria-label="What's in the shop">
        {HOME.sections.map((s, i) => (
          <article key={s.title} className={`tile tile-${i}`}>
            <span className="tile-pin" aria-hidden="true" />
            <h2>{s.title}</h2>
            <p>{s.text}</p>
          </article>
        ))}
      </section>

      <section className="container">
        <div className="section-head">
          <h2 className="rack-title">
            Fresh off the rack <span className="rack-sub">hand-picked by the clerk</span>
          </h2>
          <Link to="/products">Shop all →</Link>
        </div>
        {error ? (
          <ErrorBox message={error} />
        ) : featured ? (
          <div className="grid">
            {featured.map(p => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
        ) : (
          <Loading label="Loading featured gear…" />
        )}
        <p className="nudge">{HOME.chatNudge}</p>
        <RecentlyViewed />
      </section>
    </>
  )
}
