import { useState } from 'react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { useApi } from '../hooks/useApi'
import { formatCurrency, formatDateShort } from '../utils/format'
import { PortfolioTooltip } from './ChartTooltip'

const RANGES = ['30D', '60D', '1Q', 'YTD', '1Y']

export default function PerformanceChart() {
  const [range, setRange] = useState('30D')
  const { data, loading } = useApi(`/portfolio/performance?range=${range}`, [range])

  const chartData = data || []
  const first = chartData[0]?.value ?? 0
  const last = chartData[chartData.length - 1]?.value ?? 0
  const change = first > 0 ? ((last - first) / first) * 100 : 0
  const isUp = change >= 0

  return (
    <div className="card p-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="section-label">Portfolio Performance</p>
          {last > 0 && (
            <p className={`text-sm font-mono ${isUp ? 'text-emerald-400' : 'text-coral-400'}`}>
              {isUp ? '+' : ''}{change.toFixed(2)}% · {isUp ? '+' : ''}{formatCurrency(last - first)}
            </p>
          )}
        </div>
        <div className="flex gap-1">
          {RANGES.map((r) => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={`text-xs px-2.5 py-1 rounded transition-colors ${
                range === r
                  ? 'bg-accent text-white'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-navy-700'
              }`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="h-48 flex items-center justify-center text-slate-600 text-sm">
          Loading chart…
        </div>
      ) : chartData.length === 0 ? (
        <div className="h-48 flex items-center justify-center text-slate-600 text-sm">
          Add holdings to see performance
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={chartData} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id="perfGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis
              dataKey="date"
              tickFormatter={formatDateShort}
              tick={{ fill: '#64748b', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tickFormatter={(v) => formatCurrency(v, true)}
              tick={{ fill: '#64748b', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              width={70}
            />
            <Tooltip content={<PortfolioTooltip />} />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#3b82f6"
              strokeWidth={2}
              fill="url(#perfGrad)"
              dot={false}
              activeDot={{ r: 4, fill: '#3b82f6', stroke: '#06090f' }}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
