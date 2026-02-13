import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { CropProvider } from './context/CropContext'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <CropProvider>
      <App />
    </CropProvider>
  </StrictMode>,
)
