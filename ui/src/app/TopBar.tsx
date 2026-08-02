import { useEffect, useRef, useState } from 'react'
import './TopBar.css'
import faviconUrl from '../favicon-16x16.png'
import { RefreshCw, Lock, Menu } from 'lucide-react'
import { clearToken, hasToken, type WebDashboardResponse } from '../api'
import { type ThemeId } from './themes'
import { ThemePickerModal } from '../components/ThemePickerModal'
import { UpdateModal } from '../components/UpdateModal'
import { ReportGenerationBubble } from '../components/ReportGenerationBubble'

interface TopBarProps {
  lastRefresh: Date | null
  demo: boolean
  isStreaming: boolean
  streamingError: string | null
  health: WebDashboardResponse | null
  error: string | null
  loading: boolean
  fetchAll: () => Promise<void>
  themeId: ThemeId
  setThemeId: (theme: ThemeId) => void
  reduceTextureEffects: boolean
  setReduceTextureEffects: (value: boolean) => void
  onOpenCommandPalette: () => void
  onSignOut: () => void
  onToggleMobileSidebar: () => void
}

export function TopBar({
  lastRefresh,
  demo,
  isStreaming,
  streamingError,
  health,
  error,
  loading,
  fetchAll,
  themeId,
  setThemeId,
  reduceTextureEffects,
  setReduceTextureEffects,
  onOpenCommandPalette,
  onSignOut,
  onToggleMobileSidebar,
}: TopBarProps) {
  const REFRESH_BUTTON_DELAY_MS = 3500
  const [themeModalOpen, setThemeModalOpen] = useState(false)
  const [updateModalOpen, setUpdateModalOpen] = useState(false)
  const [showRefreshButton, setShowRefreshButton] = useState(false)
  const [statusPulse, setStatusPulse] = useState(false)
  const firstRefreshIsoRef = useRef<string | null>(null)
  const statusPulseIsoRef = useRef<string | null>(null)
  const [showRefreshInTooltip, setShowRefreshInTooltip] = useState(demo)

  useEffect(() => {
    if (demo) {
      setShowRefreshInTooltip(true)
      return
    }
    if (!lastRefresh) return
    const iso = lastRefresh.toISOString()
    if (!firstRefreshIsoRef.current) {
      firstRefreshIsoRef.current = iso
      return
    }
    if (firstRefreshIsoRef.current !== iso) {
      setShowRefreshInTooltip(true)
      firstRefreshIsoRef.current = iso
    }
  }, [demo, lastRefresh])

  useEffect(() => {
    if (!lastRefresh || health?.status !== 'healthy') return
    const iso = lastRefresh.toISOString()
    if (!statusPulseIsoRef.current) {
      statusPulseIsoRef.current = iso
      return
    }
    if (statusPulseIsoRef.current === iso) return

    statusPulseIsoRef.current = iso
    setStatusPulse(true)
    const timerId = window.setTimeout(() => setStatusPulse(false), 700)
    return () => window.clearTimeout(timerId)
  }, [lastRefresh, health?.status])

  useEffect(() => {
    if (demo || isStreaming) {
      setShowRefreshButton(false)
      return
    }

    const timerId = window.setTimeout(() => {
      setShowRefreshButton(true)
    }, REFRESH_BUTTON_DELAY_MS)

    return () => {
      window.clearTimeout(timerId)
    }
  }, [demo, isStreaming])

  const healthLabel = health?.status
    ? health.status.charAt(0).toUpperCase() + health.status.slice(1)
    : (loading ? 'Connecting…' : error ?? 'Unknown')
  const streamLabel = isStreaming ? 'Live' : streamingError ? 'Polling' : 'N/A'
  const refreshPart = showRefreshInTooltip && lastRefresh
    ? ` | Last refresh: ${lastRefresh.toLocaleTimeString('en-GB')}`
    : ''
  const statusTooltip = demo
    ? `System: ${healthLabel}${refreshPart}`
    : `System: ${healthLabel} | Updates: ${streamLabel}${refreshPart}${streamingError ? ` (${streamingError})` : ''}`

  return (
    <>
      <UpdateModal
        isOpen={updateModalOpen}
        latestVersion={health?.update?.latest_version}
        onClose={() => setUpdateModalOpen(false)}
      />

      <ThemePickerModal
        isOpen={themeModalOpen}
        themeId={themeId}
        setThemeId={setThemeId}
        reduceTextureEffects={reduceTextureEffects}
        setReduceTextureEffects={setReduceTextureEffects}
        onClose={() => setThemeModalOpen(false)}
      />

      <header className="topbar">
        <div className="topbar-brand">
          <button
            type="button"
            className="icon-btn topbar-hamburger-btn"
            onClick={onToggleMobileSidebar}
            aria-label="Toggle navigation menu"
            title="Toggle navigation menu"
          >
            <Menu size={16} />
          </button>
          <img src={faviconUrl} width={18} height={18} alt="" />
          <span
            className="brand-text"
            title={`Version: ${health?.version ?? 'unknown'}`}
            aria-label={`NyxStrike version ${health?.version ?? 'unknown'}`}
          >
            <span className="brand-text-1">Nyx</span><span className="brand-text-2">Strike</span>
          </span>
          {health?.update?.update_available && (
            <button
              type="button"
              className="brand-update-chip mono"
              onClick={() => setUpdateModalOpen(true)}
              title={`New version available: ${health.update.latest_version}`}
            >
              Update available
            </button>
          )}
        </div>

        <div className="topbar-right">
          <button
            className="icon-btn"
            title="Command palette (Ctrl/Cmd+K)"
            onClick={onOpenCommandPalette}
          >
          <span className="palette-icon-k mono">K</span>
        </button>
        <div
          className={`status-dot ${health?.status === 'healthy' ? (showRefreshButton ? 'polling' : 'online') : error ? 'error' : 'loading'}${statusPulse ? ' status-dot--pulse' : ''}`}
          title={statusTooltip}
          aria-label={statusTooltip}
        />
        {showRefreshButton && (
          <button className="icon-btn" onClick={fetchAll} title="Refresh now">
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
          </button>
        )}
        {hasToken() && (
          <button className="icon-btn" onClick={() => { clearToken(); onSignOut() }} title="Sign out">
            <Lock size={14} />
          </button>
        )}
      </div>
    </header>

      <ReportGenerationBubble />
    </>
  )
}
