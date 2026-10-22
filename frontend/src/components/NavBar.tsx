import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

const LINKS = [
  { to: '/', label: 'Home' },
  { to: '/products', label: 'Products' },
  { to: '/about', label: 'About Us' },
]

export default function NavBar() {
  const [open, setOpen] = useState(false)
  const close = () => setOpen(false)
  const { user, checking, logout } = useAuth()
  const navigate = useNavigate()
  return (
    <header className="header">
      <div className="announce">
        <span>Officially licensed Yale merchandise</span>
        <span className="announce-dot" aria-hidden="true">✦</span>
        <span>57 Broadway, New Haven</span>
        <span className="announce-dot" aria-hidden="true">✦</span>
        <span>Serving Elis since 1975</span>
      </div>
      <nav className="nav" aria-label="Main">
        <Link to="/" className="brand" onClick={close} aria-label="Campus Customs home">
          <span className="brand-mark" aria-hidden="true">
            <span className="brand-cc">CC</span>
            <span className="brand-est">EST. 1975</span>
          </span>
          <span className="brand-text">
            <span className="brand-name">Campus Customs</span>
            <small>Yale Bulldog Blue · 57 Broadway</small>
          </span>
        </Link>
        <button className="menu-toggle" aria-expanded={open} aria-controls="nav-links" onClick={() => setOpen(o => !o)}>
          {open ? 'Close' : 'Menu'}
        </button>
        <ul id="nav-links" className={`nav-links ${open ? 'open' : ''}`}>
          {LINKS.map(l => (
            <li key={l.to}>
              <NavLink to={l.to} end={l.to === '/'} onClick={close}>
                {l.label}
              </NavLink>
            </li>
          ))}
          {checking ? null : user ? (
            <>
              <li className="nav-user">Hi, {user.first_name || user.name}</li>
              <li>
                <button
                  className="btn btn-small btn-outline"
                  onClick={async () => {
                    close()
                    await logout()
                    navigate('/')
                  }}
                >
                  Log out
                </button>
              </li>
            </>
          ) : (
            <>
              <li>
                <NavLink to="/login" onClick={close}>
                  Login
                </NavLink>
              </li>
              <li>
                <NavLink to="/create-account" className="btn btn-small" onClick={close}>
                  Create Account
                </NavLink>
              </li>
            </>
          )}
        </ul>
      </nav>
      <div className="awning" aria-hidden="true" />
    </header>
  )
}
