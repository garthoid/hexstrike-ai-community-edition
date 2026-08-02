import { Sheet } from '../../components/modals/Sheet'

interface TemplateModalProps {
  show: boolean
  templateName: string
  templateError: string | null
  setTemplateName: (value: string) => void
  onClose: () => void
  onSave: () => void
}

export function TemplateModal({
  show,
  templateName,
  templateError,
  setTemplateName,
  onClose,
  onSave,
}: TemplateModalProps) {
  return (
    <Sheet
      isOpen={show}
      onClose={onClose}
      title={<span className="modal-name">Create Template</span>}
    >
      <div className="session-start-form">
        <label className="mono">Template Name *</label>
        <input
          className="search-input mono"
          name="template-name"
          placeholder="e.g. SMB Enumeration Pack"
          value={templateName}
          onChange={e => setTemplateName(e.target.value)}
        />
        {templateError && <div className="run-error">{templateError}</div>}
        <div className="session-start-actions">
          <button className="session-action-btn" onClick={onClose}>Cancel</button>
          <button className="session-run-btn" onClick={onSave}>Save Template</button>
        </div>
      </div>
    </Sheet>
  )
}
