/* Shared UI primitives */
import { Loader2 } from 'lucide-react'
import './ui.css'

export function Card({ children, className = '', accent, style }) {
  return (
    <div className={`card ${accent ? 'card-accent' : ''} ${className}`} style={style}>
      {children}
    </div>
  )
}

export function PageHeader({ title, subtitle, icon: Icon, actions }) {
  return (
    <div className="page-header">
      <div className="page-header-left">
        {Icon && <div className="page-header-icon"><Icon size={20} /></div>}
        <div>
          <h1 className="page-title">{title}</h1>
          {subtitle && <p className="page-subtitle">{subtitle}</p>}
        </div>
      </div>
      {actions && <div className="page-header-actions">{actions}</div>}
    </div>
  )
}

export function Button({ children, variant = 'primary', size = 'md', loading, disabled, className = '', ...props }) {
  return (
    <button
      className={`btn btn-${variant} btn-${size} ${loading ? 'btn-loading' : ''} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Loader2 size={14} className="spin" />}
      {children}
    </button>
  )
}

export function Input({ label, error, className = '', ...props }) {
  return (
    <div className="field">
      {label && <label className="field-label">{label}</label>}
      <input className={`field-input ${error ? 'field-error' : ''} ${className}`} {...props} />
      {error && <div className="field-err-msg">{error}</div>}
    </div>
  )
}

export function Select({ label, children, error, className = '', ...props }) {
  return (
    <div className="field">
      {label && <label className="field-label">{label}</label>}
      <select className={`field-input field-select ${error ? 'field-error' : ''} ${className}`} {...props}>
        {children}
      </select>
    </div>
  )
}

export function Badge({ children, variant = 'default' }) {
  return <span className={`badge badge-${variant}`}>{children}</span>
}

export function Spinner({ size = 20 }) {
  return <Loader2 size={size} className="spin" style={{ color: 'var(--accent)' }} />
}

export function LoadingPage() {
  return (
    <div className="loading-page">
      <div className="loading-dots">
        <span /><span /><span />
      </div>
      <span style={{ color: 'var(--text3)', fontSize: 12 }}>Loading...</span>
    </div>
  )
}

export function EmptyState({ icon: Icon, title, desc, action }) {
  return (
    <div className="empty-state">
      {Icon && <div className="empty-icon"><Icon size={36} /></div>}
      <div className="empty-title">{title}</div>
      {desc && <div className="empty-desc">{desc}</div>}
      {action}
    </div>
  )
}

export function MetricCard({ label, value, suffix = '', delta, color, icon: Icon, sublabel }) {
  const isPositive = delta > 0
  return (
    <div className="metric-card">
      <div className="metric-header">
        <span className="metric-label">{label}</span>
        {Icon && <div className="metric-icon" style={{ color }}><Icon size={16} /></div>}
      </div>
      <div className="metric-value" style={{ color: color || 'var(--text)' }}>
        {value !== undefined && value !== null ? `${value}${suffix}` : '—'}
      </div>
      {delta !== undefined && (
        <div className={`metric-delta ${isPositive ? 'delta-up' : 'delta-down'}`}>
          {isPositive ? '▲' : '▼'} {Math.abs(delta).toFixed(1)}%
        </div>
      )}
      {sublabel && <div className="metric-sublabel">{sublabel}</div>}
    </div>
  )
}

export function RiskPill({ level }) {
  const map = { Low:'green', Medium:'yellow', High:'red', Critical:'red', Unknown:'grey' }
  return <Badge variant={map[level] || 'grey'}>{level}</Badge>
}

export function RatingBadge({ rating }) {
  const map = { Excellent:'green', Good:'blue', Fair:'yellow', Weak:'red', Critical:'red' }
  return <Badge variant={map[rating] || 'grey'}>{rating}</Badge>
}

export function SectionTitle({ children }) {
  return <div className="section-title">{children}</div>
}

export function Tabs({ tabs, active, onChange }) {
  return (
    <div className="tabs">
      {tabs.map(t => (
        <button
          key={t.id}
          className={`tab ${active === t.id ? 'tab-active' : ''}`}
          onClick={() => onChange(t.id)}
        >
          {t.icon && <t.icon size={14} />}
          {t.label}
        </button>
      ))}
    </div>
  )
}

export function Table({ columns, data, emptyText = 'No data' }) {
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            {columns.map(c => <th key={c.key}>{c.label}</th>)}
          </tr>
        </thead>
        <tbody>
          {data.length === 0
            ? <tr><td colSpan={columns.length} className="table-empty">{emptyText}</td></tr>
            : data.map((row, i) => (
              <tr key={i}>
                {columns.map(c => (
                  <td key={c.key}>{c.render ? c.render(row[c.key], row) : row[c.key] ?? '—'}</td>
                ))}
              </tr>
            ))
          }
        </tbody>
      </table>
    </div>
  )
}

export function ProgressBar({ value, max = 10, color }) {
  const pct = Math.min((value / max) * 100, 100)
  const bg = color || (pct >= 70 ? 'var(--green)' : pct >= 40 ? 'var(--yellow)' : 'var(--red)')
  return (
    <div className="progress-bg">
      <div className="progress-fill" style={{ width: `${pct}%`, background: bg }} />
    </div>
  )
}
