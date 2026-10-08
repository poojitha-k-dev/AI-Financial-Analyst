import { useState, useEffect, useRef, useCallback } from 'react'
import { companiesAPI, chatAPI } from '../api'
import { Bot, X, Send, RotateCcw, MessageCircle, Sparkles, ChevronDown, User, Paperclip } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { v4 as uuid } from 'uuid'
import './FloatingChat.css'

const SUGGESTIONS = [
  { icon: '📊', text: 'What is my total profit and revenue?' },
  { icon: '📈', text: 'Where should I invest to grow money?' },
  { icon: '⚠️', text: 'What are the biggest financial risks?' },
  { icon: '💡', text: 'Give me personal investment advice' },
  { icon: '🔍', text: 'Analyse my overall financial health' },
  { icon: '💰', text: 'Should I invest more in this company?' },
]

export default function FloatingChat() {
  const [open,      setOpen]      = useState(false)
  const [companies, setCompanies] = useState([])
  const [cid,       setCid]       = useState(null)
  const [messages,  setMessages]  = useState([])
  const [input,     setInput]     = useState('')
  const [sending,   setSending]   = useState(false)
  const [sessionId, setSessionId] = useState(() => uuid())
  const [unread,    setUnread]    = useState(0)
  const [showPicker,setShowPicker]= useState(false)
  const bottomRef  = useRef(null)
  const inputRef   = useRef(null)
  const textareaRef= useRef(null)

  useEffect(() => {
    companiesAPI.list().then(r => {
      setCompanies(r.data)
      if (r.data.length) setCid(r.data[0].id)
    }).catch(() => {})
  }, [])

  useEffect(() => {
    if (open) {
      setUnread(0)
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [open])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  useEffect(() => {
    if (!open && messages.length > 0) {
      const last = messages[messages.length - 1]
      if (last?.role === 'assistant') setUnread(u => u + 1)
    }
  }, [messages])

  // Auto-resize textarea
  const autoResize = useCallback(() => {
    const el = textareaRef.current
    if (el) { el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 120) + 'px' }
  }, [])

  const send = async (text) => {
    const q = (text || input).trim()
    if (!q || sending) return
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
    setSending(true)
    setMessages(prev => [...prev, { role: 'user', content: q, id: uuid() }])
    try {
      const r = await chatAPI.send({ question: q, company_id: cid || null, session_id: sessionId })
      setMessages(prev => [...prev, { role: 'assistant', content: r.data.answer, id: uuid() }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: '❌ Something went wrong. Please try again.', id: uuid() }])
    } finally {
      setSending(false)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }

  const handleKey = e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
  }

  const reset = () => { setMessages([]); setSessionId(uuid()); setInput('') }
  const co = companies.find(c => c.id === cid)

  return (
    <>
      {/* Floating button */}
      <button
        className={`fc-fab ${open ? 'fc-fab-open' : ''}`}
        onClick={() => setOpen(o => !o)}
        title="AI Financial Analyst"
      >
        {open ? <X size={20} strokeWidth={2.5} /> : <Sparkles size={20} strokeWidth={2.5} />}
        {!open && unread > 0 && <span className="fc-unread">{unread}</span>}
      </button>

      {/* Chat panel */}
      {open && (
        <div className="fc-panel">
          {/* Header — ChatGPT style */}
          <div className="fc-head">
            <div className="fc-head-left">
              <div className="fc-head-logo">
                <Sparkles size={16} strokeWidth={2.5} />
              </div>
              <div className="fc-head-info">
                <span className="fc-head-title">FinanceAI Assistant</span>
                <span className="fc-head-sub">
                  {co ? co.name : 'General Mode'}
                  <span className="fc-online" />
                </span>
              </div>
            </div>
            <div className="fc-head-right">
              {companies.length > 0 && (
                <div className="fc-company-picker">
                  <button className="fc-company-btn" onClick={() => setShowPicker(p => !p)}>
                    {co ? co.name.split(' ')[0] : 'Company'}
                    <ChevronDown size={12} />
                  </button>
                  {showPicker && (
                    <div className="fc-company-dropdown">
                      {companies.map(c => (
                        <button key={c.id} className={`fc-co-item ${cid === c.id ? 'active' : ''}`}
                          onClick={() => { setCid(c.id); reset(); setShowPicker(false) }}>
                          <span className="fc-co-dot">{c.name[0]}</span>
                          {c.name}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
              <button className="fc-head-btn" onClick={reset} title="New chat">
                <RotateCcw size={15} strokeWidth={2.5} />
              </button>
              <button className="fc-head-btn" onClick={() => setOpen(false)}>
                <X size={15} strokeWidth={2.5} />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="fc-body">
            {messages.length === 0 ? (
              <div className="fc-empty">
                <div className="fc-empty-logo">
                  <Sparkles size={32} strokeWidth={1.5} />
                </div>
                <h3 className="fc-empty-title">How can I help you today?</h3>
                <p className="fc-empty-sub">
                  {co
                    ? `Analysing ${co.name} — ask me anything about the financials`
                    : 'Ask any financial question or upload data for personalised analysis'}
                </p>
                <div className="fc-suggestions">
                  {SUGGESTIONS.map((s, i) => (
                    <button key={i} className="fc-suggestion" onClick={() => send(s.text)} disabled={sending}>
                      <span className="fc-suggestion-icon">{s.icon}</span>
                      <span>{s.text}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="fc-messages">
                {messages.map((msg) => (
                  <div key={msg.id} className={`fc-row fc-row-${msg.role}`}>
                    {msg.role === 'assistant' && (
                      <div className="fc-avatar-ai">
                        <Sparkles size={14} strokeWidth={2.5} />
                      </div>
                    )}
                    <div className={`fc-message fc-message-${msg.role}`}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                    </div>
                    {msg.role === 'user' && (
                      <div className="fc-avatar-user">
                        <User size={14} strokeWidth={2.5} />
                      </div>
                    )}
                  </div>
                ))}
                {sending && (
                  <div className="fc-row fc-row-assistant">
                    <div className="fc-avatar-ai">
                      <Sparkles size={14} strokeWidth={2.5} />
                    </div>
                    <div className="fc-message fc-message-assistant fc-thinking">
                      <span /><span /><span />
                    </div>
                  </div>
                )}
                <div ref={bottomRef} />
              </div>
            )}
          </div>

          {/* Input — ChatGPT style */}
          <div className="fc-footer">
            <div className="fc-input-box">
              <textarea
                ref={el => { inputRef.current = el; textareaRef.current = el }}
                className="fc-input"
                placeholder="Message FinanceAI..."
                value={input}
                rows={1}
                onChange={e => { setInput(e.target.value); autoResize() }}
                onKeyDown={handleKey}
                disabled={sending}
              />
              <button
                className={`fc-send-btn ${input.trim() && !sending ? 'fc-send-active' : ''}`}
                onClick={() => send()}
                disabled={!input.trim() || sending}
              >
                <Send size={16} strokeWidth={2.5} />
              </button>
            </div>
            <p className="fc-disclaimer">
              FinanceAI analyses your uploaded financial data. Not professional financial advice.
            </p>
          </div>
        </div>
      )}
    </>
  )
}
