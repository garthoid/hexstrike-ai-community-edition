import { RefreshCw, Target } from 'lucide-react'
import { useEffect, useMemo, useRef } from 'react'
import type { AttackChainStep } from '../../api'
import type { StartMode } from './constants'
import { Sheet } from '../../components/modals/Sheet'

export function StartSessionModal({
  startMode,
  templates,
  selectedTemplateId,
  setSelectedTemplateId,
  intelligencePrecision,
  setIntelligencePrecision,
  modalTarget,
  setModalTarget,
  modalNote,
  setModalNote,
  modalError,
  creatingSession,
  submitLabel,
  onClose,
  onSubmit,
}: {
  startMode: StartMode
  templates: Array<{ template_id: string; name: string; workflow_steps?: AttackChainStep[] }>
  selectedTemplateId: string
  setSelectedTemplateId: (value: string) => void
  intelligencePrecision: 'quick' | 'comprehensive' | 'stealth'
  setIntelligencePrecision: (value: 'quick' | 'comprehensive' | 'stealth') => void
  modalTarget: string
  setModalTarget: (value: string) => void
  modalNote: string
  setModalNote: (value: string) => void
  modalError: string | null
  creatingSession: boolean
  submitLabel?: string
  onClose: () => void
  onSubmit: () => void
}) {
  const templateSelectRef = useRef<HTMLSelectElement | null>(null)
  const targetInputRef = useRef<HTMLInputElement | null>(null)
  const selectedTemplate = useMemo(
    () => templates.find(template => template.template_id === selectedTemplateId),
    [templates, selectedTemplateId]
  )
  const modalTools = useMemo(() => {
    if (startMode.key !== 'from_template') return startMode.tools
    if (!selectedTemplate) return startMode.tools
    const steps = Array.isArray(selectedTemplate.workflow_steps) ? selectedTemplate.workflow_steps : []
    const uniqueTools: string[] = []
    for (const step of steps) {
      const toolName = step?.tool
      if (!toolName || uniqueTools.includes(toolName)) continue
      uniqueTools.push(toolName)
    }
    return uniqueTools
  }, [startMode, selectedTemplate])

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      if (startMode.key === 'from_template') {
        templateSelectRef.current?.focus()
        return
      }
      targetInputRef.current?.focus()
    })
    return () => window.cancelAnimationFrame(frame)
  }, [startMode.key])

  return (
    <Sheet
      isOpen
      onClose={onClose}
      title={<span className="modal-name">Start {startMode.title}</span>}
    >
      <p className="modal-desc">{startMode.modalDescription}</p>
      <div className="modal-section">
        <span className="modal-label">Typical Tooling</span>
        <div className="modal-params">
          {modalTools.length === 0 && <span className="modal-param mono">none preloaded</span>}
          {modalTools.map(tool => (
            <span key={tool} className="modal-param mono">{tool}</span>
          ))}
        </div>
      </div>
      {startMode.key === 'from_template' && (
        <div className="session-start-form">
          <label className="mono">Template *</label>
          <select
            ref={templateSelectRef}
            name="session-template"
            className="session-objective-select"
            value={selectedTemplateId}
            onChange={e => setSelectedTemplateId(e.target.value)}
          >
            <option value="">Select template</option>
            {templates.map(template => (
              <option key={template.template_id} value={template.template_id}>{template.name}</option>
            ))}
          </select>
        </div>
      )}
      {startMode.key === 'intelligence' && (
        <div className="session-start-form">
          <label className="mono">Precision</label>
          <select
            name="session-intelligence-precision"
            className="session-objective-select"
            value={intelligencePrecision}
            onChange={e => setIntelligencePrecision(e.target.value as 'quick' | 'comprehensive' | 'stealth')}
          >
            <option value="quick">Quick (fewest tools)</option>
            <option value="comprehensive">Comprehensive (safer coverage)</option>
            <option value="stealth">Stealth (low-noise)</option>
          </select>
        </div>
      )}
      <div className="session-start-form">
        <label className="mono" htmlFor="session-target-input">Target *</label>
        <input
          id="session-target-input"
          ref={targetInputRef}
          className="search-input mono"
          value={modalTarget}
          onChange={e => setModalTarget(e.target.value)}
          placeholder={startMode.placeholder}
        />
        <label className="mono" htmlFor="session-note-input">Note (optional)</label>
        <textarea
          id="session-note-input"
          className="session-step-params mono"
          rows={3}
          value={modalNote}
          onChange={e => setModalNote(e.target.value)}
          placeholder="Context for this run"
        />
        {modalError && <div className="run-error">{modalError}</div>}
        <div className="session-start-actions">
          <button className="session-action-btn" onClick={onClose}>Cancel</button>
          <button
            className="session-run-btn"
            onClick={onSubmit}
            disabled={creatingSession}
          >
            {creatingSession ? <RefreshCw size={13} className="spin" /> : <Target size={13} />}
            {creatingSession ? 'Starting…' : (submitLabel || 'Start Session')}
          </button>
        </div>
      </div>
    </Sheet>
  )
}
