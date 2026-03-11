import { useState, useEffect } from 'react'
import { api } from '../hooks/useApi'

export default function AddHoldingForm({ onAdded, onCancel, prefill = {} }) {
  const today = new Date().toISOString().split('T')[0]
  const [form, setForm] = useState({
    ticker: prefill.ticker || '',
    name: prefill.name || '',
    shares: '',
    avg_cost: prefill.avg_cost || '',
    sector: prefill.sector || '',
    purchase_date: prefill.purchase_date || today,
  })
  const [loading, setLoading] = useState(false)
  const [lookingUp, setLookingUp] = useState(false)
  const [error, setError] = useState(null)

  // If prefill arrives after mount (e.g. from navigation state)
  useEffect(() => {
    if (prefill.ticker) {
      setForm((f) => ({
        ...f,
        ticker: prefill.ticker || f.ticker,
        name: prefill.name || f.name,
        avg_cost: prefill.avg_cost || f.avg_cost,
        sector: prefill.sector || f.sector,
      }))
    }
  }, [prefill.ticker])

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const lookupTicker = async () => {
    const t = form.ticker.trim().toUpperCase()
    if (!t) return
    setLookingUp(true)
    try {
      const info = await api.get(`/ticker/${t}/info`)
      setForm((f) => ({
        ...f,
        ticker: t,
        name: info.name || f.name,
        sector: info.sector || f.sector,
        avg_cost: f.avg_cost || (info.current_price ? info.current_price.toFixed(2) : ''),
      }))
    } catch {
      // silent — user can still fill manually
    } finally {
      setLookingUp(false)
    }
  }

  const submit = async (e) => {
    e.preventDefault()
    if (!form.ticker || !form.shares || !form.avg_cost) {
      setError('Ticker, shares, and average cost are required.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const holding = await api.post('/holdings', {
        ticker: form.ticker.toUpperCase(),
        name: form.name,
        shares: parseFloat(form.shares),
        avg_cost: parseFloat(form.avg_cost),
        sector: form.sector,
        purchase_date: form.purchase_date,
      })
      onAdded(holding)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={submit} className="card p-4 mt-3">
      <p className="section-label">Add Position</p>
      {error && <p className="text-coral-400 text-sm mb-3">{error}</p>}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Ticker *</label>
          <div className="relative">
            <input
              className="input-field font-mono uppercase w-full"
              placeholder="AAPL"
              value={form.ticker}
              onChange={set('ticker')}
              onBlur={lookupTicker}
            />
            {lookingUp && (
              <span className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 text-xs">
                ⟳
              </span>
            )}
          </div>
        </div>
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Company Name</label>
          <input
            className="input-field"
            placeholder="Auto-filled from ticker"
            value={form.name}
            onChange={set('name')}
          />
        </div>
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Sector</label>
          <input className="input-field" placeholder="Technology" value={form.sector} onChange={set('sector')} />
        </div>
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Shares *</label>
          <input className="input-field font-mono" type="number" min="0" step="0.001" placeholder="10" value={form.shares} onChange={set('shares')} />
        </div>
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Avg Cost *</label>
          <input
            className="input-field font-mono"
            type="number"
            min="0"
            step="0.01"
            placeholder="Auto-filled from ticker"
            value={form.avg_cost}
            onChange={set('avg_cost')}
          />
        </div>
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Purchase Date</label>
          <input className="input-field" type="date" value={form.purchase_date} onChange={set('purchase_date')} />
        </div>
      </div>
      <div className="flex gap-2">
        <button type="submit" disabled={loading} className="btn-primary text-sm">
          {loading ? 'Adding…' : 'Add Position'}
        </button>
        <button type="button" onClick={onCancel} className="btn-ghost text-sm">
          Cancel
        </button>
      </div>
    </form>
  )
}
