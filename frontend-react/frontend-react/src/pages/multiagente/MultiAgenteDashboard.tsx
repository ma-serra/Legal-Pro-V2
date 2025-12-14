import { useState, useEffect } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader, StatCard } from '../../components/ui/AdminComponents'
import { Bot, Play, History, TrendingUp, Users } from 'lucide-react'
import api from '../../lib/api'

interface MultiAgentStats {
    total_execucoes: number
    execucoes_sucesso: number
    media_agentes_por_execucao: number
    tempo_medio_execucacao: number
}

interface RecentExecution {
    id: number
    tipo: string
    num_agentes: number
    status: string
    created_at: string
}

export default function MultiAgenteDashboard() {
    const [stats, setStats] = useState<MultiAgentStats | null>(null)
    const [recent, setRecent] = useState<RecentExecution[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        await Promise.all([
            fetchStats(),
            fetchRecentExecutions()
        ])
        setLoading(false)
    }

    // Endpoint: GET /api/multi-agente-real/estatisticas
    const fetchStats = async () => {
        try {
            const response = await api.get('/api/multi-agente-real/estatisticas')
            setStats(response.data)
        } catch (error) {
            console.error('Error fetching stats:', error)
        }
    }

    // Endpoint: GET /api/multi-agente-real/listar
    const fetchRecentExecutions = async () => {
        try {
            const response = await api.get('/api/multi-agente-real/listar')
            setRecent(response.data.slice(0, 10))
        } catch (error) {
            console.error('Error fetching executions:', error)
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
                title="Multi-Agente Dashboard"
                description="Sistema de orquestração inteligente de múltiplos agentes IA"
            />

            {/* Stats */}
            {stats && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <StatCard
                        title="Total Execuções"
                        value={stats.total_execucoes.toString()}
                        icon={Play}
                    />
                    <StatCard
                        title="Taxa de Sucesso"
                        value={`${((stats.execucoes_sucesso / stats.total_execucoes) * 100).toFixed(1)}%`}
                        icon={TrendingUp}
                    />
                    <StatCard
                        title="Média Agentes/Exec"
                        value={stats.media_agentes_por_execucao.toFixed(1)}
                        icon={Users}
                    />
                    <StatCard
                        title="Tempo Médio"
                        value={`${stats.tempo_medio_execucacao.toFixed(1)}s`}
                        icon={Bot}
                    />
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Quick Actions */}
                <div className="space-y-6">
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Ações Rápidas</h3>
                        <div className="space-y-3">
                            <a
                                href="/multi-agente/orquestrador"
                                className="block p-4 border border-gray-200 rounded-lg hover:shadow-lg transition-shadow"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="p-3 bg-blue-100 rounded-lg">
                                        <Play className="w-6 h-6 text-blue-600" />
                                    </div>
                                    <div>
                                        <h4 className="font-semibold text-gray-900">Orquestrador</h4>
                                        <p className="text-sm text-gray-600">Executar análise multi-agente</p>
                                    </div>
                                </div>
                            </a>

                            <a
                                href="/multi-agente/selecao-inteligente"
                                className="block p-4 border border-gray-200 rounded-lg hover:shadow-lg transition-shadow"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="p-3 bg-purple-100 rounded-lg">
                                        <Bot className="w-6 h-6 text-purple-600" />
                                    </div>
                                    <div>
                                        <h4 className="font-semibold text-gray-900">Seleção Inteligente</h4>
                                        <p className="text-sm text-gray-600">IA escolhe melhores agentes</p>
                                    </div>
                                </div>
                            </a>

                            <a
                                href="/multi-agente/historico"
                                className="block p-4 border border-gray-200 rounded-lg hover:shadow-lg transition-shadow"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="p-3 bg-green-100 rounded-lg">
                                        <History className="w-6 h-6 text-green-600" />
                                    </div>
                                    <div>
                                        <h4 className="font-semibold text-gray-900">Histórico</h4>
                                        <p className="text-sm text-gray-600">Ver execuções anteriores</p>
                                    </div>
                                </div>
                            </a>

                            <a
                                href="/multi-agente/performance"
                                className="block p-4 border border-gray-200 rounded-lg hover:shadow-lg transition-shadow"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="p-3 bg-yellow-100 rounded-lg">
                                        <TrendingUp className="w-6 h-6 text-yellow-600" />
                                    </div>
                                    <div>
                                        <h4 className="font-semibold text-gray-900">Performance</h4>
                                        <p className="text-sm text-gray-600">Analytics e métricas</p>
                                    </div>
                                </div>
                            </a>
                        </div>
                    </div>
                </div>

                {/* Recent Executions */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <History className="w-5 h-5" />
                        Execuções Recentes
                    </h3>

                    <div className="space-y-3">
                        {recent.map((exec) => (
                            <div key={exec.id} className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="font-medium text-sm">{exec.tipo}</span>
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${exec.status === 'sucesso' ? 'bg-green-100 text-green-800' :
                                            exec.status === 'erro' ? 'bg-red-100 text-red-800' :
                                                'bg-yellow-100 text-yellow-800'
                                        }`}>
                                        {exec.status}
                                    </span>
                                </div>
                                <div className="flex items-center gap-4 text-sm text-gray-600">
                                    <span>{exec.num_agentes} agentes</span>
                                    <span>{new Date(exec.created_at).toLocaleString('pt-BR')}</span>
                                </div>
                            </div>
                        ))}

                        {recent.length === 0 && (
                            <p className="text-sm text-gray-500 text-center py-8">
                                Nenhuma execução recente
                            </p>
                        )}
                    </div>

                    <button className="w-full mt-4 px-4 py-2 text-center border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                        Ver Histórico Completo
                    </button>
                </div>
            </div>
        </AdminLayout>
    )
}
