import { useEffect, useMemo, useState } from 'react'
import { FlaskConical, RefreshCw, Search, ChevronDown, ChevronRight, X } from 'lucide-react'
import { api } from '../../api'
import type { WorkbenchOperation } from '../../api'
import { usePersistentState } from '../../hooks/usePersistentState'
import { OperationPanel } from './OperationPanel'
import { RecipePanel, type RecipeStep } from './RecipePanel'
import './WorkbenchPage.css'

export default function WorkbenchPage() {
  const [operations, setOperations] = useState<WorkbenchOperation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [collapsed, setCollapsed] = usePersistentState<string[]>('nyxstrike_workbench_collapsed_categories', [])
  const [recipe, setRecipe] = useState<RecipeStep[]>([])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    api.workbenchOperations()
      .then(res => {
        if (cancelled) return
        if (!res.success) {
          setError('Failed to load operations.')
          return
        }
        setOperations(res.operations)
        setSelectedId(prev => prev ?? res.operations[0]?.id ?? null)
        if (localStorage.getItem('nyxstrike_workbench_collapsed_categories') == null) {
          setCollapsed(Array.from(new Set(res.operations.map(op => op.category))))
        }
      })
      .catch(e => !cancelled && setError(String(e)))
      .finally(() => !cancelled && setLoading(false))
    return () => { cancelled = true }
  }, [])

  const byCategory = useMemo(() => {
    const q = search.trim().toLowerCase()
    const filtered = q
      ? operations.filter(op => op.name.toLowerCase().includes(q) || op.description.toLowerCase().includes(q))
      : operations
    const groups = new Map<string, WorkbenchOperation[]>()
    for (const op of filtered) {
      const list = groups.get(op.category) ?? []
      list.push(op)
      groups.set(op.category, list)
    }
    return Array.from(groups.entries()).sort(([a], [b]) => a.localeCompare(b))
  }, [operations, search])

  const selected = operations.find(op => op.id === selectedId) ?? null

  function toggleCategory(category: string) {
    setCollapsed(prev => prev.includes(category) ? prev.filter(c => c !== category) : [...prev, category])
  }

  function addToRecipe(operation: WorkbenchOperation, params: Record<string, string>) {
    const step: RecipeStep = {
      stepId: crypto.randomUUID(),
      operationId: operation.id,
      operationName: operation.name,
      params,
    }
    setRecipe(prev => [...prev, step])
  }

  return (
    <div className="page-content">
      <div className="workbench-page-header">
        <h1 className="workbench-page-title">
          <FlaskConical size={16} /> Workbench
        </h1>
        <p className="workbench-page-subtitle section-meta">
          Quick, local data transforms — encoding, hashing, ciphers, compression, and analysis.
          Runs entirely in-process, nothing leaves this session. Chain operations into a recipe
          to pipe one output into the next.
        </p>
      </div>

      {loading && (
        <div className="loading-state">
          <RefreshCw size={20} className="spin" color="var(--green)" />
        </div>
      )}

      {error && <div className="workbench-error">{error}</div>}

      {!loading && !error && (
        <div className="workbench-layout">
          <nav className="section workbench-sidebar">
            <div className="workbench-search">
              <Search size={13} className="workbench-search-icon" />
              <input
                className="workbench-search-input"
                placeholder="Find an operation…"
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
              {search && (
                <button className="workbench-search-clear" onClick={() => setSearch('')} title="Clear search">
                  <X size={12} />
                </button>
              )}
            </div>

            {byCategory.map(([category, ops]) => {
              const isCollapsed = search.trim() ? false : collapsed.includes(category)
              return (
                <div key={category} className="workbench-category">
                  <button className="workbench-category-header" onClick={() => toggleCategory(category)}>
                    {isCollapsed ? <ChevronRight size={12} /> : <ChevronDown size={12} />}
                    <span className="workbench-category-label">{category.replace(/_/g, ' ')}</span>
                  </button>
                  {!isCollapsed && ops.map(op => (
                    <button
                      key={op.id}
                      className={`workbench-op-btn${op.id === selectedId ? ' workbench-op-btn--active' : ''}`}
                      onClick={() => setSelectedId(op.id)}
                    >
                      {op.name}
                    </button>
                  ))}
                </div>
              )
            })}
            {byCategory.length === 0 && (
              <div className="workbench-empty">No operations match "{search}".</div>
            )}
          </nav>

          <div className="workbench-main">
            <section className="section workbench-panel">
              {selected
                ? <OperationPanel key={selected.id} operation={selected} onAddToRecipe={addToRecipe} />
                : <div className="workbench-empty">Select an operation to get started.</div>}
            </section>

            <RecipePanel recipe={recipe} setRecipe={setRecipe} />
          </div>
        </div>
      )}
    </div>
  )
}
