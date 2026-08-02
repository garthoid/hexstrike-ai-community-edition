import { ShieldCheck } from 'lucide-react'
import { BrowserPage } from '../../components/layout/BrowserPage'
import { RunLookupTool } from './RunLookupTool'
import { SessionIntegrityTool } from './SessionIntegrityTool'
import './VerifyPage.css'

export function VerifyPage() {
  return (
    <BrowserPage
      className="verify-page"
      top={(
        <div className="verify-page-header">
          <h1 className="verify-page-title">
            <ShieldCheck size={16} /> Verify
          </h1>
          <p className="verify-page-subtitle section-meta">
            Every tool run NyxStrike executes is hash-chained as it happens, so evidence in a
            report can be proven unmodified after the fact. Use these tools to verify that chain.
          </p>
        </div>
      )}
      main={(
        <div className="browser-main">
          <div className="browser-scroll">
            <div className="verify-tools-grid">
              <RunLookupTool />
              <SessionIntegrityTool />
            </div>
          </div>
        </div>
      )}
    />
  )
}
