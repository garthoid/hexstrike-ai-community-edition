import { usePersistentState } from './usePersistentState'
import type { Page } from '../app/routing'
import type { NavEntry } from '../app/navRegistry'
import { NAV_ENTRIES, MANDATORY_PAGE_IDS } from '../app/navRegistry'

/** Pages that cannot be disabled (always visible). */
export const ALWAYS_VISIBLE_PAGES: ReadonlySet<Page> = MANDATORY_PAGE_IDS

export interface PageConfig {
  page: Exclude<Page, 'session-detail'>
  label: string
  description: string
}

/** All navigable pages with human-readable metadata, derived from the nav registry. */
export const PAGE_CONFIGS: PageConfig[] = NAV_ENTRIES.map(({ id, label, description }) => ({
  page: id,
  label,
  description,
}))

const STORAGE_KEY = 'nyxstrike_disabled_pages'
const ORDER_STORAGE_KEY = 'nyxstrike_page_order'

const REORDERABLE_PAGE_IDS: Page[] = NAV_ENTRIES.filter(e => !e.mandatory).map(e => e.id)

function reconcileOrder(stored: string[]): Page[] {
  const validSet = new Set<string>(REORDERABLE_PAGE_IDS)
  const kept = stored.filter((id): id is Page => validSet.has(id))
  const missing = REORDERABLE_PAGE_IDS.filter(id => !kept.includes(id))
  return [...kept, ...missing]
}

export function usePageVisibility() {
  const [disabledPages, setDisabledPages] = usePersistentState<string[]>(STORAGE_KEY, [])
  const [pageOrder, setPageOrder] = usePersistentState<string[]>(ORDER_STORAGE_KEY, [])

  function isPageEnabled(page: Page): boolean {
    if (ALWAYS_VISIBLE_PAGES.has(page)) return true
    return !disabledPages.includes(page)
  }

  function togglePage(page: Page) {
    if (ALWAYS_VISIBLE_PAGES.has(page)) return
    setDisabledPages(prev =>
      prev.includes(page) ? prev.filter(p => p !== page) : [...prev, page]
    )
  }

  const orderedIds = reconcileOrder(pageOrder)

  function reorderPage(draggedId: string, targetId: string) {
    const current = reconcileOrder(pageOrder)
    const from = current.indexOf(draggedId as Page)
    const to = current.indexOf(targetId as Page)
    if (from === -1 || to === -1 || from === to) return
    const next = [...current]
    next.splice(from, 1)
    next.splice(to, 0, draggedId as Page)
    setPageOrder(next)
  }

  const orderedPageConfigs: PageConfig[] = orderedIds
    .map(id => PAGE_CONFIGS.find(c => c.page === id))
    .filter((c): c is PageConfig => !!c)

  const orderedNavEntries: NavEntry[] = [
    ...NAV_ENTRIES.filter(e => e.mandatory),
    ...orderedIds
      .map(id => NAV_ENTRIES.find(e => e.id === id))
      .filter((e): e is NavEntry => !!e),
  ]

  return {
    disabledPages, isPageEnabled, togglePage,
    orderedPageConfigs, orderedNavEntries, reorderPage,
  }
}
