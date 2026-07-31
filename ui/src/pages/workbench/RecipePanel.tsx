import { useState } from 'react'
import type { Dispatch, SetStateAction } from 'react'
import { ArrowUp, ArrowDown, X, Play, RefreshCw, Copy, Check, Workflow, Pencil } from 'lucide-react'
import { api } from '../../api'
import type { WorkbenchOperation, WorkbenchRecipeStepResult } from '../../api'

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

  function move(index: number, dir: -1 | 1) {
    setRecipe(prev => {
      const next = [...prev]
      const target = index + dir
      if (target < 0 || target >= next.length) return prev
      ;[next[index], next[target]] = [next[target], next[index]]
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

  return (
    <section className={`workbench-recipe${recipe.length > 0 ? ' section' : ''}`}>
      {recipe.length > 0 && (
        <div className="section-header">
          <h3><Workflow size={14} style={{ marginRight: 6, verticalAlign: -2 }} />Recipe</h3>
        </div>
      )}
      <div className="workbench-op-content">
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
                <li key={step.stepId} className="workbench-recipe-step-wrap">
                  <div className="workbench-recipe-step">
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
