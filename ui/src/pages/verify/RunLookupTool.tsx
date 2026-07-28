import { useState } from 'react'
import { Search, RefreshCw } from 'lucide-react'
import { api } from '../../api'
import type { RunLookupResponse } from '../../api'

function fmtTs(ts: string | undefined): string {
  if (!ts) return '—'
  const d = new Date(ts)
  return isNaN(d.getTime()) ? ts : d.toLocaleString()
}

export function RunLookupTool() {
  const [hash, setHash] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<RunLookupResponse | null>(null)

  async function runLookup() {
    const query = hash.trim()
    if (!query) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await api.lookupRun(query)
      if (!res.success) {
        setError(res.error ?? 'Lookup failed.')
        return
      }
      setResult(res)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') void runLookup()
  }

  return (
    <section className="section">
      <div className="section-header">
        <h3>Run Lookup</h3>
      </div>
      <div className="verify-tool-body">
        <p className="verify-tool-desc">
          Paste an evidence-chain hash from a report to find exactly which run produced it —
          works for runs inside a session and one-off runs made outside any session.
        </p>

        <div className="verify-tool-row">
          <input
            className="verify-input mono"
            placeholder="64-character hash, e.g. from a session's Evidence Integrity section"
            value={hash}
            onChange={e => setHash(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button className="verify-submit-btn" onClick={runLookup} disabled={loading || !hash.trim()}>
            {loading ? <><RefreshCw size={12} className="spin" /> Looking up…</> : <><Search size={12} /> Look Up</>}
          </button>
        </div>

        {error && <div className="verify-error">{error}</div>}

        {result && !result.found && (
          <div className="verify-empty">No run found for that hash.</div>
        )}

        {result && result.found && (
          <>
            <table className="verify-result-table">
              <tbody>
                <tr>
                  <td>Session</td>
                  <td className="mono">
                    {result.session_id
                      ? <a className="verify-session-link" href={`#/sessions/${result.session_id}`}>{result.session_id}</a>
                      : 'none — ad-hoc run (no session)'}
                  </td>
                </tr>
                <tr><td>Tool</td><td className="mono">{result.tool}</td></tr>
                <tr><td>Endpoint</td><td className="mono">{result.endpoint}</td></tr>
                <tr><td>Timestamp</td><td>{fmtTs(result.timestamp)}</td></tr>
                <tr><td>Return Code</td><td className="mono">{result.return_code}</td></tr>
                <tr><td>Prev Hash</td><td className="mono" style={{ wordBreak: 'break-all' }}>{result.prev_hash}</td></tr>
              </tbody>
            </table>
            {(result.stdout || result.stderr) && (
              <pre className="verify-result-output">
                {result.stdout}
                {result.stderr ? `\n--- stderr ---\n${result.stderr}` : ''}
              </pre>
            )}
          </>
        )}
      </div>
    </section>
  )
}
