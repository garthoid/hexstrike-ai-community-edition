import { Fragment, type ReactNode } from 'react'
import './Card.css'

export interface CardItem {
  icon: ReactNode
  label: string
  value: string | number
  sub?: string
  accent?: string
}

interface CardProps extends CardItem {
  layout?: 'boxed' | 'flat'
}

/** Single KPI/stat unit. Use `layout="boxed"` for a bordered card, `layout="flat"` for a divided row item (see CardGroup). */
export function Card({ icon, label, value, sub, accent, layout = 'boxed' }: CardProps) {
  if (layout === 'flat') {
    return (
      <div className="ui-card ui-card--flat">
        <div className="ui-card-flat-top">
          <span className="ui-card-icon" style={{ color: accent || 'var(--text-h)' }}>{icon}</span>
          <span className="ui-card-flat-value">{value}</span>
        </div>
        <span className="ui-card-flat-label">{label}</span>
      </div>
    )
  }

  return (
    <div className="ui-card ui-card--boxed">
      <div className="ui-card-icon" style={{ color: accent || 'var(--green)' }}>{icon}</div>
      <div className="ui-card-body">
        <div className="ui-card-label">{label}</div>
        <div className="ui-card-value" style={{ color: accent || 'var(--text-h)' }}>{value}</div>
        {sub && <div className="ui-card-sub">{sub}</div>}
      </div>
    </div>
  )
}

interface CardGroupProps {
  items: CardItem[]
  layout?: 'boxed' | 'flat'
}

/** Lays out a set of Cards — a divided flat row (replaces KpiStrip) or a boxed grid (replaces a row of StatCards). */
export function CardGroup({ items, layout = 'flat' }: CardGroupProps) {
  if (layout === 'boxed') {
    return (
      <div className="ui-card-group ui-card-group--boxed">
        {items.map(item => <Card key={item.label} layout="boxed" {...item} />)}
      </div>
    )
  }

  return (
    <div className="ui-card-group ui-card-group--flat">
      {items.map((item, i) => (
        <Fragment key={item.label}>
          {i > 0 && <div className="ui-card-group-divider" />}
          <Card layout="flat" {...item} />
        </Fragment>
      ))}
    </div>
  )
}
