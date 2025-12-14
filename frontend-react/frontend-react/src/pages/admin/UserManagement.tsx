import { useState, useEffect } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { DataTable, SearchBar, PageHeader } from '../../components/ui/AdminComponents'
import { Plus, Edit, Trash2, Shield, Users } from 'lucide-react'
import api from '../../lib/api'

interface User {
    id: number
    email: string
    name?: string
    role?: string
    tenancy_id?: number
    tenancy_name?: string
    is_active: boolean
    created_at: string
}

export default function UserManagement() {
    const [users, setUsers] = useState<User[]>([])
    const [filtered, setFiltered] = useState<User[]>([])
    const [loading, setLoading] = useState(true)
    const [showNewUserModal, setShowNewUserModal] = useState(false)

    useEffect(() => {
        fetchUsers()
    }, [])

    // Endpoint: GET /admin/usuarios
    const fetchUsers = async () => {
        try {
            const response = await api.get('/admin/usuarios')
            setUsers(response.data)
            setFiltered(response.data)
        } catch (error) {
            console.error('Error fetching users:', error)
        } finally {
            setLoading(false)
        }
    }

    // Endpoint: POST /admin/usuarios/novo
    const handleCreateUser = async (userData: any) => {
        try {
            await api.post('/admin/usuarios/novo', userData)
            fetchUsers()
            setShowNewUserModal(false)
            alert('Usuário criado com sucesso!')
        } catch (error) {
            console.error('Error creating user:', error)
            alert('Erro ao criar usuário')
        }
    }

    // Endpoint: POST /admin/usuarios/:id/editar
    const handleEditUser = async (userId: number, userData: any) => {
        try {
            await api.post(`/admin/usuarios/${userId}/editar`, userData)
            fetchUsers()
            alert('Usuário atualizado!')
        } catch (error) {
            console.error('Error editing user:', error)
            alert('Erro ao editar usuário')
        }
    }

    // Endpoint: POST /admin/usuarios/:id/excluir
    const handleDeleteUser = async (userId: number) => {
        if (!confirm('Tem certeza que deseja excluir este usuário?')) return

        try {
            await api.post(`/admin/usuarios/${userId}/excluir`)
            fetchUsers()
            alert('Usuário excluído!')
        } catch (error) {
            console.error('Error deleting user:', error)
            alert('Erro ao excluir usuário')
        }
    }

    const handleSearch = (query: string) => {
        const result = users.filter(u =>
            u.email.toLowerCase().includes(query.toLowerCase()) ||
            u.name?.toLowerCase().includes(query.toLowerCase()) ||
            u.tenancy_name?.toLowerCase().includes(query.toLowerCase())
        )
        setFiltered(result)
    }

    const columns = [
        {
            key: 'name',
            label: 'Nome',
            render: (value: string, row: User) => (
                <div>
                    <div className="font-medium text-gray-900">{value || row.email}</div>
                    <div className="text-sm text-gray-500">{row.email}</div>
                </div>
            )
        },
        {
            key: 'tenancy_name',
            label: 'Organização',
            render: (value: string) => value || '-'
        },
        {
            key: 'role',
            label: 'Função',
            render: (value: string) => (
                <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                    {value || 'member'}
                </span>
            )
        },
        {
            key: 'is_active',
            label: 'Status',
            render: (value: boolean) => (
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${value ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                    {value ? 'Ativo' : 'Inativo'}
                </span>
            )
        },
        {
            key: 'created_at',
            label: 'Criado em',
            render: (value: string) => new Date(value).toLocaleDateString('pt-BR')
        },
        {
            key: 'actions',
            label: 'Ações',
            render: (_: any, row: User) => (
                <div className="flex items-center gap-2">
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            // Open edit modal
                        }}
                        className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        title="Editar"
                    >
                        <Edit className="w-4 h-4" />
                    </button>
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteUser(row.id)
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
                title="Gerenciamento de Usuários"
                description={`Total de ${filtered.length} usuários`}
                action={
                    <button
                        onClick={() => setShowNewUserModal(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        <Plus className="w-4 h-4" />
                        Novo Usuário
                    </button>
                }
            />

            <div className="bg-white rounded-lg border border-gray-200">
                <div className="p-4 border-b border-gray-200">
                    <SearchBar
                        placeholder="Buscar por nome, email ou organização..."
                        onSearch={handleSearch}
                    />
                </div>

                {filtered.length > 0 ? (
                    <>
                        <DataTable
                            columns={columns}
                            data={filtered}
                            onRowClick={(row) => console.log('View user:', row.id)}
                        />
                        <div className="p-4 border-t border-gray-200 flex items-center justify-between">
                            <p className="text-sm text-gray-600">
                                Mostrando {filtered.length} de {users.length} usuários
                            </p>
                        </div>
                    </>
                ) : (
                    <div className="p-12 text-center">
                        <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">
                            Nenhum usuário encontrado
                        </h3>
                        <p className="text-gray-600 mb-4">
                            Crie um novo usuário para começar
                        </p>
                        <button
                            onClick={() => setShowNewUserModal(true)}
                            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                            <Plus className="w-4 h-4" />
                            Criar Usuário
                        </button>
                    </div>
                )}
            </div>

            {/* New User Modal - simplified for now */}
            {showNewUserModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full">
                        <h3 className="text-lg font-semibold mb-4">Novo Usuário</h3>
                        <form onSubmit={(e) => {
                            e.preventDefault()
                            const formData = new FormData(e.currentTarget)
                            handleCreateUser({
                                email: formData.get('email'),
                                name: formData.get('name'),
                                password: formData.get('password'),
                                role: formData.get('role')
                            })
                        }}>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Email *
                                    </label>
                                    <input
                                        type="email"
                                        name="email"
                                        required
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Nome
                                    </label>
                                    <input
                                        type="text"
                                        name="name"
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Senha *
                                    </label>
                                    <input
                                        type="password"
                                        name="password"
                                        required
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Função
                                    </label>
                                    <select
                                        name="role"
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                    >
                                        <option value="member">Member</option>
                                        <option value="admin">Admin</option>
                                        <option value="owner">Owner</option>
                                    </select>
                                </div>
                            </div>
                            <div className="flex gap-3 mt-6">
                                <button
                                    type="submit"
                                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                >
                                    Criar
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowNewUserModal(false)}
                                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                >
                                    Cancelar
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </AdminLayout>
    )
}
