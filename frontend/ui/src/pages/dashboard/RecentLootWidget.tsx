import { useEffect, useState } from 'react'
import { KeyRound } from 'lucide-react'
import { api } from '../../api'
import type { LootItem } from '../../api'

function timeAgo(epochSeconds: number): string {
  const secs = Math.max(0, Date.now() / 1000 - epochSeconds)
  if (secs < 60) return 'just now'
  if (secs < 3600) return `${Math.floor(secs / 60)}m ago`
  if (secs < 86400) return `${Math.floor(secs / 3600)}h ago`
  return `${Math.floor(secs / 86400)}d ago`
}

export function RecentLootWidget() {
  const [loot, setLoot] = useState<LootItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    api.loot()
      .then(res => { if (!cancelled) setLoot(res.loot) })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  const recent = [...loot].sort((a, b) => b.created_at - a.created_at).slice(0, 5)

  return (
    <section className="section">
      <div className="section-header">
        <h3><KeyRound size={14} className="section-title-icon" />Recent Loot</h3>
      </div>
      {loading ? (
        <p className="chart-placeholder">Loading…</p>
      ) : recent.length === 0 ? (
        <p className="chart-placeholder">No loot captured yet.</p>
      ) : (
        <div className="widget-list">
          {recent.map(item => (
            <div key={item.loot_id} className="widget-list-row">
              <span className="widget-list-row-main">{item.title}</span>
              <span className="section-meta">{item.host ?? item.source_tool ?? ''}</span>
              <span className="section-meta">{timeAgo(item.created_at)}</span>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
