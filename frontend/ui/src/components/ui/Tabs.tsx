import { useLayoutEffect, useRef, useState, type ReactNode } from 'react'
import './Tabs.css'

export interface TabItem {
  id: string
  label: ReactNode
  icon?: ReactNode
  content: ReactNode
}

interface TabsProps {
  tabs: TabItem[]
  active?: string
  defaultActive?: string
  onChange?: (id: string) => void
  /** When set, the active tab is read from and written to `?<hashKey>=<id>` in the URL hash. */
  hashKey?: string
  className?: string
}

function readHashParam(key: string): string | null {
  const hash = window.location.hash.replace(/^#/, '')
  const qIndex = hash.indexOf('?')
  if (qIndex < 0) return null
  return new URLSearchParams(hash.slice(qIndex + 1)).get(key)
}

function writeHashParam(key: string, value: string) {
  const hash = window.location.hash.replace(/^#/, '')
  const qIndex = hash.indexOf('?')
  const path = qIndex >= 0 ? hash.slice(0, qIndex) : hash
  const params = new URLSearchParams(qIndex >= 0 ? hash.slice(qIndex + 1) : '')
  params.set(key, value)
  history.replaceState(null, '', `#${path}?${params.toString()}`)
}

export function Tabs({ tabs, active, defaultActive, onChange, hashKey, className = '' }: TabsProps) {
  const [internalActive, setInternalActive] = useState(() => {
    if (hashKey) {
      const fromHash = readHashParam(hashKey)
      if (fromHash && tabs.some(t => t.id === fromHash)) return fromHash
    }
    return defaultActive ?? tabs[0]?.id
  })
  const isControlled = active !== undefined
  const activeId = isControlled ? active : internalActive

  const listRef = useRef<HTMLDivElement>(null)
  const btnRefs = useRef<Map<string, HTMLButtonElement>>(new Map())
  const [indicator, setIndicator] = useState<{ left: number; width: number } | null>(null)

  useLayoutEffect(() => {
    const btn = btnRefs.current.get(activeId ?? '')
    const list = listRef.current
    if (!btn || !list) return
    const listRect = list.getBoundingClientRect()
    const btnRect = btn.getBoundingClientRect()
    setIndicator({ left: btnRect.left - listRect.left, width: btnRect.width })
  }, [activeId, tabs.length])

  function selectTab(id: string) {
    if (hashKey) writeHashParam(hashKey, id)
    if (!isControlled) setInternalActive(id)
    onChange?.(id)
  }

  const activeTab = tabs.find(t => t.id === activeId) ?? tabs[0]

  return (
    <div className={`ui-tabs${className ? ` ${className}` : ''}`}>
      <div className="ui-tabs-list" role="tablist" ref={listRef}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            ref={el => { if (el) btnRefs.current.set(tab.id, el); else btnRefs.current.delete(tab.id) }}
            role="tab"
            type="button"
            aria-selected={tab.id === activeId}
            className={`ui-tab-btn${tab.id === activeId ? ' ui-tab-btn--active' : ''}`}
            onClick={() => selectTab(tab.id)}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
        {indicator && (
          <span
            className="ui-tabs-indicator"
            style={{ transform: `translateX(${indicator.left}px)`, width: indicator.width }}
          />
        )}
      </div>
      <div className="ui-tabs-panel" role="tabpanel">
        {activeTab?.content}
      </div>
    </div>
  )
}
