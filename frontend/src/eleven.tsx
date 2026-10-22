import { createContext, ReactNode, useContext, useEffect, useState } from 'react'

// "These go to eleven." Volume 1-10 is the normal 1975 shop; 11 flips the whole site into 1984 metal mode.
interface Volume {
  volume: number
  setVolume: (v: number) => void
}

const Ctx = createContext<Volume | null>(null)
const KEY = 'cc_volume'

export function VolumeProvider({ children }: { children: ReactNode }) {
  const [volume, setVolume] = useState(() => Number(localStorage.getItem(KEY)) || 7)
  useEffect(() => {
    localStorage.setItem(KEY, String(volume))
    document.body.classList.toggle('eleven', volume === 11)
  }, [volume])
  return <Ctx.Provider value={{ volume, setVolume }}>{children}</Ctx.Provider>
}

export function useVolume() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useVolume must be used inside VolumeProvider')
  return ctx
}
