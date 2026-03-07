/** Currency formatter — e.g. formatCurrency(1234567) → "$1.23M" */
export function formatCurrency(value, compact = false) {
  if (value == null || isNaN(value)) return '—'
  if (compact) {
    if (Math.abs(value) >= 1e12) return `$${(value / 1e12).toFixed(2)}T`
    if (Math.abs(value) >= 1e9) return `$${(value / 1e9).toFixed(2)}B`
    if (Math.abs(value) >= 1e6) return `$${(value / 1e6).toFixed(2)}M`
    if (Math.abs(value) >= 1e3) return `$${(value / 1e3).toFixed(1)}K`
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

/** Percent formatter — e.g. formatPercent(12.34) → "+12.34%" */
export function formatPercent(value, showSign = true) {
  if (value == null || isNaN(value)) return '—'
  const sign = showSign && value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

/** Format a date string — e.g. "2024-11-15" → "Nov 15, 2024" */
export function formatDate(dateStr) {
  if (!dateStr) return '—'
  try {
    const d = new Date(dateStr + 'T00:00:00')
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}

/** Short date — "Nov 15" */
export function formatDateShort(dateStr) {
  if (!dateStr) return '—'
  try {
    const d = new Date(dateStr + 'T00:00:00')
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}

/** Format amount range — e.g. "$50K – $100K" */
export function formatAmountRange(low, high) {
  if (!low && !high) return '—'
  const fmt = (v) => {
    if (!v) return '?'
    if (v >= 1e9) return `$${(v / 1e9).toFixed(1)}B`
    if (v >= 1e6) return `$${(v / 1e6).toFixed(1)}M`
    if (v >= 1e3) return `$${(v / 1e3).toFixed(0)}K`
    return `$${v}`
  }
  if (!high || low === high) return fmt(low)
  return `${fmt(low)} – ${fmt(high)}`
}

/** Score to color class */
export function scoreColor(score) {
  if (score >= 80) return 'text-amber-400'
  if (score >= 60) return 'text-blue-400'
  if (score >= 40) return 'text-slate-300'
  return 'text-slate-500'
}

/** Score to background class */
export function scoreBg(score) {
  if (score >= 80) return 'bg-amber-500'
  if (score >= 60) return 'bg-accent'
  if (score >= 40) return 'bg-slate-600'
  return 'bg-navy-600'
}
