import type { ButtonHTMLAttributes, ReactNode } from 'react'
import './ActionButton.css'

type ActionButtonVariant =
  | 'default' | 'success' | 'warning' | 'danger' | 'running'
  | 'primary' | 'secondary' | 'ghost' | 'destructive' | 'icon'

interface ActionButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ActionButtonVariant
  children: ReactNode
}

/** The app's single Button primitive — every new/migrated button should use this instead of raw `<button>` markup. */
export function ActionButton({
  variant = 'default',
  className = '',
  children,
  ...rest
}: ActionButtonProps) {
  return (
    <button
      className={`action-button action-button--${variant} press-feedback${className ? ` ${className}` : ''}`}
      {...rest}
    >
      {children}
    </button>
  )
}

export type { ActionButtonVariant }
export { ActionButton as Button }
