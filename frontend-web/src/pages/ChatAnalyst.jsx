import { useEffect, useState, useRef } from 'react'
import { companiesAPI, chatAPI } from '../api'
import { PageHeader, Card, Button, EmptyState, LoadingPage } from '../components/ui'
import { MessageSquare, Send, Trash2, Plus, Bot, User } from 'lucide-react'
import toast from 'react-hot-toast'
import ReactMarkdown from 'react-markdown'
import { v4 as uuid } from 'uuid'
import './ChatAnalyst.css'

const SUGGESTIONS = [
  'What is the current profitability outlook?',
  'How healthy is the balance sheet?',
  'What are the biggest risks?',
  'Is the company generating free cash flow?',
  'How does leverage compare to industry norms?',
  "Explain the Altman Z-Score result.",
  "What's the revenue growth trend?",
  'What strategic recommendations do you have?',
]

export default function ChatAnalyst() {
  const [companies, setCompanies] = useState([])
  const [cid,      setCid]       = useState(null)
  const [messages, setMessages]  = useState([])
  const [input,    setInput]     = useState('')
  const [sending,  setSending]   = useState(false)
  const [loading,  setLoading]   = useState(true)
  const [sessionId, setSessionId]= useState(() => uuid())
  const bottomRef = useRef(null)
  const inputRef  = useRef(null)

  useEffect(() => {
    companiesAPI.list().then(r => {
      setCompanies(r.data)
      if (r.data.length) setCid(r.data[0].id)
    }).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!cid) return
    setMessages([])
    chatAPI.history(cid, sessionId)
      .then(r => setMessages(r.data))
      .catch(() => {})
  }, [cid, sessionId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior:'smooth' })
  }, [messages, sending])

  const send = async (text) => {
    const q = text || input.trim()
    if (!q || !cid) return
    setInput('')
    setSending(true)

    setMessages(prev => [...prev, { role:'user', content:q, created_at: new Date().toISOString() }])

    try {
      const r = await chatAPI.send({ question:q, company_id:cid, session_id:sessionId })
      setMessages(prev => [...prev, { role:'assistant', content:r.data.answer, created_at: new Date().toISOString() }])
    } catch(e) {
      toast.error(e.response?.data?.detail || 'Chat failed. Check your API key.')
      setMessages(prev => prev.slice(0,-1))
    } finally { setSending(false); inputRef.current?.focus() }
  }

  const clearChat = async () => {
    await chatAPI.clear(cid, sessionId)
    setSessionId(uuid())
    setMessages([])
    toast.success('Chat cleared')
  }

  const handleKey = e => { if (e.key==='Enter' && !e.shiftKey) { e.preventDefault(); send() } }

  if (loading) return <LoadingPage/>

  const co = companies.find(c=>c.id===cid)

  return (
    <div className="chat-page">
      <PageHeader title="Chat Analyst" subtitle="Context-aware AI Q&A about your financial data" icon={MessageSquare}
        actions={
          <div style={{display:'flex',gap:8,alignItems:'center'}}>
            <select className="page-select" style={{width:180}} value={cid||''} onChange={e=>{setCid(+e.target.value);setMessages([]);setSessionId(uuid())}}>
              {companies.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            <Button size="sm" variant="secondary" onClick={clearChat} disabled={!messages.length}><Trash2 size={13}/> Clear</Button>
            <Button size="sm" variant="secondary" onClick={()=>{setSessionId(uuid());setMessages([])}}><Plus size={13}/> New</Button>
          </div>
        }
      />

      <div className="chat-layout">
        {/* Chat window */}
        <div className="chat-main">
          <Card className="chat-window">
            {messages.length === 0 ? (
              <div className="chat-empty">
                <div className="chat-empty-icon"><Bot size={32}/></div>
                <div className="chat-empty-title">AI Financial Analyst</div>
                <div className="chat-empty-sub">
                  {co ? `Ask me anything about ${co.name}'s financials.` : 'Select a company to start chatting.'}
                </div>
              </div>
            ) : (
              <div className="chat-messages">
                {messages.map((msg, i) => (
                  <div key={i} className={`chat-msg chat-msg-${msg.role}`}>
                    <div className="chat-msg-avatar">
                      {msg.role === 'user' ? <User size={14}/> : <Bot size={14}/>}
                    </div>
                    <div className="chat-msg-bubble">
                      {msg.role === 'assistant'
                        ? <div className="chat-markdown"><ReactMarkdown>{msg.content}</ReactMarkdown></div>
                        : <div>{msg.content}</div>
                      }
                      <div className="chat-msg-time">{msg.created_at?.slice(11,16)}</div>
                    </div>
                  </div>
                ))}
                {sending && (
                  <div className="chat-msg chat-msg-assistant">
                    <div className="chat-msg-avatar"><Bot size={14}/></div>
                    <div className="chat-msg-bubble">
                      <div className="typing-dots"><span/><span/><span/></div>
                    </div>
                  </div>
                )}
                <div ref={bottomRef}/>
              </div>
            )}
          </Card>

          {/* Input */}
          <div className="chat-input-row">
            <textarea
              ref={inputRef}
              className="chat-textarea"
              placeholder="Ask about financials, KPIs, risks, strategy…"
              value={input}
              onChange={e=>setInput(e.target.value)}
              onKeyDown={handleKey}
              rows={2}
              disabled={!cid || sending}
            />
            <Button onClick={() => send()} loading={sending} disabled={!input.trim()||!cid} className="chat-send-btn">
              <Send size={15}/>
            </Button>
          </div>
        </div>

        {/* Sidebar */}
        <div className="chat-sidebar">
          <Card>
            <div className="section-title" style={{marginBottom:12}}>Quick Questions</div>
            <div className="chat-suggestions">
              {SUGGESTIONS.map((s,i) => (
                <button key={i} className="chat-suggestion" onClick={() => send(s)} disabled={sending||!cid}>
                  {s}
                </button>
              ))}
            </div>
          </Card>

          {co && (
            <Card style={{marginTop:14}}>
              <div className="section-title" style={{marginBottom:10}}>Context</div>
              <div className="chat-context-item"><span>Company</span><strong>{co.name}</strong></div>
              {co.sector && <div className="chat-context-item"><span>Sector</span><strong>{co.sector}</strong></div>}
              <div className="chat-context-item"><span>Statements</span><strong>{co.statement_count}</strong></div>
              {co.latest_period && <div className="chat-context-item"><span>Latest Period</span><strong>{co.latest_period}</strong></div>}
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
