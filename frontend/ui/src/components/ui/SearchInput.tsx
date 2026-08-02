import { Search, X } from 'lucide-react'
import './SearchInput.css'

interface SearchInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
}

export function SearchInput({ value, onChange, placeholder = 'Search…', className = '' }: SearchInputProps) {
  return (
    <div className={`ui-search-wrap${className ? ` ${className}` : ''}`}>
      <Search size={13} className="ui-search-icon" />
      <input
        type="text"
        className="input ui-search-input"
        placeholder={placeholder}
        value={value}
        onChange={e => onChange(e.target.value)}
      />
      {value && (
        <button
          type="button"
          className="ui-search-clear"
          onClick={() => onChange('')}
          aria-label="Clear search"
        >
          <X size={13} />
        </button>
      )}
    </div>
  )
}
