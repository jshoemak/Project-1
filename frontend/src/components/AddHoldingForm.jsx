import { useState } from 'react'
import { api } from '../hooks/useApi'

export default function AddHoldingForm({ onAdded, onCancel }) {
  const [form, setForm] = useState({ ticker: '', name: '', shares: '', avg_cost: '', sector: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

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
          <input className="input-field font-mono uppercase" placeholder="AAPL" value={form.ticker} onChange={set('ticker')} />
        </div>
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Company Name</label>
          <input className="input-field" placeholder="Apple Inc." value={form.name} onChange={set('name')} />
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
          <input className="input-field font-mono" type="number" min="0" step="0.01" placeholder="150.00" value={form.avg_cost} onChange={set('avg_cost')} />
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
