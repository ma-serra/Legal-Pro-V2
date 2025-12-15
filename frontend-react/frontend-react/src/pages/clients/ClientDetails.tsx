import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader, LoadingSpinner } from '../../components/ui/AdminComponents'
import {
    Building2, Mail, Phone, MapPin, Calendar, FileText,
    Edit, Trash2, Plus, ArrowLeft, User
} from 'lucide-react'
import api from '../../lib/api'

interface Client {
    id: number
    name: string
    legal_name: string
    document_number: string
    email: string
    phone: string
    address: string
    city: string
    state: string
    zipcode: string
    status: string
    created_at: string
    updated_at: string
}

interface Process {
    id: number
    numero: string
    titulo: string
    status: string
    created_at: string
}

export default function ClientDetails() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [client, setClient] = useState<Client | null>(null)
    const [processes, setProcesses] = useState<Process[]>([])
    const [loading, setLoading] = useState(true)
    const [activeTab, setActiveTab] = useState<'info' | 'processes' | 'documents'>('info')

    useEffect(() => {
        if (id) {
            fetchClientDetails()
            fetchClientProcesses()
        }
    }, [id])

    const fetchClientDetails = async () => {
        try {
            const response = await api.get(`/api/clientes/${id}`)
            setClient(response.data)
        } catch (error) {
            console.error('Error fetching client:', error)
        } finally {
            setLoading(false)
        }
    }

    const fetchClientProcesses = async () => {
        try {
            const response = await api.get(`/api/clientes/${id}/processos`)
            setProcesses(response.data)
        } catch (error) {
            console.error('Error fetching processes:', error)
        }
    }

    const handleDelete = async () => {
        if (!confirm('Tem certeza que deseja excluir este cliente?')) return

        try {
            await api.delete(`/api/clientes/${id}`)
            navigate('/clientes')
        } catch (error) {
            console.error('Error deleting client:', error)
            alert('Erro ao excluir cliente')
        }
    }

    if (loading) {
        return (
            <AdminLayout>
                <LoadingSpinner />
            </AdminLayout>
        )
    }

    if (!client) {
        return (
            <AdminLayout>
                <div className="text-center py-12">
                    <p className="text-gray-500">Cliente não encontrado</p>
                    <Link to="/clientes" className="text-blue-600 hover:underline mt-4 inline-block">
                        Voltar para lista
                    </Link>
                </div>
            </AdminLayout>
        )
    }

    return (
        <AdminLayout>
            <div className="mb-6">
                <button
                    onClick={() => navigate('/clientes')}
                    className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Voltar para clientes
                </button>

                <PageHeader
                    title={client.name}
                    description={client.legal_name || 'Cliente'}
                    action={
                        <div className="flex gap-2">
                            <Link
                                to={`/clientes/${id}/editar`}
                                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                            >
                                <Edit className="w-4 h-4" />
                                Editar
                            </Link>
                            <button
                                onClick={handleDelete}
                                className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                            >
                                <Trash2 className="w-4 h-4" />
                                Excluir
                            </button>
                        </div>
                    }
                />
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200 mb-6">
                <nav className="flex gap-8">
                    <button
                        onClick={() => setActiveTab('info')}
                        className={`pb-4 border-b-2 font-medium ${activeTab === 'info'
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Informações
                    </button>
                    <button
                        onClick={() => setActiveTab('processes')}
                        className={`pb-4 border-b-2 font-medium ${activeTab === 'processes'
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Processos ({processes.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('documents')}
                        className={`pb-4 border-b-2 font-medium ${activeTab === 'documents'
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Documentos
                    </button>
                </nav>
            </div>

            {/* Tab Content */}
            {activeTab === 'info' && (
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h3 className="text-sm font-medium text-gray-500 mb-4">Informações Básicas</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                                        <User className="w-4 h-4" />
                                        Nome
                                    </label>
                                    <p className="text-gray-900">{client.name}</p>
                                </div>
                                <div>
                                    <label className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                                        <Building2 className="w-4 h-4" />
                                        Razão Social
                                    </label>
                                    <p className="text-gray-900">{client.legal_name || '-'}</p>
                                </div>
                                <div>
                                    <label className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                                        <FileText className="w-4 h-4" />
                                        CPF/CNPJ
                                    </label>
                                    <p className="text-gray-900">{client.document_number}</p>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h3 className="text-sm font-medium text-gray-500 mb-4">Contato</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                                        <Mail className="w-4 h-4" />
                                        Email
                                    </label>
                                    <p className="text-gray-900">{client.email || '-'}</p>
                                </div>
                                <div>
                                    <label className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                                        <Phone className="w-4 h-4" />
                                        Telefone
                                    </label>
                                    <p className="text-gray-900">{client.phone || '-'}</p>
                                </div>
                                <div>
                                    <label className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                                        <MapPin className="w-4 h-4" />
                                        Endereço
                                    </label>
                                    <p className="text-gray-900">
                                        {client.address && `${client.address}, ${client.city} - ${client.state}`}
                                        {!client.address && '-'}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h3 className="text-sm font-medium text-gray-500 mb-4">Status</h3>
                            <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${client.status === 'active'
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-gray-100 text-gray-800'
                                }`}>
                                {client.status === 'active' ? 'Ativo' : 'Inativo'}
                            </span>
                        </div>

                        <div>
                            <h3 className="text-sm font-medium text-gray-500 mb-4">Datas</h3>
                            <div className="space-y-2">
                                <p className="text-sm text-gray-600">
                                    <Calendar className="w-4 h-4 inline mr-2" />
                                    Cadastrado em: {new Date(client.created_at).toLocaleDateString('pt-BR')}
                                </p>
                                {client.updated_at && (
                                    <p className="text-sm text-gray-600">
                                        Atualizado em: {new Date(client.updated_at).toLocaleDateString('pt-BR')}
                                    </p>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'processes' && (
                <div className="bg-white rounded-lg border border-gray-200">
                    {processes.length > 0 ? (
                        <div className="divide-y divide-gray-200">
                            {processes.map((process) => (
                                <div key={process.id} className="p-4 hover:bg-gray-50">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h4 className="font-medium text-gray-900">{process.titulo}</h4>
                                            <p className="text-sm text-gray-600">Nº {process.numero}</p>
                                        </div>
                                        <div className="flex items-center gap-4">
                                            <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                {process.status}
                                            </span>
                                            <Link
                                                to={`/processos/${process.id}`}
                                                className="text-blue-600 hover:text-blue-700"
                                            >
                                                Ver detalhes
                                            </Link>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="p-12 text-center">
                            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-gray-900 mb-2">
                                Nenhum processo encontrado
                            </h3>
                            <p className="text-gray-600 mb-4">
                                Este cliente ainda não possui processos cadastrados
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
            )}

            {activeTab === 'documents' && (
                <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                    <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Gerenciamento de Documentos
                    </h3>
                    <p className="text-gray-600">
                        Funcionalidade em desenvolvimento
                    </p>
                </div>
            )}
        </AdminLayout>
    )
}
