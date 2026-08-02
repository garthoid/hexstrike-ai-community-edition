import { Clock, BarChart2, Brain } from 'lucide-react'

export type ReportsSection = 'timeline' | 'breakdown' | 'ai'

interface ReportsSectionNavProps {
  section: ReportsSection
  setSection: (section: ReportsSection) => void
}

export function ReportsSectionNav({ section, setSection }: ReportsSectionNavProps) {
  return (
    <nav className="browser-nav browser-nav-narrow">
      <button
        className={`browser-nav-item${section === 'timeline' ? ' browser-nav-item--active' : ''}`}
        onClick={() => setSection('timeline')}
      >
        <Clock size={13} />
        <span className="browser-nav-label">Timeline</span>
      </button>
      <button
        className={`browser-nav-item${section === 'breakdown' ? ' browser-nav-item--active' : ''}`}
        onClick={() => setSection('breakdown')}
      >
        <BarChart2 size={13} />
        <span className="browser-nav-label">Breakdown</span>
      </button>
      <button
        className={`browser-nav-item${section === 'ai' ? ' browser-nav-item--active' : ''}`}
        onClick={() => setSection('ai')}
      >
        <Brain size={13} />
        <span className="browser-nav-label">AI Analysis</span>
      </button>
    </nav>
  )
}
