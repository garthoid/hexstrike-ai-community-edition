import { useRef, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { XCircle } from 'lucide-react'
import { useEscapeClose } from '../../hooks/useEscapeClose'
import { useFocusTrap } from '../../hooks/useFocusTrap'

interface SheetProps {
  isOpen: boolean
  title: ReactNode
  onClose: () => void
  footer?: ReactNode
  children: ReactNode
  size?: 'sm' | 'md' | 'lg'
  disableClose?: boolean
  className?: string
}

export function Sheet({
  isOpen,
  title,
  onClose,
  footer,
  children,
  size = 'md',
  disableClose = false,
  className = '',
}: SheetProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const isClosable = !disableClose

  useEscapeClose(isOpen && isClosable, onClose)
  useFocusTrap(containerRef, isOpen)

  if (!isOpen) return null

  return createPortal(
    <div
      className="sheet-backdrop"
      onClick={e => { if (e.target === e.currentTarget && isClosable) onClose() }}
    >
      <div
        ref={containerRef}
        className={`sheet sheet--${size}${className ? ` ${className}` : ''}`}
        role="dialog"
        aria-modal="true"
      >
        <div className="sheet-header">
          <div className="sheet-title-row">{title}</div>
          <button className="sheet-close" onClick={onClose} disabled={!isClosable} aria-label="Close">
            <XCircle size={18} />
          </button>
        </div>

        <div className="sheet-body">{children}</div>

        {footer && <div className="sheet-footer">{footer}</div>}
      </div>
    </div>,
    document.body
  )
}
