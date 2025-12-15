import { useState, useEffect } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader, StatCard } from '../../components/ui/AdminComponents'
import { TrendingUp, Clock, CheckCircle, XCircle, BarChart3, Calendar } from 'lucide-react'
// import api from '../../lib/api'

interface PerformanceData {
    total_execucoes: number
    execucoes_sucesso: number
    execucoes_erro: number
    tempo_medio: number
    tempo_minimo: number
    tempo_maximo: number
    agente_mais_usado: string
    melhor_combinacao: string[]
}

interface AgentPerformance {
    agente_nome: string
    num_execucoes: number
    taxa_sucesso: number
    tempo_medio: number
}

export default function MultiAgentePerformance() {
    const [performance, setPerformance] = useState<PerformanceData | null>(null)
    const [agentStats, setAgentStats] = useState<AgentPerformance[]>([])
    const [loading, setLoading] = useState(true)
    const [period, setPeriod] = useState('30d')

    useEffect(() => {
        fetchPerformance()
    }, [period])

    // Endpoint: GET /api/multi-agente-real/estatisticas (with period filter)
    const fetchPerformance = async () => {
        try {
            const response = await api.get('/api/multi-agente-real/estatisticas', {
                params: { periodo: period }
            })

            setPerformance(response.data)

            // Mock agent-specific performance data
            setAgentStats([
                { agente_nome: 'Agente Cível', num_execucoes: 145, taxa_sucesso: 0.94, tempo_medio: 12.3 },
                { agente_nome: 'Agente Trabalhista', num_execucoes: 89, taxa_sucesso: 0.91, tempo_medio: 10.7 },
                { agente_nome: 'Agente Criminal', num_execucoes: 67, taxa_sucesso: 0.88, tempo_medio: 15.2 },
                { agente_nome: 'Agente Tributário', num_execucoes: 54, taxa_sucesso: 0.93, tempo_medio: 11.5 },
            ])
        } catch (error) {
            console.error('Error fetching performance:', error)
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
                title="Performance Multi-Agente"
                description="Analytics e métricas de execução"
            />

            {/* Period Filter */}
            <div className="mb-6 flex items-center gap-4">
                <label className="text-sm font-medium text-gray-700">Período:</label>
                <select
                    value={period}
                    onChange={(e) => setPeriod(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg"
                >
                    <option value="7d">Últimos 7 dias</option>
                    <option value="30d">Últimos 30 dias</option>
                    <option value="90d">Últimos 90 dias</option>
                    <option value="all">Todos os tempos</option>
                </select>
            </div>

            {/* Main Stats */}
            {performance && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <StatCard
                        title="Total Execuções"
                        value={performance.total_execucoes.toString()}
                        icon={BarChart3}
                    />
                    <StatCard
                        title="Taxa de Sucesso"
                        value={`${((performance.execucoes_sucesso / performance.total_execucoes) * 100).toFixed(1)}%`}
                        icon={TrendingUp}
                    />
                    <StatCard
                        title="Tempo Médio"
                        value={`${performance.tempo_medio.toFixed(1)}s`}
                        icon={Clock}
                    />
                    <StatCard
                        title="Sucesso/Erro"
                        value={`${performance.execucoes_sucesso}/${performance.execucoes_erro}`}
                        icon={CheckCircle}
                    />
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Performance by Agent */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance por Agente</h3>

                    <div className="space-y-4">
                        {agentStats.map((agent, idx) => (
                            <div key={idx} className="border-b border-gray-200 pb-4 last:border-0">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="font-medium text-gray-900">{agent.agente_nome}</span>
                                    <span className="text-sm text-gray-600">{agent.num_execucoes} execuções</span>
                                </div>

                                <div className="grid grid-cols-2 gap-4 text-sm">
                                    <div>
                                        <span className="text-gray-600">Taxa Sucesso:</span>
                                        <div className="flex items-center gap-2 mt-1">
                                            <div className="flex-1 bg-gray-200 rounded-full h-2">
                                                <div
                                                    className="bg-green-500 h-2 rounded-full"
                                                    style={{ width: `${agent.taxa_sucesso * 100}%` }}
                                                />
                                            </div>
                                            <span className="font-medium text-green-600">
                                                {(agent.taxa_sucesso * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                    </div>

                                    <div>
                                        <span className="text-gray-600">Tempo Médio:</span>
                                        <div className="font-medium text-blue-600 mt-1">
                                            {agent.tempo_medio.toFixed(1)}s
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Time Stats */}
                {performance && (
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Estatísticas de Tempo</h3>

                        <div className="space-y-6">
                            <div>
                                <label className="text-sm text-gray-600">Tempo Médio de Execução</label>
                                <p className="text-3xl font-bold text-blue-600 mt-1">
                                    {performance.tempo_medio.toFixed(1)}s
                                </p>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm text-gray-600">Mais Rápido</label>
                                    <p className="text-xl font-semibold text-green-600 mt-1">
                                        {performance.tempo_minimo.toFixed(1)}s
                                    </p>
                                </div>
                                <div>
                                    <label className="text-sm text-gray-600">Mais Lento</label>
                                    <p className="text-xl font-semibold text-red-600 mt-1">
                                        {performance.tempo_maximo.toFixed(1)}s
                                    </p>
                                </div>
                            </div>

                            <div className="pt-4 border-t border-gray-200">
                                <label className="text-sm text-gray-600 block mb-2">Agente Mais Usado</label>
                                <div className="flex items-center gap-2 text-purple-600">
                                    <BarChart3 className="w-5 h-5" />
                                    <span className="font-semibold">{performance.agente_mais_usado}</span>
                                </div>
                            </div>

                            {performance.melhor_combinacao && (
                                <div className="pt-4 border-t border-gray-200">
                                    <label className="text-sm text-gray-600 block mb-2">Melhor Combinação</label>
                                    <div className="flex flex-wrap gap-2">
                                        {performance.melhor_combinacao.map((agente, idx) => (
                                            <span key={idx} className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
                                                {agente}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* Success/Error Distribution */}
            {performance && (
                <div className="mt-6 bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribuição Sucesso/Erro</h3>

                    <div className="grid grid-cols-2 gap-6">
                        <div className="flex items-center gap-4 p-4 bg-green-50 rounded-lg">
                            <CheckCircle className="w-8 h-8 text-green-600" />
                            <div>
                                <p className="text-sm text-gray-600">Execuções Bem-Sucedidas</p>
                                <p className="text-2xl font-bold text-green-600">{performance.execucoes_sucesso}</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4 p-4 bg-red-50 rounded-lg">
                            <XCircle className="w-8 h-8 text-red-600" />
                            <div>
                                <p className="text-sm text-gray-600">Execuções com Erro</p>
                                <p className="text-2xl font-bold text-red-600">{performance.execucoes_erro}</p>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </AdminLayout>
    )
}
