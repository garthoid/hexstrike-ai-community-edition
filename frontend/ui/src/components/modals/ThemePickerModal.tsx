import { useEffect, useState } from 'react'
import { InformationModal } from './InformationModal'
import { THEME_OPTIONS, type ThemeId } from '../../app/themes'

interface ThemePickerModalProps {
  isOpen: boolean
  themeId: ThemeId
  setThemeId: (theme: ThemeId) => void
  reduceTextureEffects: boolean
  setReduceTextureEffects: (value: boolean) => void
  onClose: () => void
}

export function ThemePickerModal({
  isOpen,
  themeId,
  setThemeId,
  reduceTextureEffects,
  setReduceTextureEffects,
  onClose,
}: ThemePickerModalProps) {
  const [themePreviewId, setThemePreviewId] = useState<ThemeId>(themeId)
  const [themeSelectionId, setThemeSelectionId] = useState<ThemeId>(themeId)

  useEffect(() => {
    if (!isOpen) {
      setThemePreviewId(themeId)
      setThemeSelectionId(themeId)
      return
    }
    document.documentElement.setAttribute('data-theme', themePreviewId)
  }, [isOpen, themePreviewId, themeId])

  function handleClose() {
    document.documentElement.setAttribute('data-theme', themeId)
    setThemePreviewId(themeId)
    setThemeSelectionId(themeId)
    onClose()
  }

  function applyThemeSelection() {
    setThemeId(themeSelectionId)
    onClose()
  }

  return (
    <InformationModal
      isOpen={isOpen}
      title="Choose Theme"
      description="Preview themes live, then apply your selection."
      className="theme-picker-modal"
      primaryLabel="Apply Theme"
      primaryVariant="success"
      secondaryLabel="Cancel"
      onPrimary={applyThemeSelection}
      onSecondary={handleClose}
      onClose={handleClose}
    >
      <label className="theme-picker-toggle-row">
        <input
          type="checkbox"
          checked={reduceTextureEffects}
          onChange={e => setReduceTextureEffects(e.target.checked)}
        />
        <span className="theme-picker-toggle-text">Reduce background texture effects</span>
      </label>
      <div className="theme-picker-grid">
        {THEME_OPTIONS.map(option => (
          <button
            key={option.id}
            className={`theme-picker-card${themeSelectionId === option.id ? ' active' : ''}`}
            onClick={() => {
              setThemeSelectionId(option.id)
              setThemePreviewId(option.id)
            }}
            type="button"
          >
            <span className="theme-picker-card-label">
              {option.label}
              {option.light && <span className="theme-picker-card-badge">Light</span>}
            </span>
            <span className="theme-picker-card-hint">{option.hint}</span>
          </button>
        ))}
      </div>
    </InformationModal>
  )
}
