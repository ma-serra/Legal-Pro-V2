import { Search } from 'lucide-react'

interface FilterOption {
  value: string
  label: string
}

interface FilterProps {
  label: string
  options: FilterOption[]
  value: string
  onChange: (value: string) => void
}

interface FilterBarProps {
  filters: FilterProps[]
  searchValue?: string
  onSearchChange?: (value: string) => void
  searchPlaceholder?: string
}

export default function FilterBar({
  filters,
  searchValue,
  onSearchChange,
  searchPlaceholder = 'Buscar...'
}: FilterBarProps) {
  return (
    <div className="bg-card rounded-lg border border-border p-4">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {filters.map((filter, idx) => (
          <div key={idx}>
            <label className="block text-sm font-medium text-muted-foreground mb-2">
              {filter.label}
            </label>
            <select
              value={filter.value}
              onChange={(e) => filter.onChange(e.target.value)}
              className="w-full px-3 py-2 bg-background border border-border rounded-md text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {filter.options.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        ))}
        
        {onSearchChange && (
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-2">
              Buscar
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                value={searchValue}
                onChange={(e) => onSearchChange(e.target.value)}
                placeholder={searchPlaceholder}
                className="w-full pl-10 pr-3 py-2 bg-background border border-border rounded-md text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
