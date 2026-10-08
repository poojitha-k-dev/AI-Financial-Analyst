import { useState, useEffect } from 'react'
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  LayoutDashboard, Building2, Upload, BarChart2, AlertTriangle,
  TrendingUp, Brain, GitCompare, MessageSquare, FileText,
  User, LogOut, ChevronRight, Zap, Bell, Settings
} from 'lucide-react'
import FloatingChat from './FloatingChat'
import './Layout.css'

const NAV_GROUPS = [
  {
    label: 'Overview',
    items: [
      { to: '/',          icon: LayoutDashboard, label: 'Dashboard'     },
      { to: '/companies', icon: Building2,       label: 'Companies'     },
      { to: '/upload',    icon: Upload,          label: 'Upload Data'   },
    ]
  },
  {
    label: 'Analysis',
    items: [
      { to: '/kpis',      icon: BarChart2,       label: 'KPI Analysis'  },
      { to: '/risk',      icon: AlertTriangle,   label: 'Risk Analysis' },
      { to: '/forecast',  icon: TrendingUp,      label: 'Forecasting'   },
      { to: '/benchmark', icon: GitCompare,      label: 'Benchmarking'  },
    ]
  },
  {
    label: 'AI',
    items: [
      { to: '/insights',  icon: Brain,           label: 'AI Insights'   },
      { to: '/chat',      icon: MessageSquare,   label: 'Chat Analyst'  },
      { to: '/reports',   icon: FileText,        label: 'Reports'       },
    ]
  }
]

const PAGE_TITLES = {
  '/': 'Dashboard', '/companies': 'Companies', '/upload': 'Upload Data',
  '/kpis': 'KPI Analysis', '/risk': 'Risk Analysis', '/forecast': 'Forecasting',
  '/insights': 'AI Insights', '/benchmark': 'Benchmarking',
  '/chat': 'Chat Analyst', '/reports': 'Reports', '/profile': 'Profile',
}

function Clock() {
  const [time, setTime] = useState(new Date())
  useEffect(() => { const t = setInterval(() => setTime(new Date()), 1000); return () => clearInterval(t) }, [])
  return (
    <span className="topbar-clock">
      {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
    </span>
  )
}

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate  = useNavigate()
  const location  = useLocation()
  const handleLogout = () => { logout(); navigate('/login') }
  const initials = user?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || 'U'
  const pageTitle = PAGE_TITLES[location.pathname] || 'FinanceAI'

  return (
    <div className="layout">
      {/* Floating background orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />

      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon"><Zap size={18} /></div>
          <div>
            <div className="logo-name">FinanceAI</div>
            <div className="logo-badge">PRO</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {NAV_GROUPS.map(group => (
            <div key={group.label} className="nav-group">
              <div className="nav-group-label">{group.label}</div>
              {group.items.map(({ to, icon: Icon, label }) => (
                <NavLink
                  key={to} to={to} end={to === '/'}
                  className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                >
                  <span className="nav-icon"><Icon size={15} /></span>
                  <span className="nav-label">{label}</span>
                  <ChevronRight size={13} className="nav-arrow" />
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <NavLink to="/profile" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <span className="nav-icon"><User size={15} /></span>
            <span className="nav-label">Profile</span>
          </NavLink>
          <button className="nav-item logout-btn" onClick={handleLogout}>
            <span className="nav-icon"><LogOut size={15} /></span>
            <span className="nav-label">Sign Out</span>
          </button>
          <div className="user-card">
            <div className="user-avatar">{initials}</div>
            <div className="user-info">
              <div className="user-name">{user?.full_name || 'User'}</div>
              <div className="user-plan">Free Plan</div>
            </div>
          </div>
        </div>
      </aside>

      {/* ── Main ── */}
      <div className="main-content">
        {/* Topbar */}
        <div className="topbar">
          <div className="topbar-left">
            <span className="status-dot" />
            <span className="topbar-breadcrumb">
              FinanceAI &nbsp;/&nbsp; <span>{pageTitle}</span>
            </span>
          </div>
          <div className="topbar-right">
            <Clock />
          </div>
        </div>

        <div className="page-wrapper">
          <Outlet />
        </div>
      </div>

      {/* Floating chatbot — visible on every page */}
      <FloatingChat />
    </div>
  )
}
