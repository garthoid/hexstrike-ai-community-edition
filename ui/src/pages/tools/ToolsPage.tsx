import { useEffect, useState } from 'react'
import { Wrench, Database, Shield, XCircle } from 'lucide-react'
import { api, type Tool, type WebDashboardResponse } from '../../api'
import { KpiStrip } from '../../components/KpiStrip'
import { ToolModal } from '../../components/ToolModal'
import { useToast } from '../../components/ToastProvider'
import { filterToolsByOptions, getToolCategories } from '../../shared/toolUtils'
import { ToolsCategoryNav } from './ToolsCategoryNav'
import { ToolsRegistrySection } from './ToolsRegistrySection'
import './ToolsPage.css'

interface ToolsPageProps {
  health: WebDashboardResponse
  tools: Tool[]
  toolsStatus: Record<string, boolean>
}

export default function ToolsPage({ health, tools, toolsStatus }: ToolsPageProps) {
  const { pushToast } = useToast()
  const [search, setSearch] = useState('')
  const [activeCat, setActiveCat] = useState<string>('all')
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null)
  const [missingOnly, setMissingOnly] = useState(false)
  const [refreshingAvailability, setRefreshingAvailability] = useState(false)
  const [localToolsStatus, setLocalToolsStatus] = useState<Record<string, boolean>>(toolsStatus)
  const [localTotals, setLocalTotals] = useState({
    available: health.total_tools_available,
    total: health.total_tools_count,
  })

  const effectiveToolsStatus = localToolsStatus

  useEffect(() => {
    if (refreshingAvailability) return
    setLocalToolsStatus(toolsStatus)
    setLocalTotals({
      available: health.total_tools_available,
      total: health.total_tools_count,
    })
  }, [toolsStatus, health.total_tools_available, health.total_tools_count, refreshingAvailability])

  const cats = getToolCategories(tools)
  const searchFiltered = filterToolsByOptions(tools, {
    toolsStatus: effectiveToolsStatus,
    activeCategory: 'all',
    search,
    missingOnly,
    includeParentToolSearch: true,
  })
  const filtered = activeCat === 'all'
    ? searchFiltered
    : searchFiltered.filter(tool => tool.category === activeCat)
  const categoryCounts: Record<string, number> = {}
  for (const tool of searchFiltered) {
    categoryCounts[tool.category] = (categoryCounts[tool.category] ?? 0) + 1
  }

  const missingCount = localTotals.total - localTotals.available

  async function refreshAvailabilityNow() {
    setRefreshingAvailability(true)
    try {
      const response = await api.refreshToolAvailability()
      if (!response.success) {
        pushToast('error', response.error || 'Failed to refresh availability')
        return
      }
      setLocalToolsStatus(response.tools_status)
      setLocalTotals({
        available: response.total_tools_available,
        total: response.total_tools_count,
      })
      pushToast('success', 'Tool availability refreshed')
    } catch (e) {
      pushToast('error', `Refresh failed: ${String(e)}`)
    } finally {
      setRefreshingAvailability(false)
    }
  }

  return (
    <div className="tools-page browser-page">
      {selectedTool && (
        <ToolModal
          tool={selectedTool}
          onClose={() => setSelectedTool(null)}
          installed={effectiveToolsStatus[selectedTool.name]}
        />
      )}

      <div className="browser-page-top">
        <KpiStrip
          items={[
            { icon: <Wrench size={16} />, label: 'Total Server Tools', value: tools.length, accent: 'var(--blue)' },
            {
              icon: <Shield size={16} />,
              label: `Kali Tools Installed · ${((localTotals.available / Math.max(localTotals.total, 1)) * 100).toFixed(0)}% coverage`,
              value: `${localTotals.available} / ${localTotals.total}`,
              accent: 'var(--green)',
            },
            {
              icon: <XCircle size={16} />,
              label: 'Missing / not installed',
              value: missingCount,
              accent: missingCount > 0 ? 'var(--amber)' : 'var(--text-dim)',
            },
            { icon: <Database size={16} />, label: 'Tool Categories', value: cats.length - 1, accent: 'var(--purple)' },
          ]}
        />
      </div>

      <div className="browser-page-row">
        <ToolsCategoryNav
          categories={cats}
          activeCat={activeCat}
          setActiveCat={setActiveCat}
          counts={categoryCounts}
          totalCount={searchFiltered.length}
        />

        <ToolsRegistrySection
          tools={tools}
          filtered={filtered}
          activeCat={activeCat}
          search={search}
          setSearch={setSearch}
          missingOnly={missingOnly}
          setMissingOnly={setMissingOnly}
          missingCount={missingCount}
          toolsStatus={effectiveToolsStatus}
          onSelectTool={setSelectedTool}
          onRefreshAvailability={refreshAvailabilityNow}
          refreshingAvailability={refreshingAvailability}
        />
      </div>
    </div>
  )
}
