import { useApi } from '../hooks/useApi'
import { formatCurrency, formatDate, formatAmountRange, formatPercent } from '../utils/format'
import TickerChart from './TickerChart'

export default function ResearchPanel({ ticker }) {
  const { data: detail, loading } = useApi(`/signals/${ticker}`, [ticker])
  const { data: fundamentals } = useApi(`/ticker/${ticker}/fundamentals`, [ticker])

  if (loading) {
    return (
      <div className="p-6 text-center text-slate-600 text-sm">Loading research…</div>
    )
  }
  if (!detail) {
    return (
      <div className="p-6 text-center text-slate-600 text-sm">No data available.</div>
    )
  }

  let members = []
  try { members = JSON.parse(detail.contributing_members || '[]') } catch {}

  return (
    <div className="bg-navy-900 border-t border-navy-700 p-4 space-y-5">
      {/* Catalyst summary */}
      {detail.reasoning && (
        <div className="border-l-2 border-accent pl-4 py-1">
          <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">Catalyst</p>
          <p className="text-sm text-slate-300 leading-relaxed">{detail.reasoning}</p>
        </div>
      )}

      {/* Chart + Fundamentals */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="section-label">90-Day Price</p>
          <TickerChart ticker={ticker} days={90} height={160} />
        </div>
        <div>
          <p className="section-label">Fundamentals</p>
          {fundamentals ? (
            <div className="space-y-1.5 text-sm">
              <FundRow label="Market Cap" value={formatCurrency(fundamentals.market_cap, true)} />
              <FundRow label="P/E Ratio" value={fundamentals.pe_ratio?.toFixed(1) ?? '—'} />
              <FundRow
                label="52W Range"
                value={
                  fundamentals.week52_low && fundamentals.week52_high
                    ? `${formatCurrency(fundamentals.week52_low)} – ${formatCurrency(fundamentals.week52_high)}`
                    : '—'
                }
              />
              <FundRow label="Next Earnings" value={fundamentals.next_earnings ? formatDate(fundamentals.next_earnings) : '—'} />
              <FundRow label="Sector" value={fundamentals.sector ?? '—'} />
              <p className="text-xs text-slate-600 pt-1">
                via {fundamentals.provider || 'Yahoo Finance'}
                {fundamentals.provider === 'Yahoo Finance' && (
                  <> · <a href="#sources" className="text-accent hover:underline">Upgrade to Polygon.io</a></>
                )}
              </p>
            </div>
          ) : (
            <p className="text-slate-600 text-sm">Loading…</p>
          )}
        </div>
      </div>

      {/* Congressional activity */}
      {detail.trades?.length > 0 && (
        <div>
          <p className="section-label">Congressional Activity</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 text-xs border-b border-navy-700">
                  <th className="pb-2 pr-4">Member</th>
                  <th className="pb-2 pr-4">Party</th>
                  <th className="pb-2 pr-4">Committee</th>
                  <th className="pb-2 pr-4">Amount</th>
                  <th className="pb-2">Date</th>
                </tr>
              </thead>
              <tbody>
                {detail.trades.map((t, i) => {
                  let committees = []
                  try { committees = JSON.parse(t.committees || '[]') } catch {}
                  return (
                    <tr key={i} className="border-b border-navy-800 hover:bg-navy-800/50">
                      <td className="py-2 pr-4 text-slate-200">{t.member_name}</td>
                      <td className="py-2 pr-4">
                        <span className={t.party === 'R' ? 'badge-r' : t.party === 'D' ? 'badge-d' : 'text-slate-500 text-xs'}>
                          {t.party}
                        </span>
                      </td>
                      <td className="py-2 pr-4 text-slate-400 text-xs">{committees[0] || '—'}</td>
                      <td className="py-2 pr-4 font-mono text-xs text-slate-300">
                        {formatAmountRange(t.amount_low, t.amount_high)}
                      </td>
                      <td className="py-2 text-slate-500 text-xs">{formatDate(t.trade_date)}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Contracts + Donations */}
      <div className="grid grid-cols-2 gap-4">
        {detail.contracts?.length > 0 && (
          <div>
            <p className="section-label">Federal Contracts</p>
            <div className="space-y-2">
              {detail.contracts.slice(0, 4).map((c, i) => (
                <div key={i} className="bg-navy-800 rounded p-2.5 text-xs">
                  <p className="text-slate-300 font-medium">{c.agency}</p>
                  <p className="font-mono text-emerald-400">{formatCurrency(c.value, true)}</p>
                  <p className="text-slate-500 mt-0.5 truncate">{c.description || '—'}</p>
                </div>
              ))}
            </div>
          </div>
        )}
        {detail.donations?.length > 0 && (
          <div>
            <p className="section-label">Campaign Donations</p>
            <div className="space-y-2">
              {detail.donations.slice(0, 4).map((d, i) => (
                <div key={i} className="bg-navy-800 rounded p-2.5 text-xs">
                  <p className="text-slate-300 font-medium truncate">{d.donor}</p>
                  <p className="font-mono text-amber-400">{formatCurrency(d.amount, true)}</p>
                  <p className="text-slate-500 mt-0.5">{d.industry}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Score breakdown */}
      <div>
        <p className="section-label">Score Breakdown</p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {[
            ['Congressional Vol', detail.congressional_vol],
            ['Committee Relevance', detail.committee_relevance],
            ['Bipartisan', detail.bipartisan],
            ['Contract Signal', detail.contract_correlation],
            ['Donation Align', detail.donation_alignment],
            ['Direction', detail.direction_consensus],
            ['Freshness', detail.freshness],
          ].map(([label, val]) => (
            <div key={label} className="bg-navy-800 rounded p-2 text-xs">
              <p className="text-slate-500 mb-1">{label}</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-navy-700 rounded-full h-1.5">
                  <div
                    className="bg-accent h-1.5 rounded-full transition-all"
                    style={{ width: `${Math.min(100, val ?? 0)}%` }}
                  />
                </div>
                <span className="font-mono text-slate-300">{Math.round(val ?? 0)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function FundRow({ label, value }) {
  return (
    <div className="flex justify-between">
      <span className="text-slate-500">{label}</span>
      <span className="font-mono text-slate-200">{value}</span>
    </div>
  )
}
