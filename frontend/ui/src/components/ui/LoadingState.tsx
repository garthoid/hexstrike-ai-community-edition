import { Spinner } from './Spinner'
import './LoadingState.css'

interface LoadingStateProps {
  label?: string
  size?: 'sm' | 'md' | 'lg'
}

export function LoadingState({ label = 'Loading…', size = 'md' }: LoadingStateProps) {
  return (
    <div className="ui-loading-state">
      <Spinner size={size} />
      <p>{label}</p>
    </div>
  )
}
