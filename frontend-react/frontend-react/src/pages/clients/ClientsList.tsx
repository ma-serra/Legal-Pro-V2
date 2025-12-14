import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { DataTable, SearchBar, PageHeader } from '../../components/ui/AdminComponents'
import { Plus, Edit, Eye, Building2 } from 'lucide-react'
import api from '../../lib/api'

interface Client {
    id: number
    name: string
    legal_name: string
    document_number: string
    email: string
    phone: string
    status: string
    created_at: string
}

export default function ClientsList() {
    const { slug } = useParams()
    const navigate = useNavigate()
    const [clients, setClients] = useState<Client[]>([])
    const [filteredClients, setFilteredClients] = useState<Client[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchClients()
    }, [slug])

    const fetchClients = async () => {
        try {
            const response = await api.get(`/api/saas/tenancy/${slug}/clients`)
            setClients(response.data)
            setFilteredClients(response.data)
        } catch (error) {
            console.error('Error fetching clients:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSearch = (query: string) => {
        const filtered = clients.filter(client =>
            client.name.toLowerCase().includes(query.toLowerCase()) ||
            client.document_number.includes(query) ||
            client.email?.toLowerCase().includes(query.toLowerCase())
        )
        setFilteredClients(filtered)
    }

    const columns = [
        {
            key: 'name',
            label: 'Nome',
            render: (value: string, row: Client) => (
                <div>
                    <div className="font-medium text-gray-900">{value}</div>
                    {row.legal_name && (
                        <div className="text-sm text-gray-500">{row.legal_name}</div>
                    )}
                </div>
            )
        },
        {
            key: 'document_number',
            label: 'CPF/CNPJ',
        },
        {
            key: 'email',
            label: 'Email',
        },
        {
            key: 'phone',
            label: 'Telefone',
        },
        {
            key: 'status',
            label: 'Status',
            render: (value: string) => (
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${value === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                    {value === 'active' ? 'Ativo' : 'Inativo'}
                </span>
            ),
        },
        {
            key: 'actions',
            label: 'Ações',
            render: (_: any, row: Client) => (
                <div className="flex items-center gap-2">
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            navigate(`/org/${slug}/clients/${row.id}`)
                        }}
                        className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        title="Ver detalhes"
                    >
                        <Eye className="w-4 h-4" />
                    </button>
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            navigate(`/org/${slug}/clients/${row.id}/edit`)
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
                title="Clientes Atendidos"
                description={`Gerenciar clientes da organização - ${filteredClients.length} total`}
                action={
                    <Link
                        to={`/org/${slug}/clients/new`}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        <Plus className="w-4 h-4" />
                        Novo Cliente
                    </Link>
                }
            />

            <div className="bg-white rounded-lg border border-gray-200">
                {/* Search Bar */}
                <div className="p-4 border-b border-gray-200">
                    <SearchBar
                        placeholder="Buscar por nome, CPF/CNPJ ou email..."
                        onSearch={handleSearch}
                    />
                </div>

                {/* Clients Table */}
                {filteredClients.length > 0 ? (
                    <>
                        <DataTable
                            columns={columns}
                            data={filteredClients}
                            onRowClick={(row) => navigate(`/org/${slug}/clients/${row.id}`)}
                        />
                        <div className="p-4 border-t border-gray-200 flex items-center justify-between">
                            <p className="text-sm text-gray-600">
                                Mostrando {filteredClients.length} de {clients.length} clientes
                            </p>
                        </div>
                    </>
                ) : (
                    <div className="p-12 text-center">
                        <Building2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">
                            Nenhum cliente encontrado
                        </h3>
                        <p className="text-gray-600 mb-4">
                            Comece adicionando seus primeiros clientes ao sistema
                        </p>
                        <Link
                            to={`/org/${slug}/clients/new`}
                            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                            <Plus className="w-4 h-4" />
                            Adicionar Primeiro Cliente
                        </Link>
                    </div>
                )}
            </div>
        </AdminLayout>
    )
}
