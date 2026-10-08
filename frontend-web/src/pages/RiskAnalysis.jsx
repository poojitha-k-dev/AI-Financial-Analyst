import { useEffect, useState } from 'react'
import { companiesAPI, analysisAPI } from '../api'
import { PageHeader, Card, Button, EmptyState, LoadingPage, RiskPill } from '../components/ui'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts'
import ReactMarkdown from 'react-markdown'
import './RiskAnalysis.css'

export default function RiskAnalysis() {
  const [companies, setCompanies] = useState([])
  const [cid,      setCid]       = useState(null)
  const [result,   setResult]    = useState(null)
  const [loading,  setLoading]   = useState(true)
  const [running,  setRunning]   = useState(false)
  const [tab,      setTab]       = useState('altman')

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
      const r = await analysisAPI.risk(cid)
      setResult(r.data)
    } catch(e) { }
    finally { setRunning(false) }
  }

  if (loading) return <LoadingPage/>

  const risk    = result?.risk_analysis || {}
  const altman  = risk.altman_z_score    || {}
  const pio     = risk.piotroski_f_score || {}
  const beneish = risk.beneish_m_score
  const custom  = risk.custom_risk       || {}
  const anomalies = risk.anomalies       || []
  const summary = risk.risk_summary      || {}
  const narrative = result?.narrative    || ''

  const zColor = altman.zone === 'Safe Zone' ? 'var(--green)' : altman.zone === 'Grey Zone' ? 'var(--yellow)' : 'var(--red)'
  const fColor = pio.strength === 'Strong' ? 'var(--green)' : pio.strength === 'Moderate' ? 'var(--yellow)' : 'var(--red)'

  const radarData = [
    { subject:'Profitability', value: Math.min((altman.components?.X3_ebit_ratio||0)*100+5, 10) },
    { subject:'Liquidity',     value: Math.min((custom.risk_score ? 10-custom.risk_score : 5), 10) },
    { subject:'Leverage',      value: Math.min((pio.score||0)*10/9, 10) },
    { subject:'Efficiency',    value: 5 },
    { subject:'Cash Flow',     value: 6 },
  ]

  const TABS = [
    { id:'altman',  label:'Altman Z-Score' },
    { id:'pio',     label:'Piotroski F' },
    { id:'beneish', label:'Beneish M' },
    { id:'flags',   label:`Flags (${custom.risk_factors?.length||0})` },
    { id:'ai',      label:'AI Narrative' },
  ]

  return (
    <div>
      <PageHeader title="Risk Analysis" subtitle="Altman Z · Piotroski F · Beneish M · Custom Risk Flags" icon={AlertTriangle}
        actions={
          <div style={{display:'flex',gap:10,alignItems:'center'}}>
            <select className="page-select" style={{width:180}} value={cid||''} onChange={e=>setCid(+e.target.value)}>
              {companies.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            <Button onClick={run} loading={running}><RefreshCw size={14}/> Run Analysis</Button>
          </div>
        }
      />

      {!result ? (
        <EmptyState icon={AlertTriangle} title="Run risk analysis" desc="Select a company and click 'Run Analysis' to get Altman Z-Score, Piotroski F-Score, Beneish M-Score and more."/>
      ) : (
        <>
          {/* Summary banner */}
          <div className={`risk-banner risk-banner-${summary.overall_risk_level?.toLowerCase()||'unknown'}`}>
            <div>
              <div className="risk-banner-label">Overall Risk Level</div>
              <div className="risk-banner-level">{summary.overall_risk_level || '—'}</div>
              <div className="risk-banner-meta">
                Piotroski: <strong>{summary.piotroski_strength}</strong> &nbsp;·&nbsp;
                Flags: <strong>{summary.total_risk_flags}</strong> &nbsp;·&nbsp;
                Anomalies: <strong>{summary.anomaly_count}</strong>
              </div>
            </div>
            <ResponsiveContainer width={200} height={150}>
              <RadarChart data={radarData} margin={{top:10,right:10,bottom:10,left:10}}>
                <PolarGrid stroke="rgba(255,255,255,.1)"/>
                <PolarAngleAxis dataKey="subject" tick={{fill:'rgba(255,255,255,.5)',fontSize:9}}/>
                <Radar dataKey="value" fill="rgba(255,255,255,.15)" stroke="rgba(255,255,255,.6)" strokeWidth={1.5}/>
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Model cards */}
          <div className="risk-model-cards">
            <Card className="risk-model-card">
              <div className="rmcard-label">Altman Z-Score</div>
              <div className="rmcard-score" style={{color:zColor}}>{altman.score?.toFixed(2)??'—'}</div>
              <div className="rmcard-sub">{altman.zone||'—'}</div>
            </Card>
            <Card className="risk-model-card">
              <div className="rmcard-label">Piotroski F-Score</div>
              <div className="rmcard-score" style={{color:fColor}}>{pio.score!==undefined?`${pio.score}/9`:'—'}</div>
              <div className="rmcard-sub">{pio.strength||'—'}</div>
            </Card>
            <Card className="risk-model-card">
              <div className="rmcard-label">Beneish M-Score</div>
              <div className="rmcard-score" style={{color:beneish?.likely_manipulator?'var(--red)':'var(--green)'}}>{beneish?.score?.toFixed(3)??'—'}</div>
              <div className="rmcard-sub">{beneish?.likely_manipulator?'⚠️ Manipulation Risk':'✅ Low Risk'}</div>
            </Card>
            <Card className="risk-model-card">
              <div className="rmcard-label">Custom Risk Score</div>
              <div className="rmcard-score" style={{color:custom.risk_score>=7?'var(--red)':custom.risk_score>=4?'var(--yellow)':'var(--green)'}}>{custom.risk_score!==undefined?`${custom.risk_score}/10`:'—'}</div>
              <div className="rmcard-sub">{custom.risk_level||'—'}</div>
            </Card>
          </div>

          {/* Detail tabs */}
          <div className="kpi-cats" style={{marginBottom:16}}>
            {TABS.map(t=>(
              <button key={t.id} className={`kpi-cat ${tab===t.id?'active':''}`} onClick={()=>setTab(t.id)}>{t.label}</button>
            ))}
          </div>

          <Card>
            {tab === 'altman' && (
              <div className="risk-detail">
                <div className="risk-detail-score" style={{color:zColor}}>{altman.score?.toFixed(2)}</div>
                <div className="risk-detail-zone">{altman.zone}</div>
                <p style={{color:'var(--text2)',fontSize:13,marginBottom:16}}>{altman.interpretation}</p>
                <div className="risk-components">
                  {Object.entries(altman.components||{}).map(([k,v])=>(
                    <div key={k} className="risk-comp-row">
                      <span className="risk-comp-key">{k}</span>
                      <span className="risk-comp-val">{v}</span>
                    </div>
                  ))}
                </div>
                <div className="risk-thresholds">
                  {Object.entries(altman.thresholds||{}).map(([k,v])=>(
                    <div key={k} className="risk-thresh"><span>{k.replace('_',' ').toUpperCase()}</span><strong>{v}</strong></div>
                  ))}
                </div>
              </div>
            )}
            {tab === 'pio' && (
              <div className="risk-detail">
                <div className="risk-detail-score" style={{color:fColor}}>{pio.score}/9</div>
                <div className="risk-detail-zone">{pio.strength}</div>
                <p style={{color:'var(--text2)',fontSize:13,marginBottom:16}}>{pio.interpretation}</p>
                <div className="pio-grid">
                  {Object.entries(pio.components||{}).map(([k,v])=>(
                    <div key={k} className={`pio-item ${v===1?'pio-pass':'pio-fail'}`}>
                      <span>{v===1?'✅':'❌'}</span>
                      <span>{k.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {tab === 'beneish' && (
              beneish ? (
                <div className="risk-detail">
                  <div className="risk-detail-score" style={{color:beneish.likely_manipulator?'var(--red)':'var(--green)'}}>{beneish.score?.toFixed(3)}</div>
                  <div className="risk-detail-zone">{beneish.likely_manipulator ? '⚠️ Likely Manipulator' : '✅ Low Manipulation Risk'}</div>
                  <p style={{color:'var(--text2)',fontSize:13,marginBottom:16}}>{beneish.interpretation}</p>
                  <div className="risk-components">
                    {Object.entries(beneish.components||{}).map(([k,v])=>(
                      <div key={k} className="risk-comp-row"><span className="risk-comp-key">{k}</span><span className="risk-comp-val">{v}</span></div>
                    ))}
                  </div>
                </div>
              ) : <div className="no-chart">Requires 2 periods of data</div>
            )}
            {tab === 'flags' && (
              <div>
                {custom.risk_factors?.length ? custom.risk_factors.map((f,i)=>(
                  <div key={i} className={`risk-flag risk-flag-${f.severity}`}>
                    <span className="risk-flag-icon">{f.severity==='high'?'🔴':'🟡'}</span>
                    <div><strong>{f.factor}</strong><p>{f.detail}</p></div>
                  </div>
                )) : <div className="no-chart">✅ No risk flags detected</div>}
                {anomalies.length > 0 && (
                  <>
                    <div className="section-title" style={{marginTop:20,marginBottom:10}}>Anomalies Detected</div>
                    {anomalies.map((a,i)=>(
                      <div key={i} className={`risk-flag risk-flag-${a.severity}`}>
                        <span className="risk-flag-icon">⚡</span>
                        <div><strong>{a.metric}</strong><p>{a.detail}</p></div>
                      </div>
                    ))}
                  </>
                )}
              </div>
            )}
            {tab === 'ai' && (
              narrative ? <div className="risk-narrative"><ReactMarkdown>{narrative}</ReactMarkdown></div>
                        : <div className="no-chart">Run AI Insights first to generate a narrative</div>
            )}
          </Card>
        </>
      )}
    </div>
  )
}
