import { useEffect, useState } from 'react'
import { Terminal } from 'lucide-react'
import { IdeConfigSection, FlagsSection, AuthenticationSection, DemoModeSection, CommandPaletteSection, UIFeaturesSection } from './HelpSections'
import { HelpSectionNav, type HelpSection } from './HelpSectionNav'
import { IDE_CONFIGS } from './ideConfigs'
import { api } from '../../api'
import { BrowserPage } from '../../components/layout/BrowserPage'
import './HelpPage.css'

export default function HelpPage() {
  const [section, setSection] = useState<HelpSection>('ide')
  const [activeIde, setActiveIde] = useState('claude')
  const [installPath, setInstallPath] = useState('/path/to/nyxstrike')
  const [pathDetected, setPathDetected] = useState(false)
  const ide = IDE_CONFIGS.find(i => i.id === activeIde) ?? IDE_CONFIGS[0]

  useEffect(() => {
    let mounted = true

    api.getSettings().then(response => {
      const detectedPath = response.settings.server.working_dir?.trim()
      if (!mounted || !detectedPath) {
        return
      }
      setInstallPath(detectedPath)
      setPathDetected(true)
    }).catch(() => {
      if (mounted) {
        setPathDetected(false)
      }
    })

    return () => {
      mounted = false
    }
  }, [])

  return (
    <BrowserPage
      className="help-page"
      top={(
        <div className="help-page-header">
          <h1 className="help-page-title">
            <Terminal size={16} /> Help &amp; Documentation
          </h1>
          <p className="help-page-subtitle section-meta">
            MCP client setup, keyboard shortcuts, and dashboard features.
          </p>
        </div>
      )}
      nav={<HelpSectionNav section={section} setSection={setSection} />}
      main={(
        <div className="browser-main">
          <div className="browser-scroll">
            {section === 'ide' && (
              <IdeConfigSection
                installPath={installPath}
                setInstallPath={setInstallPath}
                pathDetected={pathDetected}
                activeIde={activeIde}
                setActiveIde={setActiveIde}
                ideConfigs={IDE_CONFIGS}
                selectedIde={ide}
              />
            )}
            {section === 'flags' && <FlagsSection />}
            {section === 'auth' && <AuthenticationSection />}
            {section === 'palette' && <CommandPaletteSection />}
            {section === 'ui' && <UIFeaturesSection />}
            {section === 'demo' && <DemoModeSection />}
          </div>
        </div>
      )}
    />
  )
}
