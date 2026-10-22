import { createContext, ReactNode, useContext, useEffect, useState } from 'react'
import * as api from './api'
import type { User } from './types'

interface AuthState {
  user: User | null
  checking: boolean
  setUser: (u: User | null) => void
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

// The session itself lives in an HttpOnly cookie the browser JS can't read; we only keep the public user here.
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    api
      .fetchMe()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setChecking(false))
  }, [])

  async function logout() {
    await api.logout().catch(() => undefined)
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, checking, setUser, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
