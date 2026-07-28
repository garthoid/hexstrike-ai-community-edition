import { useEffect, useState } from 'react'
import { routeFromHash, type Page } from './routing'

export function useAppRouting(isPageEnabled: (page: Page) => boolean) {
  const initialRoute = routeFromHash()
  const [page, setPageState] = useState<Page>(initialRoute.page)
  const [activeSessionId, setActiveSessionId] = useState<string | null>(initialRoute.sessionId)
  const [activeToolName, setActiveToolNameState] = useState<string | null>(initialRoute.toolName)
  const [sidebarMobileOpen, setSidebarMobileOpen] = useState(false)

  function setPage(p: Page) {
    if (p === 'session-detail') return
    window.location.hash = `/${p === 'dashboard' ? '' : p}`
    setPageState(p)
    setActiveSessionId(null)
    setActiveToolNameState(null)
    setSidebarMobileOpen(false)
  }

  function openSessionDetail(sessionId: string) {
    window.location.hash = `/sessions/${sessionId}`
    setPageState('session-detail')
    setActiveSessionId(sessionId)
    setActiveToolNameState(null)
    setSidebarMobileOpen(false)
  }

  // Reflects the currently selected Run-page tool into the URL, so it's bookmarkable/shareable.
  // Does not carry any tool params/inputs — just which tool the Run page should open with.
  function setActiveToolName(toolName: string | null) {
    window.location.hash = toolName ? `/run/${encodeURIComponent(toolName)}` : '/run'
    setActiveToolNameState(toolName)
  }

  // Keep state in sync if the user presses Back/Forward
  useEffect(() => {
    function onHashChange() {
      const route = routeFromHash()
      setPageState(route.page)
      setActiveSessionId(route.sessionId)
      setActiveToolNameState(route.toolName)
      setSidebarMobileOpen(false)
    }
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  // If the active page gets disabled, fall back to dashboard
  useEffect(() => {
    if (!isPageEnabled(page)) {
      setPage('dashboard')
    }
  }, [page, isPageEnabled])

  return {
    page,
    activeSessionId,
    activeToolName,
    sidebarMobileOpen,
    setSidebarMobileOpen,
    setPage,
    openSessionDetail,
    setActiveToolName,
  }
}
