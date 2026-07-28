import { useState } from 'react'
import { ShieldCheck, ShieldAlert, ShieldQuestion, RefreshCw } from 'lucide-react'
import { api } from '../../api'
import type { SessionIntegrityResponse } from '../../api'

export function SessionIntegrityTool() {
  const [sessionId, setSessionId] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<SessionIntegrityResponse | null>(null)

  async function verify() {
    const id = sessionId.trim()
    if (!id) return
    setLoading(true)
    setResult(null)
    try {
      const res = await api.verifySessionIntegrity(id)
      setResult(res)
    } catch (e) {
      setResult({ success: false, error: String(e) })
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') void verify()
  }

  return (
    <section className="section">
      <div className="section-header">
        <h3>Session Integrity Check</h3>
      </div>
      <div className="verify-tool-body">
        <p className="verify-tool-desc">
          Check any session's evidence chain by ID — confirms none of its recorded tool runs
          were edited after the fact. The same check is also available inline from a session's
          report modal.
        </p>

        <div className="verify-tool-row">
          <input
            className="verify-input mono"
            placeholder="session id, e.g. sess_a1b2c3d4e5"
            value={sessionId}
            onChange={e => setSessionId(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button className="verify-submit-btn" onClick={verify} disabled={loading || !sessionId.trim()}>
            {loading ? <><RefreshCw size={12} className="spin" /> Verifying…</> : <><ShieldCheck size={12} /> Verify</>}
          </button>
        </div>

        {result && (
          <div className={
            !result.success ? 'verify-error'
              : result.total_runs === 0 ? 'verify-badge verify-badge--neutral'
              : result.valid ? 'verify-badge verify-badge--ok'
              : 'verify-badge verify-badge--bad'
          }>
            {!result.success
              ? (result.error ?? 'Session not found.')
              : result.total_runs === 0
                ? <><ShieldQuestion size={12} /> No run history to verify for this session.</>
                : result.valid
                  ? <><ShieldCheck size={12} /> {result.verified_runs}/{result.total_runs} runs verified — evidence chain intact.</>
                  : <><ShieldAlert size={12} /> Tamper detected at run #{result.broken_at_index} ({result.verified_runs}/{result.total_runs} verified before the break).</>
            }
          </div>
        )}
      </div>
    </section>
  )
}
