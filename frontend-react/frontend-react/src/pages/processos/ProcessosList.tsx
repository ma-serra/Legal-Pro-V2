import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { DataTable, SearchBar, PageHeader } from '../../components/ui/AdminComponents'
import { Plus, Eye, FileText, Calendar } from 'lucide-react'
import api from '../../lib/api'

interface Process {
    id: number
    numero_processo: string
    client_name?: string
    status: string
    area_direito: string
    valor_causa?: number
    data_distribuicao: string
    vara: string
}

export default function ProcessosList() {
    const navigate = useNavigate()
    const [processos, setProcessos] = useState<Process[]>([])
    const [filtered, setFiltered] = useState<Process[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchProcessos()
    }, [])

    const fetchProcessos = async () => {
        try {
            const response = await api.get('/api/processos')
            setProcessos(response.data)
            setFiltered(response.data)
        } catch (error) {
            console.error('Error fetching processos:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSearch = (query: string) => {
        const result = processos.filter(p =>
            p.numero_processo.includes(query) ||
            p.client_name?.toLowerCase().includes(query.toLowerCase()) ||
            p.area_direito.toLowerCase().includes(query.toLowerCase())
        )
        setFiltered(result)
    }

    const columns = [
        {
            key: 'numero_processo',
            label: 'Número do Processo',
            render: (value: string) => (
                <div className="font-mono text-sm font-medium">{value}</div>
            )
        },
        {
            key: 'client_name',
            label: 'Cliente',
        },
        {
            key: 'area_direito',
            label: 'Área',
            render: (value: string) => (
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                    {value}
                </span>
            )
        },
        {
            key: 'status',
            label: 'Status',
            render: (value: string) => (
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${value === 'ativo' ? 'bg-green-100 text-green-800' :
                        value === 'arquivado' ? 'bg-gray-100 text-gray-800' :
                            'bg-yellow-100 text-yellow-800'
                    }`}>
                    {value || 'Em andamento'}
                </span>
            )
        },
        {
            key: 'data_distribuicao',
            label: 'Data Distribuição',
            render: (value: string) => value ? new Date(value).toLocaleDateString('pt-BR') : '-'
        },
        {
            key: 'actions',
            label: 'Ações',
            render: (_: any, row: Process) => (
                <button
                    onClick={(e) => {
                        e.stopPropagation()
                        navigate(`/processos/${row.id}`)
                    }}
                    className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                >
                    <Eye className="w-4 h-4" />
                </button>
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
                title="Processos Jurídicos"
                description={`Gerenciar todos os processos - ${filtered.length} total`}
                action={
                    <Link
                        to="/processos/novo"
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        <Plus className="w-4 h-4" />
                        Novo Processo
                    </Link>
                }
            />

            <div className="bg-white rounded-lg border border-gray-200">
                <div className="p-4 border-b border-gray-200">
                    <SearchBar
                        placeholder="Buscar por número, cliente ou área..."
                        onSearch={handleSearch}
                    />
                </div>

                {filtered.length > 0 ? (
                    <>
                        <DataTable
                            columns={columns}
                            data={filtered}
                            onRowClick={(row) => navigate(`/processos/${row.id}`)}
                        />
                        <div className="p-4 border-t border-gray-200 flex items-center justify-between">
                            <p className="text-sm text-gray-600">
                                Mostrando {filtered.length} de {processos.length} processos
                            </p>
                        </div>
                    </>
                ) : (
                    <div className="p-12 text-center">
                        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">
                            Nenhum processo encontrado
                        </h3>
                        <p className="text-gray-600 mb-4">
                            Adicione processos para começar a gerenciar seus casos
                        </p>
                        <Link
                            to="/processos/novo"
                            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                            <Plus className="w-4 h-4" />
                            Adicionar Processo
                        </Link>
                    </div>
                )}
            </div>
        </AdminLayout>
    )
}
