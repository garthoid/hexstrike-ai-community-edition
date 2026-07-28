import { useEffect, useRef, useState } from 'react'
import { Palette, PanelBottomOpen, X, Github } from 'lucide-react'
import { DiscordIcon } from './DiscordIcon'

interface QuickActionsFabProps {
  onOpenCommandPalette: () => void
  onOpenThemeModal: () => void
}

export function QuickActionsFab({ onOpenCommandPalette, onOpenThemeModal }: QuickActionsFabProps) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    function onPointerDown(e: MouseEvent) {
      if (!ref.current) return
      if (!ref.current.contains(e.target as Node)) setOpen(false)
    }

    function onEscClose(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false)
    }

    if (open) {
      window.addEventListener('mousedown', onPointerDown)
      window.addEventListener('keydown', onEscClose)
    }

    return () => {
      window.removeEventListener('mousedown', onPointerDown)
      window.removeEventListener('keydown', onEscClose)
    }
  }, [open])

  return (
    <div ref={ref} className={`quick-actions-fab${open ? ' open' : ''}`}>
      <div className="quick-actions-panel" aria-hidden={!open}>
        <button
          className="quick-actions-item"
          onClick={() => {
            onOpenCommandPalette()
            setOpen(false)
          }}
          title="Open command palette"
        >
          <span className="quick-actions-item-icon mono">K</span>
          <span>Command Palette</span>
        </button>
        <button
          className="quick-actions-item"
          onClick={() => {
            onOpenThemeModal()
            setOpen(false)
          }}
          title="Choose theme"
        >
          <Palette size={14} />
          <span>Theme Picker</span>
        </button>
        <button
          className="quick-actions-item"
          onClick={() => {
            window.open('https://github.com/CommonHuman-Lab/nyxstrike', '_blank', 'noopener,noreferrer')
            setOpen(false)
          }}
          title="Open GitHub"
        >
          <Github size={14} />
          <span>GitHub</span>
        </button>
        <button
          className="quick-actions-item"
          onClick={() => {
            window.open('https://discord.gg/aC8Q2xJFgp', '_blank', 'noopener,noreferrer')
            setOpen(false)
          }}
          title="Join Discord community"
        >
          <DiscordIcon size={14} />
          <span>Discord</span>
        </button>
      </div>

      <button
        className="quick-actions-trigger"
        onClick={() => setOpen(v => !v)}
        aria-expanded={open}
        aria-label={open ? 'Close quick actions' : 'Open quick actions'}
        title={open ? 'Close quick actions' : 'Open quick actions'}
      >
        {open ? <X size={16} /> : <PanelBottomOpen size={16} />}
      </button>
    </div>
  )
}
