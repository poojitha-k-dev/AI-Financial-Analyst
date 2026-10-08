import { useEffect, useState } from 'react'
import { companiesAPI, analysisAPI } from '../api'
import { PageHeader, Card, EmptyState, LoadingPage, Badge } from '../components/ui'
import { GitCompare } from 'lucide-react'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend, Cell } from 'recharts'
import './Benchmarking.css'

const SECTOR_BENCHMARKS = {
  Technology:             { gross_margin:58, operating_margin:18, net_margin:14, return_on_equity:22, current_ratio:2.1, debt_to_equity:0.45, fcf_margin:12, revenue_growth:12 },
  Healthcare:             { gross_margin:55, operating_margin:12, net_margin:9,  return_on_equity:15, current_ratio:2.5, debt_to_equity:0.6,  fcf_margin:8,  revenue_growth:8  },
  Finance:                { gross_margin:45, operating_margin:22, net_margin:18, return_on_equity:12, current_ratio:1.2, debt_to_equity:4.0,  fcf_margin:15, revenue_growth:6  },
  'Consumer Discretionary':{ gross_margin:35, operating_margin:8, net_margin:5.5, return_on_equity:16, current_ratio:1.5, debt_to_equity:1.1, fcf_margin:4,  revenue_growth:7  },
  'Consumer Staples':     { gross_margin:32, operating_margin:11, net_margin:7,  return_on_equity:20, current_ratio:1.2, debt_to_equity:0.9,  fcf_margin:6,  revenue_growth:4  },
  Energy:                 { gross_margin:30, operating_margin:10, net_margin:6,  return_on_equity:10, current_ratio:1.3, debt_to_equity:0.8,  fcf_margin:5,  revenue_growth:3  },
  Industrials:            { gross_margin:28, operating_margin:9,  net_margin:6,  return_on_equity:14, current_ratio:1.8, debt_to_equity:0.75, fcf_margin:5,  revenue_growth:5  },
  Default:                { gross_margin:38, operating_margin:11, net_margin:7.5, return_on_equity:14, current_ratio:1.6, debt_to_equity:0.85, fcf_margin:6, revenue_growth:6  },
}

const METRIC_LABELS = {
  gross_margin:'Gross Margin', operating_margin:'Operating Margin', net_margin:'Net Margin',
  return_on_equity:'ROE', current_ratio:'Current Ratio', debt_to_equity:'D/E Ratio',
  fcf_margin:'FCF Margin', revenue_growth:'Revenue Growth',
}

export default function Benchmarking() {
  const [companies, setCompanies] = useState([])
  const [cid,      setCid]       = useState(null)
  const [kpis,     setKpis]      = useState(null)
  const [loading,  setLoading]   = useState(true)
  const [view,     setView]      = useState('bar')

  useEffect(() => {
    companiesAPI.list().then(r => {
      setCompanies(r.data)
      if (r.data.length) setCid(r.data[0].id)
    }).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!cid) return
    setKpis(null)
    analysisAPI.kpis(cid).then(r => setKpis(r.data)).catch(()=>{})
  }, [cid])

  if (loading) return <LoadingPage/>

  const co      = companies.find(c=>c.id===cid)
  const sector  = co?.sector || 'Default'
  const bench   = SECTOR_BENCHMARKS[sector] || SECTOR_BENCHMARKS.Default
  const kData   = kpis?.kpis || {}
  const flatKpis = { ...kData.profitability||{}, ...kData.liquidity||{}, ...kData.leverage||{}, ...kData.cash_flow||{}, ...kData.growth||{} }

  const comparisons = Object.entries(bench).map(([key, industryVal]) => {
    const companyVal = flatKpis[key]
    if (companyVal == null) return null
    const delta = companyVal - industryVal
    const pct   = industryVal ? (delta / Math.abs(industryVal)) * 100 : 0
    const inv   = key === 'debt_to_equity'
    const rating = inv
      ? (pct < -20 ? 'Outperforming' : pct < 0 ? 'Above Average' : pct < 20 ? 'Below Average' : 'Underperforming')
      : (pct > 20  ? 'Outperforming' : pct > 0  ? 'Above Average' : pct > -20 ? 'Below Average' : 'Underperforming')
    return { key, label: METRIC_LABELS[key]||key, companyVal, industryVal, delta, pct, rating }
  }).filter(Boolean)

  const barData = comparisons.map(c => ({
    name:    c.label,
    Company: parseFloat(c.companyVal.toFixed(2)),
    Industry:parseFloat(c.industryVal.toFixed(2)),
    rating:  c.rating,
  }))

  const radarData = comparisons.slice(0,6).map(c => {
    const max = Math.max(Math.abs(c.companyVal), Math.abs(c.industryVal), 1)
    return {
      subject: c.label,
      Company: parseFloat(((c.companyVal/max)*10).toFixed(1)),
      Industry:parseFloat(((c.industryVal/max)*10).toFixed(1)),
    }
  })

  const outCount   = comparisons.filter(c=>c.rating==='Outperforming').length
  const underCount = comparisons.filter(c=>c.rating==='Underperforming').length

  const ratingColor = r => r==='Outperforming'?'var(--green)':r==='Above Average'?'var(--accent)':r==='Below Average'?'var(--yellow)':'var(--red)'
  const ratingBg    = r => r==='Outperforming'?'rgba(16,185,129,.12)':r==='Above Average'?'rgba(59,130,246,.1)':r==='Below Average'?'rgba(245,158,11,.1)':'rgba(239,68,68,.1)'

  return (
    <div>
      <PageHeader title="Industry Benchmarking" subtitle="Compare KPIs against sector medians" icon={GitCompare}
        actions={
          <div style={{display:'flex',gap:10,alignItems:'center'}}>
            <select className="page-select" style={{width:200}} value={cid||''} onChange={e=>setCid(+e.target.value)}>
              {companies.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
        }
      />

      {!kpis ? (
        <EmptyState icon={GitCompare} title="No KPI data" desc="Upload statements and run KPI analysis first."/>
      ) : (
        <>
          {/* Summary */}
          <div className="bench-summary">
            <Card className="bench-stat"><div className="bench-stat-label">Sector</div><div className="bench-stat-val">{sector}</div></Card>
            <Card className="bench-stat"><div className="bench-stat-label">Metrics Compared</div><div className="bench-stat-val">{comparisons.length}</div></Card>
            <Card className="bench-stat"><div className="bench-stat-label">Outperforming</div><div className="bench-stat-val" style={{color:'var(--green)'}}>{outCount}</div></Card>
            <Card className="bench-stat"><div className="bench-stat-label">Underperforming</div><div className="bench-stat-val" style={{color:'var(--red)'}}>{underCount}</div></Card>
            <Card className="bench-stat"><div className="bench-stat-label">Above Average</div><div className="bench-stat-val" style={{color:'var(--accent)'}}>{comparisons.filter(c=>c.rating==='Above Average').length}</div></Card>
          </div>

          {/* View switcher */}
          <div className="kpi-views" style={{marginBottom:16}}>
            {[['bar','Bar Chart'],['radar','Radar'],['table','Table']].map(([id,label])=>(
              <button key={id} className={`kpi-view ${view===id?'active':''}`} onClick={()=>setView(id)}>{label}</button>
            ))}
          </div>

          <Card>
            {view === 'bar' && (
              <>
                <div className="chart-header"><span className="chart-title">Company vs Industry Median</span><div style={{display:'flex',gap:12,marginLeft:'auto'}}><span style={{fontSize:11,color:'var(--primary-light)'}}>■ Company</span><span style={{fontSize:11,color:'rgba(255,255,255,.3)'}}>■ Industry</span></div></div>
                <ResponsiveContainer width="100%" height={360}>
                  <BarChart data={barData} margin={{top:10,right:10,left:0,bottom:60}}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false}/>
                    <XAxis dataKey="name" tick={{fill:'var(--text3)',fontSize:10}} angle={-30} textAnchor="end" interval={0} axisLine={false} tickLine={false}/>
                    <YAxis tick={{fill:'var(--text3)',fontSize:10}} axisLine={false} tickLine={false}/>
                    <Tooltip contentStyle={{background:'rgba(22,13,46,0.95)',border:'1px solid rgba(255,255,255,0.12)',borderRadius:10,fontSize:12,backdropFilter:'blur(16px)',color:'#f5f0ff'}}/>
                    <Bar dataKey="Company" radius={[4,4,0,0]} maxBarSize={40}>
                      {barData.map((d,i)=><Cell key={i} fill={ratingColor(d.rating)}/>)}
                    </Bar>
                    <Bar dataKey="Industry" fill="rgba(255,255,255,.15)" radius={[4,4,0,0]} maxBarSize={40}/>
                  </BarChart>
                </ResponsiveContainer>
                <div className="bench-legend">
                  {[['Outperforming','var(--green)'],['Above Average','var(--accent)'],['Below Average','var(--yellow)'],['Underperforming','var(--red)']].map(([label,color])=>(
                    <span key={label} style={{fontSize:11,color,display:'flex',alignItems:'center',gap:4}}><span style={{width:10,height:10,borderRadius:2,background:color,display:'inline-block'}}/>{label}</span>
                  ))}
                  <span style={{fontSize:11,color:'rgba(255,255,255,.3)',display:'flex',alignItems:'center',gap:4}}><span style={{width:10,height:10,borderRadius:2,background:'rgba(255,255,255,.15)',display:'inline-block'}}/> Industry Median</span>
                </div>
              </>
            )}

            {view === 'radar' && radarData.length >= 3 && (
              <ResponsiveContainer width="100%" height={380}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="var(--border)"/>
                  <PolarAngleAxis dataKey="subject" tick={{fill:'var(--text3)',fontSize:10}}/>
                  <Radar dataKey="Company"  fill="rgba(168,85,247,.2)"  stroke="#a855f7" strokeWidth={2} name="Company"/>
                  <Radar dataKey="Industry" fill="rgba(6,182,212,.1)"   stroke="#06b6d4" strokeWidth={2} strokeDasharray="4 2" name="Industry"/>
                  <Legend wrapperStyle={{fontSize:11,color:'var(--text3)'}}/>
                </RadarChart>
              </ResponsiveContainer>
            )}

            {view === 'table' && (
              <table className="table">
                <thead>
                  <tr><th>Metric</th><th>Company</th><th>Industry</th><th>Delta</th><th>vs Industry</th><th>Rating</th></tr>
                </thead>
                <tbody>
                  {comparisons.map(c=>(
                    <tr key={c.key}>
                      <td style={{fontWeight:600}}>{c.label}</td>
                      <td style={{fontWeight:700,color:ratingColor(c.rating)}}>{c.companyVal.toFixed(2)}</td>
                      <td style={{color:'var(--text3)'}}>{c.industryVal.toFixed(2)}</td>
                      <td style={{color:c.delta>=0?'var(--green)':'var(--red)'}}>{c.delta>0?'+':''}{c.delta.toFixed(2)}</td>
                      <td style={{color:c.pct>=0?'var(--green)':'var(--red)'}}>{c.pct>0?'+':''}{c.pct.toFixed(1)}%</td>
                      <td><span style={{fontSize:11,fontWeight:600,color:ratingColor(c.rating),background:ratingBg(c.rating),padding:'2px 10px',borderRadius:'999px'}}>{c.rating}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Card>
        </>
      )}
    </div>
  )
}
