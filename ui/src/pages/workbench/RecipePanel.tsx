import { useState } from 'react'
import type { Dispatch, SetStateAction } from 'react'
import { ArrowUp, ArrowDown, X, Play, RefreshCw, Copy, Check, Workflow } from 'lucide-react'
import { api } from '../../api'
import type { WorkbenchRecipeStepResult } from '../../api'

export interface RecipeStep {
  stepId: string
  operationId: string
  operationName: string
  params: Record<string, string>
}

interface RecipePanelProps {
  recipe: RecipeStep[]
  setRecipe: Dispatch<SetStateAction<RecipeStep[]>>
}

export function RecipePanel({ recipe, setRecipe }: RecipePanelProps) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [output, setOutput] = useState<string | null>(null)
  const [steps, setSteps] = useState<WorkbenchRecipeStepResult[]>([])
  const [copied, setCopied] = useState(false)

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
    <section className="section workbench-recipe">
      <div className="section-header">
        <h3><Workflow size={14} style={{ marginRight: 6, verticalAlign: -2 }} />Recipe</h3>
      </div>
      <div className="workbench-op-content">
        {recipe.length === 0 ? (
          <div className="workbench-empty">
            Use "Add to Recipe" on any operation to chain it here — each step's output feeds the next step's input.
          </div>
        ) : (
          <ol className="workbench-recipe-steps">
            {recipe.map((step, i) => (
              <li key={step.stepId} className="workbench-recipe-step">
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
                  <button className="icon-btn" onClick={() => remove(i)} title="Remove">
                    <X size={12} />
                  </button>
                </span>
              </li>
            ))}
          </ol>
        )}

        {recipe.length > 0 && (
          <>
            <label className="workbench-field">
              <span className="workbench-field-label">Input</span>
              <textarea
                className="verify-input mono workbench-textarea"
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
