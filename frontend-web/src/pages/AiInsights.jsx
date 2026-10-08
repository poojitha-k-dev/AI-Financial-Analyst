import { useEffect, useState } from 'react'
import { companiesAPI, analysisAPI } from '../api'
import { PageHeader, Card, Button, EmptyState, LoadingPage, RatingBadge, RiskPill, MetricCard } from '../components/ui'
import { Brain, Zap, RefreshCw, Download, FileText, FileSpreadsheet } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import toast from 'react-hot-toast'
import './AiInsights.css'

export default function AiInsights() {
  const [companies, setCompanies] = useState([])
  const [cid,      setCid]       = useState(null)
  const [stmts,    setStmts]     = useState([])
  const [stmtId,   setStmtId]    = useState(null)
  const [result,   setResult]    = useState(null)
  const [reports,  setReports]   = useState([])
  const [loading,  setLoading]   = useState(true)
  const [running,  setRunning]   = useState(false)
  const [tab,      setTab]       = useState('analysis')
  const [dlPdf,    setDlPdf]     = useState(false)
  const [dlXl,     setDlXl]     = useState(false)

  useEffect(() => {
    companiesAPI.list().then(r => {
      setCompanies(r.data)
      if (r.data.length) setCid(r.data[0].id)
    }).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!cid) return
    setResult(null); setStmts([])
    companiesAPI.statements(cid).then(r => {
      setStmts(r.data)
      // Always default to the LATEST uploaded period (index 0 = most recent)
      if (r.data.length) setStmtId(r.data[0].id)
    })
    analysisAPI.reports(cid).then(r => setReports(r.data)).catch(()=>{})
  }, [cid])

  const run = async () => {
    if (!cid) return
    setRunning(true)
    try {
      const r = await analysisAPI.full(cid, stmtId)
      setResult(r.data)
      toast.success('Analysis complete!')
      setTab('analysis')
      analysisAPI.reports(cid).then(r2 => setReports(r2.data))
    } catch(e) { toast.error(e.response?.data?.detail || 'Analysis failed. Check your API key.') }
    finally { setRunning(false) }
  }

  const downloadFile = async (type) => {
    const setter = type==='pdf' ? setDlPdf : setDlXl
    setter(true)
    try {
      const r = type==='pdf' ? await analysisAPI.exportPdf(cid) : await analysisAPI.exportExcel(cid)
      const co = companies.find(c=>c.id===cid)
      const ext = type==='pdf' ? 'pdf' : 'xlsx'
      const mime = type==='pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      const url = URL.createObjectURL(new Blob([r.data], { type: mime }))
      const a   = document.createElement('a')
      a.href = url; a.download = `${co?.name||'report'}_report.${ext}`; a.click()
      URL.revokeObjectURL(url)
      toast.success(`${type.toUpperCase()} downloaded!`)
    } catch { toast.error('Export failed. Run an analysis first.') }
    finally { setter(false) }
  }

  if (loading) return <LoadingPage/>

  const kpis    = result?.kpis || {}
  const risk    = result?.risk_analysis || {}
  const forecasts = result?.forecasts || {}
  const pr      = kpis.profitability || {}
  const liq     = kpis.liquidity     || {}
  const lev     = kpis.leverage      || {}
  const gr      = kpis.growth        || {}
  const composite = kpis.composite_scores || {}
  const riskSum = risk.risk_summary  || {}

  const TABS = [
    { id:'analysis', label:'📝 Full Analysis' },
    { id:'kpis',     label:'📊 KPI Summary' },
    { id:'risk',     label:'⚠️ Risk' },
    { id:'history',  label:`📁 History (${reports.length})` },
  ]

  return (
    <div>
      <PageHeader
        title="AI Financial Insights"
        subtitle="Full analysis powered by GPT-4o or Gemini 1.5 Pro"
        icon={Brain}
        actions={
          <div style={{display:'flex',gap:8,alignItems:'center',flexWrap:'wrap'}}>
            <select className="page-select" style={{width:180}} value={cid||''} onChange={e=>setCid(+e.target.value)}>
              {companies.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            {stmts.length > 0 && (
              <select className="page-select" style={{width:150}} value={stmtId||''} onChange={e => { setStmtId(+e.target.value); setResult(null) }}>
                {stmts.map((s, i) => (
                  <option key={s.id} value={s.id}>
                    {i === 0 ? `📌 ${s.period} (Latest)` : s.period}
                  </option>
                ))}
              </select>
            )}
            <Button onClick={run} loading={running} disabled={!stmts.length}>
              <Zap size={14}/> {running ? 'Analysing…' : result ? 'Re-run Analysis' : 'Run Analysis'}
            </Button>
          </div>
        }
      />

      {!stmts.length && !loading && (
        <div className="insights-no-data">
          <Brain size={40} color="var(--text3)"/>
          <p>No financial statements found. Upload data first.</p>
          <Button size="sm" onClick={()=>window.location.href='/upload'}>Upload Data →</Button>
        </div>
      )}

      {!result && stmts.length > 0 && reports.length > 0 && (
        <div className="insights-history-preview">
          <div className="section-title" style={{marginBottom:12}}>Previous Reports</div>
          {reports.slice(0,3).map(r => (
            <div key={r.id} className="prev-report" onClick={() => toast('Re-run analysis to update')}>
              <div className="prev-report-left">
                <div className="prev-report-title">{r.title}</div>
                <div className="prev-report-meta">
                  {r.created_at?.slice(0,10)} · {r.llm_provider}
                  {r.overall_rating && <> · <RatingBadge rating={r.overall_rating}/></>}
                </div>
                {r.executive_summary && <div className="prev-report-excerpt">{r.executive_summary.slice(0,140)}…</div>}
              </div>
              <Button size="sm" variant="secondary" onClick={run} loading={running}>
                <RefreshCw size={12}/> Re-run
              </Button>
            </div>
          ))}
        </div>
      )}

      {result && (
        <>
          {/* Summary strip */}
          <div className="insights-summary">
            <div className="insights-summary-left">
              <div className="insights-company">{result.company}</div>
              <div className="insights-period">Period: {result.period}</div>
              {result.overall_rating && <RatingBadge rating={result.overall_rating}/>}
            </div>
            <div className="insights-summary-metrics">
              <div className="ins-metric">
                <div className="ins-metric-val" style={{color: composite.overall_health>=7?'var(--green)':composite.overall_health>=4?'var(--yellow)':'var(--red)'}}>
                  {composite.overall_health?.toFixed(1)??'—'}
                </div>
                <div className="ins-metric-label">Health /10</div>
              </div>
              <div className="ins-metric">
                <div className="ins-metric-val" style={{color:'var(--text)'}}>{riskSum.overall_risk_level||'—'}</div>
                <div className="ins-metric-label">Risk Level</div>
              </div>
              <div className="ins-metric">
                <div className="ins-metric-val">{risk.altman_z_score?.score?.toFixed(2)??'—'}</div>
                <div className="ins-metric-label">Altman Z</div>
              </div>
              <div className="ins-metric">
                <div className="ins-metric-val">{risk.piotroski_f_score?.score!==undefined?`${risk.piotroski_f_score.score}/9`:'—'}</div>
                <div className="ins-metric-label">Piotroski</div>
              </div>
            </div>
            <div className="insights-exports">
              <Button size="sm" variant="secondary" onClick={()=>downloadFile('pdf')} loading={dlPdf}>
                <FileText size={13}/> PDF
              </Button>
              <Button size="sm" variant="secondary" onClick={()=>downloadFile('excel')} loading={dlXl}>
                <FileSpreadsheet size={13}/> Excel
              </Button>
            </div>
          </div>

          {/* Executive summary */}
          {result.executive_summary && (
            <Card accent style={{marginBottom:20}}>
              <div className="section-title" style={{marginBottom:8}}>Executive Summary</div>
              <div className="exec-summary"><ReactMarkdown>{result.executive_summary}</ReactMarkdown></div>
            </Card>
          )}

          {/* Tabs */}
          <div className="kpi-cats" style={{marginBottom:16}}>
            {TABS.map(t=>(
              <button key={t.id} className={`kpi-cat ${tab===t.id?'active':''}`} onClick={()=>setTab(t.id)}>{t.label}</button>
            ))}
          </div>

          <Card className="insights-tab-content">
            {tab === 'analysis' && (
              <div className="insights-markdown">
                <ReactMarkdown>{result.insights}</ReactMarkdown>
              </div>
            )}

            {tab === 'kpis' && (
              <div>
                {[['💰 Profitability','profitability'],['💧 Liquidity','liquidity'],['🏦 Leverage','leverage'],['💸 Cash Flow','cash_flow'],['📈 Growth','growth']].map(([label,key]) => {
                  const data = kpis[key] || {}
                  const entries = Object.entries(data).filter(([,v])=>v!=null)
                  if (!entries.length) return null
                  return (
                    <div key={key} className="kpi-section">
                      <div className="kpi-section-title">{label}</div>
                      <div className="kpi-mini-grid">
                        {entries.map(([k,v]) => {
                          const unit = k.includes('margin')||k.includes('return')||k.includes('growth')||k.includes('rate') ? '%' : k.includes('ratio')||k.includes('coverage')||k.includes('turnover') ? 'x' : k.includes('days') ? 'd' : ''
                          return (
                            <div key={k} className="kpi-mini-card">
                              <div className="kpi-mini-label">{k.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}</div>
                              <div className="kpi-mini-val">{v.toFixed(2)}<span className="kpi-mini-unit">{unit}</span></div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}

            {tab === 'risk' && (
              <div>
                <div className="risk-mini-row">
                  {[
                    ['Altman Z-Score', risk.altman_z_score?.score?.toFixed(2), risk.altman_z_score?.zone],
                    ['Piotroski F', risk.piotroski_f_score?.score!==undefined?`${risk.piotroski_f_score.score}/9`:null, risk.piotroski_f_score?.strength],
                    ['Custom Risk',  risk.custom_risk?.risk_score!==undefined?`${risk.custom_risk.risk_score}/10`:null, risk.custom_risk?.risk_level],
                  ].map(([label,val,sub])=>(
                    <div key={label} className="risk-mini-card">
                      <div className="rmcard-label">{label}</div>
                      <div className="rmcard-score">{val??'—'}</div>
                      <div className="rmcard-sub">{sub||'—'}</div>
                    </div>
                  ))}
                </div>
                {risk.custom_risk?.risk_factors?.length > 0 && (
                  <div style={{marginTop:16}}>
                    <div className="section-title" style={{marginBottom:10}}>Risk Flags</div>
                    {risk.custom_risk.risk_factors.map((f,i)=>(
                      <div key={i} className={`risk-flag risk-flag-${f.severity}`}>
                        <span className="risk-flag-icon">{f.severity==='high'?'🔴':'🟡'}</span>
                        <div><strong>{f.factor}</strong><p>{f.detail}</p></div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {tab === 'history' && (
              reports.length === 0 ? <div style={{color:'var(--text3)',textAlign:'center',padding:'40px 0'}}>No previous reports</div> :
              <div style={{display:'flex',flexDirection:'column',gap:12}}>
                {reports.map(r=>(
                  <div key={r.id} className="prev-report">
                    <div className="prev-report-left">
                      <div className="prev-report-title">{r.title}</div>
                      <div className="prev-report-meta">{r.created_at?.slice(0,10)} · {r.llm_provider} {r.overall_rating && <RatingBadge rating={r.overall_rating}/>}</div>
                      {r.executive_summary && <div className="prev-report-excerpt">{r.executive_summary.slice(0,160)}…</div>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  )
}
