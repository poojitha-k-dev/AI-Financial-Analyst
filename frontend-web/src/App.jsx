import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Companies from './pages/Companies'
import Upload from './pages/Upload'
import KpiAnalysis from './pages/KpiAnalysis'
import RiskAnalysis from './pages/RiskAnalysis'
import Forecasting from './pages/Forecasting'
import AiInsights from './pages/AiInsights'
import Benchmarking from './pages/Benchmarking'
import ChatAnalyst from './pages/ChatAnalyst'
import Reports from './pages/Reports'
import Profile from './pages/Profile'

function PrivateRoute({ children }) {
  const { token } = useAuth()
  return token ? children : <Navigate to="/login" replace />
}

function PublicRoute({ children }) {
  const { token } = useAuth()
  return !token ? children : <Navigate to="/" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster
          position="top-right"
          gutter={10}
          toastOptions={{
            duration: 4000,
            style: {
              background: '#111827',
              color: '#f1f5f9',
              border: '1px solid rgba(255,255,255,0.08)',
              fontSize: '13px',
              fontWeight: '500',
              borderRadius: '12px',
              padding: '12px 16px',
              boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
              maxWidth: '380px',
            },
            success: {
              iconTheme: { primary: '#10b981', secondary: '#fff' },
              style: { borderLeft: '3px solid #10b981' },
            },
            error: {
              iconTheme: { primary: '#ef4444', secondary: '#fff' },
              style: { borderLeft: '3px solid #ef4444' },
            },
          }}
        />
        <Routes>
          <Route path="/login"    element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
          <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
            <Route index             element={<Dashboard />} />
            <Route path="companies"  element={<Companies />} />
            <Route path="upload"     element={<Upload />} />
            <Route path="kpis"       element={<KpiAnalysis />} />
            <Route path="risk"       element={<RiskAnalysis />} />
            <Route path="forecast"   element={<Forecasting />} />
            <Route path="insights"   element={<AiInsights />} />
            <Route path="benchmark"  element={<Benchmarking />} />
            <Route path="chat"       element={<ChatAnalyst />} />
            <Route path="reports"    element={<Reports />} />
            <Route path="profile"    element={<Profile />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
