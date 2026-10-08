import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { authAPI } from '../api'
import toast from 'react-hot-toast'
import { Zap, Eye, EyeOff, TrendingUp, Shield, Brain, ArrowRight } from 'lucide-react'
import './Auth.css'

const FEATURES = [
  { icon: TrendingUp, title: '40+ KPI Ratios', desc: 'Auto-calculated from your financial data' },
  { icon: Shield,     title: 'Risk Models',    desc: 'Altman Z, Beneish M, Piotroski F-Score' },
  { icon: Brain,      title: 'AI Narratives',  desc: 'GPT-4o & Gemini powered analysis' },
]

export default function Login() {
  const [form, setForm]   = useState({ email: '', password: '' })
  const [show, setShow]   = useState(false)
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate  = useNavigate()

  const handle = async e => {
    e.preventDefault()
    if (!form.email || !form.password) { toast.error('Fill in all fields'); return }
    setLoading(true)
    try {
      const res = await authAPI.login({ username: form.email, password: form.password })
      login(res.data.access_token, res.data.user)
      toast.success(`Welcome back, ${res.data.user.full_name}!`)
      navigate('/')
    } catch (err) {
      const msg = err.response?.data?.detail
      const errorMsg = typeof msg === 'string' ? msg
        : Array.isArray(msg) ? msg.map(e => e.msg).join(', ')
        : err.message || 'Login failed'
      toast.error(errorMsg)
    } finally { setLoading(false) }
  }

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
            Intelligent<br />
            <span className="highlight">Financial</span><br />
            Analysis
          </h2>
          <p className="auth-tagdesc">
            Upload your financial statements and get AI-powered insights, risk scores, and forecasts in seconds.
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
            { val: '40+',   label: 'KPI Metrics' },
            { val: '3',     label: 'Risk Models'  },
            { val: 'AI',    label: 'Powered'      },
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
          <h1 className="auth-title">Sign in</h1>
          <p className="auth-subtitle">Welcome back — your dashboard is waiting</p>

          <form onSubmit={handle} className="auth-form">
            <div className="auth-field">
              <label>Email <span className="req">*</span></label>
              <input
                type="email" placeholder="you@company.com"
                value={form.email}
                onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
                autoFocus autoComplete="email"
              />
            </div>
            <div className="auth-field">
              <label>Password <span className="req">*</span></label>
              <div className="auth-pass-wrap">
                <input
                  type={show ? 'text' : 'password'} placeholder="••••••••"
                  value={form.password}
                  onChange={e => setForm(p => ({ ...p, password: e.target.value }))}
                  autoComplete="current-password"
                />
                <button type="button" className="auth-eye" onClick={() => setShow(s => !s)}>
                  {show ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>
            <button className="auth-submit" type="submit" disabled={loading}>
              {loading
                ? <><span className="auth-spinner" /> Signing in…</>
                : <><ArrowRight size={16} /> Sign In</>
              }
            </button>
          </form>

          <p className="auth-switch">
            Don't have an account? <Link to="/register">Create one free →</Link>
          </p>
          <p className="auth-terms">
            By signing in you agree to our <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>
          </p>
        </div>
      </div>
    </div>
  )
}
