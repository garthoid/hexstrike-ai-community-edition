interface PluginsCategoryNavProps {
  categories: string[]
  activeCategory: string
  setActiveCategory: (value: string) => void
  counts: Record<string, number>
  totalCount: number
}

export function PluginsCategoryNav({ categories, activeCategory, setActiveCategory, counts, totalCount }: PluginsCategoryNavProps) {
  return (
    <nav className="browser-nav browser-nav-narrow">
      <button
        className={`browser-nav-item${activeCategory === 'all' ? ' browser-nav-item--active' : ''}`}
        onClick={() => setActiveCategory('all')}
      >
        <span className="browser-nav-label">All Plugins</span>
        <span className="browser-nav-count">{totalCount}</span>
      </button>
      {categories.filter(c => c !== 'all').map(category => (
        <button
          key={category}
          className={`browser-nav-item${activeCategory === category ? ' browser-nav-item--active' : ''}`}
          onClick={() => setActiveCategory(activeCategory === category ? 'all' : category)}
        >
          <span className="browser-nav-label">{category.replace(/_/g, ' ')}</span>
          <span className="browser-nav-count">{counts[category] ?? 0}</span>
        </button>
      ))}
    </nav>
  )
}
