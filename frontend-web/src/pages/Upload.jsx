import { useEffect, useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { companiesAPI, uploadAPI } from '../api'
import { PageHeader, Card, Button, Select, EmptyState } from '../components/ui'
import { Upload as UploadIcon, FileText, CheckCircle, AlertCircle, Building2, Info } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import './Upload.css'

const fmt = v => {
  if (!v && v!==0) return '—'
  const a = Math.abs(v)
  if (a>=1e9) return `$${(v/1e9).toFixed(2)}B`
  if (a>=1e6) return `$${(v/1e6).toFixed(1)}M`
  return `$${v.toLocaleString()}`
}

export default function Upload() {
  const [companies, setCompanies] = useState([])
  const [form,      setForm]      = useState({ company_id:'', period:'', period_type:'annual', statement_type:'combined' })
  const [file,      setFile]      = useState(null)
  const [uploading, setUploading] = useState(false)
  const [result,    setResult]    = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    companiesAPI.list().then(r => {
      setCompanies(r.data)
      if (r.data.length) setForm(p => ({ ...p, company_id: r.data[0].id }))
    })
  }, [])

  const onDrop = useCallback(files => {
    if (files[0]) { setFile(files[0]); setResult(null) }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'application/pdf':[], 'text/csv':[], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':[], 'application/vnd.ms-excel':[] },
    multiple: false, maxSize: 50*1024*1024
  })

  const submit = async () => {
    if (!form.company_id) { toast.error('Select a company'); return }
    if (!form.period.trim()) { toast.error('Enter a period e.g. 2023-FY'); return }
    if (!file) { toast.error('Select a file'); return }
    setUploading(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('company_id', form.company_id)
      fd.append('period', form.period)
      fd.append('period_type', form.period_type)
      fd.append('statement_type', form.statement_type)
      const r = await uploadAPI.statement(fd)
      setResult(r.data)
      toast.success(`Parsed ${r.data.fields_extracted} fields, ${r.data.kpis_calculated} KPIs!`)
      setFile(null)
    } catch(err) {
      toast.error(err.response?.data?.detail || 'Upload failed')
    } finally { setUploading(false) }
  }

  if (!companies.length) return (
    <EmptyState icon={Building2} title="No companies yet"
      desc="Add a company first, then upload financial statements."
      action={<Button onClick={() => navigate('/companies')}><Building2 size={14}/> Add Company</Button>}/>
  )

  return (
    <div>
      <PageHeader title="Upload Financial Statement" subtitle="Import PDF, CSV, or Excel financial data" icon={UploadIcon}/>

      <div className="upload-layout">
        {/* Form */}
        <div className="upload-form-col">
          <Card>
            <div className="section-title" style={{marginBottom:16}}>Statement Details</div>

            <div className="upload-fields">
              <div className="field">
                <label className="field-label">Company *</label>
                <select className="field-input field-select" value={form.company_id} onChange={e => setForm(p=>({...p,company_id:e.target.value}))}>
                  {companies.map(c => <option key={c.id} value={c.id}>{c.name}{c.ticker?` (${c.ticker})`:''}</option>)}
                </select>
              </div>
              <div className="field">
                <label className="field-label">Period *</label>
                <input className="field-input" placeholder="e.g. 2023-FY  or  2023-Q3" value={form.period} onChange={e => setForm(p=>({...p,period:e.target.value}))}/>
              </div>
              <div className="field">
                <label className="field-label">Period Type</label>
                <select className="field-input field-select" value={form.period_type} onChange={e=>setForm(p=>({...p,period_type:e.target.value}))}>
                  <option value="annual">Annual</option>
                  <option value="quarterly">Quarterly</option>
                </select>
              </div>
              <div className="field">
                <label className="field-label">Statement Type</label>
                <select className="field-input field-select" value={form.statement_type} onChange={e=>setForm(p=>({...p,statement_type:e.target.value}))}>
                  <option value="combined">Combined (All)</option>
                  <option value="income_statement">Income Statement</option>
                  <option value="balance_sheet">Balance Sheet</option>
                  <option value="cash_flow">Cash Flow</option>
                </select>
              </div>
            </div>

            {/* Dropzone */}
            <div {...getRootProps()} className={`dropzone ${isDragActive ? 'dropzone-active' : ''} ${file ? 'dropzone-has-file' : ''}`}>
              <input {...getInputProps()} />
              {file ? (
                <div className="dropzone-file">
                  <FileText size={28} color="var(--accent)"/>
                  <div className="dropzone-filename">{file.name}</div>
                  <div className="dropzone-filesize">{(file.size/1024).toFixed(0)} KB</div>
                  <button className="dropzone-remove" onClick={e=>{e.stopPropagation();setFile(null)}}>Remove</button>
                </div>
              ) : (
                <div className="dropzone-idle">
                  <UploadIcon size={32} color={isDragActive ? 'var(--accent)' : 'var(--text3)'}/>
                  <div className="dropzone-text">{isDragActive ? 'Drop it here!' : 'Drag & drop or click to upload'}</div>
                  <div className="dropzone-hint">PDF · CSV · Excel (max 50MB)</div>
                </div>
              )}
            </div>

            <Button className="upload-btn" onClick={submit} loading={uploading} disabled={!file||!form.period}>
              <UploadIcon size={14}/> Upload & Parse
            </Button>
          </Card>

          {/* Result */}
          {result && (
            <Card className="upload-result fade-in">
              <div className="result-header">
                <CheckCircle size={20} color="var(--green)"/>
                <span className="result-title">Upload Successful</span>
              </div>
              <div className="result-stats">
                <div className="result-stat"><div className="result-stat-val">{result.fields_extracted}</div><div className="result-stat-label">Fields</div></div>
                <div className="result-stat"><div className="result-stat-val">{result.kpis_calculated}</div><div className="result-stat-label">KPIs</div></div>
                <div className="result-stat"><div className="result-stat-val">{result.periods_imported?.length||1}</div><div className="result-stat-label">Periods</div></div>
              </div>
              {result.preview && (
                <div className="result-preview">
                  {[
                    ['Revenue',      result.preview.revenue],
                    ['Net Income',   result.preview.net_income],
                    ['Total Assets', result.preview.total_assets],
                  ].map(([label,val]) => val && (
                    <div key={label} className="result-preview-item">
                      <span className="result-preview-label">{label}</span>
                      <span className="result-preview-val">{fmt(val)}</span>
                    </div>
                  ))}
                  {[
                    ['Gross Margin', result.preview.gross_margin],
                    ['Net Margin',   result.preview.net_margin],
                  ].map(([label,val]) => val && (
                    <div key={label} className="result-preview-item">
                      <span className="result-preview-label">{label}</span>
                      <span className="result-preview-val">{val.toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              )}
              <Button size="sm" onClick={() => navigate('/insights')} style={{marginTop:14}}>
                Run AI Analysis →
              </Button>
            </Card>
          )}
        </div>

        {/* Guide */}
        <div className="upload-guide-col">
          <Card>
            <div className="section-title" style={{marginBottom:14}}>Supported Formats</div>
            <div className="guide-blocks">
              <div className="guide-block">
                <div className="guide-block-title">📄 PDF Annual Reports</div>
                <ul className="guide-list">
                  <li>Annual reports, 10-K filings</li>
                  <li>Extracts financial tables automatically</li>
                  <li>Works with most structured PDFs</li>
                </ul>
              </div>
              <div className="guide-block">
                <div className="guide-block-title">📊 CSV / Excel Files</div>
                <div className="guide-code">Metric,Value<br/>Revenue,394328000000<br/>Net Income,99803000000</div>
                <div className="guide-or">OR multi-period (all years imported):</div>
                <div className="guide-code">Metric,2021,2022,2023<br/>Revenue,365B,394B,383B</div>
              </div>
              <div className="guide-block">
                <div className="guide-block-title">💡 Tips</div>
                <ul className="guide-list">
                  <li>Numbers like (1,234) treated as negative</li>
                  <li>Suffixes 1.2B, 350M auto-converted</li>
                  <li>Multi-period CSVs import all years at once</li>
                </ul>
              </div>
            </div>
          </Card>

          <Card style={{marginTop:16}}>
            <div className="section-title" style={{marginBottom:12}}>Sample Data</div>
            <p style={{fontSize:12,color:'var(--text3)',marginBottom:14}}>Download ready-to-use sample files to test the platform instantly.</p>
            <div className="sample-btns">
              <a href="/sample/apple_financials_2023.csv" download className="sample-btn">⬇ Apple Inc. CSV</a>
              <a href="/sample/tesla_financials_2023.csv" download className="sample-btn">⬇ Tesla Inc. CSV</a>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
