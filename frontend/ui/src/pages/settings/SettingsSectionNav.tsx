import type { ReactNode } from 'react'
import { Server, Eye, SlidersHorizontal, ListTodo, MessageSquare } from 'lucide-react'

export type SettingsSection = 'server' | 'pages' | 'runtime' | 'wordlists' | 'chat'

interface SettingsSectionNavProps {
  section: SettingsSection
  setSection: (section: SettingsSection) => void
}

const ITEMS: { id: SettingsSection; label: string; icon: ReactNode }[] = [
  { id: 'server', label: 'Server Environment', icon: <Server size={13} /> },
  { id: 'pages', label: 'Navigation Pages', icon: <Eye size={13} /> },
  { id: 'runtime', label: 'Runtime Config', icon: <SlidersHorizontal size={13} /> },
  { id: 'wordlists', label: 'Wordlists', icon: <ListTodo size={13} /> },
  { id: 'chat', label: 'Chat Widget', icon: <MessageSquare size={13} /> },
]

export function SettingsSectionNav({ section, setSection }: SettingsSectionNavProps) {
  return (
    <nav className="browser-nav browser-nav-narrow">
      {ITEMS.map(item => (
        <button
          key={item.id}
          className={`browser-nav-item${section === item.id ? ' browser-nav-item--active' : ''}`}
          onClick={() => setSection(item.id)}
        >
          {item.icon}
          <span className="browser-nav-label">{item.label}</span>
        </button>
      ))}
    </nav>
  )
}
