import type { ReactNode } from 'react'

interface BrowserPageProps {
  className?: string
  top?: ReactNode
  nav?: ReactNode
  main: ReactNode
  aside?: ReactNode
  asideExpanded?: boolean
}

export function BrowserPage({ className, top, nav, main, aside, asideExpanded }: BrowserPageProps) {
  return (
    <div className={`browser-page${className ? ` ${className}` : ''}`}>
      {top && <div className="browser-page-top">{top}</div>}
      <div className={`browser-page-row${aside && asideExpanded ? ' browser-page-row--aside-grow' : ''}`}>
        {nav}
        {main}
        {aside}
      </div>
    </div>
  )
}
