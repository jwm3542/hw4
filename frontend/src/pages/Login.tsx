import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../api'
import { useAuth } from '../auth'

export default function Login() {
  const { setUser } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      setUser(await login(email, password))
      navigate('/products')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed.')
      setPassword('')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="container auth">
      <h1>Log in</h1>
      <form onSubmit={onSubmit} className="form">
        <label>
          Email
          <input type="email" autoComplete="email" required value={email} onChange={e => setEmail(e.target.value)} />
        </label>
        <label>
          Password
          <input
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={e => setPassword(e.target.value)}
          />
        </label>
        {error && (
          <p className="status status-error" role="alert">
            {error}
          </p>
        )}
        <button className="btn" disabled={busy}>
          {busy ? 'Logging in…' : 'Log in'}
        </button>
      </form>
      <p>
        New here? <Link to="/create-account">Create an account</Link>
      </p>
    </section>
  )
}
