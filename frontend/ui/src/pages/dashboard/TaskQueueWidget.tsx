import { useEffect, useState } from 'react'
import { ListTodo } from 'lucide-react'
import { api } from '../../api'
import type { ProcessDashboardResponse } from '../../api'
import { isDemoMode } from '../../app/demoUtils'

export function TaskQueueWidget() {
  const [data, setData] = useState<ProcessDashboardResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    function fetchOnce() {
      const load = isDemoMode()
        ? import('../../app/demo').then(m => m.DEMO_PROCESSES)
        : api.processDashboard()
      load
        .then(res => { if (!cancelled) setData(res) })
        .catch(() => {})
        .finally(() => { if (!cancelled) setLoading(false) })
    }

    fetchOnce()
    if (isDemoMode()) return () => { cancelled = true }

    const id = setInterval(fetchOnce, 5000)
    return () => { cancelled = true; clearInterval(id) }
  }, [])

  const processes = data?.processes ?? []

  return (
    <section className="section">
      <div className="section-header">
        <h3><ListTodo size={14} className="section-title-icon" />Task Queue</h3>
        {data && <span className="section-meta">{data.total_processes} running</span>}
      </div>
      {loading ? (
        <p className="chart-placeholder">Loading…</p>
      ) : processes.length === 0 ? (
        <p className="chart-placeholder">No background tasks running.</p>
      ) : (
        <div className="widget-list">
          {processes.slice(0, 5).map(p => (
            <div key={p.task_id ?? p.pid ?? p.command} className="widget-list-row">
              <span className="mono widget-list-row-main">{p.command}</span>
              <span className="section-meta">{p.status}</span>
              <span className="section-meta">{p.progress_percent}</span>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
