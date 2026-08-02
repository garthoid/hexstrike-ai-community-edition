import type { CSSProperties, HTMLAttributes, ReactNode, TdHTMLAttributes, ThHTMLAttributes } from 'react'
import './Table.css'

export function Table({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className="ui-table-wrap">
      <table className={`ui-table${className ? ` ${className}` : ''}`}>{children}</table>
    </div>
  )
}

export function TableHead({ children }: { children: ReactNode }) {
  return <thead className="ui-table-head">{children}</thead>
}

export function TableBody({ children }: { children: ReactNode }) {
  return <tbody>{children}</tbody>
}

export function TableRow({
  children,
  className = '',
  style,
  ...rest
}: HTMLAttributes<HTMLTableRowElement> & { style?: CSSProperties }) {
  return (
    <tr className={`ui-table-row${className ? ` ${className}` : ''}`} style={style} {...rest}>
      {children}
    </tr>
  )
}

export function TableHeaderCell({ children, className = '', ...rest }: ThHTMLAttributes<HTMLTableCellElement>) {
  return <th className={`ui-table-th${className ? ` ${className}` : ''}`} {...rest}>{children}</th>
}

export function TableCell({ children, className = '', ...rest }: TdHTMLAttributes<HTMLTableCellElement>) {
  return <td className={`ui-table-td${className ? ` ${className}` : ''}`} {...rest}>{children}</td>
}
