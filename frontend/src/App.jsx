import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import NavBar from './components/NavBar'
import HomePage from './pages/HomePage'
import SignalsPage from './pages/SignalsPage'
import SourcesPage from './pages/SourcesPage'
import ProfilePage from './pages/ProfilePage'
import LoginPage from './pages/LoginPage'

function RequireAuth({ children }) {
  const token = localStorage.getItem('ct_token')
  if (!token) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/*"
          element={
            <RequireAuth>
              <div className="min-h-screen bg-navy-950">
                <NavBar />
                <main>
                  <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/signals" element={<SignalsPage />} />
                    <Route path="/sources" element={<SourcesPage />} />
                    <Route path="/profile" element={<ProfilePage />} />
                  </Routes>
                </main>
              </div>
            </RequireAuth>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}
