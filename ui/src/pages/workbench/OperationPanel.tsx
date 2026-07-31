import { useState } from 'react'
import { Copy, Check, Play, RefreshCw, ListPlus } from 'lucide-react'
import { api } from '../../api'
import type { WorkbenchOperation } from '../../api'

interface OperationPanelProps {
  operation: WorkbenchOperation
  onAddToRecipe: (operation: WorkbenchOperation, params: Record<string, string>, inputValue: string) => void
}

export function OperationPanel({ operation, onAddToRecipe }: OperationPanelProps) {
  const [values, setValues] = useState<Record<string, string>>(() =>
    Object.fromEntries(operation.params.map(p => [p.name, String(p.default ?? '')]))
  )
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [output, setOutput] = useState<string | null>(null)
  const [note, setNote] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [added, setAdded] = useState(false)

  function setValue(name: string, value: string) {
    setValues(prev => ({ ...prev, [name]: value }))
  }

  async function run() {
    setLoading(true)
    setError(null)
    setOutput(null)
    setNote(null)
    try {
      const res = await api.workbenchRun(operation.id, values)
      if (!res.success) {
        setError(res.error ?? 'Operation failed.')
        return
      }
      setOutput(res.output ?? '')
      setNote(res.note ?? null)
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

  function addToRecipe() {
    const { input: rawInput, ...rest } = values
    onAddToRecipe(operation, rest, rawInput ?? '')
    setAdded(true)
    setTimeout(() => setAdded(false), 1500)
  }

  const canRun = !loading && operation.params.every(p => !p.required || values[p.name]?.trim())

  return (
    <div className="workbench-op-body">
      <div className="section-header">
        <h3>{operation.name}</h3>
      </div>
      <div className="workbench-op-content">
        <p className="verify-tool-desc">{operation.description}</p>

        <div className="workbench-form">
          {operation.params.filter(p => !p.hidden).map(p => (
            <label key={p.name} className="workbench-field">
              <span className="workbench-field-label">{p.label}{p.required ? ' *' : ''}</span>
              {p.type === 'textarea' && (
                <textarea
                  className="input workbench-textarea mono"
                  value={values[p.name] ?? ''}
                  onChange={e => setValue(p.name, e.target.value)}
                  rows={4}
                />
              )}
              {p.type === 'select' && (
                <select
                  className="input input-full"
                  value={values[p.name] ?? ''}
                  onChange={e => setValue(p.name, e.target.value)}
                >
                  {(p.choices ?? []).map(choice => (
                    <option key={choice} value={choice}>{choice}</option>
                  ))}
                </select>
              )}
              {(p.type === 'text' || p.type === 'number') && (
                <input
                  className="input input-full mono"
                  type={p.type}
                  value={values[p.name] ?? ''}
                  onChange={e => setValue(p.name, e.target.value)}
                />
              )}
            </label>
          ))}
        </div>

        <div className="workbench-actions">
          <button className="workbench-run-btn" onClick={run} disabled={!canRun}>
            {loading ? <><RefreshCw size={13} className="spin" /> Running…</> : <><Play size={13} /> Run</>}
          </button>
          <button className="workbench-secondary-btn" onClick={addToRecipe} title="Add this operation (with its current settings) to the recipe">
            {added ? <><Check size={13} color="var(--green)" /> Added</> : <><ListPlus size={13} /> Add to Recipe</>}
          </button>
        </div>

        {error && <div className="verify-error">{error}</div>}

        {output !== null && (
          <div className="workbench-output-wrap">
            <div className="workbench-output-header">
              <span className="workbench-field-label">Output</span>
              <button className="icon-btn" onClick={copyOutput} title="Copy output">
                {copied ? <Check size={12} color="var(--green)" /> : <Copy size={12} />}
              </button>
            </div>
            <pre className="verify-result-output mono">{output}</pre>
            {note && <div className="workbench-note">{note}</div>}
          </div>
        )}
      </div>
    </div>
  )
}
