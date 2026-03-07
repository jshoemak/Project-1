import { BrowserRouter, Routes, Route } from 'react-router-dom'
import NavBar from './components/NavBar'
import HomePage from './pages/HomePage'
import SignalsPage from './pages/SignalsPage'
import SourcesPage from './pages/SourcesPage'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-navy-950">
        <NavBar />
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/signals" element={<SignalsPage />} />
            <Route path="/sources" element={<SourcesPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
