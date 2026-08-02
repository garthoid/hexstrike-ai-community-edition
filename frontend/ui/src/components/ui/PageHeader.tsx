import type { ReactNode } from 'react'
import './PageHeader.css'

interface PageHeaderProps {
  title: ReactNode
  description?: ReactNode
  actions?: ReactNode
  breadcrumb?: ReactNode
}

export function PageHeader({ title, description, actions, breadcrumb }: PageHeaderProps) {
  return (
    <div className="ui-page-header">
      {breadcrumb && <div className="ui-page-header-breadcrumb">{breadcrumb}</div>}
      <div className="ui-page-header-row">
        <div className="ui-page-header-titles">
          <h1 className="ui-page-header-title">{title}</h1>
          {description && <p className="ui-page-header-description">{description}</p>}
        </div>
        {actions && <div className="ui-page-header-actions">{actions}</div>}
      </div>
    </div>
  )
}
