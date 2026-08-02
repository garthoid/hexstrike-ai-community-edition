import { XCircle } from 'lucide-react'
import './ErrorState.css'

interface ErrorStateProps {
  message: string
  onRetry?: () => void
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="ui-error-state">
      <XCircle size={15} />
      <span className="ui-error-state-message">{message}</span>
      {onRetry && (
        <button type="button" className="ui-error-state-retry press-feedback" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  )
}
