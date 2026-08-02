import { useState } from 'react'
import { Copy, Check } from 'lucide-react'

export function CopyHash({ value }: { value: string | null | undefined }) {
  const [copied, setCopied] = useState(false)

  if (!value) return null

  function copy() {
    navigator.clipboard?.writeText(value!).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }).catch(() => {})
  }

  return (
    <span className="verify-hash-value mono" style={{ wordBreak: 'break-all' }}>
      {value}
      <button className="icon-btn verify-copy-btn" onClick={copy} title="Copy hash">
        {copied ? <Check size={12} color="var(--green)" /> : <Copy size={12} />}
      </button>
    </span>
  )
}
