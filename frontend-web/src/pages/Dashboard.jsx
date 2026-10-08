import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { companiesAPI, analysisAPI } from '../api'
import { useAuth } from '../context/AuthContext'
import { Card, MetricCard, Button, EmptyState, LoadingPage, RatingBadge } from '../components/ui'
import {
  Building2, Plus, Brain, ArrowRight, Upload,
  Activity, ShieldCheck, Zap, ChevronDown, CheckCircle2,
  Globe, Hash, Calendar, BarChart2
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts'
import './Dashboard.css'

const chartTooltipStyle = {
  background: '#ffffff',
  border: '1px solid #e2e8f0',
  borderRadius: 10,
  fontSize: 12,
  color: '#0f172a',
  boxShadow: '0 4px 16px rgba(15,23,42,0.1)',
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{...chartTooltipStyle, padding: '10px 14px'}}>
      <div style={{ color: '#64748b', marginBottom: 6, fontWeight: 700, fontSize: 11 }}>{label}</div>
      {payload.map(p => (
        <div key={p.name} style={{ color: p.color, display: 'flex', gap: 8, alignItems: 'center', marginBottom: 3 }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: p.color, flexShrink: 0 }} />
          <span style={{ color: '#64748b' }}>{p.name}:</span>
          <strong style={{ color: '#0f172a' }}>${p.value?.toFixed(2)}B</strong>
        </div>
      ))}
    </div>
  )
}

// ── Company Dropdown Component ────────────────────────────────
function CompanyDropdown({ companies, selected, onSelect }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    const handler = e => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  return (
    <div className="company-dropdown" ref={ref}>
      <button className="company-dropdown-trigger" onClick={() => setOpen(o => !o)}>
        <div className="cdt-left">
          <div className="cdt-avatar">{selected?.name?.charAt(0).toUpperCase() || '?'}</div>
          <div>
            <div className="cdt-name">{selected?.name || 'Select a company'}</div>
            <div className="cdt-sub">
              {selected?.ticker && <span>{selected.ticker}</span>}
              {selected?.industry && <span> · {selected.industry}</span>}
              {!selected && <span>Choose from {companies.length} companies</span>}
            </div>
          </div>
        </div>
        <ChevronDown size={16} className={`cdt-chevron ${open ? 'open' : ''}`} />
      </button>

      {open && (
        <div className="company-dropdown-menu">
          <div className="cdm-header">
            <span>{companies.length} {companies.length === 1 ? 'company' : 'companies'} available</span>
          </div>
          {companies.map(c => (
            <button
              key={c.id}
              className={`cdm-item ${selected?.id === c.id ? 'active' : ''}`}
              onClick={() => { onSelect(c); setOpen(false) }}
            >
              <div className="cdm-avatar">{c.name.charAt(0).toUpperCase()}</div>
              <div className="cdm-info">
                <div className="cdm-name">{c.name}</div>
                <div className="cdm-meta">
                  {c.ticker && <span><Hash size={10} />{c.ticker}</span>}
                  {c.industry && <span><Globe size={10} />{c.industry}</span>}
                  {c.fiscal_year_end && <span><Calendar size={10} />FY {c.fiscal_year_end}</span>}
                </div>
              </div>
              {selected?.id === c.id && <CheckCircle2 size={15} className="cdm-check" />}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default function Dashboard() {
  const { user }    = useAuth()
  const navigate    = useNavigate()
  const [companies, setCompanies] = useState([])
  const [selected,  setSelected]  = useState(null)
  const [kpis,      setKpis]      = useState(null)
  const [stmts,     setStmts]     = useState([])
  const [reports,   setReports]   = useState([])
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    companiesAPI.list().then(r => {
      setCompanies(r.data)
      if (r.data.length) setSelected(r.data[0])
    }).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selected) return
    analysisAPI.kpis(selected.id).then(r => setKpis(r.data)).catch(() => setKpis(null))
    companiesAPI.statements(selected.id).then(r => setStmts(r.data)).catch(() => setStmts([]))
    analysisAPI.reports(selected.id).then(r => setReports(r.data)).catch(() => setReports([]))
  }, [selected])

  if (loading) return <LoadingPage />

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'
  const firstName = user?.full_name?.split(' ')[0] || 'Analyst'

  const kpiData   = kpis?.kpis || {}
  const pr        = kpiData.profitability || {}
  const liq       = kpiData.liquidity     || {}
  const lev       = kpiData.leverage      || {}
  const gr        = kpiData.growth        || {}
  const composite = kpiData.composite_scores || {}
  const latestReport = reports[0] || null

  const trendData = [...stmts].reverse().map(s => ({
    period:    s.period,
    revenue:   s.revenue    ? s.revenue / 1e9    : null,
    netIncome: s.net_income ? s.net_income / 1e9 : null,
  }))

  return (
    <div>
      {/* ── Hero ── */}
      <div className="dash-hero">
        <div className="dash-hero-grid" />
        <div className="dash-hero-content">
          <div className="dash-greeting">
            {greeting}, <span>{firstName}</span> 👋
          </div>
          <div className="dash-hero-sub">
            {companies.length
              ? `You have ${companies.length} ${companies.length === 1 ? 'company' : 'companies'} under analysis`
              : 'Start by adding a company and uploading financial data'}
          </div>
        </div>
        <div className="dash-hero-actions">
          <Button variant="secondary" size="md" onClick={() => navigate('/upload')}>
            <Upload size={14} /> Upload Data
          </Button>
          <Button size="md" onClick={() => navigate('/insights')}>
            <Brain size={14} /> AI Analysis
          </Button>
        </div>
      </div>

      {/* ── Platform Stats ── */}
      <div className="dash-stats">
        {[
          { label: 'Companies',    value: companies.length || '0', icon: Building2,  color: '#3b82f6', bg: 'rgba(59,130,246,0.12)',  trend: null },
          { label: 'KPI Metrics',  value: '40+',                   icon: BarChart2,  color: '#10b981', bg: 'rgba(16,185,129,0.12)',  trend: null },
          { label: 'Risk Models',  value: '3',                     icon: ShieldCheck,color: '#f59e0b', bg: 'rgba(245,158,11,0.12)',  trend: null },
          { label: 'AI Providers', value: '2',                     icon: Zap,        color: '#8b5cf6', bg: 'rgba(139,92,246,0.12)',  trend: null },
        ].map(m => (
          <div key={m.label} className="dash-stat-card">
            <div className="dash-stat-top">
              <div className="dash-stat-icon" style={{ color: m.color, background: m.bg }}>
                <m.icon size={18} />
              </div>
            </div>
            <div className="dash-stat-val">{m.value}</div>
            <div className="dash-stat-label">{m.label}</div>
          </div>
        ))}
      </div>

      {/* ── Empty state ── */}
      {companies.length === 0 ? (
        <EmptyState
          icon={Building2}
          title="No companies yet"
          desc="Add your first company and upload financial statements to start getting AI-powered insights, risk scores, and forecasts."
          action={
            <Button onClick={() => navigate('/companies')}>
              <Plus size={14} /> Add Your First Company
            </Button>
          }
        />
      ) : (
        <>
          {/* ── Company Selector ── */}
          <div className="company-selector-section">
            <div className="company-selector-header">
              <div className="company-count-badge">
                <Building2 size={14} />
                <span>{companies.length} {companies.length === 1 ? 'Company' : 'Companies'}</span>
              </div>
              <Button size="sm" variant="ghost" onClick={() => navigate('/companies')}>
                Manage <ArrowRight size={12} />
              </Button>
            </div>

            {/* Dropdown selector */}
            <CompanyDropdown
              companies={companies}
              selected={selected}
              onSelect={setSelected}
            />

            {/* Company cards grid */}
            <div className="company-cards-grid">
              {companies.map(c => (
                <div
                  key={c.id}
                  className={`company-select-card ${selected?.id === c.id ? 'active' : ''}`}
                  onClick={() => setSelected(c)}
                >
                  <div className="csc-avatar">
                    {c.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="csc-info">
                    <div className="csc-name">{c.name}</div>
                    <div className="csc-meta">
                      {c.ticker && <span className="csc-ticker">{c.ticker}</span>}
                      {c.industry && <span className="csc-industry">{c.industry}</span>}
                    </div>
                  </div>
                  {selected?.id === c.id && (
                    <CheckCircle2 size={16} className="csc-check" />
                  )}
                </div>
              ))}
              {/* Add company shortcut */}
              <div className="company-select-card add-card" onClick={() => navigate('/companies')}>
                <div className="csc-avatar add-avatar"><Plus size={18} /></div>
                <div className="csc-info">
                  <div className="csc-name">Add Company</div>
                  <div className="csc-meta"><span className="csc-industry">Click to add new</span></div>
                </div>
              </div>
            </div>
          </div>

          {selected && (
            <>
              {/* KPI Cards */}
              <div className="dash-metrics">
                <MetricCard label="Gross Margin"   value={pr.gross_margin?.toFixed(1)}      suffix="%" color={pr.gross_margin > 30 ? 'var(--green)' : 'var(--yellow)'} />
                <MetricCard label="Net Margin"     value={pr.net_margin?.toFixed(1)}        suffix="%" color={pr.net_margin > 0 ? 'var(--green)' : 'var(--red)'} />
                <MetricCard label="ROE"            value={pr.return_on_equity?.toFixed(1)}  suffix="%" color="var(--blue)" />
                <MetricCard label="Current Ratio"  value={liq.current_ratio?.toFixed(2)}   suffix="x" color={liq.current_ratio >= 1.5 ? 'var(--green)' : 'var(--yellow)'} />
                <MetricCard label="D/E Ratio"      value={lev.debt_to_equity?.toFixed(2)}  suffix="x" color={lev.debt_to_equity < 1 ? 'var(--green)' : 'var(--yellow)'} />
                <MetricCard label="Revenue Growth" value={gr.revenue_growth?.toFixed(1)}   suffix="%" color={gr.revenue_growth > 0 ? 'var(--green)' : 'var(--red)'} />
              </div>

              {/* Charts + Health */}
              <div className="dash-charts">
                {/* Revenue chart */}
                <Card className="dash-chart-main">
                  <div className="chart-header">
                    <span className="chart-title">Revenue & Net Income Trend</span>
                    <span className="chart-sub">$ Billions</span>
                  </div>
                  {trendData.length >= 2 ? (
                    <ResponsiveContainer width="100%" height={240}>
                      <BarChart data={trendData} margin={{ top: 4, right: 4, left: 0, bottom: 4 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                        <XAxis dataKey="period" tick={{ fill: 'var(--text3)', fontSize: 11 }} axisLine={false} tickLine={false} />
                        <YAxis tick={{ fill: 'var(--text3)', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `$${v}B`} />
                        <Tooltip content={<CustomTooltip />} />
                        <Bar dataKey="revenue"   name="Revenue"    fill="url(#blueGrad)"  radius={[4,4,0,0]} />
                        <Bar dataKey="netIncome" name="Net Income" fill="url(#greenGrad)" radius={[4,4,0,0]} />
                        <defs>
                          <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.9} />
                            <stop offset="100%" stopColor="#6366f1" stopOpacity={0.6} />
                          </linearGradient>
                          <linearGradient id="greenGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#10b981" stopOpacity={0.9} />
                            <stop offset="100%" stopColor="#059669" stopOpacity={0.6} />
                          </linearGradient>
                        </defs>
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="no-chart">
                      <Activity size={28} style={{ color: 'var(--text4)' }} />
                      <span>Upload 2+ periods to see trends</span>
                    </div>
                  )}
                </Card>

                {/* Health Score */}
                <Card className="dash-health-card">
                  <div className="chart-header">
                    <span className="chart-title">Financial Health</span>
                  </div>
                  {composite.overall_health !== undefined ? (
                    <div className="health-display">
                      <div className="health-ring">
                        <svg viewBox="0 0 120 120" width="150" height="150">
                          <defs>
                            <linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1">
                              <stop offset="0%" stopColor="#3b82f6" />
                              <stop offset="100%" stopColor="#8b5cf6" />
                            </linearGradient>
                          </defs>
                          <circle cx="60" cy="60" r="50" fill="none" stroke="var(--bg5)" strokeWidth="10"/>
                          <circle cx="60" cy="60" r="50" fill="none"
                            stroke="url(#ringGrad)" strokeWidth="10" strokeLinecap="round"
                            strokeDasharray={`${(composite.overall_health / 10) * 314} 314`}
                            transform="rotate(-90 60 60)"
                            style={{ transition: 'stroke-dasharray 1s cubic-bezier(0.4,0,0.2,1)', filter: 'drop-shadow(0 0 8px rgba(59,130,246,0.5))' }}
                          />
                          <text x="60" y="55" textAnchor="middle" fontSize="26" fontWeight="900" fill="var(--text)">{composite.overall_health?.toFixed(1)}</text>
                          <text x="60" y="72" textAnchor="middle" fontSize="12" fill="var(--text3)">out of 10</text>
                        </svg>
                      </div>
                      <div className="health-scores" style={{ width: '100%' }}>
                        {[
                          ['Profitability', composite.profitability_score],
                          ['Liquidity',     composite.liquidity_score],
                          ['Leverage',      composite.leverage_score],
                        ].map(([label, val]) => val !== undefined && (
                          <div key={label} className="health-score-row">
                            <span className="health-score-label">{label}</span>
                            <div className="health-score-bar">
                              <div className="health-score-fill" style={{
                                width: `${(val / 10) * 100}%`,
                                background: val >= 7 ? 'var(--green)' : val >= 4 ? 'var(--yellow)' : 'var(--red)'
                              }} />
                            </div>
                            <span className="health-score-val">{val?.toFixed(1)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="no-chart">
                      <Brain size={28} style={{ color: 'var(--text4)' }} />
                      <span>No analysis yet</span>
                      <Button size="sm" onClick={() => navigate('/insights')}>Run AI Analysis</Button>
                    </div>
                  )}
                </Card>
              </div>

              {/* Latest Report */}
              {latestReport && (
                <Card className="dash-report" style={{ borderLeft: '3px solid var(--blue)' }}>
                  <div className="dash-report-left" style={{ flex: 1 }}>
                    <div className="dash-report-meta">
                      <span className="dash-report-date">{latestReport.created_at?.slice(0, 10)}</span>
                      {latestReport.overall_rating && <RatingBadge rating={latestReport.overall_rating} />}
                    </div>
                    <div className="dash-report-title">{latestReport.title}</div>
                    {latestReport.executive_summary && (
                      <div className="dash-report-excerpt">
                        {latestReport.executive_summary.slice(0, 200)}…
                      </div>
                    )}
                  </div>
                  <Button size="sm" variant="secondary" onClick={() => navigate('/insights')}>
                    View Full Report <ArrowRight size={13} />
                  </Button>
                </Card>
              )}
            </>
          )}
        </>
      )}
    </div>
  )
}
