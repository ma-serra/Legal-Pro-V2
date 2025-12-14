import { useEffect, useState } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { StatCard, PageHeader } from '../../components/ui/AdminComponents'
import {
    Users,
    FileText,
    Activity,
    Database,
    TrendingUp,
    AlertCircle
} from 'lucide-react'
import api from '../../lib/api'

interface SystemStats {
    totalAgents: number
    totalUsers: number
    totalProcesses: number
    totalAnalyses: number
    dbStatus: 'healthy' | 'warning' | 'error'
    apiHealth: {
        openai: boolean
        anthropic: boolean
        google: boolean
    }
}

export default function AdminDashboard() {
    const [stats, setStats] = useState<SystemStats | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchSystemStats()
    }, [])

    const fetchSystemStats = async () => {
        try {
            const response = await api.get('/api/admin/api/system-stats')
            setStats(response.data)
        } catch (error) {
            console.error('Error fetching stats:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <AdminLayout>
                <div className="flex items-center justify-center h-96">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
            </AdminLayout>
        )
    }

    return (
        <AdminLayout>
            <PageHeader
                title="Dashboard Administrativo"
                description="Visão geral do sistema Legal Pro"
            />

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard
                    title="Agentes Ativos"
                    value={stats?.total Agents || 368}
                icon={Users}
                trend={{ value: 5.2, isPositive: true }}
        />
                <StatCard
                    title="Usuários"
                    value={stats?.totalUsers || 0}
                    icon={Users}
                />
                <StatCard
                    title="Processos"
                    value={stats?.totalProcesses || 0}
                    icon={FileText}
                    trend={{ value: 12.5, isPositive: true }}
                />
                <StatCard
                    title="Análises (24h)"
                    value={stats?.totalAnalyses || 0}
                    icon={Activity}
                    trend={{ value: 8.1, isPositive: true }}
                />
            </div>

            {/* System Status */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Database Status */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <Database className="w-6 h-6 text-blue-600" />
                        <h2 className="text-lg font-semibold text-gray-900">PostgreSQL Database</h2>
                    </div>
                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Status</span>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${stats?.dbStatus === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                }`}>
                                {stats?.dbStatus === 'healthy' ? '●  Online' : '● Offline'}
                            </span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Uptime</span>
                            <span className="text-sm font-medium text-gray-900">99.9%</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Conexões</span>
                            <span className="text-sm font-medium text-gray-900">8/100</span>
                        </div>
                    </div>
                </div>

                {/* API Health */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <TrendingUp className="w-6 h-6 text-green-600" />
                        <h2 className="text-lg font-semibold text-gray-900">API Status</h2>
                    </div>
                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">OpenAI</span>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${stats?.apiHealth?.openai ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                }`}>
                                {stats?.apiHealth?.openai ? '● Ativo' : '○ Inativo'}
                            </span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Anthropic</span>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${stats?.apiHealth?.anthropic ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                }`}>
                                {stats?.apiHealth?.anthropic ? '● Ativo' : '○ Inativo'}
                            </span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Google AI</span>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${stats?.apiHealth?.google ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                }`}>
                                {stats?.apiHealth?.google ? '● Ativo' : '○ Inativo'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-center gap-3 mb-4">
                    <AlertCircle className="w-6 h-6 text-blue-600" />
                    <h2 className="text-lg font-semibold text-gray-900">Atividade Recente</h2>
                </div>
                <div className="space-y-3">
                    <div className="flex items-start gap-3 pb-3 border-b border-gray-100">
                        <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                        <div className="flex-1">
                            <p className="text-sm text-gray-900">Sistema iniciado com sucesso</p>
                            <p className="text-xs text-gray-500">Há 2 horas</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-3 pb-3 border-b border-gray-100">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                        <div className="flex-1">
                            <p className="text-sm text-gray-900">Nova análise multi-agente concluída</p>
                            <p className="text-xs text-gray-500">Há 3 horas</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-3">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
                        <div className="flex-1">
                            <p className="text-sm text-gray-900">Backup automático do banco de dados</p>
                            <p className="text-xs text-gray-500">Há 8 horas</p>
                        </div>
                    </div>
                </div>
            </div>
        </AdminLayout>
    )
}
