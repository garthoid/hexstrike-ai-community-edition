import React, { useEffect, useRef, useState } from 'react'
import { api, type Tool } from '../../api'
import type { RunHistoryEntry } from '../../shared/types'
import { RunResultModal } from '../../components/RunResultModal'
import { usePersistentState } from '../../hooks/usePersistentState'
import { buildRunPayload } from '../../components/tool-run/payload'
import { filterToolsByOptions, getToolCategories } from '../../shared/toolUtils'
import { buildRunDiff } from './compare'
import { RunToolPicker } from './RunToolPicker'
import { RunPanel } from './RunPanel'
import { RunHistoryPanel } from './RunHistoryPanel'
import { RunQuickBar } from './RunQuickBar'
import { deriveTargetFromParams, RUN_FAVORITES_KEY, RUN_RECENT_TARGETS_KEY, RUN_TOPOLOGY_SESSION_KEY } from './storage'
import { useToast } from '../../components/ToastProvider'
import { AppFooter } from '../../app/AppFooter'
import '../../components/tool-run/shared.css'
import './RunPage.css'

// ─── Run Page ─────────────────────────────────────────────────────────────────

interface RunPageProps {
  tools: Tool[]
  toolsStatus: Record<string, boolean>
  runHistory: RunHistoryEntry[]
  setRunHistory: React.Dispatch<React.SetStateAction<RunHistoryEntry[]>>
  commandToolRequest?: { toolName: string; requestId: number } | null
  onCommandToolHandled?: () => void
  urlToolName?: string | null
  onToolSelected?: (toolName: string | null) => void
  onRefresh?: () => void
  onClearHistory?: () => Promise<void>
  onOpenSession?: (sessionId: string) => void
}

export function RunPage({
  tools,
  toolsStatus,
  runHistory: history,
  setRunHistory: setHistory,
  commandToolRequest,
  onCommandToolHandled,
  urlToolName,
  onToolSelected,
  onRefresh,
  onClearHistory,
  onOpenSession,
}: RunPageProps) {
  const { pushToast } = useToast()
  const [search, setSearch] = useState('')
  const [activeCat, setActiveCat] = useState('all')
  const [selected, setSelected] = useState<Tool | null>(null)
  const [fieldValues, setFieldValues] = useState<Record<string, string>>({})
  const [showOptional, setShowOptional] = useState(true)
  const [running, setRunning] = useState(false)
  const [viewEntry, setViewEntry] = useState<RunHistoryEntry | null>(null)
  const [modalEntry, setModalEntry] = useState<RunHistoryEntry | null>(null)
  const [histSearch, setHistSearch] = useState('')
  const [runError, setRunError] = useState<string | null>(null)
  const [liveOutput, setLiveOutput] = useState<string | null>(null)
  const [favorites, setFavorites] = usePersistentState<string[]>(RUN_FAVORITES_KEY, [])
  const [recentTargets, setRecentTargets] = usePersistentState<string[]>(RUN_RECENT_TARGETS_KEY, [])
  const [autoTopology, setAutoTopology] = useState(false)
  const [topologySessionId, setTopologySessionId] = usePersistentState<string | null>(RUN_TOPOLOGY_SESSION_KEY, null)
  const runIdRef = useRef(0)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const liveStreamRef = useRef<EventSource | null>(null)

  function stopLiveTracking() {
    if (pollRef.current) {
      clearInterval(pollRef.current)
      pollRef.current = null
    }
    liveStreamRef.current?.close()
    liveStreamRef.current = null
  }

  useEffect(() => stopLiveTracking, [])

  const cats = getToolCategories(tools)
  const filtered = filterToolsByOptions(tools, {
    toolsStatus,
    activeCategory: activeCat,
    search,
    requireAvailable: true,
  })

  function selectTool(t: Tool) {
    setSelected(t)
    setShowOptional(true)
    setRunError(null)
    setViewEntry(null)
    const defaults: Record<string, string> = {}
    for (const k of Object.keys(t.params)) defaults[k] = ''
    for (const [k, v] of Object.entries(t.optional)) defaults[k] = String(v)
    setFieldValues(defaults)
    onToolSelected?.(t.name)
  }

  function toggleFavoriteSelected() {
    if (!selected) return
    const name = selected.name
    setFavorites(prev => prev.includes(name) ? prev.filter(t => t !== name) : [name, ...prev].slice(0, 30))
  }

  function applyTarget(target: string) {
    const targetKeys = ['target', 'url', 'domain', 'host', 'ip', 'rhost', 'hostname']
    setFieldValues(prev => {
      const next = { ...prev }
      for (const key of targetKeys) {
        if (Object.prototype.hasOwnProperty.call(next, key)) {
          next[key] = target
          break
        }
      }
      return next
    })
  }

  async function exportTopology(entry: RunHistoryEntry, navigate: boolean) {
    try {
      const res = await api.exportTopology(entry.tool, entry.params, entry.result, topologySessionId ?? undefined)
      if (!res.success) {
        pushToast('error', res.error || 'Topology export failed')
        return
      }
      if (!res.topology) {
        pushToast('info', res.message || 'No hosts/ports found in output')
        return
      }
      if (res.session_id) setTopologySessionId(res.session_id)
      if (navigate && res.session_id) {
        onOpenSession?.(res.session_id)
      } else {
        pushToast('success', `Topology map updated (session ${res.session_id})`)
      }
    } catch (e) {
      pushToast('error', `Topology export failed: ${String(e)}`)
    }
  }

  async function runTool() {
    if (!selected) return
    const { payload, missing } = buildRunPayload(selected, fieldValues)
    if (missing.length) { setRunError(`Missing required: ${missing.join(', ')}`); return }
    setRunError(null)
    setRunning(true)
    setViewEntry(null)
    setLiveOutput(null)
    const id = ++runIdRef.current
    stopLiveTracking()
    try {
      const { task_id } = await api.executeToolAsync(selected.name, payload)

      const liveSource = api.processesStream()
      liveStreamRef.current = liveSource
      liveSource.onmessage = e => {
        try {
          const streamPayload = JSON.parse(e.data) as { processes?: Record<string, { task_id?: string | null; last_output?: string }> }
          const match = Object.values(streamPayload.processes ?? {}).find(p => p.task_id === task_id)
          if (match) setLiveOutput(match.last_output || null)
        } catch {
          // ignore malformed SSE frames — the poll loop is the source of truth for completion
        }
      }

      const result = await new Promise<import('../../api').ToolExecResponse>((resolve, reject) => {
        pollRef.current = setInterval(async () => {
          try {
            const res = await api.getTaskResult(task_id)
            const { status } = res.result
            if (status === 'completed') {
              stopLiveTracking()
              resolve(res.result.result as import('../../api').ToolExecResponse)
            } else if (status === 'failed' || status === 'not_found') {
              stopLiveTracking()
              reject(new Error(res.result.error || `Tool execution ${status}`))
            }
          } catch (e) {
            stopLiveTracking()
            reject(e)
          }
        }, 1500)
      })

      const entry: RunHistoryEntry = { id, tool: selected.name, params: payload, result, ts: new Date(), source: 'browser' }
      setHistory(h => [entry, ...h].slice(0, 100)) // Limit to last 100 runs
      setViewEntry(entry)
      const target = deriveTargetFromParams(payload)
      if (target) {
        setRecentTargets(prev => [target, ...prev.filter(t => t !== target)].slice(0, 10))
      }
      if (autoTopology && selected.topology_capable) {
        void exportTopology(entry, false)
      }
    } catch (e) {
      setRunError(String(e))
    } finally {
      stopLiveTracking()
      setLiveOutput(null)
      setRunning(false)
    }
  }

  useEffect(() => {
    onRefresh?.()
  }, [])

  useEffect(() => {
    if (!commandToolRequest) return
    const tool = tools.find(t => t.name === commandToolRequest.toolName)
    if (tool) {
      selectTool(tool)
      setSearch('')
    }
    onCommandToolHandled?.()
  }, [commandToolRequest, tools, onCommandToolHandled])

  // Keeps the selected tool in sync with the URL: opens directly into a tool when the
  // page is loaded from a deep link (#/run/<tool>), and follows Back/Forward navigation
  // between tools. Never pre-fills params from the URL — only picks the tool.
  useEffect(() => {
    if (!urlToolName || selected?.name === urlToolName) return
    const tool = tools.find(t => t.name === urlToolName)
    if (tool) selectTool(tool)
  }, [urlToolName, tools, selected])

  const compareText = modalEntry
    ? (() => {
        const prev = history.find(e => e.id !== modalEntry.id && e.tool === modalEntry.tool)
        return prev ? buildRunDiff(modalEntry, prev) : undefined
      })()
    : undefined

  const favoriteTools = filtered
    .filter(tool => favorites.includes(tool.name))
    .sort((a, b) => favorites.indexOf(a.name) - favorites.indexOf(b.name))

  const nonFavoriteTools = filtered.filter(tool => !favorites.includes(tool.name))

  return (
    <div className="run-page">
      {modalEntry && (
        <RunResultModal
          entry={modalEntry}
          compareText={compareText}
          onClose={() => setModalEntry(null)}
          onRerun={() => {
            const t = tools.find(t => t.name === modalEntry.tool)
            if (t) {
              selectTool(t)
              setFieldValues(prev => {
                const next = { ...prev }
                for (const [k, v] of Object.entries(modalEntry.params)) next[k] = String(v)
                return next
              })
            }
            setModalEntry(null)
          }}
          topologyCapable={tools.find(t => t.name === modalEntry.tool)?.topology_capable}
          onExportTopology={entry => void exportTopology(entry, true)}
        />
      )}
      <RunToolPicker
        search={search}
        setSearch={setSearch}
        activeCat={activeCat}
        setActiveCat={setActiveCat}
        cats={cats}
        filtered={nonFavoriteTools}
        favorites={favoriteTools}
        selected={selected}
        onSelectTool={selectTool}
      />

      <div className="run-main-col">
        <RunPanel
          selected={selected}
          toolsStatus={toolsStatus}
          fieldValues={fieldValues}
          setFieldValues={setFieldValues}
          showOptional={showOptional}
          setShowOptional={setShowOptional}
          running={running}
          runError={runError}
          liveOutput={liveOutput}
          isFavorite={selected ? favorites.includes(selected.name) : false}
          onToggleFavorite={toggleFavoriteSelected}
          onRunTool={runTool}
          viewEntry={viewEntry}
          autoTopology={autoTopology}
          setAutoTopology={setAutoTopology}
          onExportTopology={entry => void exportTopology(entry, true)}
        />
        <AppFooter />
      </div>

      <RunQuickBar
        recentTargets={recentTargets}
        onPickTarget={applyTarget}
        onClearRecentTargets={() => setRecentTargets([])}
      />

      <RunHistoryPanel
        history={history}
        setHistory={setHistory}
        onRefresh={onRefresh}
        onClearHistory={onClearHistory}
        histSearch={histSearch}
        setHistSearch={setHistSearch}
        viewEntry={viewEntry}
        onOpenModalEntry={setModalEntry}
      />
    </div>
  )
}
