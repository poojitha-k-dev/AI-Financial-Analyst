import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { authAPI } from '../api'
import toast from 'react-hot-toast'
import { Zap, Eye, EyeOff, BarChart2, Shield, TrendingUp, CheckCircle2, ArrowRight } from 'lucide-react'
import './Auth.css'

const FEATURES = [
  { icon: BarChart2,  title: 'KPI Engine',     desc: '40+ financial ratios calculated automatically' },
  { icon: Shield,     title: 'Risk Scoring',   desc: '3 academic models — Altman, Beneish, Piotroski' },
  { icon: TrendingUp, title: 'AI Forecasting', desc: 'Multi-period trend analysis and predictions' },
]

const PERKS = ['Free forever — no credit card', 'Upload CSV or Excel files', 'Unlimited AI analysis']

export default function Register() {
  const [form, setForm] = useState({ full_name: '', email: '', password: '', confirm: '', company_name: '' })
  const [show, setShow] = useState({ password: false, confirm: false })
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate  = useNavigate()

  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }))

  const handle = async e => {
    e.preventDefault()
    if (!form.full_name || !form.email || !form.password) { toast.error('Please fill all required fields'); return }
    if (form.password !== form.confirm) { toast.error('Passwords do not match'); return }
    if (form.password.length < 8) { toast.error('Password must be at least 8 characters'); return }
    setLoading(true)
    try {
      const res = await authAPI.register({
        full_name: form.full_name, email: form.email,
        password: form.password, company_name: form.company_name || undefined
      })
      login(res.data.access_token, res.data.user)
      toast.success(`Welcome to FinanceAI, ${res.data.user.full_name}!`)
      navigate('/')
    } catch (err) {
      const msg = err.response?.data?.detail
      const errorMsg = typeof msg === 'string' ? msg
        : Array.isArray(msg) ? msg.map(e => e.msg).join(', ')
        : err.message || 'Registration failed'
      toast.error(errorMsg)
    } finally { setLoading(false) }
  }

  const pwStrength = p => {
    if (!p) return 0
    let s = 0
    if (p.length >= 8) s++
    if (/[A-Z]/.test(p)) s++
    if (/[0-9]/.test(p)) s++
    if (/[^A-Za-z0-9]/.test(p)) s++
    return s
  }
  const strength = pwStrength(form.password)
  const strengthColors = ['', '#ef4444', '#f59e0b', '#3b82f6', '#10b981']
  const strengthLabels = ['', 'Weak', 'Fair', 'Good', 'Strong']

  return (
    <div className="auth-layout">
      <div className="auth-left">
        <div className="auth-orb1" />
        <div className="auth-orb2" />
        <div className="auth-brand">
          <div className="auth-logo"><Zap size={20} /></div>
          <div className="auth-brand-name"><span>Finance</span>AI</div>
        </div>

        <div className="auth-left-content">
          <h2 className="auth-tagline">
            Start analysing<br />
            financials in<br />
            <span className="highlight">60 seconds</span>
          </h2>
          <p className="auth-tagdesc">
            Upload a CSV and instantly get AI-generated KPI analysis, risk scores, and forecasts.
          </p>
          <div className="auth-features">
            {FEATURES.map(({ icon: Icon, title, desc }) => (
              <div key={title} className="auth-feature">
                <div className="auth-feature-icon"><Icon size={16} /></div>
                <div className="auth-feature-text">
                  <div className="auth-feature-title">{title}</div>
                  <div className="auth-feature-desc">{desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="auth-stats">
          {[
            { val: 'Free',  label: 'Forever'    },
            { val: 'CSV',   label: 'Excel PDF'  },
            { val: 'AI',    label: 'Powered'    },
          ].map(s => (
            <div key={s.label} className="auth-stat">
              <div className="auth-stat-val">{s.val}</div>
              <div className="auth-stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-card">
          <h1 className="auth-title">Create account</h1>
          <p className="auth-subtitle">Join thousands of analysts — free forever</p>

          {/* Perks */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 24 }}>
            {PERKS.map(p => (
              <div key={p} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: 'var(--text3)' }}>
                <CheckCircle2 size={13} color="var(--green)" />
                {p}
              </div>
            ))}
          </div>

          <form onSubmit={handle} className="auth-form">
            <div className="auth-field">
              <label>Full Name <span className="req">*</span></label>
              <input type="text" placeholder="Jane Smith"
                value={form.full_name} onChange={set('full_name')} autoFocus autoComplete="name" />
            </div>
            <div className="auth-field">
              <label>Work Email <span className="req">*</span></label>
              <input type="email" placeholder="jane@company.com"
                value={form.email} onChange={set('email')} autoComplete="email" />
            </div>
            <div className="auth-field">
              <label>Company / Organisation</label>
              <input type="text" placeholder="Acme Corp (optional)"
                value={form.company_name} onChange={set('company_name')} autoComplete="organization" />
            </div>
            <div className="auth-field">
              <label>Password <span className="req">*</span></label>
              <div className="auth-pass-wrap">
                <input type={show.password ? 'text' : 'password'} placeholder="Min. 8 characters"
                  value={form.password} onChange={set('password')} autoComplete="new-password" />
                <button type="button" className="auth-eye" onClick={() => setShow(s => ({ ...s, password: !s.password }))}>
                  {show.password ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
              {/* Password strength bar */}
              {form.password && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 2 }}>
                  <div style={{ flex: 1, display: 'flex', gap: 3 }}>
                    {[1,2,3,4].map(i => (
                      <div key={i} style={{
                        flex: 1, height: 3, borderRadius: 99,
                        background: i <= strength ? strengthColors[strength] : 'var(--bg5)',
                        transition: 'background 0.3s'
                      }} />
                    ))}
                  </div>
                  <span style={{ fontSize: 11, color: strengthColors[strength], fontWeight: 600 }}>
                    {strengthLabels[strength]}
                  </span>
                </div>
              )}
            </div>
            <div className="auth-field">
              <label>Confirm Password <span className="req">*</span></label>
              <div className="auth-pass-wrap">
                <input type={show.confirm ? 'text' : 'password'} placeholder="Repeat password"
                  value={form.confirm} onChange={set('confirm')} autoComplete="new-password" />
                <button type="button" className="auth-eye" onClick={() => setShow(s => ({ ...s, confirm: !s.confirm }))}>
                  {show.confirm ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
              {form.confirm && form.password !== form.confirm && (
                <div style={{ fontSize: 11, color: 'var(--red)', marginTop: 2 }}>Passwords don't match</div>
              )}
              {form.confirm && form.password === form.confirm && form.confirm.length >= 8 && (
                <div style={{ fontSize: 11, color: 'var(--green)', display: 'flex', alignItems: 'center', gap: 4, marginTop: 2 }}>
                  <CheckCircle2 size={11} /> Passwords match
                </div>
              )}
            </div>
            <button className="auth-submit" type="submit" disabled={loading}>
              {loading
                ? <><span className="auth-spinner" /> Creating account…</>
                : <><ArrowRight size={16} /> Create Free Account</>
              }
            </button>
          </form>

          <p className="auth-switch">
            Already have an account? <Link to="/login">Sign in →</Link>
          </p>
          <p className="auth-terms">
            By signing up you agree to our <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>
          </p>
        </div>
      </div>
    </div>
  )
}
