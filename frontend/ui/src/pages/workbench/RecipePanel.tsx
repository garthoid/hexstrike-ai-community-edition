import { useEffect, useRef, useState } from 'react'
import type { Dispatch, SetStateAction } from 'react'
import {
  ArrowUp, ArrowDown, X, Play, RefreshCw, Copy, Check, Workflow, Pencil,
  Save, FolderOpen, FolderPlus, Trash2, GripVertical, SkipForward, Sparkles, Download,
  Link2, Upload, Eraser, Send,
} from 'lucide-react'
import { api } from '../../api'
import type { WorkbenchOperation, WorkbenchRecipeStepResult, WorkbenchSavedRecipe } from '../../api'
import { useDragReorder } from '../../hooks/useDragReorder'
import { usePersistentState } from '../../hooks/usePersistentState'
import { downloadWorkbenchOutput } from './fileIO'
import { downloadRecipeAsFile, parseRecipeFile } from './recipeIO'
import { ConfirmActionModal } from '../../components/modals/ConfirmActionModal'
import { SendToLootModal } from '../../components/modals/SendToLootModal'
import { useToast } from '../../components/feedback/ToastProvider'

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
  const [outputMime, setOutputMime] = useState<string | undefined>(undefined)
  const [hasErrors, setHasErrors] = useState(false)
  const [steps, setSteps] = useState<WorkbenchRecipeStepResult[]>([])
  const [copied, setCopied] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editValues, setEditValues] = useState<Record<string, string>>({})
  const [continueOnError, setContinueOnError] = usePersistentState('nyxstrike_workbench_continue_on_error', false)
  const [overrideEditingId, setOverrideEditingId] = useState<string | null>(null)
  const [overrideDraft, setOverrideDraft] = useState('')
  const [stepOverrides, setStepOverrides] = useState<Record<number, string>>({})

  const [savedRecipes, setSavedRecipes] = useState<WorkbenchSavedRecipe[]>([])
  const [savedLoading, setSavedLoading] = useState(false)
  const [savedError, setSavedError] = useState<string | null>(null)
  const [savingAs, setSavingAs] = useState(false)
  const [saveAsName, setSaveAsName] = useState('')
  const [renamingRecipeId, setRenamingRecipeId] = useState<string | null>(null)
  const [renameDraft, setRenameDraft] = useState('')
  const [loadedRecipeId, setLoadedRecipeId] = useState<string | null>(null)
  const [savingInPlace, setSavingInPlace] = useState(false)
  const [pendingDelete, setPendingDelete] = useState<WorkbenchSavedRecipe | null>(null)
  const [deletingRecipe, setDeletingRecipe] = useState(false)
  const [sendToLootOpen, setSendToLootOpen] = useState(false)
  const importFileRef = useRef<HTMLInputElement>(null)
  const { pushToast } = useToast()

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
    setStepOverrides({})
  }

  function reorderByStepId(draggedStepId: string, targetStepId: string) {
    setRecipe(prev => {
      const next = [...prev]
      const fromIndex = next.findIndex(s => s.stepId === draggedStepId)
      const toIndex = next.findIndex(s => s.stepId === targetStepId)
      if (fromIndex === -1 || toIndex === -1) return prev
      const [moved] = next.splice(fromIndex, 1)
      next.splice(toIndex, 0, moved)
      return next
    })
    setStepOverrides({})
  }

  const { dragHandlers, dragClassName } = useDragReorder(reorderByStepId)

  function remove(index: number) {
    setRecipe(prev => prev.filter((_, i) => i !== index))
    setEditingId(prev => (recipe[index]?.stepId === prev ? null : prev))
    setStepOverrides({})
  }

  function duplicate(index: number) {
    setRecipe(prev => {
      const step = prev[index]
      if (!step) return prev
      const copy: RecipeStep = { ...step, stepId: crypto.randomUUID(), params: { ...step.params } }
      const next = [...prev]
      next.splice(index + 1, 0, copy)
      return next
    })
    setStepOverrides({})
  }

  function clearRecipe() {
    setRecipe([])
    setLoadedRecipeId(null)
    pushToast('info', 'Recipe cleared — undo with Ctrl+Z.')
  }

  function copyRecipeLink() {
    navigator.clipboard?.writeText(window.location.href)
      .then(() => pushToast('success', 'Recipe link copied.'))
      .catch(() => pushToast('error', 'Failed to copy link.'))
  }

  function exportRecipe() {
    downloadRecipeAsFile(recipe)
  }

  function triggerImport() {
    importFileRef.current?.click()
  }

  function handleImportFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      try {
        const { steps, skipped } = parseRecipeFile(String(reader.result ?? ''), operations)
        setRecipe(steps)
        setLoadedRecipeId(null)
        pushToast('success', skipped > 0 ? `Recipe imported — ${skipped} step(s) skipped (unknown operation).` : 'Recipe imported.')
      } catch (err) {
        pushToast('error', `Failed to import recipe: ${String(err)}`)
      }
    }
    reader.readAsText(file)
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

  async function runRecipe(stopAfterStepIndex?: number) {
    setLoading(true)
    setError(null)
    setOutput(null)
    setOutputMime(undefined)
    setHasErrors(false)
    setSteps([])
    try {
      const res = await api.workbenchRunRecipe(
        input,
        recipe.map(s => ({ operation_id: s.operationId, params: s.params })),
        { continueOnError, stopAfterStepIndex, stepInputOverrides: stepOverrides }
      )
      setSteps(res.steps ?? [])
      setHasErrors(!!res.has_errors)
      if (!res.success) {
        setError(res.error ?? 'Recipe failed.')
        return
      }
      setOutput(res.output ?? '')
      setOutputMime(res.output_mime)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  function run() {
    return runRecipe(undefined)
  }

  function runToStep(index: number) {
    return runRecipe(index)
  }

  function startOverride(index: number, current: string) {
    setOverrideEditingId(String(index))
    setOverrideDraft(stepOverrides[index] ?? current)
  }

  function cancelOverride() {
    setOverrideEditingId(null)
  }

  function saveOverride(index: number) {
    setStepOverrides(prev => ({ ...prev, [index]: overrideDraft }))
    setOverrideEditingId(null)
  }

  function clearOverride(index: number) {
    setStepOverrides(prev => {
      const next = { ...prev }
      delete next[index]
      return next
    })
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
      setLoadedRecipeId(res.recipe?.recipe_id ?? null)
      loadSavedRecipes()
      pushToast('success', `Saved as "${name}".`)
    } else {
      setSavedError(res.error ?? 'Failed to save recipe.')
    }
  }

  async function saveInPlace() {
    if (!loadedRecipeId) return
    setSavingInPlace(true)
    const res = await api.updateWorkbenchRecipe(loadedRecipeId, {
      steps: recipe.map(s => ({ operation_id: s.operationId, params: s.params })),
    })
    setSavingInPlace(false)
    if (res.success) {
      loadSavedRecipes()
      pushToast('success', 'Recipe saved.')
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
    setLoadedRecipeId(saved.recipe_id)
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

  async function confirmDelete() {
    if (!pendingDelete) return
    setDeletingRecipe(true)
    const res = await api.deleteWorkbenchRecipe(pendingDelete.recipe_id)
    setDeletingRecipe(false)
    if (res.success) {
      if (loadedRecipeId === pendingDelete.recipe_id) setLoadedRecipeId(null)
      setPendingDelete(null)
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
          <span className="workbench-recipe-toolbar">
            <button className="icon-btn" onClick={copyRecipeLink} title="Copy link to this recipe">
              <Link2 size={12} />
            </button>
            <button className="icon-btn" onClick={exportRecipe} title="Export recipe as a JSON file">
              <Download size={12} />
            </button>
            <button className="icon-btn" onClick={triggerImport} title="Import recipe from a JSON file">
              <Upload size={12} />
            </button>
            <input
              ref={importFileRef}
              type="file"
              accept="application/json"
              className="workbench-hidden-file-input"
              onChange={handleImportFile}
            />
            <button className="icon-btn" onClick={clearRecipe} title="Clear recipe (undo with Ctrl+Z)">
              <Eraser size={12} />
            </button>
          </span>
        </div>
      )}
      <div className="workbench-op-content">
        <div className="workbench-saved-recipes">
          <div className="workbench-saved-recipes-header">
            <span className="workbench-field-label"><FolderOpen size={12} style={{ marginRight: 4, verticalAlign: -2 }} />Saved Recipes</span>
            {recipe.length > 0 && !savingAs && (
              <span className="workbench-saved-recipe-actions">
                {loadedRecipeId && (
                  <button className="icon-btn" onClick={() => void saveInPlace()} disabled={savingInPlace} title="Save changes to the loaded recipe">
                    <Save size={12} />
                  </button>
                )}
                <button className="icon-btn" onClick={startSaveAs} title="Save as a new recipe">
                  <FolderPlus size={12} />
                </button>
              </span>
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
                    <button className="icon-btn" onClick={() => setPendingDelete(saved)} title="Delete">
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
                  className={dragClassName(step.stepId, 'workbench-recipe-step-wrap')}
                  {...dragHandlers(step.stepId)}
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
                    {stepOverrides[i] !== undefined && (
                      <span className="workbench-recipe-step-override-badge" title="This step's input is overridden for the next run">
                        input overridden
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
                      <button
                        className="icon-btn"
                        onClick={() => (overrideEditingId === String(i) ? cancelOverride() : startOverride(i, ''))}
                        title="Override this step's input for debugging"
                      >
                        <Sparkles size={12} />
                      </button>
                      <button className="icon-btn" onClick={() => void runToStep(i)} disabled={loading} title="Run recipe up to this step">
                        <SkipForward size={12} />
                      </button>
                      <button className="icon-btn" onClick={() => duplicate(i)} title="Duplicate step">
                        <Copy size={12} />
                      </button>
                      <button className="icon-btn" onClick={() => remove(i)} title="Remove">
                        <X size={12} />
                      </button>
                    </span>
                  </div>

                  {overrideEditingId === String(i) && (
                    <div className="workbench-recipe-step-edit">
                      <label className="workbench-field">
                        <span className="workbench-field-label">Override input for this step</span>
                        <textarea
                          className="input workbench-textarea mono"
                          value={overrideDraft}
                          onChange={e => setOverrideDraft(e.target.value)}
                          rows={2}
                        />
                      </label>
                      <div className="workbench-actions">
                        <button className="workbench-secondary-btn" onClick={() => saveOverride(i)}>
                          <Check size={13} /> Save Override
                        </button>
                        <button className="workbench-secondary-btn" onClick={cancelOverride}>
                          <X size={13} /> Cancel
                        </button>
                        {stepOverrides[i] !== undefined && (
                          <button className="workbench-secondary-btn" onClick={() => clearOverride(i)}>
                            <X size={13} /> Clear
                          </button>
                        )}
                      </div>
                    </div>
                  )}

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

            <label className="workbench-continue-toggle">
              <input
                type="checkbox"
                checked={continueOnError}
                onChange={e => setContinueOnError(e.target.checked)}
              />
              Continue on error
            </label>

            <div className="workbench-actions">
              <button className="workbench-run-btn" onClick={run} disabled={loading}>
                {loading ? <><RefreshCw size={13} className="spin" /> Running…</> : <><Play size={13} /> Run Recipe</>}
              </button>
            </div>

            {error && <div className="verify-error">{error}</div>}
            {hasErrors && !error && (
              <div className="workbench-note">Some steps failed and were skipped (continue-on-error was on) — see the trace below.</div>
            )}

            {steps.length > 0 && (
              <ol className="workbench-recipe-trace">
                {steps.map((s, i) => {
                  const traceClass = s.error
                    ? (continueOnError ? 'workbench-recipe-trace-error-continued' : 'workbench-recipe-trace-error')
                    : ''
                  return (
                    <li key={i} className={traceClass}>
                      <span className="workbench-recipe-step-index">{i + 1}</span>
                      <span className="workbench-field-label">{s.name ?? s.operation_id}</span>
                      {s.input !== undefined && (
                        <span className="workbench-recipe-trace-input mono">in: {s.input.length > 120 ? `${s.input.slice(0, 120)}…` : s.input}</span>
                      )}
                      {s.error ? (
                        <span className="mono">
                          {continueOnError ? 'Skipped (chain continued): ' : 'Error: '}{s.error}
                        </span>
                      ) : s.output_mime?.startsWith('image/') ? (
                        <img className="workbench-recipe-trace-image-thumb" src={`data:${s.output_mime},${s.output}`} alt="Step output" />
                      ) : (
                        <span className="mono">{s.output}</span>
                      )}
                    </li>
                  )
                })}
              </ol>
            )}

            {output !== null && (
              <div className="workbench-output-wrap">
                <div className="workbench-output-header">
                  <span className="workbench-field-label">Final Output</span>
                  <span className="workbench-output-actions">
                    <button className="icon-btn" onClick={copyOutput} title="Copy output">
                      {copied ? <Check size={12} color="var(--green)" /> : <Copy size={12} />}
                    </button>
                    <button
                      className="icon-btn"
                      onClick={() => downloadWorkbenchOutput(output, outputMime, 'recipe')}
                      title="Download output"
                    >
                      <Download size={12} />
                    </button>
                    <button className="icon-btn" onClick={() => setSendToLootOpen(true)} title="Send output to Loot">
                      <Send size={12} />
                    </button>
                  </span>
                </div>
                {outputMime?.startsWith('image/') ? (
                  <img className="workbench-output-image" src={`data:${outputMime},${output}`} alt="Recipe output" />
                ) : (
                  <pre className="verify-result-output mono">{output}</pre>
                )}
              </div>
            )}
          </>
        )}
      </div>

      <ConfirmActionModal
        isOpen={!!pendingDelete}
        title="Delete saved recipe?"
        description={`This will permanently delete "${pendingDelete?.name}". This can't be undone.`}
        confirmLabel="Delete"
        isConfirming={deletingRecipe}
        onConfirm={confirmDelete}
        onClose={() => setPendingDelete(null)}
      />

      {output !== null && (
        <SendToLootModal
          isOpen={sendToLootOpen}
          onClose={() => setSendToLootOpen(false)}
          defaultTitle="Recipe output"
          content={output}
        />
      )}
    </section>
  )
}
