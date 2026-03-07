import { useState } from 'react'
import SignalBadge from './SignalBadge'
import ResearchPanel from './ResearchPanel'
import { formatCurrency } from '../utils/format'
import { useApi } from '../hooks/useApi'

export default function SignalCard({ signal }) {
  const [expanded, setExpanded] = useState(false)
  const { data: price } = useApi(`/ticker/${signal.ticker}/chart?days=2`, [signal.ticker])

  let members = []
  try { members = JSON.parse(signal.contributing_members || '[]') } catch {}

  const currentPrice = price?.[price.length - 1]?.close ?? null
  const isBuy = signal.trade_direction === 'BUY'
  const isBipartisan = signal.bipartisan >= 70

  return (
    <div className={`border rounded-lg overflow-hidden transition-all ${
      expanded ? 'border-accent' : 'border-navy-700 hover:border-navy-600'
    }`}>
      <div
        className="flex items-center gap-3 px-4 py-3.5 cursor-pointer bg-navy-800 hover:bg-navy-700/50 transition-colors"
        onClick={() => setExpanded((x) => !x)}
      >
        {/* Score badge */}
        <SignalBadge score={signal.conviction_score} />

        {/* Ticker + metadata */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono font-bold text-slate-100">{signal.ticker}</span>
            <span className={isBuy ? 'badge-buy' : 'badge-sell'}>
              {signal.trade_direction}
            </span>
            {isBipartisan && (
              <span className="text-xs bg-purple-900 text-purple-300 px-1.5 py-0.5 rounded">
                Bipartisan
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-0.5 truncate">
            {members.slice(0, 3).join(', ')}{members.length > 3 ? ` +${members.length - 3}` : ''}
          </p>
        </div>

        {/* Price */}
        <div className="text-right">
          <p className="font-mono text-slate-300 text-sm">
            {currentPrice ? formatCurrency(currentPrice) : '—'}
          </p>
          <p className="text-xs text-slate-600">{members.length} member{members.length !== 1 ? 's' : ''}</p>
        </div>

        <span className="text-slate-600 text-xs ml-1">{expanded ? '▲' : '▼'}</span>
      </div>

      {expanded && <ResearchPanel ticker={signal.ticker} />}
    </div>
  )
}
