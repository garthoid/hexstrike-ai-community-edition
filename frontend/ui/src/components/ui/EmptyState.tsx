import type { ReactNode } from 'react'
import './EmptyState.css'

interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description?: string
  action?: ReactNode
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="ui-empty-state">
      {icon && <div className="ui-empty-state-icon">{icon}</div>}
      <div className="ui-empty-state-title">{title}</div>
      {description && <div className="ui-empty-state-description">{description}</div>}
      {action && <div className="ui-empty-state-action">{action}</div>}
    </div>
  )
}
