import { usePersistentState } from './usePersistentState'
import { WIDGET_REGISTRY, WIDGET_IDS, DEFAULT_WIDGET_ORDER } from '../app/widgetRegistry'
import type { WidgetEntry } from '../app/widgetRegistry'

const STORAGE_KEY = 'nyxstrike_dashboard_widgets'

function reconcileWidgetOrder(stored: string[]): string[] {
  const validIds = new Set(WIDGET_IDS)
  return stored.filter(id => validIds.has(id))
}

export function useWidgetLayout() {
  const [widgetOrder, setWidgetOrder] = usePersistentState<string[]>(STORAGE_KEY, DEFAULT_WIDGET_ORDER)

  const orderedIds = reconcileWidgetOrder(widgetOrder)

  const enabledWidgets: WidgetEntry[] = orderedIds
    .map(id => WIDGET_REGISTRY.find(w => w.id === id))
    .filter((w): w is WidgetEntry => !!w)

  const availableWidgets: WidgetEntry[] = WIDGET_REGISTRY.filter(w => !orderedIds.includes(w.id))

  function addWidget(id: string) {
    setWidgetOrder(prev => (prev.includes(id) ? prev : [...prev, id]))
  }

  function removeWidget(id: string) {
    setWidgetOrder(prev => prev.filter(w => w !== id))
  }

  function reorderWidget(draggedId: string, targetId: string) {
    setWidgetOrder(prev => {
      const current = reconcileWidgetOrder(prev)
      const from = current.indexOf(draggedId)
      const to = current.indexOf(targetId)
      if (from === -1 || to === -1 || from === to) return prev
      const next = [...current]
      next.splice(from, 1)
      next.splice(to, 0, draggedId)
      return next
    })
  }

  return { enabledWidgets, availableWidgets, addWidget, removeWidget, reorderWidget }
}
