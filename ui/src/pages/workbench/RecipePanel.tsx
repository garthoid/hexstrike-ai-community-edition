import { useEffect, useState } from 'react'
import type { Dispatch, SetStateAction } from 'react'
import {
  ArrowUp, ArrowDown, X, Play, RefreshCw, Copy, Check, Workflow, Pencil,
  Save, FolderOpen, Trash2, GripVertical,
} from 'lucide-react'
import { api } from '../../api'
import type { WorkbenchOperation, WorkbenchRecipeStepResult, WorkbenchSavedRecipe } from '../../api'

export interface RecipeStep {
  stepId: string
  operationId: string
  operationName: string
  params: Record<string, string>
}

interface RecipePanelProps {
  recipe: RecipeStep[]
  setRecipe: Dispatch<SetStateAction<RecipeStep[]>>
  operations: WorkbenchOperation[]
  input: string
  setInput: Dispatch<SetStateAction<string>>
}

export function RecipePanel({ recipe, setRecipe, operations, input, setInput }: RecipePanelProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [output, setOutput] = useState<string | null>(null)
  const [steps, setSteps] = useState<WorkbenchRecipeStepResult[]>([])
  const [copied, setCopied] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editValues, setEditValues] = useState<Record<string, string>>({})
  const [dragIndex, setDragIndex] = useState<number | null>(null)

  const [savedRecipes, setSavedRecipes] = useState<WorkbenchSavedRecipe[]>([])
  const [savedLoading, setSavedLoading] = useState(false)
  const [savedError, setSavedError] = useState<string | null>(null)
  const [savingAs, setSavingAs] = useState(false)
  const [saveAsName, setSaveAsName] = useState('')
  const [renamingRecipeId, setRenamingRecipeId] = useState<string | null>(null)
  const [renameDraft, setRenameDraft] = useState('')

  function loadSavedRecipes() {
    setSavedLoading(true)
    setSavedError(null)
    api.workbenchRecipes()
      .then(res => {
        if (!res.success) {
          setSavedError('Failed to load saved recipes.')
          return
        }
        setSavedRecipes(res.recipes)
      })
      .catch(e => setSavedError(String(e)))
      .finally(() => setSavedLoading(false))
  }

  useEffect(() => {
    loadSavedRecipes()
  }, [])

  function move(index: number, dir: -1 | 1) {
    setRecipe(prev => {
      const next = [...prev]
      const target = index + dir
      if (target < 0 || target >= next.length) return prev
      ;[next[index], next[target]] = [next[target], next[index]]
      return next
    })
  }

  function reorder(from: number, to: number) {
    if (from === to) return
    setRecipe(prev => {
      const next = [...prev]
      const [moved] = next.splice(from, 1)
      next.splice(to, 0, moved)
      return next
    })
  }

  function remove(index: number) {
    setRecipe(prev => prev.filter((_, i) => i !== index))
    setEditingId(prev => (recipe[index]?.stepId === prev ? null : prev))
  }

  function startEdit(step: RecipeStep) {
    setEditingId(step.stepId)
    setEditValues({ ...step.params })
  }

  function cancelEdit() {
    setEditingId(null)
  }

  function saveEdit(stepId: string) {
    setRecipe(prev => prev.map(s => (s.stepId === stepId ? { ...s, params: editValues } : s)))
    setEditingId(null)
  }

  async function run() {
    setLoading(true)
    setError(null)
    setOutput(null)
    setSteps([])
    try {
      const res = await api.workbenchRunRecipe(
        input,
        recipe.map(s => ({ operation_id: s.operationId, params: s.params }))
      )
      setSteps(res.steps ?? [])
      if (!res.success) {
        setError(res.error ?? 'Recipe failed.')
        return
      }
      setOutput(res.output ?? '')
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  function copyOutput() {
    if (!output) return
    navigator.clipboard?.writeText(output).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }).catch(() => {})
  }

  function startSaveAs() {
    setSaveAsName('')
    setSavingAs(true)
  }

  function cancelSaveAs() {
    setSavingAs(false)
  }

  async function confirmSaveAs() {
    const name = saveAsName.trim()
    if (!name) return
    const res = await api.createWorkbenchRecipe(
      name,
      recipe.map(s => ({ operation_id: s.operationId, params: s.params }))
    )
    if (res.success) {
      setSavingAs(false)
      loadSavedRecipes()
    } else {
      setSavedError(res.error ?? 'Failed to save recipe.')
    }
  }

  function loadSavedRecipe(saved: WorkbenchSavedRecipe) {
    const loaded = saved.steps
      .map((s): RecipeStep | null => {
        const operation = operations.find(op => op.id === s.operation_id)
        if (!operation) return null
        return {
          stepId: crypto.randomUUID(),
          operationId: s.operation_id,
          operationName: operation.name,
          params: (s.params ?? {}) as Record<string, string>,
        }
      })
      .filter((s): s is RecipeStep => s !== null)
    setRecipe(loaded)
    setEditingId(null)
  }

  function startRenameRecipe(saved: WorkbenchSavedRecipe) {
    setRenamingRecipeId(saved.recipe_id)
    setRenameDraft(saved.name)
  }

  function cancelRenameRecipe() {
    setRenamingRecipeId(null)
  }

  async function confirmRenameRecipe(recipeId: string) {
    const name = renameDraft.trim()
    if (!name) return
    const res = await api.updateWorkbenchRecipe(recipeId, { name })
    if (res.success) {
      setRenamingRecipeId(null)
      loadSavedRecipes()
    } else {
      setSavedError(res.error ?? 'Failed to rename recipe.')
    }
  }

  async function deleteSavedRecipe(recipeId: string) {
    const res = await api.deleteWorkbenchRecipe(recipeId)
    if (res.success) {
      loadSavedRecipes()
    } else {
      setSavedError(res.error ?? 'Failed to delete recipe.')
    }
  }

  return (
    <section className={`workbench-recipe${recipe.length > 0 ? ' section' : ''}`}>
      {recipe.length > 0 && (
        <div className="section-header">
          <h3><Workflow size={14} style={{ marginRight: 6, verticalAlign: -2 }} />Recipe</h3>
        </div>
      )}
      <div className="workbench-op-content">
        <div className="workbench-saved-recipes">
          <div className="workbench-saved-recipes-header">
            <span className="workbench-field-label"><FolderOpen size={12} style={{ marginRight: 4, verticalAlign: -2 }} />Saved Recipes</span>
            {recipe.length > 0 && !savingAs && (
              <button className="icon-btn" onClick={startSaveAs} title="Save current recipe">
                <Save size={12} />
              </button>
            )}
          </div>

          {savingAs && (
            <div className="workbench-saved-recipe-row workbench-saved-recipe-row--edit">
              <input
                className="input input-full mono"
                placeholder="Recipe name…"
                value={saveAsName}
                autoFocus
                onChange={e => setSaveAsName(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter') void confirmSaveAs()
                  if (e.key === 'Escape') cancelSaveAs()
                }}
              />
              <button className="icon-btn" onClick={() => void confirmSaveAs()} title="Confirm"><Check size={12} /></button>
              <button className="icon-btn" onClick={cancelSaveAs} title="Cancel"><X size={12} /></button>
            </div>
          )}

          {savedLoading && <div className="workbench-panel-empty-hint">Loading…</div>}
          {savedError && <div className="verify-error">{savedError}</div>}

          {!savedLoading && savedRecipes.length === 0 && !savingAs && (
            <div className="workbench-panel-empty-hint">No saved recipes yet.</div>
          )}

          {savedRecipes.map(saved => (
            <div key={saved.recipe_id} className="workbench-saved-recipe-row">
              {renamingRecipeId === saved.recipe_id ? (
                <>
                  <input
                    className="input input-full mono"
                    value={renameDraft}
                    autoFocus
                    onChange={e => setRenameDraft(e.target.value)}
                    onKeyDown={e => {
                      if (e.key === 'Enter') void confirmRenameRecipe(saved.recipe_id)
                      if (e.key === 'Escape') cancelRenameRecipe()
                    }}
                  />
                  <button className="icon-btn" onClick={() => void confirmRenameRecipe(saved.recipe_id)} title="Confirm"><Check size={12} /></button>
                  <button className="icon-btn" onClick={cancelRenameRecipe} title="Cancel"><X size={12} /></button>
                </>
              ) : (
                <>
                  <span className="workbench-saved-recipe-name mono" title={saved.name}>{saved.name}</span>
                  <span className="workbench-saved-recipe-actions">
                    <button className="icon-btn" onClick={() => loadSavedRecipe(saved)} title="Load into working recipe">
                      <FolderOpen size={12} />
                    </button>
                    <button className="icon-btn" onClick={() => startRenameRecipe(saved)} title="Rename">
                      <Pencil size={12} />
                    </button>
                    <button className="icon-btn" onClick={() => void deleteSavedRecipe(saved.recipe_id)} title="Delete">
                      <Trash2 size={12} />
                    </button>
                  </span>
                </>
              )}
            </div>
          ))}
        </div>

        {recipe.length === 0 ? (
          <div className="workbench-panel-empty">
            <Workflow size={28} color="var(--text-dim)" />
            <span className="workbench-panel-empty-title">No recipe yet</span>
            <span className="workbench-panel-empty-hint">
              Use "Add to Recipe" on any operation to chain it here — each step's output feeds the next step's input.
            </span>
          </div>
        ) : (
          <ol className="workbench-recipe-steps">
            {recipe.map((step, i) => {
              const operation = operations.find(op => op.id === step.operationId)
              const editableParams = operation?.params.filter(p => p.name !== 'input') ?? []
              const isEditing = editingId === step.stepId
              return (
                <li
                  key={step.stepId}
                  className={`workbench-recipe-step-wrap${dragIndex === i ? ' workbench-recipe-step-wrap--dragging' : ''}`}
                  draggable
                  onDragStart={() => setDragIndex(i)}
                  onDragOver={e => e.preventDefault()}
                  onDrop={e => {
                    e.preventDefault()
                    if (dragIndex !== null) reorder(dragIndex, i)
                    setDragIndex(null)
                  }}
                  onDragEnd={() => setDragIndex(null)}
                >
                  <div className="workbench-recipe-step">
                    <span className="workbench-recipe-step-drag" title="Drag to reorder">
                      <GripVertical size={12} />
                    </span>
                    <span className="workbench-recipe-step-index">{i + 1}</span>
                    <span className="workbench-recipe-step-name">{step.operationName}</span>
                    {Object.keys(step.params).length > 0 && (
                      <span className="workbench-recipe-step-params mono">
                        {Object.entries(step.params).map(([k, v]) => `${k}=${v}`).join(', ')}
                      </span>
                    )}
                    <span className="workbench-recipe-step-actions">
                      <button className="icon-btn" onClick={() => move(i, -1)} disabled={i === 0} title="Move up">
                        <ArrowUp size={12} />
                      </button>
                      <button className="icon-btn" onClick={() => move(i, 1)} disabled={i === recipe.length - 1} title="Move down">
                        <ArrowDown size={12} />
                      </button>
                      {editableParams.length > 0 && (
                        <button
                          className="icon-btn"
                          onClick={() => (isEditing ? cancelEdit() : startEdit(step))}
                          title="Edit settings"
                        >
                          <Pencil size={12} />
                        </button>
                      )}
                      <button className="icon-btn" onClick={() => remove(i)} title="Remove">
                        <X size={12} />
                      </button>
                    </span>
                  </div>

                  {isEditing && (
                    <div className="workbench-recipe-step-edit">
                      {editableParams.map(p => (
                        <label key={p.name} className="workbench-field">
                          <span className="workbench-field-label">{p.label}</span>
                          {p.type === 'select' ? (
                            <select
                              className="input input-full"
                              value={editValues[p.name] ?? ''}
                              onChange={e => setEditValues(prev => ({ ...prev, [p.name]: e.target.value }))}
                            >
                              {(p.choices ?? []).map(choice => (
                                <option key={choice} value={choice}>{choice}</option>
                              ))}
                            </select>
                          ) : p.type === 'textarea' ? (
                            <textarea
                              className="input workbench-textarea mono"
                              value={editValues[p.name] ?? ''}
                              onChange={e => setEditValues(prev => ({ ...prev, [p.name]: e.target.value }))}
                              rows={2}
                            />
                          ) : (
                            <input
                              className="input input-full mono"
                              type={p.type === 'number' ? 'number' : 'text'}
                              value={editValues[p.name] ?? ''}
                              onChange={e => setEditValues(prev => ({ ...prev, [p.name]: e.target.value }))}
                            />
                          )}
                          {p.help_text && <span className="workbench-field-hint">{p.help_text}</span>}
                        </label>
                      ))}
                      <div className="workbench-actions">
                        <button className="workbench-secondary-btn" onClick={() => saveEdit(step.stepId)}>
                          <Check size={13} /> Save
                        </button>
                        <button className="workbench-secondary-btn" onClick={cancelEdit}>
                          <X size={13} /> Cancel
                        </button>
                      </div>
                    </div>
                  )}
                </li>
              )
            })}
          </ol>
        )}

        {recipe.length > 0 && (
          <>
            <label className="workbench-field">
              <span className="workbench-field-label">Input</span>
              <textarea
                className="input workbench-textarea mono"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => {
                  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !loading) {
                    e.preventDefault()
                    void run()
                  }
                }}
                rows={3}
              />
            </label>

            <div className="workbench-actions">
              <button className="workbench-run-btn" onClick={run} disabled={loading}>
                {loading ? <><RefreshCw size={13} className="spin" /> Running…</> : <><Play size={13} /> Run Recipe</>}
              </button>
            </div>

            {error && <div className="verify-error">{error}</div>}

            {steps.length > 0 && (
              <ol className="workbench-recipe-trace">
                {steps.map((s, i) => (
                  <li key={i} className={s.error ? 'workbench-recipe-trace-error' : ''}>
                    <span className="workbench-recipe-step-index">{i + 1}</span>
                    <span className="workbench-field-label">{s.name ?? s.operation_id}</span>
                    <span className="mono">{s.error ? `Error: ${s.error}` : s.output}</span>
                  </li>
                ))}
              </ol>
            )}

            {output !== null && (
              <div className="workbench-output-wrap">
                <div className="workbench-output-header">
                  <span className="workbench-field-label">Final Output</span>
                  <button className="icon-btn" onClick={copyOutput} title="Copy output">
                    {copied ? <Check size={12} color="var(--green)" /> : <Copy size={12} />}
                  </button>
                </div>
                <pre className="verify-result-output mono">{output}</pre>
              </div>
            )}
          </>
        )}
      </div>
    </section>
  )
}
