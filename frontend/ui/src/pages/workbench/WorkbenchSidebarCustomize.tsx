import { Eye, EyeOff, GripVertical, Star } from 'lucide-react'
import type { WorkbenchOperation } from '../../api'
import { useDragReorder } from '../../hooks/useDragReorder'

interface WorkbenchSidebarCustomizeProps {
  allByCategory: [string, WorkbenchOperation[]][]
  isCategoryHidden: (category: string) => boolean
  isOperationHidden: (id: string) => boolean
  hideCategory: (category: string) => void
  showCategory: (category: string) => void
  hideOperation: (id: string) => void
  showOperation: (id: string) => void
  isFavorite: (id: string) => boolean
  toggleFavorite: (id: string) => void
  reorderCategory: (draggedId: string, targetId: string) => void
  reorderOperation: (draggedId: string, targetId: string) => void
}

export function WorkbenchSidebarCustomize({
  allByCategory,
  isCategoryHidden,
  isOperationHidden,
  hideCategory,
  showCategory,
  hideOperation,
  showOperation,
  isFavorite,
  toggleFavorite,
  reorderCategory,
  reorderOperation,
}: WorkbenchSidebarCustomizeProps) {
  const { dragHandlers: catDragHandlers, dragClassName: catDragClassName } = useDragReorder(reorderCategory)
  const { dragHandlers: opDragHandlers, dragClassName: opDragClassName } = useDragReorder(reorderOperation)

  return (
    <>
      {allByCategory.map(([category, ops]) => {
        const hidden = isCategoryHidden(category)
        const allOpsHidden = ops.length > 0 && ops.every(op => isOperationHidden(op.id))
        return (
          <div
            key={category}
            className={catDragClassName(category, `workbench-category workbench-category--customize${hidden ? ' workbench-category--hidden' : ''}`)}
            {...catDragHandlers(category)}
          >
            <div className="workbench-category-header workbench-category-header--customize">
              <span className="workbench-row-drag" title="Drag to reorder">
                <GripVertical size={12} />
              </span>
              <span className="workbench-category-label">{category.replace(/_/g, ' ')}</span>
              {!hidden && allOpsHidden && <span className="workbench-category-hint">(all tools hidden)</span>}
              <button
                type="button"
                className="workbench-row-icon-btn"
                onClick={() => hidden ? showCategory(category) : hideCategory(category)}
                title={hidden ? `Show ${category}` : `Hide ${category}`}
              >
                {hidden ? <EyeOff size={13} /> : <Eye size={13} />}
              </button>
            </div>
            {ops.map(op => {
              const opHidden = isOperationHidden(op.id)
              const favorite = isFavorite(op.id)
              return (
                <div
                  key={op.id}
                  className={opDragClassName(op.id, `workbench-op-row${opHidden ? ' workbench-op-row--hidden' : ''}`)}
                  {...opDragHandlers(op.id)}
                >
                  <span className="workbench-row-drag" title="Drag to reorder">
                    <GripVertical size={11} />
                  </span>
                  <span className="workbench-op-row-name">{op.name}</span>
                  <button
                    type="button"
                    className={`workbench-row-icon-btn${favorite ? ' workbench-star-btn--active' : ''}`}
                    onClick={() => toggleFavorite(op.id)}
                    title={favorite ? `Unstar ${op.name}` : `Star ${op.name}`}
                  >
                    <Star size={12} fill={favorite ? 'currentColor' : 'none'} />
                  </button>
                  <button
                    type="button"
                    className="workbench-row-icon-btn"
                    onClick={() => opHidden ? showOperation(op.id) : hideOperation(op.id)}
                    title={opHidden ? `Show ${op.name}` : `Hide ${op.name}`}
                  >
                    {opHidden ? <EyeOff size={12} /> : <Eye size={12} />}
                  </button>
                </div>
              )
            })}
          </div>
        )
      })}
    </>
  )
}
