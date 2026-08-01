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
    <nav className="tools-cat-nav">
      <div className="tools-cat-nav-title">
        <LayoutGrid size={14} /> Categories
      </div>
      <button
        className={`tools-cat-item${activeCat === 'all' ? ' tools-cat-item--active' : ''}`}
        onClick={() => setActiveCat('all')}
      >
        <span className="tools-cat-label">All Tools</span>
        <span className="tools-cat-count">{totalCount}</span>
      </button>
      {categories.filter(c => c !== 'all').map(category => (
        <button
          key={category}
          className={`tools-cat-item${activeCat === category ? ' tools-cat-item--active' : ''}`}
          onClick={() => setActiveCat(activeCat === category ? 'all' : category)}
        >
          <span className="tools-cat-label">{category.replace(/_/g, ' ')}</span>
          <span className="tools-cat-count">{counts[category] ?? 0}</span>
        </button>
      ))}
    </nav>
  )
}
