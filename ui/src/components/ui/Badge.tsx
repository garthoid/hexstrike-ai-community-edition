import type { ReactNode } from 'react'
import './Badge.css'

export type BadgeTone = 'neutral' | 'success' | 'danger' | 'warning' | 'info' | 'accent'

interface BadgeProps {
  tone?: BadgeTone
  children: ReactNode
  className?: string
}

export function Badge({ tone = 'neutral', children, className = '' }: BadgeProps) {
  return (
    <span className={`ui-badge ui-badge--${tone}${className ? ` ${className}` : ''}`}>
      {children}
    </span>
  )
}
