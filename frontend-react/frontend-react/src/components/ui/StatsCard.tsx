import { LucideIcon } from 'lucide-react'

interface StatsCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: LucideIcon
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
}

const variantStyles = {
  primary: 'from-blue-600 to-blue-800',
  success: 'from-green-600 to-green-800',
  warning: 'from-yellow-500 to-yellow-700',
  danger: 'from-red-600 to-red-800',
  info: 'from-cyan-600 to-cyan-800'
}

export default function StatsCard({ title, value, subtitle, icon: Icon, variant = 'primary' }: StatsCardProps) {
  return (
    <div className={`bg-gradient-to-br ${variantStyles[variant]} rounded-xl p-4 text-white shadow-lg hover:shadow-xl transition-all hover:-translate-y-1`}>
      <div className="flex justify-between items-start">
        <div>
          <h6 className="text-sm font-medium opacity-90">{title}</h6>
          <h3 className="text-2xl font-bold mt-1">{value}</h3>
          {subtitle && (
            <p className="text-xs mt-1 opacity-75">{subtitle}</p>
          )}
        </div>
        <div className="opacity-75">
          <Icon className="w-8 h-8" />
        </div>
      </div>
    </div>
  )
}
