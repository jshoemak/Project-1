import { scoreBg } from '../utils/format'

export default function SignalBadge({ score, size = 'md' }) {
  const bg = scoreBg(score)
  const sizeClass = size === 'lg'
    ? 'text-base px-3 py-1.5 min-w-[3rem]'
    : 'text-xs px-2 py-0.5 min-w-[2.5rem]'

  return (
    <span
      className={`${bg} text-white font-mono font-bold rounded text-center inline-block ${sizeClass}`}
    >
      {Math.round(score)}
    </span>
  )
}
