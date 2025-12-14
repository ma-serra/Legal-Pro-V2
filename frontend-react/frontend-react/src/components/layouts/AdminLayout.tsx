import { ReactNode } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
    LayoutDashboard,
    Users,
    Settings,
    Database,
    Activity,
    FileText,
    Palette,
    Shield,
    Cloud,
    LogOut
} from 'lucide-react'

interface AdminLayoutProps {
    children: ReactNode
}

export function AdminLayout({ children }: AdminLayoutProps) {
    const navigate = useNavigate()

    const menuItems = [
        { icon: LayoutDashboard, label: 'Dashboard', path: '/admin' },
        { icon: Activity, label: 'Monitoramento', path: '/admin/monitoring' },
        { icon: Database, label: 'Banco de Dados', path: '/admin/database' },
        { icon: Users, label: 'Agentes', path: '/admin/agents' },
        { icon: Shield, label: 'Usuários', path: '/admin/users' },
        { icon: Settings, label: 'APIs', path: '/admin/api-config' },
        { icon: FileText, label: 'Templates', path: '/admin/templates' },
        { icon: Palette, label: 'Temas', path: '/admin/themes' },
        { icon: Cloud, label: 'Vector DB', path: '/admin/vector-status' },
    ]

    const handleLogout = () => {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        navigate('/login')
    }

    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Sidebar */}
            <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
                {/* Logo */}
                <div className="h-16 flex items-center px-6 border-b border-gray-200">
                    <h1 className="text-xl font-bold text-gray-900">Legal Pro Admin</h1>
                </div>

                {/* Menu */}
                <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
                    {menuItems.map((item) => (
                        <Link
                            key={item.path}
                            to={item.path}
                            className="flex items-center gap-3 px-3 py-2 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                            <item.icon className="w-5 h-5" />
                            <span className="text-sm font-medium">{item.label}</span>
                        </Link>
                    ))}
                </nav>

                {/* User Info */}
                <div className="p-4 border-t border-gray-200">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
                                A
                            </div>
                            <div>
                                <p className="text-sm font-medium text-gray-900">Admin</p>
                                <p className="text-xs text-gray-500">Administrador</p>
                            </div>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
                            title="Sair"
                        >
                            <LogOut className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                <div className="p-8">
                    {children}
                </div>
            </main>
        </div>
    )
}
