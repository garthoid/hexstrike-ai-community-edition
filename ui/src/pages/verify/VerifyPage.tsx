import { ShieldCheck } from 'lucide-react'
import { RunLookupTool } from './RunLookupTool'
import { SessionIntegrityTool } from './SessionIntegrityTool'
import './VerifyPage.css'

export function VerifyPage() {
  return (
    <div className="page-content">
      <div className="verify-page-header">
        <h1 className="verify-page-title">
          <ShieldCheck size={16} /> Verify
        </h1>
        <p className="verify-page-subtitle section-meta">
          Every tool run NyxStrike executes is hash-chained as it happens, so evidence in a
          report can be proven unmodified after the fact. Use these tools to verify that chain.
        </p>
      </div>

      <div className="verify-tools-grid">
        <RunLookupTool />
        <SessionIntegrityTool />
      </div>
    </div>
  )
}
