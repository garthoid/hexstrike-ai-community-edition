import { LayoutGrid } from 'lucide-react'

interface ToolsCategoryNavProps {
  categories: string[]
  activeCat: string
  setActiveCat: (value: string) => void
  counts: Record<string, number>
  totalCount: number
}

export function ToolsCategoryNav({ categories, activeCat, setActiveCat, counts, totalCount }: ToolsCategoryNavProps) {
  return (
    <nav className="browser-nav">
      <div className="browser-nav-title">
        <LayoutGrid size={14} /> Categories
      </div>
      <button
        className={`browser-nav-item${activeCat === 'all' ? ' browser-nav-item--active' : ''}`}
        onClick={() => setActiveCat('all')}
      >
        <span className="browser-nav-label">All Tools</span>
        <span className="browser-nav-count">{totalCount}</span>
      </button>
      {categories.filter(c => c !== 'all').map(category => (
        <button
          key={category}
          className={`browser-nav-item${activeCat === category ? ' browser-nav-item--active' : ''}`}
          onClick={() => setActiveCat(activeCat === category ? 'all' : category)}
        >
          <span className="browser-nav-label">{category.replace(/_/g, ' ')}</span>
          <span className="browser-nav-count">{counts[category] ?? 0}</span>
        </button>
      ))}
    </nav>
  )
}
