import { Palette, RefreshCw, Trash2, XCircle } from 'lucide-react'
import { useState } from 'react'
import { ThemePickerModal } from '../../components/ThemePickerModal'
import { THEME_OPTIONS, type ThemeId } from '../../app/themes'
import { useSettingsData } from './useSettingsData'
import {
  ChatSettingsSection,
  PageVisibilitySection,
  RuntimeConfigSection,
  ServerEnvironmentSection,
  WordlistsSection,
} from './SettingsSections'
import type { Page } from '../../app/routing'
import './SettingsPage.css'

export default function SettingsPage({
  themeId,
  setThemeId,
  reduceTextureEffects,
  setReduceTextureEffects,
  isPageEnabled,
  togglePage,
}: {
  themeId: ThemeId
  setThemeId: (theme: ThemeId) => void
  reduceTextureEffects: boolean
  setReduceTextureEffects: (value: boolean) => void
  isPageEnabled: (page: Page) => boolean
  togglePage: (page: Page) => void
}) {
  const [themeModalOpen, setThemeModalOpen] = useState(false)

  const {
    settings,
    loading,
    error,
    saving,
    wordlistsSaving,
    clearingCache,
    timeout,
    requestTimeout,
    inactivityTimeout,
    maxRuntime,
    cacheSize,
    cacheTtl,
    toolTtl,
    wordlistsDraft,
    binaryPathOverrides,
    setTimeout_,
    setRequestTimeout,
    setInactivityTimeout,
    setMaxRuntime,
    setCacheSize,
    setCacheTtl,
    setToolTtl,
    addWordlist,
    removeWordlist,
    updateWordlist,
    addBinaryOverride,
    removeBinaryOverride,
    updateBinaryOverride,
    testBinaryOverride,
    saveRuntime,
    saveWordlists,
    saveChatSettings,
    clearCache,
    withCurrentTypeOption,
    withCurrentSpeedOption,
    withCurrentCoverageOption,
    chatPersonality,
    customPrompt,
    personalityPresets,
    summarizationThreshold,
    contextInjectionChars,
    llmThink,
    setChatPersonality,
    setCustomPrompt,
    setSummarizationThreshold,
    setContextInjectionChars,
    setLlmThink,
  } = useSettingsData()

  if (loading) {
    return (
      <div className="loading-state">
        <RefreshCw size={20} className="spin" color="var(--green)" />
        <p>Loading settings…</p>
      </div>
    )
  }

  if (error) {
    return <div className="error-banner"><XCircle size={16} /> {error}</div>
  }

  if (!settings) return null

  return (
    <div className="settings-page">
      <ThemePickerModal
        isOpen={themeModalOpen}
        themeId={themeId}
        setThemeId={setThemeId}
        reduceTextureEffects={reduceTextureEffects}
        setReduceTextureEffects={setReduceTextureEffects}
        onClose={() => setThemeModalOpen(false)}
      />

      <div className="kpi-row settings-appearance-row">
        <div
          className="stat-card settings-appearance-card settings-appearance-card--action settings-appearance-card--clickable"
          role="button"
          tabIndex={0}
          onClick={() => setThemeModalOpen(true)}
          onKeyDown={e => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault()
              setThemeModalOpen(true)
            }
          }}
          title="Open theme picker"
        >
          <div className="stat-icon" style={{ color: 'var(--accent)' }}><Palette size={20} /></div>
          <div className="stat-body settings-appearance-body">
            <div className="stat-label">Appearance</div>
            <div className="stat-value settings-appearance-value">{THEME_OPTIONS.find(t => t.id === themeId)?.label ?? themeId}</div>
            <div className="stat-sub">Preview and apply a theme instantly</div>
            <div className="settings-appearance-tap-hint mono">Click card to open picker</div>
          </div>
        </div>

        <div className="stat-card settings-appearance-card settings-maintenance-card">
          <div className="stat-icon" style={{ color: 'var(--warning)' }}><Trash2 size={20} /></div>
          <div className="stat-body settings-appearance-body">
            <div className="stat-label">Maintenance</div>
            <div className="stat-value settings-appearance-value">Cache</div>
            <div className="stat-sub">Clear cached tool results and force fresh data</div>
            <div className="settings-appearance-actions">
              <button className="btn-secondary settings-appearance-btn" onClick={clearCache} disabled={clearingCache}>
                {clearingCache ? 'Clearing…' : 'Clear Cache'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <ServerEnvironmentSection settings={settings} />

      <PageVisibilitySection
        isPageEnabled={isPageEnabled}
        togglePage={togglePage}
      />

      <RuntimeConfigSection
        timeout={timeout}
        requestTimeout={requestTimeout}
        inactivityTimeout={inactivityTimeout}
        maxRuntime={maxRuntime}
        cacheSize={cacheSize}
        cacheTtl={cacheTtl}
        toolTtl={toolTtl}
        setTimeout_={setTimeout_}
        setRequestTimeout={setRequestTimeout}
        setInactivityTimeout={setInactivityTimeout}
        setMaxRuntime={setMaxRuntime}
        setCacheSize={setCacheSize}
        setCacheTtl={setCacheTtl}
        setToolTtl={setToolTtl}
        binaryPathOverrides={binaryPathOverrides}
        onAddBinaryOverride={addBinaryOverride}
        onRemoveBinaryOverride={removeBinaryOverride}
        onUpdateBinaryOverride={updateBinaryOverride}
        onTestBinaryOverride={testBinaryOverride}
        saving={saving}
        onSave={saveRuntime}
      />

      <WordlistsSection
        wordlistsDraft={wordlistsDraft}
        wordlistsSaving={wordlistsSaving}
        onAddWordlist={addWordlist}
        onSaveWordlists={saveWordlists}
        onUpdateWordlist={updateWordlist}
        onRemoveWordlist={removeWordlist}
        withCurrentTypeOption={withCurrentTypeOption}
        withCurrentSpeedOption={withCurrentSpeedOption}
        withCurrentCoverageOption={withCurrentCoverageOption}
      />

      <ChatSettingsSection
        chatPersonality={chatPersonality}
        setChatPersonality={setChatPersonality}
        customPrompt={customPrompt}
        setCustomPrompt={setCustomPrompt}
        personalityPresets={personalityPresets}
        summarizationThreshold={summarizationThreshold}
        setSummarizationThreshold={setSummarizationThreshold}
        contextInjectionChars={contextInjectionChars}
        setContextInjectionChars={setContextInjectionChars}
        llmThink={llmThink}
        setLlmThink={setLlmThink}
        saving={saving}
        onSave={saveChatSettings}
      />
    </div>
  )
}
