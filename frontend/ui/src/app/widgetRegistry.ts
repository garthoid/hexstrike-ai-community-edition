import { createElement, lazy, Suspense, type ReactNode } from 'react'
import type { LucideIcon } from 'lucide-react'
import { LayoutDashboard, Cpu, Wrench, History, Layers, KeyRound, ListTodo } from 'lucide-react'
import type { Tool, WebDashboardResponse } from '../api'
import type { RunHistoryEntry, HistoryPoint } from '../shared/types'
import { KpiSection } from '../pages/dashboard/KpiSection'
import { ToolAvailabilitySection } from '../pages/dashboard/ToolAvailabilitySection'
import { RecentActivityWidget } from '../pages/dashboard/RecentActivityWidget'
import { ActiveSessionsWidget } from '../pages/dashboard/ActiveSessionsWidget'
import { RecentLootWidget } from '../pages/dashboard/RecentLootWidget'
import { TaskQueueWidget } from '../pages/dashboard/TaskQueueWidget'

const LazyResourceSection = lazy(() =>
  import('../pages/dashboard/ResourceSection').then(m => ({ default: m.ResourceSection }))
)

export interface DashboardWidgetContext {
  health: WebDashboardResponse
  tools: Tool[]
  runHistory: RunHistoryEntry[]
  toolCategories: Record<string, string[]>
  demo?: boolean
  demoCpuHistory?: unknown
}

export interface WidgetEntry {
  id: string
  label: string
  icon: LucideIcon
  description: string
  render: (ctx: DashboardWidgetContext) => ReactNode
}

export const WIDGET_REGISTRY: WidgetEntry[] = [
  {
    id: 'kpi-row',
    label: 'KPI Overview',
    icon: LayoutDashboard,
    description: 'Server status, tool counts, and command totals',
    render: ctx => createElement(KpiSection, { health: ctx.health, tools: ctx.tools, runHistory: ctx.runHistory }),
  },
  {
    id: 'system-resources',
    label: 'System Resources',
    icon: Cpu,
    description: 'Live CPU, memory, and disk usage',
    render: ctx => createElement(
      Suspense,
      { fallback: createElement('div', { className: 'loading-state' }, createElement('div', { className: 'spin spin--sm spin--green' })) },
      createElement(LazyResourceSection, {
        demoResources: ctx.demo ? ctx.health?.resources : undefined,
        demoHistory: ctx.demo ? (ctx.demoCpuHistory as HistoryPoint[] | undefined) : undefined,
      }),
    ),
  },
  {
    id: 'tool-availability',
    label: 'Tool Availability',
    icon: Wrench,
    description: 'Installed-tool breakdown by category',
    render: ctx => createElement(ToolAvailabilitySection, { health: ctx.health, tools: ctx.tools, toolCategories: ctx.toolCategories }),
  },
  {
    id: 'recent-activity',
    label: 'Recent Activity',
    icon: History,
    description: 'Latest tool runs from this session',
    render: ctx => createElement(RecentActivityWidget, { runHistory: ctx.runHistory }),
  },
  {
    id: 'active-sessions',
    label: 'Active Sessions',
    icon: Layers,
    description: 'Recon/engagement sessions currently in progress',
    render: () => createElement(ActiveSessionsWidget),
  },
  {
    id: 'recent-loot',
    label: 'Recent Loot',
    icon: KeyRound,
    description: 'Recently captured credentials and artefacts',
    render: () => createElement(RecentLootWidget),
  },
  {
    id: 'task-queue',
    label: 'Task Queue',
    icon: ListTodo,
    description: 'Running and queued background tasks',
    render: () => createElement(TaskQueueWidget),
  },
]

export const WIDGET_IDS: string[] = WIDGET_REGISTRY.map(w => w.id)

/** Dashboard widgets shown on a fresh install — new widget types are opt-in via "Add Widget". */
export const DEFAULT_WIDGET_ORDER: string[] = ['kpi-row', 'system-resources', 'tool-availability']
