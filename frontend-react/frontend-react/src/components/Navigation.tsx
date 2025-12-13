import { Link, useNavigate, useLocation } from 'react-router-dom'
import { LogOut, LayoutDashboard, Gavel, FileSearch, Users, Home } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

const navItems = [
  { path: '/', label: 'Home', icon: Home },
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/processos', label: 'Processos', icon: Gavel },
  { path: '/analises', label: 'Análises', icon: FileSearch },
  { path: '/assistentes', label: 'Assistentes', icon: Users }
]

export default function Navigation() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="border-b border-border bg-card">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <Link to="/" className="text-xl font-bold text-primary">
            Legal Pro
          </Link>
          <div className="flex gap-1 items-center">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md transition ${isActive
                      ? 'bg-primary/10 text-primary'
                      : 'text-foreground hover:bg-accent hover:text-primary'
                    }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden md:inline">{item.label}</span>
                </Link>
              )
            })}
            <div className="w-px h-6 bg-border mx-2" />
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-red-500/10 hover:text-red-400 transition"
              title="Sair"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
