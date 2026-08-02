import { useEffect, useState } from 'react'
import { Layers } from 'lucide-react'
import { api } from '../../api'
import type { SessionSummary } from '../../api'
import { isDemoMode } from '../../app/demoUtils'

export function ActiveSessionsWidget() {
  const [active, setActive] = useState<SessionSummary[]>([])
  const [totalCompleted, setTotalCompleted] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    const load = isDemoMode()
      ? import('../../app/demo').then(m => m.DEMO_SESSIONS)
      : api.sessions()
    load
      .then(res => {
        if (cancelled) return
        setActive(res.active)
        setTotalCompleted(res.total_completed)
      })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  return (
    <section className="section">
      <div className="section-header">
        <h3><Layers size={14} className="section-title-icon" />Active Sessions</h3>
        {!loading && <span className="section-meta">{totalCompleted} completed</span>}
      </div>
      {loading ? (
        <p className="chart-placeholder">Loading…</p>
      ) : active.length === 0 ? (
        <p className="chart-placeholder">No active sessions.</p>
      ) : (
        <div className="widget-list">
          {active.slice(0, 5).map(s => (
            <div key={s.session_id} className="widget-list-row">
              <span className="widget-list-row-main">{s.name || s.target}</span>
              <span className="section-meta">{s.total_findings} findings</span>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
