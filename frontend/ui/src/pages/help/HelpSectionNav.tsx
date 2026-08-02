import type { ReactNode } from 'react'
import { Terminal, Flag, Lock, Keyboard, Layout, FlaskConical } from 'lucide-react'

export type HelpSection = 'ide' | 'flags' | 'auth' | 'palette' | 'ui' | 'demo'

interface HelpSectionNavProps {
  section: HelpSection
  setSection: (section: HelpSection) => void
}

const ITEMS: { id: HelpSection; label: string; icon: ReactNode }[] = [
  { id: 'ide', label: 'IDE / Agent Config', icon: <Terminal size={13} /> },
  { id: 'flags', label: 'MCP Client Flags', icon: <Flag size={13} /> },
  { id: 'auth', label: 'Authentication', icon: <Lock size={13} /> },
  { id: 'palette', label: 'Command Palette', icon: <Keyboard size={13} /> },
  { id: 'ui', label: 'UI Features', icon: <Layout size={13} /> },
  { id: 'demo', label: 'Demo Mode', icon: <FlaskConical size={13} /> },
]

export function HelpSectionNav({ section, setSection }: HelpSectionNavProps) {
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
