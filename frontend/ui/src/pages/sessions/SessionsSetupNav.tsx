import { Layers, Pencil, Play, Trash2 } from 'lucide-react'
import type { SessionTemplate } from '../../api'
import type { StartMode } from './constants'

interface SessionsSetupNavProps {
  startModes: StartMode[]
  templates: SessionTemplate[]
  onOpenStartMode: (mode: StartMode) => void
  onUseTemplate: (templateId: string) => void
  onEditTemplate: (template: SessionTemplate) => void
  onDeleteTemplate: (template: SessionTemplate) => void
  templateActionBusyId: string | null
}

export function SessionsSetupNav({
  startModes,
  templates,
  onOpenStartMode,
  onUseTemplate,
  onEditTemplate,
  onDeleteTemplate,
  templateActionBusyId,
}: SessionsSetupNavProps) {
  return (
    <nav className="browser-nav">
      <div className="browser-nav-title">
        <Play size={14} /> Session Setup
      </div>
      {startModes.map(mode => (
        <button
          key={mode.key}
          className="browser-nav-item browser-nav-item--column"
          onClick={() => onOpenStartMode(mode)}
        >
          <span className="browser-nav-label">{mode.title}</span>
          <span className="browser-nav-desc">{mode.description}</span>
        </button>
      ))}

      {templates.length > 0 && (
        <>
          <div className="browser-nav-title">
            <Layers size={14} /> Custom Templates <span className="badge">{templates.length}</span>
          </div>
          {templates.map(template => (
            <div key={template.template_id} className="sessions-setup-template-row">
              <button
                className="browser-nav-item browser-nav-item--column sessions-setup-template-btn"
                onClick={() => onUseTemplate(template.template_id)}
                title={`${template.workflow_steps.length} tools`}
              >
                <span className="browser-nav-label">{template.name}</span>
                <span className="browser-nav-desc">{template.workflow_steps.length} tools</span>
              </button>
              <div className="sessions-setup-template-actions">
                <button onClick={() => onEditTemplate(template)} title="Edit template">
                  <Pencil size={12} />
                </button>
                <button
                  onClick={() => onDeleteTemplate(template)}
                  disabled={templateActionBusyId === template.template_id}
                  title="Delete template"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            </div>
          ))}
        </>
      )}
    </nav>
  )
}
