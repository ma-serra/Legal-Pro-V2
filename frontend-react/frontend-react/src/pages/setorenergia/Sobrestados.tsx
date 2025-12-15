import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader, DataTable } from '../../components/ui/AdminComponents'
import { AlertTriangle, Eye, FileText, Clock, TrendingUp } from 'lucide-react'
import api from '../../lib/api'

interface ProcessoSobrestado {
    id: number
    numero: string
    titulo: string
    motivo_sobrestamento: string
    data_sobrestamento: string
    prazo_estimado: string
    valor_causa: number
    comarca: string
    acao_recomendada: string
}

export default function Sobrestados() {
    const navigate = useNavigate()
    const [processos, setProcessos] = useState<ProcessoSobrestado[]>([])
    const [loading, setLoading] = useState(true)
    const [stats, setStats] = useState({
        total: 0,
        criticos: 0,
        valor_total: 0
    })

    useEffect(() => {
        fetchProcessos()
    }, [])

    const fetchProcessos = async () => {
        try {
            const response = await api.get('/setorenergia/sobrestados')
            setProcessos(response.data)

            //Calcular estatísticas
            const total = response.data.length
            const criticos = response.data.filter((p: ProcessoSobrestado) =>
                p.acao_recomendada === 'urgente'
            ).length
            const valor_total = response.data.reduce((sum: number, p: ProcessoSobrestado) =>
                sum + p.valor_causa, 0
            )

            setStats({ total, criticos, valor_total })
        } catch (error) {
            console.error('Error fetching sobrestados:', error)
        } finally {
            setLoading(false)
        }
    }

    const columns = [
        {
            key: 'numero',
            label: 'Número do Processo',
            render: (value: string, row: ProcessoSobrestado) => (
                <div>
                    <p className="font-medium text-gray-900">{value}</p>
                    <p className="text-sm text-gray-600">{row.titulo}</p>
                </div>
            )
        },
        {
            key: 'motivo_sobrestamento',
            label: 'Motivo',
            render: (value: string) => (
                <span className="text-sm text-gray-700">{value}</span>
            )
        },
        {
            key: 'data_sobrestamento',
            label: 'Data',
            render: (value: string) => (
                <span className="text-sm text-gray-600">
                    {new Date(value).toLocaleDateString('pt-BR')}
                </span>
            )
        },
        {
            key: 'prazo_estimado',
            label: 'Prazo Estimado',
            render: (value: string) => (
                <span className="text-sm text-gray-600">{value}</span>
            )
        },
        {
            key: 'acao_recomendada',
            label: 'Ação',
            render: (value: string) => (
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${value === 'urgente'
                        ? 'bg-red-100 text-red-800'
                        : value === 'monitorar'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                    }`}>
                    {value}
                </span>
            )
        },
        {
            key: 'actions',
            label: 'Ações',
            render: (_: any, row: ProcessoSobrestado) => (
                <button
                    onClick={() => navigate(`/processos/${row.id}`)}
                    className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                    title="Ver detalhes"
                >
                    <Eye className="w-4 h-4" />
                </button>
            )
        }
    ]

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
                title="Processos Sobrestados"
                description="Listagem e análise de processos com sobrestamento"
            />

            {/* Estatísticas */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="bg-white p-6 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600 mb-1">Total Sobrestados</p>
                            <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
                        </div>
                        <AlertTriangle className="w-10 h-10 text-orange-600" />
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600 mb-1">Críticos</p>
                            <p className="text-3xl font-bold text-red-600">{stats.criticos}</p>
                        </div>
                        <FileText className="w-10 h-10 text-red-600" />
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600 mb-1">Valor Total</p>
                            <p className="text-2xl font-bold text-gray-900">
                                {new Intl.NumberFormat('pt-BR', {
                                    style: 'currency',
                                    currency: 'BRL',
                                    notation: 'compact'
                                }).format(stats.valor_total)}
                            </p>
                        </div>
                        <TrendingUp className="w-10 h-10 text-green-600" />
                    </div>
                </div>
            </div>

            {/* Tabela de Processos */}
            <div className="bg-white rounded-lg border border-gray-200">
                {processos.length > 0 ? (
                    <>
                        <DataTable
                            columns={columns}
                            data={processos}
                            onRowClick={(row) => navigate(`/processos/${row.id}`)}
                        />
                        <div className="p-4 border-t border-gray-200">
                            <p className="text-sm text-gray-600">
                                Mostrando {processos.length} processos sobrestados
                            </p>
                        </div>
                    </>
                ) : (
                    <div className="p-12 text-center">
                        <Clock className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">
                            Nenhum processo sobrestado
                        </h3>
                        <p className="text-gray-600">
                            Todos os processos estão em andamento normal
                        </p>
                    </div>
                )}
            </div>

            {/* Alertas */}
            {stats.criticos > 0 && (
                <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                        <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
                        <div>
                            <h4 className="font-semibold text-red-900 mb-1">
                                Atenção: {stats.criticos} processos críticos
                            </h4>
                            <p className="text-sm text-red-700">
                                Estes processos requerem ação urgente devido ao tempo de sobrestamento prolongado.
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </AdminLayout>
    )
}
