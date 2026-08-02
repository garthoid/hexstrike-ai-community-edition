import { KeyRound, Package } from 'lucide-react'

type Tab = 'credentials' | 'loot'

interface LootTabNavProps {
  tab: Tab
  setTab: (tab: Tab) => void
}

export function LootTabNav({ tab, setTab }: LootTabNavProps) {
  return (
    <nav className="browser-nav browser-nav-narrow">
      <button
        className={`browser-nav-item${tab === 'credentials' ? ' browser-nav-item--active' : ''}`}
        onClick={() => setTab('credentials')}
      >
        <KeyRound size={13} />
        <span className="browser-nav-label">Credentials</span>
      </button>
      <button
        className={`browser-nav-item${tab === 'loot' ? ' browser-nav-item--active' : ''}`}
        onClick={() => setTab('loot')}
      >
        <Package size={13} />
        <span className="browser-nav-label">Loot</span>
      </button>
    </nav>
  )
}
