import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <section className="container">
      <h1>Page not found</h1>
      <p>
        That page wandered off campus. <Link to="/">Head home</Link>.
      </p>
    </section>
  )
}
