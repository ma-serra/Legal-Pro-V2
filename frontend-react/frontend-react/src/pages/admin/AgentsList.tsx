import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { DataTable, SearchBar, PageHeader } from '../../components/ui/AdminComponents'
import { Plus, Edit, Eye } from 'lucide-react'
import api from '../../lib/api'

interface Agent {
    id: number
    nome: string
    categoria: string
    classe: string
    ativo: boolean
    nivel_especializacao: string
}

export default function AgentsList() {
    const navigate = useNavigate()
    const [agents, setAgents] = useState<Agent[]>([])
    const [filteredAgents, setFilteredAgents] = useState<Agent[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchAgents()
    }, [])

    const fetchAgents = async () => {
        try {
            const response = await api.get('/api/admin/api/admin/agentes-lista')
            setAgents(response.data)
            setFilteredAgents(response.data)
        } catch (error) {
            console.error('Error fetching agents:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSearch = (query: string) => {
        const filtered = agents.filter(agent =>
            agent.nome.toLowerCase().includes(query.toLowerCase()) ||
            agent.categoria.toLowerCase().includes(query.toLowerCase())
        )
        setFilteredAgents(filtered)
    }

    const columns = [
        {
            key: 'id',
            label: 'ID',
        },
        {
            key: 'nome',
            label: 'Nome',
        },
        {
            key: 'categoria',
            label: 'Categoria',
        },
        {
            key: 'nivel_especializacao',
            label: 'Nível',
        },
        {
            key: 'ativo',
            label: 'Status',
            render: (value: boolean) => (
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${value ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                    {value ? 'Ativo' : 'Inativo'}
                </span>
            ),
        },
        {
            key: 'actions',
            label: 'Ações',
            render: (_: any, row: Agent) => (
                <div className="flex items-center gap-2">
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            navigate(`/admin/agents/${row.id}`)
                        }}
                        className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        title="Ver detalhes"
                    >
                        <Eye className="w-4 h-4" />
                    </button>
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            navigate(`/admin/agents/${row.id}/edit`)
                        }}
                        className="p-1 text-gray-600 hover:bg-gray-50 rounded"
                        title="Editar"
                    >
                        <Edit className="w-4 h-4" />
                    </button>
                </div>
            ),
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
                title="Agentes Jurídicos"
                description={`Gerenciar todos os ${agents.length} agentes de IA do sistema`}
                action={
                    <button
                        onClick={() => navigate('/admin/agents/new')}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        <Plus className="w-4 h-4" />
                        Novo Agente
                    </button>
                }
            />

            <div className="bg-white rounded-lg border border-gray-200">
                {/* Search Bar */}
                <div className="p-4 border-b border-gray-200">
                    <SearchBar
                        placeholder="Buscar por nome ou categoria..."
                        onSearch={handleSearch}
                    />
                </div>

                {/* Table */}
                <DataTable
                    columns={columns}
                    data={filteredAgents}
                    onRowClick={(row) => navigate(`/admin/agents/${row.id}`)}
                />

                {/* Pagination */}
                <div className="p-4 border-t border-gray-200 flex items-center justify-between">
                    <p className="text-sm text-gray-600">
                        Mostrando {filteredAgents.length} de {agents.length} agentes
                    </p>
                </div>
            </div>
        </AdminLayout>
    )
}
