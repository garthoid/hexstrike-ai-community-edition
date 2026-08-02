import { AlertTriangle } from 'lucide-react'
import { ActionButton, type ActionButtonVariant } from '../ui/ActionButton'
import { Sheet } from './Sheet'
import './ConfirmActionModal.css'

interface ConfirmActionModalProps {
  isOpen: boolean
  title: string
  description: string
  impactItems?: string[]
  confirmLabel?: string
  cancelLabel?: string
  confirmVariant?: ActionButtonVariant
  isConfirming?: boolean
  onConfirm: () => void | Promise<void>
  onClose: () => void
}

export function ConfirmActionModal({
  isOpen,
  title,
  description,
  impactItems = [],
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  confirmVariant = 'danger',
  isConfirming = false,
  onConfirm,
  onClose,
}: ConfirmActionModalProps) {
  return (
    <Sheet
      isOpen={isOpen}
      onClose={onClose}
      variant="centered"
      disableClose={isConfirming}
      className="confirm-action-modal"
      ariaLabel={title}
      title={
        <>
          <span className="modal-icon modal-icon--danger" aria-hidden="true">
            <AlertTriangle size={14} />
          </span>
          <span className="modal-name">{title}</span>
        </>
      }
    >
      <p className="modal-desc">{description}</p>

      {impactItems.length > 0 && (
        <div className="confirm-action-impact">
          {impactItems.map(item => (
            <div key={item} className="confirm-action-impact-item">{item}</div>
          ))}
        </div>
      )}

      <div className="confirm-action-buttons">
        <ActionButton variant="default" onClick={onClose} disabled={isConfirming}>
          {cancelLabel}
        </ActionButton>
        <ActionButton
          variant={confirmVariant}
          onClick={() => { void onConfirm() }}
          disabled={isConfirming}
        >
          {isConfirming ? 'Working…' : confirmLabel}
        </ActionButton>
      </div>
    </Sheet>
  )
}
