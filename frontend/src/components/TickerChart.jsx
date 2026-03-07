import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { useApi } from '../hooks/useApi'
import { formatCurrency, formatDateShort } from '../utils/format'
import { PriceTooltip } from './ChartTooltip'

export default function TickerChart({ ticker, days = 90, height = 160 }) {
  const { data, loading } = useApi(`/ticker/${ticker}/chart?days=${days}`, [ticker, days])

  if (loading) {
    return (
      <div style={{ height }} className="flex items-center justify-center text-slate-600 text-sm">
        Loading…
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div style={{ height }} className="flex items-center justify-center text-slate-600 text-sm">
        No price data
      </div>
    )
  }

  const first = data[0]?.close ?? 0
  const last = data[data.length - 1]?.close ?? 0
  const isUp = last >= first
  const strokeColor = isUp ? '#10b981' : '#f87171'
  const gradId = `grad-${ticker}`

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={strokeColor} stopOpacity={0.2} />
            <stop offset="95%" stopColor={strokeColor} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
        <XAxis
          dataKey="date"
          tickFormatter={formatDateShort}
          tick={{ fill: '#64748b', fontSize: 10 }}
          axisLine={false}
          tickLine={false}
          interval="preserveStartEnd"
        />
        <YAxis
          tickFormatter={(v) => formatCurrency(v, true)}
          tick={{ fill: '#64748b', fontSize: 10 }}
          axisLine={false}
          tickLine={false}
          width={58}
          domain={['auto', 'auto']}
        />
        <Tooltip content={<PriceTooltip />} />
        <Area
          type="monotone"
          dataKey="close"
          stroke={strokeColor}
          strokeWidth={1.5}
          fill={`url(#${gradId})`}
          dot={false}
          activeDot={{ r: 3, fill: strokeColor, stroke: '#06090f' }}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
