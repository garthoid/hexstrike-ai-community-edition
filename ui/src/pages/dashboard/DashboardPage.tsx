import { useState } from 'react'
import { XCircle, Settings2, Plus } from 'lucide-react'
import { type WebDashboardResponse, type Tool } from '../../api'
import type { RunHistoryEntry } from '../../shared/types'
import { ActionButton } from '../../components/ui/ActionButton'
import { InformationModal } from '../../components/modals/InformationModal'
import { useDragReorder } from '../../hooks/useDragReorder'
import { useWidgetLayout } from '../../hooks/useWidgetLayout'
import type { DashboardWidgetContext } from '../../app/widgetRegistry'
import { WidgetFrame } from './WidgetFrame'
import './DashboardPage.css'

// ─── Dashboard Page ───────────────────────────────────────────────────────────

interface DashboardPageProps {
  health: WebDashboardResponse
  tools: Tool[]
  runHistory: RunHistoryEntry[]
  loading: boolean
  error: string | null
  toolCategories: Record<string, string[]>
  demo?: boolean
  demoCpuHistory?: unknown
}

export function DashboardPage({ health, tools, runHistory, loading, error, toolCategories, demo, demoCpuHistory }: DashboardPageProps) {
  const [isCustomizing, setIsCustomizing] = useState(false)
  const [isAddOpen, setIsAddOpen] = useState(false)
  const { enabledWidgets, availableWidgets, addWidget, removeWidget, reorderWidget } = useWidgetLayout()
  const { dragHandlers, dragClassName } = useDragReorder(reorderWidget)

  const ctx: DashboardWidgetContext = { health, tools, runHistory, toolCategories, demo, demoCpuHistory }

  return (
    <>
      {loading && !health && (
        <div className="loading-state">
          <div className="spin spin--sm spin--green" />
          <p>Connecting to server…</p>
        </div>
      )}

      {error && !health && (
        <div className="error-banner">
          <XCircle size={16} /> {error} — is the server running on port 8888?
        </div>
      )}

      <div className="dashboard-toolbar">
        <ActionButton variant={isCustomizing ? 'success' : 'default'} onClick={() => setIsCustomizing(prev => !prev)}>
          <Settings2 size={14} /> {isCustomizing ? 'Done' : 'Customize'}
        </ActionButton>
        {isCustomizing && (
          <ActionButton variant="default" onClick={() => setIsAddOpen(true)}>
            <Plus size={14} /> Add Widget
          </ActionButton>
        )}
      </div>

      {enabledWidgets.length === 0 && (
        <div className="dashboard-empty-state">
          <p>No widgets on your dashboard.</p>
          <ActionButton variant="success" onClick={() => setIsAddOpen(true)}>
            <Plus size={14} /> Add Widget
          </ActionButton>
        </div>
      )}

      {enabledWidgets.map(widget => (
        <WidgetFrame
          key={widget.id}
          id={widget.id}
          label={widget.label}
          isCustomizing={isCustomizing}
          dragHandlers={dragHandlers}
          dragClassName={dragClassName}
          onRemove={removeWidget}
        >
          {widget.render(ctx)}
        </WidgetFrame>
      ))}

      <InformationModal isOpen={isAddOpen} title="Add Widget" onClose={() => setIsAddOpen(false)}>
        {availableWidgets.length === 0 ? (
          <p className="modal-desc">All available widgets are already on your dashboard.</p>
        ) : (
          <div className="dashboard-add-widget-list">
            {availableWidgets.map(w => {
              const Icon = w.icon
              return (
                <button
                  key={w.id}
                  type="button"
                  className="dashboard-add-widget-item"
                  onClick={() => { addWidget(w.id); setIsAddOpen(false) }}
                >
                  <span className="dashboard-add-widget-icon"><Icon size={16} /></span>
                  <span className="dashboard-add-widget-text">
                    <span className="dashboard-add-widget-label">{w.label}</span>
                    <span className="dashboard-add-widget-desc">{w.description}</span>
                  </span>
                  <Plus size={14} />
                </button>
              )
            })}
          </div>
        )}
      </InformationModal>
    </>
  )
}
