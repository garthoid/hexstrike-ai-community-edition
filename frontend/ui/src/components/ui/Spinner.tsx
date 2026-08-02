import { RefreshCw } from 'lucide-react'

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  color?: string
  className?: string
}

const SIZE_PX: Record<NonNullable<SpinnerProps['size']>, number> = {
  sm: 13,
  md: 16,
  lg: 22,
}

export function Spinner({ size = 'md', color = 'var(--green)', className = '' }: SpinnerProps) {
  return (
    <RefreshCw
      size={SIZE_PX[size]}
      color={color}
      className={`spin${className ? ` ${className}` : ''}`}
    />
  )
}
