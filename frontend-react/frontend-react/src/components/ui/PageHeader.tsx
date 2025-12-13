import { LucideIcon } from 'lucide-react'

interface PageHeaderProps {
  title: string
  icon?: LucideIcon
  children?: React.ReactNode
}

export default function PageHeader({ title, icon: Icon, children }: PageHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
      <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
        {Icon && <Icon className="w-7 h-7 text-primary" />}
        {title}
      </h1>
      {children && (
        <div className="flex gap-2">
          {children}
        </div>
      )}
    </div>
  )
}
