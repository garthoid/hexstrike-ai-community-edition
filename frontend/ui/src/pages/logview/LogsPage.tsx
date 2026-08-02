import React, { useState } from 'react'
import { Terminal } from 'lucide-react'
import { BrowserPage } from '../../components/layout/BrowserPage'
import { LogsToolbar, LogsViewer } from './LogsSections'
import { getVisibleLogLines } from './utils'
import './LogsPage.css'

interface LogsPageProps {
  logLines: string[]
  logAutoScroll: boolean
  setLogAutoScroll: (v: boolean) => void
  logLimit: number
  setLogLimit: (v: number) => void
  logEndRef: React.RefObject<HTMLDivElement | null>
}

export default function LogsPage({
  logLines,
  logAutoScroll,
  setLogAutoScroll,
  logLimit,
  setLogLimit,
  logEndRef,
}: LogsPageProps) {
  const [showHttpAccess, setShowHttpAccess] = useState(false)

  const visible = getVisibleLogLines(logLines, showHttpAccess)

  return (
    <BrowserPage
      className="logs-page"
      top={(
        <div className="logs-page-header">
          <h1 className="logs-page-title">
            <Terminal size={16} /> Server Log
          </h1>
          <LogsToolbar
            logAutoScroll={logAutoScroll}
            setLogAutoScroll={setLogAutoScroll}
            showHttpAccess={showHttpAccess}
            setShowHttpAccess={setShowHttpAccess}
            logLimit={logLimit}
            setLogLimit={setLogLimit}
            visibleCount={visible.length}
            totalCount={logLines.length}
          />
        </div>
      )}
      main={(
        <div className="browser-main">
          <LogsViewer visible={visible} logLimit={logLimit} logEndRef={logEndRef} />
        </div>
      )}
    />
  )
}
