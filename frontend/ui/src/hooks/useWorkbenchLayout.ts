import { usePersistentState } from './usePersistentState'
import type { WorkbenchOperation } from '../api'

function reconcileOrder(stored: string[], liveIds: string[]): string[] {
  const valid = new Set(liveIds)
  const kept = stored.filter(id => valid.has(id))
  const missing = liveIds.filter(id => !kept.includes(id))
  return [...kept, ...missing]
}

export function useWorkbenchLayout(categories: string[], operations: WorkbenchOperation[]) {
  const [hiddenCategories, setHiddenCategories] = usePersistentState<string[]>('nyxstrike_workbench_hidden_categories', [])
  const [hiddenOperations, setHiddenOperations] = usePersistentState<string[]>('nyxstrike_workbench_hidden_operations', [])
  const [categoryOrderStored, setCategoryOrderStored] = usePersistentState<string[]>('nyxstrike_workbench_category_order', [])
  const [operationOrderStored, setOperationOrderStored] = usePersistentState<string[]>('nyxstrike_workbench_operation_order', [])

  const categoryOrder = reconcileOrder(categoryOrderStored, categories)
  const operationIds = operations.map(op => op.id)
  const operationOrder = reconcileOrder(operationOrderStored, operationIds)

  const allByCategory: [string, WorkbenchOperation[]][] = categoryOrder.map(category => [
    category,
    operationOrder
      .map(id => operations.find(op => op.id === id))
      .filter((op): op is WorkbenchOperation => !!op && op.category === category),
  ])

  const visibleByCategory: [string, WorkbenchOperation[]][] = allByCategory
    .filter(([category]) => !hiddenCategories.includes(category))
    .map(([category, ops]): [string, WorkbenchOperation[]] => [
      category,
      ops.filter(op => !hiddenOperations.includes(op.id)),
    ])

  function isCategoryHidden(category: string): boolean {
    return hiddenCategories.includes(category)
  }

  function isOperationHidden(id: string): boolean {
    return hiddenOperations.includes(id)
  }

  function hideCategory(category: string) {
    setHiddenCategories(prev => prev.includes(category) ? prev : [...prev, category])
  }

  function showCategory(category: string) {
    setHiddenCategories(prev => prev.filter(c => c !== category))
  }

  function hideOperation(id: string) {
    setHiddenOperations(prev => prev.includes(id) ? prev : [...prev, id])
  }

  function showOperation(id: string) {
    setHiddenOperations(prev => prev.filter(o => o !== id))
  }

  function reorderCategory(draggedId: string, targetId: string) {
    const current = reconcileOrder(categoryOrderStored, categories)
    const from = current.indexOf(draggedId)
    const to = current.indexOf(targetId)
    if (from === -1 || to === -1 || from === to) return
    const next = [...current]
    next.splice(from, 1)
    next.splice(to, 0, draggedId)
    setCategoryOrderStored(next)
  }

  function reorderOperation(draggedId: string, targetId: string) {
    const current = reconcileOrder(operationOrderStored, operationIds)
    const from = current.indexOf(draggedId)
    const to = current.indexOf(targetId)
    if (from === -1 || to === -1 || from === to) return
    const next = [...current]
    next.splice(from, 1)
    next.splice(to, 0, draggedId)
    setOperationOrderStored(next)
  }

  function resetLayout() {
    setHiddenCategories([])
    setHiddenOperations([])
    setCategoryOrderStored([])
    setOperationOrderStored([])
  }

  return {
    allByCategory,
    visibleByCategory,
    isCategoryHidden,
    isOperationHidden,
    hideCategory,
    showCategory,
    hideOperation,
    showOperation,
    reorderCategory,
    reorderOperation,
    resetLayout,
  }
}
