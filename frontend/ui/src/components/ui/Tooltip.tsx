import { cloneElement, isValidElement, useId, type ReactElement, type ReactNode } from 'react'
import './Tooltip.css'

interface TooltipProps {
  content: ReactNode
  children: ReactElement
  placement?: 'top' | 'bottom' | 'left' | 'right'
}

export function Tooltip({ content, children, placement = 'top' }: TooltipProps) {
  const id = useId()
  const trigger = isValidElement(children)
    ? cloneElement(children, { 'aria-describedby': id } as Record<string, unknown>)
    : children

  return (
    <span className="ui-tooltip-wrap">
      {trigger}
      <span id={id} role="tooltip" className={`ui-tooltip ui-tooltip--${placement}`}>
        {content}
      </span>
    </span>
  )
}
