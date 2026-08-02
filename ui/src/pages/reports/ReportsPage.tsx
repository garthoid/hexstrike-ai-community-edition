import { useState } from 'react'
import {
  BarChart2, CheckCircle, Clock, TrendingUp, FileText,
} from 'lucide-react'
import { KpiStrip } from '../../components/data-display/KpiStrip'
import { RunResultModal } from '../../components/modals/RunResultModal'
import { BrowserPage } from '../../components/layout/BrowserPage'
import { type RunHistoryEntry } from '../../shared/types'
import { ReportsBreakdownSection, ReportsTimelineSection } from './ReportsSections'
import { AiAnalysisSection } from './AiAnalysisSection'
import { ReportsSectionNav, type ReportsSection } from './ReportsSectionNav'
import { extractTarget, type GroupBy } from './reportUtils'
import { safeFixed } from '../../shared/utils'
import './ReportsPage.css'

interface ReportsPageProps {
  runHistory: RunHistoryEntry[]
}

export default function ReportsPage({ runHistory }: ReportsPageProps) {
  const [section, setSection] = useState<ReportsSection>('timeline')
  const [groupBy, setGroupBy] = useState<GroupBy>('tool')
  const [search, setSearch] = useState('')
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [modalEntry, setModalEntry] = useState<RunHistoryEntry | null>(null)

  const byTool = runHistory.reduce<Record<string, RunHistoryEntry[]>>((acc, e) => {
    ;(acc[e.tool] = acc[e.tool] || []).push(e)
    return acc
  }, {})

  const byTarget = runHistory.reduce<Record<string, RunHistoryEntry[]>>((acc, e) => {
    const t = extractTarget(e)
    ;(acc[t] = acc[t] || []).push(e)
    return acc
  }, {})

  const grouped = groupBy === 'tool' ? byTool : byTarget

  function toggleExpanded(key: string) {
    setExpanded(prev => {
      const next = new Set(prev)
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })
  }

  const q = search.toLowerCase()
  const keys = Object.keys(grouped).filter(k => !q || k.toLowerCase().includes(q)).sort()

  if (runHistory.length === 0) return (
    <div className="reports-page-empty">
      <div className="tasks-empty">
        <FileText size={32} color="var(--text-dim)" />
        <p>No run history yet. Execute tools from the Run tab to see reports.</p>
      </div>
    </div>
  )

  const okCount = runHistory.filter(e => e.result.success).length
  const failCount = runHistory.length - okCount

  return (
    <>
      {modalEntry && (
        <RunResultModal entry={modalEntry} onClose={() => setModalEntry(null)} />
      )}

      <BrowserPage
        className="reports-page"
        top={(
          <KpiStrip
            items={[
              { icon: <BarChart2 size={16} />, label: 'Total Runs · all time', value: runHistory.length, accent: 'var(--blue)' },
              {
                icon: <CheckCircle size={16} />,
                label: `Success Rate · ${okCount} ok · ${failCount} failed`,
                value: runHistory.length > 0 ? `${((okCount / runHistory.length) * 100).toFixed(0)}%` : '—',
                accent: 'var(--green)',
              },
              {
                icon: <Clock size={16} />,
                label: 'Avg Time · per run',
                value: `${safeFixed(runHistory.length > 0 ? runHistory.reduce((s, e) => s + (e.result.execution_time ?? 0), 0) / runHistory.length : undefined, 1)}s`,
                accent: 'var(--purple)',
              },
              { icon: <TrendingUp size={16} />, label: 'Unique Tools · used', value: Object.keys(byTool).length, accent: 'var(--amber)' },
            ]}
          />
        )}
        nav={<ReportsSectionNav section={section} setSection={setSection} />}
        main={(
          <div className="browser-main">
            <div className="browser-scroll">
              {section === 'timeline' && (
                <ReportsTimelineSection runHistory={runHistory} onOpenEntry={setModalEntry} />
              )}
              {section === 'breakdown' && (
                <ReportsBreakdownSection
                  grouped={grouped}
                  keys={keys}
                  groupBy={groupBy}
                  search={search}
                  setSearch={setSearch}
                  setGroupBy={setGroupBy}
                  expanded={expanded}
                  toggleExpanded={toggleExpanded}
                  onOpenEntry={setModalEntry}
                />
              )}
              {section === 'ai' && <AiAnalysisSection />}
            </div>
          </div>
        )}
      />
    </>
  )
}
