import { NavLink } from 'react-router-dom'
import { useApi } from '../hooks/useApi'

export default function NavBar() {
  const { data: signals } = useApi('/signals?min_score=80')
  const highCount = signals?.length ?? 0

  return (
    <nav className="sticky top-0 z-50 bg-navy-900 border-b border-navy-700 px-4 h-14 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <span className="text-accent font-bold text-lg tracking-tight font-mono">
          &#9641; CONGRESS TRACKER
        </span>
      </div>

      <div className="flex items-center gap-1">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              isActive
                ? 'bg-navy-700 text-slate-100'
                : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800'
            }`
          }
        >
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
        <NavLink
          to="/sources"
          className={({ isActive }) =>
            `px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              isActive
                ? 'bg-navy-700 text-slate-100'
                : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800'
            }`
          }
        >
          Data Sources
        </NavLink>
      </div>
    </nav>
  )
}
