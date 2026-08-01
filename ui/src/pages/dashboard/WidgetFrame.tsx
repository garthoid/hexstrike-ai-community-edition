import type { DragEvent, ReactNode } from 'react'
import { GripVertical, X } from 'lucide-react'

interface WidgetFrameProps {
  id: string
  label: string
  isCustomizing: boolean
  dragHandlers: (id: string) => {
    draggable: true
    onDragStart: () => void
    onDragOver: (e: DragEvent) => void
    onDrop: (e: DragEvent) => void
    onDragEnd: () => void
  }
  dragClassName: (id: string, baseClassName?: string) => string
  onRemove: (id: string) => void
  children: ReactNode
}

export function WidgetFrame({ id, label, isCustomizing, dragHandlers, dragClassName, onRemove, children }: WidgetFrameProps) {
  if (!isCustomizing) return <>{children}</>

  return (
    <div className={dragClassName(id, 'dashboard-widget-frame')} {...dragHandlers(id)}>
      <div className="dashboard-widget-toolbar">
        <span className="dashboard-widget-grip" title="Drag to reorder">
          <GripVertical size={14} />
        </span>
        <span className="dashboard-widget-frame-label">{label}</span>
        <button
          type="button"
          className="icon-btn dashboard-widget-remove"
          onClick={() => onRemove(id)}
          title={`Remove ${label}`}
        >
          <X size={14} />
        </button>
      </div>
      <div className="dashboard-widget-frame-body">{children}</div>
    </div>
  )
}
