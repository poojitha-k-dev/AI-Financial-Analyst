import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { authAPI } from '../api'
import { PageHeader, Card, Button, Input } from '../components/ui'
import { User, Lock, BarChart2, LogOut } from 'lucide-react'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'
import './Profile.css'

export default function Profile() {
  const { user, logout, updateUser } = useAuth()
  const navigate = useNavigate()
  const [tab, setTab] = useState('profile')
  const [form, setForm] = useState({ full_name: user?.full_name||'', company_name: user?.company_name||'', bio: user?.bio||'' })
  const [pass, setPass] = useState({ current:'', new_pass:'', confirm:'' })
  const [savingProfile, setSavingProfile] = useState(false)
  const [savingPass,    setSavingPass]    = useState(false)

  const set  = k => e => setForm(p=>({...p,[k]:e.target.value}))
  const setp = k => e => setPass(p=>({...p,[k]:e.target.value}))

  const initials = user?.full_name?.split(' ').map(n=>n[0]).join('').toUpperCase().slice(0,2)||'U'

  const saveProfile = async () => {
    setSavingProfile(true)
    try {
      const r = await authAPI.update({ full_name:form.full_name||undefined, company_name:form.company_name||undefined, bio:form.bio||undefined })
      updateUser(r.data.user)
      toast.success('Profile updated!')
    } catch { toast.error('Update failed') }
    finally { setSavingProfile(false) }
  }

  const savePass = async () => {
    if (pass.new_pass !== pass.confirm) { toast.error('Passwords do not match'); return }
    if (pass.new_pass.length < 8) { toast.error('Min 8 characters'); return }
    setSavingPass(true)
    try {
      await authAPI.changePassword({ current_password:pass.current, new_password:pass.new_pass })
      toast.success('Password changed!')
      setPass({current:'',new_pass:'',confirm:''})
    } catch(e) { toast.error(e.response?.data?.detail||'Failed') }
    finally { setSavingPass(false) }
  }

  const handleLogout = () => { logout(); navigate('/login') }

  const TABS = [{ id:'profile',label:'Profile'},{id:'security',label:'Security'},{id:'usage',label:'Usage'}]

  return (
    <div>
      <PageHeader title="Profile & Settings" subtitle="Manage your account" icon={User}/>

      {/* User card */}
      <Card style={{marginBottom:24}}>
        <div className="profile-hero">
          <div className="profile-avatar">{initials}</div>
          <div className="profile-info">
            <div className="profile-name">{user?.full_name}</div>
            <div className="profile-email">{user?.email}</div>
            <span className="profile-plan">{user?.plan?.toUpperCase()||'FREE'}</span>
          </div>
          <Button variant="danger" size="sm" onClick={handleLogout} style={{marginLeft:'auto'}}>
            <LogOut size={13}/> Sign Out
          </Button>
        </div>
      </Card>

      {/* Tabs */}
      <div className="kpi-cats" style={{marginBottom:20}}>
        {TABS.map(t=>(
          <button key={t.id} className={`kpi-cat ${tab===t.id?'active':''}`} onClick={()=>setTab(t.id)}>{t.label}</button>
        ))}
      </div>

      {tab === 'profile' && (
        <Card>
          <div className="section-title" style={{marginBottom:16}}>Account Details</div>
          <div className="profile-form-grid">
            <Input label="Full Name" value={form.full_name} onChange={set('full_name')} placeholder="Jane Smith"/>
            <Input label="Email" value={user?.email||''} disabled/>
            <Input label="Company / Organisation" value={form.company_name} onChange={set('company_name')} placeholder="Acme Corp"/>
          </div>
          <div className="field" style={{marginTop:14}}>
            <label className="field-label">Bio</label>
            <textarea className="field-input" rows={3} value={form.bio} onChange={set('bio')} placeholder="Brief professional bio…" style={{resize:'vertical'}}/>
          </div>
          <Button onClick={saveProfile} loading={savingProfile} style={{marginTop:16}}>Save Changes</Button>
        </Card>
      )}

      {tab === 'security' && (
        <Card>
          <div className="section-title" style={{marginBottom:16}}>Change Password</div>
          <div className="profile-form-grid">
            <Input label="Current Password" type="password" value={pass.current} onChange={setp('current')} placeholder="••••••••"/>
            <Input label="New Password"     type="password" value={pass.new_pass} onChange={setp('new_pass')} placeholder="Min 8 characters"/>
            <Input label="Confirm Password" type="password" value={pass.confirm}  onChange={setp('confirm')}  placeholder="Repeat new password"/>
          </div>
          <Button onClick={savePass} loading={savingPass} style={{marginTop:16}}><Lock size={13}/> Change Password</Button>
        </Card>
      )}

      {tab === 'usage' && (
        <div className="usage-grid">
          {[
            ['Current Plan', user?.plan?.toUpperCase()||'FREE', 'var(--primary-light)'],
            ['Role',         user?.role?.toUpperCase()||'USER', 'var(--green)'],
            ['Member Since', user?.created_at?.slice(0,10)||'—', 'var(--text)'],
          ].map(([label,val,color])=>(
            <Card key={label} style={{textAlign:'center',padding:'20px 16px'}}>
              <div className="section-title" style={{marginBottom:8}}>{label}</div>
              <div style={{fontSize:20,fontWeight:800,color}}>{val}</div>
            </Card>
          ))}
          <Card style={{padding:'18px 20px'}}>
            <div className="section-title" style={{marginBottom:10}}>Platform Info</div>
            <div style={{fontSize:13,color:'var(--text2)',lineHeight:1.7}}>
              FinanceAI v3.0 · FastAPI + React · GPT-4o / Gemini 1.5 Pro
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
