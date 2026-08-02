import { type ReactNode } from 'react'
import { Info } from 'lucide-react'
import { ActionButton, type ActionButtonVariant } from '../ui/ActionButton'
import { Sheet } from './Sheet'
import './InformationModal.css'

interface InformationModalProps {
  isOpen: boolean
  title: string
  description?: string
  children?: ReactNode
  primaryLabel?: string
  secondaryLabel?: string
  primaryVariant?: ActionButtonVariant
  isPrimaryBusy?: boolean
  disableClose?: boolean
  className?: string
  onPrimary?: () => void | Promise<void>
  onSecondary?: () => void
  onClose: () => void
}

export function InformationModal({
  isOpen,
  title,
  description,
  children,
  primaryLabel = 'Continue',
  secondaryLabel = 'Cancel',
  primaryVariant = 'default',
  isPrimaryBusy = false,
  disableClose = false,
  className = '',
  onPrimary,
  onSecondary,
  onClose,
}: InformationModalProps) {
  return (
    <Sheet
      isOpen={isOpen}
      onClose={onClose}
      variant="centered"
      disableClose={disableClose || isPrimaryBusy}
      className={`information-modal${className ? ` ${className}` : ''}`}
      ariaLabel={title}
      title={
        <>
          <span className="modal-icon modal-icon--accent" aria-hidden="true">
            <Info size={14} />
          </span>
          <span className="modal-name">{title}</span>
        </>
      }
    >
      {description && <p className="modal-desc">{description}</p>}
      {children}

      {(onPrimary || onSecondary) && (
        <div className="information-modal-buttons">
          {onSecondary && (
            <ActionButton variant="default" onClick={onSecondary} disabled={isPrimaryBusy}>
              {secondaryLabel}
            </ActionButton>
          )}
          {onPrimary && (
            <ActionButton variant={primaryVariant} onClick={() => { void onPrimary() }} disabled={isPrimaryBusy}>
              {isPrimaryBusy ? 'Working…' : primaryLabel}
            </ActionButton>
          )}
        </div>
      )}
    </Sheet>
  )
}
