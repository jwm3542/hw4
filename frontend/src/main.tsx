import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { AuthProvider } from './auth'
import { ChatResultsProvider } from './chatResults'
import { VolumeProvider } from './eleven'
import './styles.css'
import './theme.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <ChatResultsProvider>
          <VolumeProvider>
            <App />
          </VolumeProvider>
        </ChatResultsProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
