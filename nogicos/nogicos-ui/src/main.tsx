import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'

// Note: StrictMode removed to prevent duplicate WebSocket connections
// In development, StrictMode causes useEffect to run twice, creating 2 WS clients
createRoot(document.getElementById('root')!).render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>,
)
