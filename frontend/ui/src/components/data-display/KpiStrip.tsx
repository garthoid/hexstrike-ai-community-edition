import { Fragment, type ReactNode } from 'react'

export interface KpiStripItem {
  icon: ReactNode
  label: string
  value: string | number
  accent?: string
}

interface KpiStripProps {
  items: KpiStripItem[]
}

/** Flat, boxless KPI row — icon + value + label per item, divided by hairlines, meant to sit on a panel background. */
export function KpiStrip({ items }: KpiStripProps) {
  return (
    <div className="kpi-strip">
      {items.map((item, i) => (
        <Fragment key={item.label}>
          {i > 0 && <div className="kpi-strip-divider" />}
          <div className="kpi-strip-item">
            <div className="kpi-strip-top">
              <span className="kpi-strip-icon" style={{ color: item.accent || 'var(--text-h)' }}>{item.icon}</span>
              <span className="kpi-strip-value">{item.value}</span>
            </div>
            <span className="kpi-strip-label">{item.label}</span>
          </div>
        </Fragment>
      ))}
    </div>
  )
}
