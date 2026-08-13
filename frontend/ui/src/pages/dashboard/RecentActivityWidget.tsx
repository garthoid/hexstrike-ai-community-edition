import { History, CheckCircle, XCircle } from 'lucide-react'
import type { RunHistoryEntry } from '../../shared/types'

function timeAgo(ts: Date): string {
  const secs = Math.max(0, (Date.now() - ts.getTime()) / 1000)
  if (secs < 60) return 'just now'
  if (secs < 3600) return `${Math.floor(secs / 60)}m ago`
  if (secs < 86400) return `${Math.floor(secs / 3600)}h ago`
  return `${Math.floor(secs / 86400)}d ago`
}

export function RecentActivityWidget({ runHistory }: { runHistory: RunHistoryEntry[] }) {
  const entries = [...runHistory].sort((a, b) => b.ts.getTime() - a.ts.getTime()).slice(0, 5)

  return (
    <section className="section">
      <div className="section-header">
        <h3><History size={14} className="section-title-icon" />Recent Activity</h3>
      </div>
      {entries.length === 0 ? (
        <p className="chart-placeholder">No tool runs yet this session.</p>
      ) : (
        <div className="widget-list">
          {entries.map(entry => (
            <div key={entry.id} className="widget-list-row">
              {entry.result.success
                ? <CheckCircle size={14} color="var(--green)" />
                : <XCircle size={14} color="var(--red)" />}
              <span className="mono widget-list-row-main">{entry.tool}</span>
              <span className="section-meta">{timeAgo(entry.ts)}</span>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
