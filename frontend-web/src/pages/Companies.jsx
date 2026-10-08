import { useEffect, useState } from 'react'
import { companiesAPI } from '../api'
import { PageHeader, Card, Button, Input, Select, Badge, EmptyState, Table } from '../components/ui'
import { Building2, Plus, Pencil, Trash2, X, Check, ChevronDown, ChevronUp } from 'lucide-react'
import toast from 'react-hot-toast'
import './Companies.css'

const SECTORS = ['','Technology','Healthcare','Finance','Consumer Discretionary',
  'Consumer Staples','Energy','Industrials','Materials','Real Estate','Utilities','Communication Services']
const CURRENCIES = ['USD','EUR','GBP','JPY','CAD','AUD','CHF','CNY','INR']

const EMPTY = { name:'', ticker:'', sector:'', industry:'', country:'', currency:'USD', website:'', description:'' }

export default function Companies() {
  const [companies, setCompanies] = useState([])
  const [loading,   setLoading]   = useState(true)
  const [showAdd,   setShowAdd]   = useState(false)
  const [editId,    setEditId]    = useState(null)
  const [form,      setForm]      = useState(EMPTY)
  const [saving,    setSaving]    = useState(false)
  const [deleting,  setDeleting]  = useState(null)
  const [search,    setSearch]    = useState('')
  const [expanded,  setExpanded]  = useState(null)

  const load = () => {
    setLoading(true)
    companiesAPI.list({ search: search || undefined }).then(r => setCompanies(r.data)).finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [search])

  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }))

  const save = async () => {
    if (!form.name.trim()) { toast.error('Company name is required'); return }
    setSaving(true)
    try {
      const payload = { ...form, ticker: form.ticker||null, sector: form.sector||null, industry: form.industry||null, country: form.country||null, website: form.website||null, description: form.description||null }
      if (editId) {
        await companiesAPI.update(editId, payload)
        toast.success('Company updated')
      } else {
        await companiesAPI.create(payload)
        toast.success(`${form.name} added!`)
      }
      setShowAdd(false); setEditId(null); setForm(EMPTY); load()
    } catch(err) { toast.error(err.response?.data?.detail || 'Save failed') }
    finally { setSaving(false) }
  }

  const del = async id => {
    setDeleting(id)
    try {
      await companiesAPI.delete(id)
      toast.success('Company deleted')
      load()
    } catch { toast.error('Delete failed') }
    finally { setDeleting(null) }
  }

  const startEdit = c => {
    setForm({ name:c.name, ticker:c.ticker||'', sector:c.sector||'', industry:c.industry||'',
      country:c.country||'', currency:c.currency||'USD', website:c.website||'', description:c.description||'' })
    setEditId(c.id); setShowAdd(true)
  }

  return (
    <div>
      <PageHeader
        title="Company Portfolio"
        subtitle="Manage the companies you're analysing"
        icon={Building2}
        actions={
          <Button onClick={() => { setShowAdd(s=>!s); setEditId(null); setForm(EMPTY) }}>
            <Plus size={14}/> Add Company
          </Button>
        }
      />

      {/* Add / Edit form */}
      {showAdd && (
        <Card className="add-form fade-in" style={{marginBottom:24}}>
          <div className="add-form-header">
            <span className="add-form-title">{editId ? 'Edit Company' : 'New Company'}</span>
            <button className="icon-btn" onClick={() => { setShowAdd(false); setEditId(null); setForm(EMPTY) }}><X size={16}/></button>
          </div>
          <div className="add-form-grid">
            <Input label="Company Name *" value={form.name} onChange={set('name')} placeholder="Apple Inc." />
            <Input label="Ticker Symbol"  value={form.ticker} onChange={set('ticker')} placeholder="AAPL" />
            <Select label="Sector" value={form.sector} onChange={set('sector')}>
              {SECTORS.map(s => <option key={s} value={s}>{s || 'Select sector…'}</option>)}
            </Select>
            <Input label="Industry"  value={form.industry} onChange={set('industry')} placeholder="Consumer Electronics" />
            <Input label="Country"   value={form.country}  onChange={set('country')}  placeholder="United States" />
            <Select label="Currency" value={form.currency} onChange={set('currency')}>
              {CURRENCIES.map(c => <option key={c} value={c}>{c}</option>)}
            </Select>
            <Input label="Website" value={form.website} onChange={set('website')} placeholder="https://apple.com" className="col-span-2"/>
          </div>
          <div className="field" style={{marginTop:12}}>
            <label className="field-label">Description</label>
            <textarea className="field-input" rows={2} value={form.description} onChange={set('description')} placeholder="Brief company description…" style={{resize:'vertical'}}/>
          </div>
          <div className="add-form-actions">
            <Button variant="secondary" onClick={() => { setShowAdd(false); setEditId(null); setForm(EMPTY) }}>Cancel</Button>
            <Button onClick={save} loading={saving}>
              <Check size={14}/> {editId ? 'Save Changes' : 'Add Company'}
            </Button>
          </div>
        </Card>
      )}

      {/* Search */}
      <div style={{marginBottom:16}}>
        <input className="field-input" style={{maxWidth:320}} placeholder="🔍  Search companies…" value={search} onChange={e=>setSearch(e.target.value)}/>
      </div>

      {/* List */}
      {loading ? (
        <div className="loading-page"><div className="auth-spinner"/></div>
      ) : companies.length === 0 ? (
        <EmptyState icon={Building2} title="No companies yet" desc="Add your first company to get started with financial analysis."
          action={<Button onClick={() => setShowAdd(true)}><Plus size={14}/> Add Company</Button>}/>
      ) : (
        <div className="companies-list">
          {companies.map(c => (
            <Card key={c.id} className="company-row">
              <div className="company-row-main">
                <div className="company-avatar">{c.name[0].toUpperCase()}</div>
                <div className="company-info">
                  <div className="company-name">{c.name} {c.ticker && <span className="company-ticker">{c.ticker}</span>}</div>
                  <div className="company-meta">
                    {c.sector   && <span className="meta-tag">{c.sector}</span>}
                    {c.industry && <span className="meta-tag">{c.industry}</span>}
                    {c.country  && <span className="meta-tag">📍 {c.country}</span>}
                    <span className="meta-tag">{c.statement_count} period{c.statement_count!==1?'s':''}</span>
                    {c.latest_period && <span className="meta-tag">Latest: {c.latest_period}</span>}
                  </div>
                </div>
                <div className="company-actions">
                  <button className="icon-btn" title="Edit" onClick={() => startEdit(c)}><Pencil size={15}/></button>
                  <button className="icon-btn danger" title="Delete" onClick={() => del(c.id)} disabled={deleting===c.id}>
                    {deleting===c.id ? <span className="auth-spinner" style={{width:14,height:14}}/> : <Trash2 size={15}/>}
                  </button>
                  <button className="icon-btn" onClick={() => setExpanded(expanded===c.id ? null : c.id)}>
                    {expanded===c.id ? <ChevronUp size={15}/> : <ChevronDown size={15}/>}
                  </button>
                </div>
              </div>

              {expanded===c.id && (
                <div className="company-expanded fade-in">
                  <div className="company-detail-grid">
                    <div><span className="detail-label">Currency</span><span className="detail-val">{c.currency}</span></div>
                    {c.website && <div><span className="detail-label">Website</span><a href={c.website} target="_blank" rel="noreferrer" className="detail-link">{c.website}</a></div>}
                    {c.description && <div className="col-span-2"><span className="detail-label">Description</span><span className="detail-val">{c.description}</span></div>}
                  </div>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
