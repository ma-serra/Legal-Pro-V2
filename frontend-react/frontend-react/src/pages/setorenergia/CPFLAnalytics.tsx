import { useState, useEffect } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader, StatCard } from '../../components/ui/AdminComponents'
import { Zap, TrendingUp, AlertTriangle, MapPin, FileText, BarChart3 } from 'lucide-react'
import api from '../../lib/api'

interface AnalyticsData {
    total_processos: number
    processos_ativos: number
    taxa_sucesso: number
    valor_total: number
}

interface Predicao {
    processo_id: number
    numero_processo: string
    probabilidade_sucesso: number
    risco: string
    valor_estimado: number
}

interface Alerta {
    id: number
    tipo: string
    mensagem: string
    severidade: string
    created_at: string
}

export default function CPFLAnalytics() {
    const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
    const [predicoes, setPredicoes] = useState<Predicao[]>([])
    const [alertas, setAlertas] = useState<Alerta[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchAllData()
    }, [])

    const fetchAllData = async () => {
        await Promise.all([
            fetchAnalytics(),
            fetchPredicoes(),
            fetchAlertas()
        ])
        setLoading(false)
    }

    // Endpoint: GET /setorenergia/analytics
    const fetchAnalytics = async () => {
        try {
            const response = await api.get('/setorenergia/analytics')
            setAnalytics(response.data)
        } catch (error) {
            console.error('Error fetching analytics:', error)
        }
    }

    // Endpoint: GET /setorenergia/predicoes
    const fetchPredicoes = async () => {
        try {
            const response = await api.get('/setorenergia/predicoes')
            setPredicoes(response.data.slice(0, 5)) // Top 5
        } catch (error) {
            console.error('Error fetching predictions:', error)
        }
    }

    // Endpoint: GET /setorenergia/alertas
    const fetchAlertas = async () => {
        try {
            const response = await api.get('/setorenergia/alertas')
            setAlertas(response.data.slice(0, 5)) // Latest 5
        } catch (error) {
            console.error('Error fetching alerts:', error)
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
                title="CPFL/RGE - Analytics do Setor de Energia"
                description="Dashboard completo de análises e predições"
            />

            {/* Stats Grid */}
            {analytics && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <StatCard
                        title="Total de Processos"
                        value={analytics.total_processos.toString()}
                        icon={FileText}
                    />
                    <StatCard
                        title="Processos Ativos"
                        value={analytics.processos_ativos.toString()}
                        icon={Zap}
                    />
                    <StatCard
                        title="Taxa de Sucesso"
                        value={`${analytics.taxa_sucesso.toFixed(1)}%`}
                        icon={TrendingUp}
                    />
                    <StatCard
                        title="Valor Total"
                        value={`R$ ${(analytics.valor_total / 1000000).toFixed(1)}M`}
                        icon={BarChart3}
                    />
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                {/* Predições ML */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-blue-600" />
                        Predições de Machine Learning
                    </h3>

                    <div className="space-y-3">
                        {predicoes.map((pred, idx) => (
                            <div key={idx} className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="font-mono text-sm font-medium">{pred.numero_processo}</span>
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${pred.risco === 'baixo' ? 'bg-green-100 text-green-800' :
                                            pred.risco === 'medio' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-red-100 text-red-800'
                                        }`}>
                                        Risco {pred.risco.toUpperCase()}
                                    </span>
                                </div>
                                <div className="flex items-center gap-4 text-sm">
                                    <div>
                                        <span className="text-gray-600">Prob. Sucesso:</span>
                                        <span className="ml-2 font-medium">{(pred.probabilidade_sucesso * 100).toFixed(1)}%</span>
                                    </div>
                                    <div>
                                        <span className="text-gray-600">Valor Est.:</span>
                                        <span className="ml-2 font-medium">R$ {pred.valor_estimado.toLocaleString('pt-BR')}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    <button className="w-full mt-4 px-4 py-2 text-center border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                        Ver Todas as Predições
                    </button>
                </div>

                {/* Alertas */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-yellow-600" />
                        Alertas Recentes
                    </h3>

                    <div className="space-y-3">
                        {alertas.map((alerta) => (
                            <div key={alerta.id} className="p-4 border border-gray-200 rounded-lg">
                                <div className="flex items-start gap-3">
                                    <AlertTriangle className={`w-5 h-5 flex-shrink-0 ${alerta.severidade === 'alta' ? 'text-red-600' :
                                            alerta.severidade === 'media' ? 'text-yellow-600' :
                                                'text-blue-600'
                                        }`} />
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="font-medium text-sm">{alerta.tipo}</span>
                                            <span className="text-xs text-gray-500">
                                                {new Date(alerta.created_at).toLocaleDateString('pt-BR')}
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-600">{alerta.mensagem}</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    <button className="w-full mt-4 px-4 py-2 text-center border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                        Ver Todos os Alertas
                    </button>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <a
                    href="/setorenergia/mapa-risco"
                    className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow"
                >
                    <MapPin className="w-8 h-8 text-blue-600 mb-3" />
                    <h3 className="font-semibold text-gray-900 mb-2">Mapa de Risco</h3>
                    <p className="text-sm text-gray-600">Visualização geográfica de riscos por região</p>
                </a>

                <a
                    href="/setorenergia/sobrestados"
                    className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow"
                >
                    <FileText className="w-8 h-8 text-purple-600 mb-3" />
                    <h3 className="font-semibold text-gray-900 mb-2">Sobrestados</h3>
                    <p className="text-sm text-gray-600">Processos sobrestados e análises</p>
                </a>

                <a
                    href="/setorenergia/relatorios"
                    className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow"
                >
                    <BarChart3 className="w-8 h-8 text-green-600 mb-3" />
                    <h3 className="font-semibold text-gray-900 mb-2">Relatórios</h3>
                    <p className="text-sm text-gray-600">Relatórios executivos e análises detalhadas</p>
                </a>
            </div>
        </AdminLayout>
    )
}
