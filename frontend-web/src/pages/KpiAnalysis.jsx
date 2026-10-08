import { useEffect, useState } from 'react'
import { companiesAPI, analysisAPI } from '../api'
import { PageHeader, Card, Tabs, EmptyState, MetricCard, Table, LoadingPage } from '../components/ui'
import { BarChart2, TrendingUp } from 'lucide-react'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, LineChart, Line } from 'recharts'
import './KpiAnalysis.css'

const RATING = (key, val) => {
  const cfg = {
    gross_margin:{good:40,warn:20}, operating_margin:{good:15,warn:5},
    net_margin:{good:10,warn:2}, return_on_equity:{good:15,warn:8},
    current_ratio:{good:2,warn:1}, quick_ratio:{good:1,warn:.7},
    debt_to_equity:{good:1,warn:2,inv:true}, interest_coverage:{good:5,warn:2},
  }
  const c = cfg[key]; if (!c) return 'default'
  if (c.inv) return val <= c.good ? 'green' : val <= c.warn ? 'yellow' : 'red'
  return val >= c.good ? 'green' : val >= c.warn ? 'yellow' : 'red'
}

const CATEGORIES = [
  { id:'profitability', label:'Profitability', icon:'💰' },
  { id:'liquidity',     label:'Liquidity',     icon:'💧' },
  { id:'leverage',      label:'Leverage',      icon:'🏦' },
  { id:'efficiency',    label:'Efficiency',    icon:'⚙️' },
  { id:'cash_flow',     label:'Cash Flow',     icon:'💸' },
  { id:'growth',        label:'Growth',        icon:'📈' },
]

const VIEWS = [
  { id:'cards', label:'Cards' },
  { id:'bar',   label:'Bar Chart' },
  { id:'radar', label:'Radar' },
  { id:'table', label:'Table' },
]

export default function KpiAnalysis() {
  const [companies, setCompanies] = useState([])
  const [cid,       setCid]       = useState(null)
  const [kpiResp,   setKpiResp]   = useState(null)
  const [stmts,     setStmts]     = useState([])
  const [cat,       setCat]       = useState('profitability')
  const [view,      setView]      = useState('cards')
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    companiesAPI.list().then(r => {
      setCompanies(r.data)
      if (r.data.length) setCid(r.data[0].id)
    }).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!cid) return
    setKpiResp(null)
    analysisAPI.kpis(cid).then(r => setKpiResp(r.data)).catch(() => {})
    companiesAPI.statements(cid).then(r => setStmts(r.data)).catch(() => {})
  }, [cid])

  if (loading) return <LoadingPage/>

  const kpis      = kpiResp?.kpis || {}
  const composite = kpis.composite_scores || {}
  const catData   = kpis[cat] || {}
  const period    = kpiResp?.period || '—'

  const chartItems = Object.entries(catData)
    .filter(([,v]) => v !== null && v !== undefined)
    .map(([k,v]) => ({ name: k.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase()), value: v, key: k }))

  const trendMetric = 'revenue'
  const trendData = [...stmts].reverse().map(s => ({
    period: s.period, value: s[trendMetric] ? s[trendMetric]/1e9 : null
  })).filter(d => d.value !== null)

  return (
    <div>
      <PageHeader title="KPI Analysis" subtitle="40+ financial ratios — cards, charts, tables" icon={BarChart2}/>

      {companies.length === 0 ? <EmptyState icon={BarChart2} title="No data" desc="Add a company and upload statements first."/> : (
        <>
          {/* Controls */}
          <div className="kpi-controls">
            <select className="page-select" style={{width:200}} value={cid||''} onChange={e=>setCid(+e.target.value)}>
              {companies.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            <span className="kpi-period">Period: <strong>{period}</strong></span>
          </div>

          {/* Composite scores */}
          <div className="kpi-scores">
            {[['💰','Profitability','profitability_score'],['💧','Liquidity','liquidity_score'],['🏦','Leverage','leverage_score'],['❤️','Overall','overall_health']].map(([icon,label,key]) => {
              const val = composite[key]
              const color = val>=7?'var(--green)':val>=4?'var(--yellow)':'var(--red)'
              return (
                <Card key={key} className="score-card">
                  <div className="score-icon">{icon}</div>
                  <div className="score-label">{label}</div>
                  <div className="score-value" style={{color}}>{val?.toFixed(1) ?? '—'}</div>
                  <div className="score-max">/10</div>
                  {val !== undefined && <div className="score-bar"><div className="score-bar-fill" style={{width:`${(val/10)*100}%`,background:color}}/></div>}
                </Card>
              )
            })}
          </div>

          {/* Category tabs + view switcher */}
          <div className="kpi-tab-bar">
            <div className="kpi-cats">
              {CATEGORIES.map(c => (
                <button key={c.id} className={`kpi-cat ${cat===c.id?'active':''}`} onClick={() => setCat(c.id)}>
                  {c.icon} {c.label}
                </button>
              ))}
            </div>
            <div className="kpi-views">
              {VIEWS.map(v => (
                <button key={v.id} className={`kpi-view ${view===v.id?'active':''}`} onClick={() => setView(v.id)}>{v.label}</button>
              ))}
            </div>
          </div>

          {/* Content */}
          <Card className="kpi-content">
            {chartItems.length === 0
              ? <div className="no-chart">No {cat} data available for this period.</div>
              : view === 'cards' ? (
                <div className="kpi-cards-grid">
                  {chartItems.map(item => {
                    const rating = RATING(item.key, item.value)
                    const color  = rating==='green'?'var(--green)':rating==='yellow'?'var(--yellow)':rating==='red'?'var(--red)':'var(--text3)'
                    const unit   = item.key.includes('margin')||item.key.includes('growth')||item.key.includes('return')||item.key.includes('rate') ? '%' : item.key.includes('ratio')||item.key.includes('coverage')||item.key.includes('turnover') ? 'x' : item.key.includes('days') ? 'd' : ''
                    return (
                      <div key={item.key} className="kpi-card-item" style={{borderTop:`3px solid ${color}`}}>
                        <div className="kpi-card-label">{item.name}</div>
                        <div className="kpi-card-value" style={{color}}>{item.value.toFixed(2)}<span className="kpi-card-unit">{unit}</span></div>
                        <div className="kpi-card-dot" style={{background:color}}/>
                      </div>
                    )
                  })}
                </div>
              ) : view === 'bar' ? (
                <ResponsiveContainer width="100%" height={340}>
                  <BarChart data={chartItems} margin={{top:10,right:10,left:0,bottom:60}}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false}/>
                    <XAxis dataKey="name" tick={{fill:'var(--text3)',fontSize:10}} angle={-30} textAnchor="end" interval={0} axisLine={false} tickLine={false}/>
                    <YAxis tick={{fill:'var(--text3)',fontSize:10}} axisLine={false} tickLine={false}/>
                    <Tooltip contentStyle={{background:'rgba(22,13,46,0.95)',border:'1px solid rgba(255,255,255,0.12)',borderRadius:10,fontSize:12,backdropFilter:'blur(16px)',color:'#f5f0ff'}} formatter={v=>[v.toFixed(2),'']}/>
                    <Bar dataKey="value" fill="url(#barGrad)" radius={[4,4,0,0]} maxBarSize={50}/>
                    <defs><linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#a855f7"/><stop offset="100%" stopColor="#06b6d4"/></linearGradient></defs>
                  </BarChart>
                </ResponsiveContainer>
              ) : view === 'radar' ? (
                chartItems.length >= 3 ? (
                  <ResponsiveContainer width="100%" height={340}>
                    <RadarChart data={chartItems.slice(0,8)}>
                      <PolarGrid stroke="var(--border)"/>
                      <PolarAngleAxis dataKey="name" tick={{fill:'var(--text3)',fontSize:10}}/>
                      <Radar dataKey="value" fill="rgba(59,130,246,.2)" stroke="#3b82f6" strokeWidth={2}/>
                    </RadarChart>
                  </ResponsiveContainer>
                ) : <div className="no-chart">Need 3+ metrics for radar chart</div>
              ) : (
                <Table
                  columns={[
                    { key:'name',  label:'KPI' },
                    { key:'value', label:'Value', render: (v,r) => {
                      const unit = r.key?.includes('margin')||r.key?.includes('return')||r.key?.includes('growth') ? '%' : 'x'
                      return `${v.toFixed(2)}${unit}`
                    }},
                    { key:'key', label:'Rating', render: (k, r) => {
                      const rating = RATING(k, r.value)
                      const map = {green:'🟢 Strong', yellow:'🟡 Adequate', red:'🔴 Weak', default:'—'}
                      return map[rating] || '—'
                    }},
                  ]}
                  data={chartItems.map(i=>({...i, name:i.name}))}
                />
              )
            }
          </Card>

          {/* Trend */}
          {trendData.length >= 2 && (
            <Card style={{marginTop:20}}>
              <div className="chart-header"><span className="chart-title">Revenue Trend</span><span className="chart-sub">($ Billions)</span></div>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={trendData} margin={{top:5,right:10,left:0,bottom:5}}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false}/>
                  <XAxis dataKey="period" tick={{fill:'var(--text3)',fontSize:11}} axisLine={false} tickLine={false}/>
                  <YAxis tick={{fill:'var(--text3)',fontSize:11}} axisLine={false} tickLine={false} tickFormatter={v=>`$${v}B`}/>
                  <Tooltip contentStyle={{background:'rgba(22,13,46,0.95)',border:'1px solid rgba(255,255,255,0.12)',borderRadius:10,fontSize:12,backdropFilter:'blur(16px)',color:'#f5f0ff'}} formatter={v=>[`$${v?.toFixed(2)}B`,'Revenue']}/>
                  <Line dataKey="value" stroke="#a855f7" strokeWidth={2.5} dot={{fill:'#a855f7',r:4}} activeDot={{r:6}}/>
                </LineChart>
              </ResponsiveContainer>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
