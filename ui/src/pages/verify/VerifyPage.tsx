import { ShieldCheck } from 'lucide-react'
import { RunLookupTool } from './RunLookupTool'
import { SessionIntegrityTool } from './SessionIntegrityTool'
import './VerifyPage.css'

export function VerifyPage() {
  return (
    <div className="page-content">
      <p className="verify-intro">
        <ShieldCheck size={13} style={{ verticalAlign: 'middle', marginRight: 6 }} />
        Every tool run NyxStrike executes is hash-chained as it happens, so evidence in a
        report can be proven unmodified after the fact. Use these tools to verify that chain.
      </p>

      <RunLookupTool />
      <SessionIntegrityTool />
    </div>
  )
}
