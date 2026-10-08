import { useEffect, useState } from 'react'
import { companiesAPI, analysisAPI } from '../api'
import { PageHeader, Card, Button, EmptyState, LoadingPage, RatingBadge } from '../components/ui'
import { FileText, FileSpreadsheet, Download, Clock, Brain } from 'lucide-react'
import toast from 'react-hot-toast'
import './Reports.css'

export default function Reports() {
  const [companies, setCompanies] = useState([])
  const [cid,      setCid]       = useState(null)
  const [reports,  setReports]   = useState([])
  const [loading,  setLoading]   = useState(true)
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
    analysisAPI.reports(cid).then(r => setReports(r.data)).catch(()=>setReports([]))
  }, [cid])

  const download = async (type) => {
    const setter = type==='pdf' ? setDlPdf : setDlXl
    setter(true)
    try {
      const r   = type==='pdf' ? await analysisAPI.exportPdf(cid) : await analysisAPI.exportExcel(cid)
      const co  = companies.find(c=>c.id===cid)
      const ext = type==='pdf' ? 'pdf' : 'xlsx'
      const mime= type==='pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      const url = URL.createObjectURL(new Blob([r.data],{type:mime}))
      const a   = document.createElement('a')
      a.href=url; a.download=`${co?.name||'report'}_financial_report.${ext}`; a.click()
      URL.revokeObjectURL(url)
      toast.success(`${type.toUpperCase()} report downloaded!`)
    } catch { toast.error('Export failed — run an AI analysis first.') }
    finally { setter(false) }
  }

  if (loading) return <LoadingPage/>

  return (
    <div>
      <PageHeader title="Reports" subtitle="Export professional PDF and Excel financial reports" icon={FileText}
        actions={
          <select className="page-select" style={{width:200}} value={cid||''} onChange={e=>setCid(+e.target.value)}>
            {companies.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        }
      />

      {/* Export buttons */}
      <div className="reports-export-grid">
        <Card className="export-card">
          <div className="export-card-icon" style={{background:'rgba(59,130,246,.1)',color:'var(--accent)'}}>
            <FileText size={28}/>
          </div>
          <div className="export-card-title">PDF Report</div>
          <div className="export-card-desc">
            Professional A4 PDF with cover page, full KPI tables, risk model scores,
            composite health scores, and complete AI-generated narrative.
          </div>
          <ul className="export-features">
            <li>✓ Cover page with company & period</li>
            <li>✓ Key metrics summary table</li>
            <li>✓ 5-category KPI analysis</li>
            <li>✓ Altman Z-Score breakdown</li>
            <li>✓ Full AI narrative</li>
          </ul>
          <Button onClick={() => download('pdf')} loading={dlPdf} className="export-btn">
            <Download size={14}/> Download PDF
          </Button>
        </Card>

        <Card className="export-card">
          <div className="export-card-icon" style={{background:'rgba(16,185,129,.1)',color:'var(--green)'}}>
            <FileSpreadsheet size={28}/>
          </div>
          <div className="export-card-title">Excel Report</div>
          <div className="export-card-desc">
            Multi-sheet Excel workbook with fully formatted data across all KPI
            categories — ready for further analysis or board presentations.
          </div>
          <ul className="export-features">
            <li>✓ Summary sheet</li>
            <li>✓ Profitability sheet</li>
            <li>✓ Liquidity & Leverage sheets</li>
            <li>✓ Efficiency & Cash Flow sheets</li>
            <li>✓ Growth KPIs sheet</li>
          </ul>
          <Button variant="secondary" onClick={() => download('excel')} loading={dlXl} className="export-btn">
            <Download size={14}/> Download Excel
          </Button>
        </Card>
      </div>

      {/* Report history */}
      {reports.length > 0 && (
        <div style={{marginTop:28}}>
          <div className="section-title" style={{marginBottom:14}}>Analysis Report History</div>
          <div className="reports-history">
            {reports.map(r => (
              <Card key={r.id} className="report-history-item">
                <div className="rhi-left">
                  <div className="rhi-header">
                    <Brain size={15} color="var(--accent)"/>
                    <span className="rhi-title">{r.title}</span>
                    {r.overall_rating && <RatingBadge rating={r.overall_rating}/>}
                    {r.is_pinned && <span className="rhi-pinned">📌</span>}
                  </div>
                  {r.executive_summary && (
                    <div className="rhi-excerpt">{r.executive_summary.slice(0,180)}…</div>
                  )}
                  <div className="rhi-meta">
                    <Clock size={11}/>
                    <span>{r.created_at?.slice(0,16).replace('T',' ')}</span>
                    <span>·</span>
                    <span>{r.llm_provider}</span>
                    {r.has_pdf   && <span className="rhi-badge">PDF</span>}
                    {r.has_excel && <span className="rhi-badge">Excel</span>}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Tips */}
      <Card style={{marginTop:24}}>
        <div className="section-title" style={{marginBottom:10}}>Tips for Best Reports</div>
        <div className="report-tips">
          {[
            ['🤖','Run AI Insights first','Generates the narrative that populates the report.'],
            ['📅','Upload 3+ periods','Enables growth KPIs and trend sections.'],
            ['🏷️','Set company sector','Enables industry benchmarking context in AI narrative.'],
            ['💱','Set correct currency','Ensures financial values are labelled correctly.'],
          ].map(([icon,title,desc])=>(
            <div key={title} className="report-tip">
              <div className="tip-icon">{icon}</div>
              <div><div className="tip-title">{title}</div><div className="tip-desc">{desc}</div></div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
