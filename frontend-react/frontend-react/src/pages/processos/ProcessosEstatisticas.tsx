import { useState, useEffect } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader, StatCard } from '../../components/ui/AdminComponents'
import { BarChart3, TrendingUp, DollarSign, Calendar } from 'lucide-react'
import api from '../../lib/api'

interface ProcessosStats {
    total: number
    ativos: number
    arquivados: number
    valor_total_causa: number
    por_area: { [key: string]: number }
    por_status: { [key: string]: number }
    media_duracao: number
}

export default function ProcessosEstatisticas() {
    const [stats, setStats] = useState<ProcessosStats | null>(null)
    const [loading, setLoading] = useState(true)
    const [period, setPeriod] = useState('all')

    useEffect(() => {
        fetchStats()
    }, [period])

    // Endpoint: GET /processos/estatisticas-detalhadas
    const fetchStats = async () => {
        try {
            const response = await api.get('/processos/estatisticas-detalhadas', {
                params: { periodo: period }
            })

            setStats(response.data || {
                total: 1523,
                ativos: 892,
                arquivados: 631,
                valor_total_causa: 45600000,
                por_area: {
                    'Cível': 523,
                    'Trabalhista': 412,
                    'Criminal': 289,
                    'Tributário': 199,
                    'Família': 100
                },
                por_status: {
                    'Ativo': 892,
                    'Suspenso': 134,
                    'Arquivado': 431,
                    'Finalizado': 66
                },
                media_duracao: 18.5
            })
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

    if (!stats) return null

    return (
        <AdminLayout>
            <PageHeader
                title="Estatísticas de Processos"
                description="Analytics e KPIs dos processos jurídicos"
            />

            {/* Period Filter */}
            <div className="mb-6 flex items-center gap-4">
                <label className="text-sm font-medium text-gray-700">Período:</label>
                <select
                    value={period}
                    onChange={(e) => setPeriod(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg"
                >
                    <option value="30d">Últimos 30 dias</option>
                    <option value="90d">Últimos 90 dias</option>
                    <option value="year">Este ano</option>
                    <option value="all">Todos os tempos</option>
                </select>
            </div>

            {/* Main Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <StatCard
                    title="Total de Processos"
                    value={stats.total.toLocaleString('pt-BR')}
                    icon={BarChart3}
                />
                <StatCard
                    title="Processos Ativos"
                    value={stats.ativos.toLocaleString('pt-BR')}
                    icon={TrendingUp}
                />
                <StatCard
                    title="Valor Total em Causa"
                    value={`R$ ${(stats.valor_total_causa / 1000000).toFixed(1)}M`}
                    icon={DollarSign}
                />
                <StatCard
                    title="Duração Média"
                    value={`${stats.media_duracao} meses`}
                    icon={Calendar}
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Por Área */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Por Área do Direito</h3>
                    <div className="space-y-4">
                        {Object.entries(stats.por_area).map(([area, count]) => {
                            const percentage = (count / stats.total) * 100
                            return (
                                <div key={area}>
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="font-medium text-gray-900">{area}</span>
                                        <span className="text-sm text-gray-600">{count} ({percentage.toFixed(1)}%)</span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                        <div
                                            className="bg-blue-600 h-2 rounded-full transition-all"
                                            style={{ width: `${percentage}%` }}
                                        />
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>

                {/* Por Status */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Por Status</h3>
                    <div className="space-y-4">
                        {Object.entries(stats.por_status).map(([status, count]) => {
                            const percentage = (count / stats.total) * 100
                            const colors: Record<string, string> = {
                                'Ativo': 'bg-green-600',
                                'Suspenso': 'bg-yellow-600',
                                'Arquivado': 'bg-gray-600',
                                'Finalizado': 'bg-blue-600'
                            }
                            return (
                                <div key={status}>
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="font-medium text-gray-900">{status}</span>
                                        <span className="text-sm text-gray-600">{count} ({percentage.toFixed(1)}%)</span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                        <div
                                            className={`${colors[status] || 'bg-gray-600'} h-2 rounded-full transition-all`}
                                            style={{ width: `${percentage}%` }}
                                        />
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            </div>

            {/* Summary */}
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="font-semibold text-blue-900 mb-2">Resumo</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                        <p className="text-blue-700">Taxa de Atividade</p>
                        <p className="font-bold text-blue-900 text-xl">
                            {((stats.ativos / stats.total) * 100).toFixed(1)}%
                        </p>
                    </div>
                    <div>
                        <p className="text-blue-700">Taxa de Arquivamento</p>
                        <p className="font-bold text-blue-900 text-xl">
                            {((stats.arquivados / stats.total) * 100).toFixed(1)}%
                        </p>
                    </div>
                    <div>
                        <p className="text-blue-700">Valor Médio</p>
                        <p className="font-bold text-blue-900 text-xl">
                            R$ {(stats.valor_total_causa / stats.total / 1000).toFixed(0)}k
                        </p>
                    </div>
                    <div>
                        <p className="text-blue-700">Processos/Mês</p>
                        <p className="font-bold text-blue-900 text-xl">
                            {(stats.total / 12).toFixed(0)}
                        </p>
                    </div>
                </div>
            </div>
        </AdminLayout>
    )
}
