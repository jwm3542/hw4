import { ChangeEvent, FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { signup } from '../api'
import { useAuth } from '../auth'

const EMPTY = { first_name: '', last_name: '', email: '', password: '', confirm_password: '' }

export default function CreateAccount() {
  const { setUser } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const update = (field: keyof typeof EMPTY) => (e: ChangeEvent<HTMLInputElement>) =>
    setForm(f => ({ ...f, [field]: e.target.value }))

  const mismatch = form.confirm_password !== '' && form.password !== form.confirm_password

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (form.password !== form.confirm_password) return setError('Passwords don’t match.')
    if (form.password.length < 8) return setError('Password must be at least 8 characters.')
    setBusy(true)
    setError('')
    try {
      setUser(await signup(form))
      navigate('/products')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create the account.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="container auth">
      <h1>Create an account</h1>
      <form onSubmit={onSubmit} className="form">
        <div className="form-row">
          <label>
            First name
            <input autoComplete="given-name" required value={form.first_name} onChange={update('first_name')} />
          </label>
          <label>
            Last name
            <input autoComplete="family-name" required value={form.last_name} onChange={update('last_name')} />
          </label>
        </div>
        <label>
          Email
          <input type="email" autoComplete="email" required value={form.email} onChange={update('email')} />
        </label>
        <label>
          Password <span className="hint">(8+ characters)</span>
          <input
            type="password"
            autoComplete="new-password"
            minLength={8}
            required
            value={form.password}
            onChange={update('password')}
          />
        </label>
        <label>
          Confirm password
          <input
            type="password"
            autoComplete="new-password"
            required
            value={form.confirm_password}
            onChange={update('confirm_password')}
            aria-invalid={mismatch}
            aria-describedby="pw-match"
          />
        </label>
        <p id="pw-match" className={mismatch ? 'field-error' : 'sr-only'} aria-live="polite">
          {mismatch ? 'Passwords don’t match yet.' : ''}
        </p>
        {error && (
          <p className="status status-error" role="alert">
            {error}
          </p>
        )}
        <button className="btn" disabled={busy}>
          {busy ? 'Creating account…' : 'Create account'}
        </button>
      </form>
      <p>
        Already have one? <Link to="/login">Log in</Link>
      </p>
    </section>
  )
}
