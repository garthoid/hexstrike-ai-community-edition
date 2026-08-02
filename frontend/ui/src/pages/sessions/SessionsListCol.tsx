import { Info, Layers } from 'lucide-react'
import type { SessionSummary } from '../../api'
import { SessionCard } from './SessionCard'

interface SessionsListColProps {
  active: SessionSummary[]
  completed: SessionSummary[]
  view: 'active' | 'completed'
  setView: (v: 'active' | 'completed') => void
  streamStatus: 'streaming' | 'polling' | 'error'
  onOpenSession: (sessionId: string) => void
}

export function SessionsListCol({
  active,
  completed,
  view,
  setView,
  streamStatus,
  onOpenSession,
}: SessionsListColProps) {
  const sessions = view === 'active' ? active : completed

  return (
    <div className="browser-main">
      <div className="section-header">
        <h3>Sessions <span className="badge">{sessions.length}</span></h3>
        <div className="sessions-header-actions">
          <span className={`sessions-stream-status sessions-stream-status--${streamStatus}`}>
            {streamStatus === 'streaming' ? 'Live' : streamStatus === 'polling' ? 'Polling' : 'Offline'}
          </span>
        </div>
      </div>
      <div className="registry-controls">
        <div className="registry-controls-top">
          <div className="cat-tabs sessions-view-tabs">
            <button className={`cat-tab${view === 'active' ? ' active' : ''}`} onClick={() => setView('active')}>
              Active <span className="badge">{active.length}</span>
            </button>
            {completed.length > 0 && (
              <button className={`cat-tab${view === 'completed' ? ' active' : ''}`} onClick={() => setView('completed')}>
                Completed <span className="badge">{completed.length}</span>
              </button>
            )}
          </div>
        </div>
      </div>
      <div className="browser-scroll">
        {sessions.length === 0 ? (
          <div className="tasks-empty">
            <Layers size={28} color="var(--text-dim)" />
            <p>{view === 'active' ? 'No active sessions. Start one from Session Setup.' : 'No completed sessions yet.'}</p>
          </div>
        ) : (
          <div className="sessions-grid">
            {sessions.map(session => <SessionCard key={session.session_id} session={session} onOpen={onOpenSession} />)}
          </div>
        )}
        {view === 'active' && active.length > 0 && (
          <div className="section-meta session-list-footer-tip">
            <Info size={12} />
            Call MCP tool <span className="mono">handover_session("&lt;session_id&gt;", "optional note")</span> to continue the session with AI.
          </div>
        )}
      </div>
    </div>
  )
}
