import { formatCurrency, formatDate } from '../utils/format'

export function PortfolioTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-navy-800 border border-navy-600 rounded-lg px-3 py-2 shadow-xl text-xs">
      <p className="text-slate-400 mb-1">{formatDate(label)}</p>
      <p className="font-mono font-semibold text-emerald-400">
        {formatCurrency(payload[0]?.value)}
      </p>
    </div>
  )
}

export function PriceTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-navy-800 border border-navy-600 rounded-lg px-3 py-2 shadow-xl text-xs">
      <p className="text-slate-400 mb-1">{label}</p>
      <p className="font-mono font-semibold text-slate-200">
        {formatCurrency(payload[0]?.value)}
      </p>
    </div>
  )
}
