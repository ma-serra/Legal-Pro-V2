import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { DataTable, SearchBar, PageHeader } from '../../components/ui/AdminComponents'
import { Eye, Trash2, Download, History } from 'lucide-react'
import api from '../../lib/api'

interface HistoricoItem {
    id: number
    tipo_analise: string
    num_agentes: number
    texto_preview: string
    status: string
    created_at: string
    tempo_execucao?: number
}

export default function MultiAgenteHistorico() {
    const navigate = useNavigate()
    const [historico, setHistorico] = useState<HistoricoItem[]>([])
    const [filtered, setFiltered] = useState<HistoricoItem[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchHistorico()
    }, [])

    // Endpoint: GET /historico-analises-multiagente
    const fetchHistorico = async () => {
        try {
            const response = await api.get('/historico-analises-multiagente')
            setHistorico(response.data)
            setFiltered(response.data)
        } catch (error) {
            console.error('Error fetching history:', error)
        } finally {
            setLoading(false)
        }
    }

    // Endpoint: GET /analise-multiagente/:analise_id/detalhes
    const handleViewDetails = (id: number) => {
        navigate(`/multi-agente/analise/${id}`)
    }

    // Endpoint: DELETE /api/analise-multiagente/:analise_id
    const handleDelete = async (id: number) => {
        if (!confirm('Deseja excluir esta análise?')) return

        try {
            await api.delete(`/api/analise-multiagente/${id}`)
            fetchHistorico()
            alert('Análise excluída!')
        } catch (error) {
            console.error('Error deleting:', error)
            alert('Erro ao excluir análise')
        }
    }

    // Endpoint: POST /analise-multiagente/:analise_id/exportar-docx
    const handleExport = async (id: number) => {
        try {
            const response = await api.post(`/analise-multiagente/${id}/exportar-docx`, {}, {
                responseType: 'blob'
            })

            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `analise-multiagente-${id}.docx`)
            document.body.appendChild(link)
            link.click()
            link.remove()
        } catch (error) {
            console.error('Error exporting:', error)
            alert('Erro ao exportar análise')
        }
    }

    const handleSearch = (query: string) => {
        const result = historico.filter(item =>
            item.tipo_analise.toLowerCase().includes(query.toLowerCase()) ||
            item.texto_preview.toLowerCase().includes(query.toLowerCase())
        )
        setFiltered(result)
    }

    const columns = [
        {
            key: 'tipo_analise',
            label: 'Tipo',
            render: (value: string) => (
                <span className="font-medium text-gray-900">{value}</span>
            )
        },
        {
            key: 'num_agentes',
            label: 'Agentes',
            render: (value: number) => (
                <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                    {value} agentes
                </span>
            )
        },
        {
            key: 'texto_preview',
            label: 'Texto',
            render: (value: string) => (
                <span className="text-sm text-gray-600 truncate max-w-xs block">
                    {value.substring(0, 80)}...
                </span>
            )
        },
        {
            key: 'status',
            label: 'Status',
            render: (value: string) => (
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${value === 'sucesso' ? 'bg-green-100 text-green-800' :
                        value === 'erro' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                    }`}>
                    {value}
                </span>
            )
        },
        {
            key: 'created_at',
            label: 'Data',
            render: (value: string) => new Date(value).toLocaleString('pt-BR')
        },
        {
            key: 'actions',
            label: 'Ações',
            render: (_: any, row: HistoricoItem) => (
                <div className="flex items-center gap-2">
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            handleViewDetails(row.id)
                        }}
                        className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        title="Ver detalhes"
                    >
                        <Eye className="w-4 h-4" />
                    </button>
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            handleExport(row.id)
                        }}
                        className="p-1 text-green-600 hover:bg-green-50 rounded"
                        title="Exportar"
                    >
                        <Download className="w-4 h-4" />
                    </button>
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            handleDelete(row.id)
                        }}
                        className="p-1 text-red-600 hover:bg-red-50 rounded"
                        title="Excluir"
                    >
                        <Trash2 className="w-4 h-4" />
                    </button>
                </div>
            )
        },
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
                title="Histórico Multi-Agente"
                description={`${filtered.length} execuções registradas`}
            />

            <div className="bg-white rounded-lg border border-gray-200">
                <div className="p-4 border-b border-gray-200">
                    <SearchBar
                        placeholder="Buscar por tipo ou texto..."
                        onSearch={handleSearch}
                    />
                </div>

                {filtered.length > 0 ? (
                    <>
                        <DataTable
                            columns={columns}
                            data={filtered}
                            onRowClick={(row) => handleViewDetails(row.id)}
                        />
                        <div className="p-4 border-t border-gray-200 flex items-center justify-between">
                            <p className="text-sm text-gray-600">
                                Mostrando {filtered.length} de {historico.length} análises
                            </p>
                        </div>
                    </>
                ) : (
                    <div className="p-12 text-center">
                        <History className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">
                            Nenhuma análise encontrada
                        </h3>
                        <p className="text-gray-600">
                            Execute análises multi-agente para vê-las aqui
                        </p>
                    </div>
                )}
            </div>
        </AdminLayout>
    )
}
