import { useEffect, useState } from 'react'
import { companiesAPI, analysisAPI } from '../api'
import { PageHeader, Card, Button, EmptyState, LoadingPage } from '../components/ui'
import { TrendingUp, RefreshCw } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine, Area, AreaChart, ComposedChart, Bar } from 'recharts'
import ReactMarkdown from 'react-markdown'
import './Forecasting.css'

const METRICS = ['revenue','net_income','gross_profit','operating_income','ebitda','total_assets','free_cash_flow','operating_cash_flow']

export default function Forecasting() {
  const [companies, setCompanies] = useState([])
  const [cid,      setCid]       = useState(null)
  const [periods,  setPeriods]   = useState(4)
  const [result,   setResult]    = useState(null)
  const [loading,  setLoading]   = useState(true)
  const [running,  setRunning]   = useState(false)
  const [metric,   setMetric]    = useState('revenue')
  const [method,   setMethod]    = useState('ensemble')

  useEffect(() => {
    companiesAPI.list().then(r => {
      setCompanies(r.data)
      if (r.data.length) setCid(r.data[0].id)
    }).finally(() => setLoading(false))
  }, [])

  const run = async () => {
    if (!cid) return
    setRunning(true)
    try {
      const r = await analysisAPI.forecast(cid, periods)
      setResult(r.data)
    } catch {}
    finally { setRunning(false) }
  }

  if (loading) return <LoadingPage/>

  const forecasts   = result?.forecasts || {}
  const narrative   = result?.narrative || ''
  const available   = Object.keys(forecasts).filter(k => forecasts[k]?.historical?.length >= 2)
  const fdata       = forecasts[metric] || {}
  const historical  = fdata.historical || []
  const ensembleF   = fdata.ensemble_forecast || []
  const linearF     = fdata.linear_forecast || []
  const expF        = fdata.exponential_forecast || []
  const ciLow       = fdata.confidence_interval?.lower || []
  const ciHigh      = fdata.confidence_interval?.upper || []
  const trend       = fdata.trend || {}
  const cagr        = fdata.cagr_pct

  const n = historical.length
  const histLabels  = historical.map((_,i) => i === n-1 ? 'Now' : `T-${n-1-i}`)
  const futureLabels = ensembleF.map((_,i) => `T+${i+1}`)

  const activeF = method === 'linear' ? linearF : method === 'exp' ? expF : ensembleF

  const chartData = [
    ...historical.map((v,i) => ({ label: histLabels[i], historical: v, type:'hist' })),
    ...activeF.map((v,i) => ({
      label: futureLabels[i],
      forecast: v,
      ci_low:  ciLow[i],
      ci_high: ciHigh[i],
      type: 'forecast',
    }))
  ]

  const fmtY = v => {
    if (!v) return ''
    const a = Math.abs(v)
    if (a>=1e9) return `$${(v/1e9).toFixed(1)}B`
    if (a>=1e6) return `$${(v/1e6).toFixed(0)}M`
    return v.toFixed(0)
  }

  return (
    <div>
      <PageHeader title="Financial Forecasting" subtitle="Linear · Exponential · Ensemble with 95% confidence intervals" icon={TrendingUp}
        actions={
          <div style={{display:'flex',gap:10,alignItems:'center'}}>
            <select className="page-select" style={{width:160}} value={cid||''} onChange={e=>setCid(+e.target.value)}>
              {companies.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            <select className="page-select" style={{width:100}} value={periods} onChange={e=>setPeriods(+e.target.value)}>
              {[2,3,4,6,8].map(p=><option key={p} value={p}>{p} periods</option>)}
            </select>
            <Button onClick={run} loading={running}><RefreshCw size={14}/> Forecast</Button>
          </div>
        }
      />

      {!result ? (
        <EmptyState icon={TrendingUp} title="Generate forecasts" desc="Select a company and click Forecast. Requires at least 2 historical periods."/>
      ) : available.length === 0 ? (
        <EmptyState icon={TrendingUp} title="Insufficient data" desc="Upload at least 2 periods of financial statements to enable forecasting."/>
      ) : (
        <>
          {/* Controls */}
          <div className="forecast-controls">
            <div className="forecast-metric-tabs">
              {available.map(m => (
                <button key={m} className={`kpi-cat ${metric===m?'active':''}`} onClick={()=>setMetric(m)}>
                  {m.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}
                </button>
              ))}
            </div>
            <div className="forecast-method-tabs">
              {[['ensemble','Ensemble'],['linear','Linear'],['exp','Exponential']].map(([id,label])=>(
                <button key={id} className={`kpi-view ${method===id?'active':''}`} onClick={()=>setMethod(id)}>{label}</button>
              ))}
            </div>
          </div>

          {/* Stat row */}
          <div className="forecast-stats">
            <Card className="fc-stat"><div className="fcstat-label">Historical Periods</div><div className="fcstat-val">{n}</div></Card>
            <Card className="fc-stat"><div className="fcstat-label">CAGR</div><div className="fcstat-val" style={{color:cagr>0?'var(--green)':'var(--red)'}}>{cagr?`${cagr.toFixed(1)}%`:'—'}</div></Card>
            <Card className="fc-stat"><div className="fcstat-label">Trend</div><div className="fcstat-val" style={{color:trend.direction==='upward'?'var(--green)':'var(--red)'}}>{trend.direction==='upward'?'↑ Upward':'↓ Downward'}</div></Card>
            <Card className="fc-stat"><div className="fcstat-label">R² Fit</div><div className="fcstat-val">{trend.r_squared?.toFixed(3)??'—'}</div></Card>
            <Card className="fc-stat"><div className="fcstat-label">Forecast Periods</div><div className="fcstat-val">{ensembleF.length}</div></Card>
          </div>

          {/* Main chart */}
          <Card style={{padding:24,marginBottom:20}}>
            <div className="chart-header">
              <span className="chart-title">{metric.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())} — Forecast</span>
              <span className="forecast-badge">Forecast →</span>
            </div>
            <ResponsiveContainer width="100%" height={320}>
              <ComposedChart data={chartData} margin={{top:10,right:10,left:0,bottom:10}}>
                <defs>
                  <linearGradient id="histGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#3b82f6" stopOpacity={0.15}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="fcGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#10b981" stopOpacity={0.15}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false}/>
                <XAxis dataKey="label" tick={{fill:'var(--text3)',fontSize:10}} axisLine={false} tickLine={false}/>
                <YAxis tick={{fill:'var(--text3)',fontSize:10}} axisLine={false} tickLine={false} tickFormatter={fmtY}/>
                <Tooltip
                  contentStyle={{background:'rgba(22,13,46,0.95)',border:'1px solid rgba(255,255,255,0.12)',borderRadius:10,fontSize:12,backdropFilter:'blur(16px)',color:'#f5f0ff'}}
                  formatter={(v,n)=>[fmtY(v), n==='historical'?'Historical':n==='forecast'?'Forecast':n]}
                />
                <ReferenceLine x="Now" stroke="rgba(255,255,255,.2)" strokeDasharray="4 4"/>
                <Area dataKey="historical" fill="url(#histGrad)" stroke="#3b82f6" strokeWidth={2.5} dot={{fill:'#3b82f6',r:4}} activeDot={{r:6}} connectNulls/>
                <Area dataKey="forecast"   fill="url(#fcGrad)"  stroke="#10b981" strokeWidth={2.5} strokeDasharray="6 3" dot={{fill:'#10b981',r:5,symbol:'diamond'}} connectNulls/>
                <Bar dataKey="ci_high" fill="rgba(16,185,129,.06)" stackId="ci" legendType="none"/>
              </ComposedChart>
            </ResponsiveContainer>
          </Card>

          {/* Forecast table + multi-metric */}
          <div className="forecast-bottom">
            {activeF.length > 0 && (
              <Card>
                <div className="section-title" style={{marginBottom:12}}>Forecast Values</div>
                <table className="table">
                  <thead><tr><th>Period</th><th>Forecast</th>{ciLow.length?<><th>Lower 95%</th><th>Upper 95%</th></>:null}</tr></thead>
                  <tbody>
                    {activeF.map((v,i) => (
                      <tr key={i}>
                        <td>{futureLabels[i]}</td>
                        <td style={{fontWeight:700,color:'var(--green)'}}>{fmtY(v)}</td>
                        {ciLow.length ? <><td style={{color:'var(--text3)'}}>{fmtY(ciLow[i])}</td><td style={{color:'var(--text3)'}}>{fmtY(ciHigh[i])}</td></> : null}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Card>
            )}

            {available.length > 1 && (
              <Card>
                <div className="section-title" style={{marginBottom:12}}>Multi-Metric Outlook</div>
                <div className="multi-metric-grid">
                  {available.map(m => {
                    const fd = forecasts[m]
                    const dir = fd?.trend?.direction
                    const c = fd?.cagr_pct
                    return (
                      <div key={m} className="multi-metric-item">
                        <div className="multi-metric-name">{m.replace(/_/g,' ').replace(/\b\w/g,x=>x.toUpperCase())}</div>
                        <div className="multi-metric-arrow" style={{color:dir==='upward'?'var(--green)':'var(--red)'}}>{dir==='upward'?'↑':'↓'}</div>
                        <div className="multi-metric-cagr">{c?`CAGR ${c.toFixed(1)}%`:dir||'—'}</div>
                      </div>
                    )
                  })}
                </div>
              </Card>
            )}
          </div>

          {narrative && (
            <Card style={{marginTop:20}}>
              <div className="section-title" style={{marginBottom:12}}>AI Forecast Narrative</div>
              <div className="risk-narrative"><ReactMarkdown>{narrative}</ReactMarkdown></div>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
