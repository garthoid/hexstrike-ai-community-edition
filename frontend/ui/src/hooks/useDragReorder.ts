import { useState } from 'react'
import type { DragEvent } from 'react'

interface UseDragReorderResult {
  dragHandlers: (id: string) => {
    draggable: true
    onDragStart: () => void
    onDragOver: (e: DragEvent) => void
    onDrop: (e: DragEvent) => void
    onDragEnd: () => void
  }
  dragClassName: (id: string, baseClassName?: string) => string
  draggingId: string | null
}

export function useDragReorder(onReorder: (draggedId: string, targetId: string) => void): UseDragReorderResult {
  const [dragId, setDragId] = useState<string | null>(null)
  const [dragOverId, setDragOverId] = useState<string | null>(null)

  function dragHandlers(id: string) {
    return {
      draggable: true as const,
      onDragStart: () => setDragId(id),
      onDragEnd: () => {
        setDragId(null)
        setDragOverId(null)
      },
      onDragOver: (e: DragEvent) => {
        e.preventDefault()
        setDragOverId(id)
      },
      onDrop: (e: DragEvent) => {
        e.preventDefault()
        if (dragId && dragId !== id) onReorder(dragId, id)
        setDragId(null)
        setDragOverId(null)
      },
    }
  }

  function dragClassName(id: string, baseClassName = ''): string {
    return [
      baseClassName,
      'drag-reorder-item',
      dragId === id ? 'drag-reorder-item--dragging' : '',
      dragOverId === id && dragId !== id ? 'drag-reorder-item--drag-over' : '',
    ].filter(Boolean).join(' ')
  }

  return { dragHandlers, dragClassName, draggingId: dragId }
}
