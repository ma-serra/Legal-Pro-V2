import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader, StatsCard } from '../../components/ui/AdminComponents'
import {
    TrendingUp, AlertTriangle, MapPin, Calendar,
    FileText, DollarSign, Users, BarChart3
} from 'lucide-react'
import api from '../../lib/api'

interface DashboardStats {
    total_processos: number
    processos_ativos: number
    processos_sobrestados: number
    total_audiencias: number
    valor_total_causa: number
    taxa_sucesso: number
    proximas_audiencias: number
    alertas_pendentes: number
}

interface RecentProcess {
    id: number
    numero: string
    titulo: string
    status: string
    valor_causa: number
    data_atualizacao: string
}

export default function CPFLDashboard() {
    const navigate = useNavigate()
    const [stats, setStats] = useState<DashboardStats>({
        total_processos: 0,
        processos_ativos: 0,
        processos_sobrestados: 0,
        total_audiencias: 0,
        valor_total_causa: 0,
        taxa_sucesso: 0,
        proximas_audiencias: 0,
        alertas_pendentes: 0
    })
    const [recentProcesses, setRecentProcesses] = useState<RecentProcess[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchDashboardData()
    }, [])

    const fetchDashboardData = async () => {
        try {
            const [statsRes, processesRes] = await Promise.all([
                api.get('/setorenergia/api/stats'),
                api.get('/setorenergia/api/processos?limit=5')
            ])
            setStats(statsRes.data)
            setRecentProcesses(processesRes.data)
        } catch (error) {
            console.error('Error fetching dashboard data:', error)
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value)
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
                title="Setor Energia - Dashboard"
                description="Visão geral dos processos CPFL e RGE"
            />

            {/* KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                <StatsCard
                    title="Total de Processos"
                    value={stats.total_processos.toString()}
                    icon={FileText}
                    trend={`${stats.processos_ativos} ativos`}
                    trendUp={true}
                />
                <StatsCard
                    title="Processos Sobrestados"
                    value={stats.processos_sobrestados.toString()}
                    icon={AlertTriangle}
                    iconColor="text-orange-600"
                    trend="Requer atenção"
                />
                <StatsCard
                    title="Valor Total em Causa"
                    value={formatCurrency(stats.valor_total_causa)}
                    icon={DollarSign}
                    iconColor="text-green-600"
                />
                <StatsCard
                    title="Taxa de Sucesso"
                    value={`${stats.taxa_sucesso}%`}
                    icon={TrendingUp}
                    iconColor="text-blue-600"
                    trend="Últimos 6 meses"
                    trendUp={true}
                />
            </div>

            {/* Ações Rápidas */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <button
                    onClick={() => navigate('/setorenergia/sobrestados')}
                    className="bg-white p-6 rounded-lg border border-gray-200 hover:border-orange-300 hover:shadow-md transition-all text-left"
                >
                    <AlertTriangle className="w-8 h-8 text-orange-600 mb-3" />
                    <h3 className="font-semibold text-gray-900 mb-1">Sobrestados</h3>
                    <p className="text-sm text-gray-600">{stats.processos_sobrestados} processos</p>
                </button>

                <button
                    onClick={() => navigate('/setorenergia/audiencias')}
                    className="bg-white p-6 rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all text-left"
                >
                    <Calendar className="w-8 h-8 text-blue-600 mb-3" />
                    <h3 className="font-semibold text-gray-900 mb-1">Audiências</h3>
                    <p className="text-sm text-gray-600">{stats.proximas_audiencias} próximas</p>
                </button>

                <button
                    onClick={() => navigate('/setorenergia/mapa-risco')}
                    className="bg-white p-6 rounded-lg border border-gray-200 hover:border-red-300 hover:shadow-md transition-all text-left"
                >
                    <MapPin className="w-8 h-8 text-red-600 mb-3" />
                    <h3 className="font-semibold text-gray-900 mb-1">Mapa de Risco</h3>
                    <p className="text-sm text-gray-600">Visualização geográfica</p>
                </button>

                <button
                    onClick={() => navigate('/setorenergia/analytics')}
                    className="bg-white p-6 rounded-lg border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all text-left"
                >
                    <BarChart3 className="w-8 h-8 text-purple-600 mb-3" />
                    <h3 className="font-semibold text-gray-900 mb-1">Analytics</h3>
                    <p className="text-sm text-gray-600">Análises detalhadas</p>
                </button>
            </div>

            {/* Processos Recentes & Alertas */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Processos Recentes */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Processos Recentes</h3>
                    <div className="space-y-3">
                        {recentProcesses.map((process) => (
                            <div
                                key={process.id}
                                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                                onClick={() => navigate(`/processos/${process.id}`)}
                            >
                                <div className="flex-1">
                                    <p className="font-medium text-gray-900 text-sm">{process.titulo}</p>
                                    <p className="text-xs text-gray-600">Nº {process.numero}</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm font-medium text-gray-900">
                                        {formatCurrency(process.valor_causa)}
                                    </p>
                                    <span className={`text-xs px-2 py-1 rounded ${process.status === 'ativo' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                        }`}>
                                        {process.status}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                    <button
                        onClick={() => navigate('/setorenergia/todos-processos')}
                        className="w-full mt-4 py-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                        Ver todos os processos →
                    </button>
                </div>

                {/* Alertas e Notificações */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Alertas & Notificações</h3>
                    <div className="space-y-3">
                        {stats.alertas_pendentes > 0 ? (
                            <>
                                <div className="flex items-start gap-3 p-3 bg-orange-50 rounded-lg">
                                    <AlertTriangle className="w-5 h-5 text-orange-600 mt-0.5" />
                                    <div>
                                        <p className="font-medium text-gray-900 text-sm">
                                            {stats.processos_sobrestados} processos sobrestados
                                        </p>
                                        <p className="text-xs text-gray-600 mt-1">
                                            Requerem análise e ação imediata
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                                    <Calendar className="w-5 h-5 text-blue-600 mt-0.5" />
                                    <div>
                                        <p className="font-medium text-gray-900 text-sm">
                                            {stats.proximas_audiencias} audiências próximas
                                        </p>
                                        <p className="text-xs text-gray-600 mt-1">
                                            Nos próximos 7 dias
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                                    <TrendingUp className="w-5 h-5 text-green-600 mt-0.5" />
                                    <div>
                                        <p className="font-medium text-gray-900 text-sm">
                                            Taxa de sucesso em alta
                                        </p>
                                        <p className="text-xs text-gray-600 mt-1">
                                            {stats.taxa_sucesso}% de decisões favoráveis
                                        </p>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div className="text-center py-8 text-gray-500">
                                <AlertTriangle className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                                <p className="text-sm">Nenhum alerta no momento</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </AdminLayout>
    )
}
