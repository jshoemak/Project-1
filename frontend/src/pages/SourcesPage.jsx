import { useApi, api } from '../hooks/useApi'
import { FreeSourceCard, PremiumSourceCard } from '../components/DataSourceCard'
import { useState } from 'react'

export default function SourcesPage() {
  const { data, loading, refetch } = useApi('/sources')
  const [reporting, setReporting] = useState(false)
  const [reportMsg, setReportMsg] = useState(null)

  const handleReport = async () => {
    setReporting(true)
    setReportMsg(null)
    try {
      const r = await api.post('/report', {})
      setReportMsg('Report generated' + (r.pdf ? ` — ${r.pdf.split('/').pop()}` : ''))
    } catch (e) {
      setReportMsg('Error: ' + e.message)
    } finally {
      setReporting(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 space-y-8">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Data Sources</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Manage your data connections. Swap stock providers instantly by adding an API key.
        </p>
      </div>

      {/* Active provider pill */}
      {data && (
        <div className="inline-flex items-center gap-2 text-xs bg-navy-800 border border-navy-700 px-3 py-1.5 rounded-full">
          <span className="text-slate-400">Stock data via</span>
          <span className="font-semibold text-accent capitalize">{data.active_stock_provider}</span>
        </div>
      )}

      {/* Free tier */}
      <section>
        <p className="section-label">Free Tier — Active by Default</p>
        {loading ? (
          <div className="text-slate-600 text-sm">Loading…</div>
        ) : (
          <div className="grid sm:grid-cols-2 gap-3">
            {data?.free?.map((s) => <FreeSourceCard key={s.name} source={s} />)}
          </div>
        )}
      </section>

      {/* Premium tier */}
      <section>
        <p className="section-label">Premium Upgrades</p>
        <p className="text-xs text-slate-500 mb-4">
          Paste your API key to instantly activate. Stock provider upgrades auto-swap Yahoo Finance.
        </p>
        {loading ? (
          <div className="text-slate-600 text-sm">Loading…</div>
        ) : (
          <div className="grid sm:grid-cols-2 gap-3">
            {data?.premium?.map((s) => (
              <PremiumSourceCard key={s.name} source={s} onConnected={refetch} />
            ))}
          </div>
        )}
      </section>

      {/* Provider abstraction note */}
      <div className="card p-4 border-l-2 border-accent">
        <p className="text-sm font-medium text-slate-200 mb-1">Provider Abstraction</p>
        <p className="text-xs text-slate-500 leading-relaxed">
          All pages fetch prices and fundamentals through a unified provider layer.
          When you save a Polygon.io or Alpha Vantage key, it becomes the active provider
          with no code changes required — just refresh the page.
        </p>
      </div>

      {/* Daily report */}
      <section>
        <p className="section-label">Daily Report</p>
        <div className="card p-4">
          <p className="text-sm text-slate-300 mb-3">
            Generate a PDF summary of top signals and portfolio snapshot.
            If email is configured, it will also be sent automatically.
          </p>
          {reportMsg && (
            <p className={`text-xs mb-3 ${reportMsg.startsWith('Error') ? 'text-coral-400' : 'text-emerald-400'}`}>
              {reportMsg}
            </p>
          )}
          <button onClick={handleReport} disabled={reporting} className="btn-primary text-sm">
            {reporting ? 'Generating…' : 'Generate Report'}
          </button>
        </div>
      </section>
    </div>
  )
}
