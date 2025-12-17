import { Link, useNavigate, useLocation } from 'react-router-dom'
import {
    LogOut, LayoutDashboard, Gavel, FileSearch, Users, Home,
    FileUp, Scale, TrendingUp, Menu, X, Brain, Upload
} from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { useState } from 'react'

const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    {
        path: '/processos',
        label: 'Processos',
        icon: Gavel,
        subItems: [
            { path: '/processos', label: 'Lista de Processos' },
            { path: '/processos/importar', label: 'Importar Planilha', icon: FileUp },
            { path: '/processos/teses', label: 'Teses Tributárias', icon: Scale },
            { path: '/processos/indices', label: 'Índices Monetários', icon: TrendingUp },
            { path: '/processos/ml-analise', label: 'Análise ML Tributário', icon: Brain }
        ]
    },
    { path: '/analises', label: 'Análises', icon: FileSearch },
    { path: '/assistentes', label: 'Assistentes', icon: Users }
]

export default function Navigation() {
    const { logout } = useAuth()
    const navigate = useNavigate()
    const location = useLocation()
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
    const [openSubmenu, setOpenSubmenu] = useState<string | null>(null)

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    const isActivePath = (path: string) => {
        if (path === '/processos') {
            return location.pathname.startsWith('/processos')
        }
        return location.pathname === path
    }

    return (
        <nav className="border-b border-border bg-card shadow-sm sticky top-0 z-50">
            <div className="container mx-auto px-4 py-3">
                <div className="flex items-center justify-between">
                    <Link to="/dashboard" className="flex items-center gap-2">
                        <div className="p-1.5 bg-primary/10 rounded-lg">
                            <Scale className="w-5 h-5 text-primary" />
                        </div>
                        <span className="text-xl font-bold text-primary hidden sm:inline">Legal Pro</span>
                    </Link>

                    <div className="hidden md:flex items-center gap-1">
                        {navItems.map((item) => {
                            const Icon = item.icon
                            const isActive = isActivePath(item.path)

                            if (item.subItems) {
                                return (
                                    <div key={item.path} className="relative group">
                                        <Link
                                            to={item.path}
                                            className={`flex items-center gap-2 px-3 py-2 rounded-md transition ${isActive
                                                ? 'bg-primary/10 text-primary'
                                                : 'text-foreground hover:bg-accent hover:text-primary'
                                                }`}
                                        >
                                            <Icon className="w-4 h-4" />
                                            <span>{item.label}</span>
                                        </Link>

                                        <div className="absolute left-0 top-full mt-1 w-56 bg-card border border-border rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                                            {item.subItems.map((subItem) => {
                                                const SubIcon = subItem.icon
                                                return (
                                                    <Link
                                                        key={subItem.path}
                                                        to={subItem.path}
                                                        className={`flex items-center gap-2 px-4 py-3 hover:bg-accent transition-colors first:rounded-t-lg last:rounded-b-lg ${location.pathname === subItem.path ? 'bg-primary/10 text-primary' : ''
                                                            }`}
                                                    >
                                                        {SubIcon && <SubIcon className="w-4 h-4" />}
                                                        <span className="text-sm">{subItem.label}</span>
                                                    </Link>
                                                )
                                            })}
                                        </div>
                                    </div>
                                )
                            }

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
                                    <span>{item.label}</span>
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
                            <span className="hidden lg:inline text-sm">Sair</span>
                        </button>
                    </div>

                    <button
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        className="md:hidden p-2 rounded-lg hover:bg-accent transition-colors"
                    >
                        {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                    </button>
                </div>

                {mobileMenuOpen && (
                    <div className="md:hidden mt-4 pb-4 border-t border-border pt-4 space-y-1">
                        {navItems.map((item) => {
                            const Icon = item.icon
                            const isActive = isActivePath(item.path)

                            if (item.subItems) {
                                return (
                                    <div key={item.path}>
                                        <button
                                            onClick={() => setOpenSubmenu(openSubmenu === item.path ? null : item.path)}
                                            className={`w-full flex items-center justify-between px-3 py-2 rounded-md transition ${isActive ? 'bg-primary/10 text-primary' : 'hover:bg-accent'
                                                }`}
                                        >
                                            <div className="flex items-center gap-2">
                                                <Icon className="w-4 h-4" />
                                                <span>{item.label}</span>
                                            </div>
                                            <span className="text-xs">{openSubmenu === item.path ? '▼' : '▶'}</span>
                                        </button>

                                        {openSubmenu === item.path && (
                                            <div className="ml-6 mt-1 space-y-1">
                                                {item.subItems.map((subItem) => {
                                                    const SubIcon = subItem.icon
                                                    return (
                                                        <Link
                                                            key={subItem.path}
                                                            to={subItem.path}
                                                            onClick={() => setMobileMenuOpen(false)}
                                                            className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm transition ${location.pathname === subItem.path
                                                                ? 'bg-primary/10 text-primary'
                                                                : 'hover:bg-accent'
                                                                }`}
                                                        >
                                                            {SubIcon && <SubIcon className="w-4 h-4" />}
                                                            <span>{subItem.label}</span>
                                                        </Link>
                                                    )
                                                })}
                                            </div>
                                        )}
                                    </div>
                                )
                            }

                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={`flex items-center gap-2 px-3 py-2 rounded-md transition ${isActive ? 'bg-primary/10 text-primary' : 'hover:bg-accent'
                                        }`}
                                >
                                    <Icon className="w-4 h-4" />
                                    <span>{item.label}</span>
                                </Link>
                            )
                        })}

                        <button
                            onClick={handleLogout}
                            className="w-full flex items-center gap-2 px-3 py-2 rounded-md hover:bg-red-500/10 hover:text-red-400 transition mt-4"
                        >
                            <LogOut className="w-4 h-4" />
                            <span>Sair</span>
                        </button>
                    </div>
                )}
            </div>
        </nav>
    )
}
