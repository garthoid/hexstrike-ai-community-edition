import { useState } from 'react'
import { Check, Copy } from 'lucide-react'
import { InformationModal } from './InformationModal'

interface UpdateModalProps {
  isOpen: boolean
  latestVersion?: string
  onClose: () => void
}

export function UpdateModal({ isOpen, latestVersion, onClose }: UpdateModalProps) {
  const [copied, setCopied] = useState(false)

  function copyUpdateCommand() {
    navigator.clipboard.writeText('git pull').then(() => {
      setCopied(true)
      window.setTimeout(() => setCopied(false), 2000)
    }).catch(() => {})
  }

  return (
    <InformationModal
      isOpen={isOpen}
      title="Update Available"
      description={latestVersion
        ? `A newer release (${latestVersion}) is available.`
        : 'A newer release is available.'}
      primaryLabel="Open GitHub"
      secondaryLabel="Close"
      onPrimary={() => {
        window.open('https://github.com/CommonHuman-Lab/nyxstrike', '_blank', 'noopener,noreferrer')
      }}
      onSecondary={onClose}
      onClose={onClose}
    >
      <div className="modal-section">
        <span className="modal-label">Update command</span>
        <div className="modal-code-wrap">
          <div className="modal-code mono">git pull</div>
          <button
            className="modal-copy-btn"
            onClick={copyUpdateCommand}
            title="Copy update command"
          >
            {copied ? <Check size={13} /> : <Copy size={13} />}
            {copied ? 'Copied!' : 'Copy'}
          </button>
        </div>
      </div>
      <p className="modal-desc">Run <span className="mono">git pull</span> in your project folder, then restart NyxStrike.</p>
    </InformationModal>
  )
}
