import { NavLink, useNavigate } from 'react-router-dom'
import { useApi } from '../hooks/useApi'

export default function NavBar() {
  const { data: signals } = useApi('/signals?min_score=80')
  const highCount = signals?.length ?? 0
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('ct_token')
    navigate('/login')
  }

  const navCls = ({ isActive }) =>
    `px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
      isActive
        ? 'bg-navy-700 text-slate-100'
        : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800'
    }`

  return (
    <nav className="sticky top-0 z-50 bg-navy-900 border-b border-navy-700 px-4 h-14 flex items-center">
      {/* Logo — left */}
      <div className="w-48 flex items-center">
        <span className="text-accent font-bold text-lg tracking-tight font-mono">
          &#9641; CONGRESS TRACKER
        </span>
      </div>

      {/* Primary nav — centered */}
      <div className="flex-1 flex items-center justify-center gap-1">
        <NavLink to="/" end className={navCls}>
          Portfolio
        </NavLink>
        <NavLink
          to="/signals"
          className={({ isActive }) =>
            `relative px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              isActive
                ? 'bg-navy-700 text-slate-100'
                : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800'
            }`
          }
        >
          Signals
          {highCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 bg-amber-500 text-navy-950 text-xs font-bold rounded-full w-4 h-4 flex items-center justify-center leading-none">
              {highCount}
            </span>
          )}
        </NavLink>
      </div>

      {/* Right-side nav */}
      <div className="w-48 flex items-center justify-end gap-1">
        <NavLink to="/sources" className={navCls}>
          Data Sources
        </NavLink>
        <NavLink to="/profile" className={navCls}>
          Profile
        </NavLink>
        {localStorage.getItem('ct_token') && (
          <button
            onClick={handleLogout}
            className="px-3 py-1.5 rounded-md text-sm font-medium text-slate-500 hover:text-slate-300 hover:bg-navy-800 transition-colors"
          >
            Sign out
          </button>
        )}
      </div>
    </nav>
  )
}
