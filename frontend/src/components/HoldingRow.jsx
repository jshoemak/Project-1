import { useState } from 'react'
import { formatCurrency, formatPercent } from '../utils/format'
import { useApi, api } from '../hooks/useApi'
import TickerChart from './TickerChart'

export default function HoldingRow({ holding, onDelete }) {
  const [expanded, setExpanded] = useState(false)
  const { data: price } = useApi(`/ticker/${holding.ticker}/chart?days=2`, [holding.ticker])

  const currentPrice = price?.[price.length - 1]?.close ?? null
  const prevPrice = price?.[price.length - 2]?.close ?? null
  const todayChange = currentPrice && prevPrice ? ((currentPrice - prevPrice) / prevPrice) * 100 : null
  const positionValue = currentPrice ? currentPrice * holding.shares : null
  const pnl = positionValue ? positionValue - holding.shares * holding.avg_cost : null
  const pnlPct = pnl && holding.shares * holding.avg_cost > 0
    ? (pnl / (holding.shares * holding.avg_cost)) * 100
    : null

  const isUp = todayChange !== null ? todayChange >= 0 : null
  const isPnlUp = pnl !== null ? pnl >= 0 : null

  const handleDelete = async (e) => {
    e.stopPropagation()
    if (!confirm(`Remove ${holding.ticker} from portfolio?`)) return
    try {
      await api.del(`/holdings/${holding.id}`)
      onDelete(holding.id)
    } catch (e) {
      alert(e.message)
    }
  }

  return (
    <div className="border border-navy-700 rounded-lg overflow-hidden">
      <div
        className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-navy-700/40 transition-colors"
        onClick={() => setExpanded((x) => !x)}
      >
        {/* Ticker */}
        <div className="w-20">
          <p className="font-mono font-semibold text-slate-100">{holding.ticker}</p>
          <p className="text-xs text-slate-500 truncate">{holding.name || '—'}</p>
        </div>

        {/* Price + today change */}
        <div className="flex-1 min-w-0">
          <p className="font-mono text-slate-200">
            {currentPrice ? formatCurrency(currentPrice) : '—'}
          </p>
          {todayChange !== null && (
            <p className={`text-xs font-mono ${isUp ? 'text-emerald-400' : 'text-coral-400'}`}>
              {formatPercent(todayChange)} today
            </p>
          )}
        </div>

        {/* Position value */}
        <div className="text-right min-w-[100px]">
          <p className="font-mono text-slate-200">
            {positionValue ? formatCurrency(positionValue) : '—'}
          </p>
          <p className="text-xs text-slate-500">{holding.shares} shares</p>
        </div>

        {/* P&L */}
        <div className="text-right min-w-[90px]">
          {pnl !== null ? (
            <>
              <p className={`font-mono text-sm ${isPnlUp ? 'text-emerald-400' : 'text-coral-400'}`}>
                {formatCurrency(pnl, true)}
              </p>
              <p className={`text-xs font-mono ${isPnlUp ? 'text-emerald-400' : 'text-coral-400'}`}>
                {formatPercent(pnlPct)}
              </p>
            </>
          ) : (
            <p className="text-slate-600 text-sm">—</p>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 ml-2">
          <span className="text-slate-600 text-xs">{expanded ? '▲' : '▼'}</span>
          <button
            onClick={handleDelete}
            className="text-slate-600 hover:text-coral-400 text-xs px-1 transition-colors"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="bg-navy-900 border-t border-navy-700 p-4">
          <div className="grid grid-cols-2 gap-4 mb-3">
            <div>
              <p className="section-label">90-Day Price Chart</p>
              <TickerChart ticker={holding.ticker} days={90} height={140} />
            </div>
            <div>
              <p className="section-label">Position Details</p>
              <div className="space-y-2 text-sm">
                <Row label="Shares" value={holding.shares.toLocaleString()} />
                <Row label="Avg Cost" value={formatCurrency(holding.avg_cost)} />
                <Row label="Current Price" value={currentPrice ? formatCurrency(currentPrice) : '—'} />
                <Row label="Position Value" value={positionValue ? formatCurrency(positionValue) : '—'} />
                <Row
                  label="Total P&L"
                  value={pnl !== null ? formatCurrency(pnl) : '—'}
                  valueClass={isPnlUp ? 'text-emerald-400' : 'text-coral-400'}
                />
                <Row label="Sector" value={holding.sector || '—'} />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function Row({ label, value, valueClass = 'text-slate-200' }) {
  return (
    <div className="flex justify-between">
      <span className="text-slate-500">{label}</span>
      <span className={`font-mono ${valueClass}`}>{value}</span>
    </div>
  )
}
