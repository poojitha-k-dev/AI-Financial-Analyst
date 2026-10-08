import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({ baseURL: BASE, timeout: 120000 })

// Attach token
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// Handle 401
api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────
export const authAPI = {
  login:    d => api.post('/auth/login', new URLSearchParams(d), { headers:{'Content-Type':'application/x-www-form-urlencoded'} }),
  register: d => api.post('/auth/register', d),
  me:       ()=> api.get('/auth/me'),
  update:   d => api.patch('/auth/me', d),
  changePassword: d => api.post('/auth/change-password', d),
}

// ── Companies ─────────────────────────────────────────────────────────
export const companiesAPI = {
  list:    p => api.get('/companies/', { params: p }),
  create:  d => api.post('/companies/', d),
  update:  (id,d) => api.patch(`/companies/${id}`, d),
  delete:  id => api.delete(`/companies/${id}`),
  get:     id => api.get(`/companies/${id}`),
  statements: id => api.get(`/companies/${id}/statements`),
  deleteStatement: (cid, sid) => api.delete(`/companies/${cid}/statements/${sid}`),
}

// ── Upload ────────────────────────────────────────────────────────────
export const uploadAPI = {
  statement: formData => api.post('/upload/statement', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
}

// ── Analysis ──────────────────────────────────────────────────────────
export const analysisAPI = {
  full:     (id, stmtId) => api.post(`/analysis/${id}/full${stmtId ? `?statement_id=${stmtId}` : ''}`),
  kpis:     id => api.get(`/analysis/${id}/kpis`),
  risk:     id => api.get(`/analysis/${id}/risk`),
  forecast: (id, p) => api.get(`/analysis/${id}/forecast`, { params:{ periods: p } }),
  reports:  id => api.get(`/analysis/${id}/reports`),
  exportPdf:   id => api.post(`/analysis/${id}/export/pdf`, {}, { responseType:'blob' }),
  exportExcel: id => api.post(`/analysis/${id}/export/excel`, {}, { responseType:'blob' }),
}

// ── Chat ──────────────────────────────────────────────────────────────
export const chatAPI = {
  send:    d => api.post('/chat/', d),
  history: (id, sid) => api.get(`/chat/history/${id}`, { params: sid ? { session_id: sid } : {} }),
  clear:   (id, sid) => api.delete(`/chat/history/${id}${sid ? `?session_id=${sid}` : ''}`),
}

export default api
