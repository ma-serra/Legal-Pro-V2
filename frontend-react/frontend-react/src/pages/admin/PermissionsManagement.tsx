import { useState, useEffect } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { Shield, Plus, Edit, Trash2 } from 'lucide-react'
import api from '../../lib/api'

interface Role {
    id: number
    name: string
    description: string
    permissions: string[]
    user_count: number
}

interface Permission {
    id: number
    name: string
    description: string
    category: string
}

export default function PermissionsManagement() {
    const [roles, setRoles] = useState<Role[]>([])
    const [permissions, setPermissions] = useState<Permission[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        await Promise.all([
            fetchRoles(),
            fetchPermissions()
        ])
        setLoading(false)
    }

    // Endpoint: GET /admin/roles
    const fetchRoles = async () => {
        try {
            const response = await api.get('/admin/roles')
            setRoles(response.data || [
                { id: 1, name: 'Admin', description: 'Administrador do sistema', permissions: ['all'], user_count: 5 },
                { id: 2, name: 'Manager', description: 'Gerente', permissions: ['read', 'write'], user_count: 12 },
                { id: 3, name: 'Viewer', description: 'Visualizador', permissions: ['read'], user_count: 45 },
            ])
        } catch (error) {
            console.error('Error fetching roles:', error)
        }
    }

    // Endpoint: GET /admin/permissoes
    const fetchPermissions = async () => {
        try {
            const response = await api.get('/admin/permissoes')
            setPermissions(response.data || [
                { id: 1, name: 'processos.read', description: 'Visualizar processos', category: 'Processos' },
                { id: 2, name: 'processos.write', description: 'Criar/editar processos', category: 'Processos' },
                { id: 3, name: 'clientes.read', description: 'Visualizar clientes', category: 'Clientes' },
                { id: 4, name: 'admin.all', description: 'Admin total', category: 'Admin' },
            ])
        } catch (error) {
            console.error('Error fetching permissions:', error)
        }
    }

    // Endpoint: POST /admin/roles/novo
    const handleCreateRole = async () => {
        const name = prompt('Nome da role:')
        if (!name) return

        try {
            await api.post('/admin/roles/novo', { name })
            fetchRoles()
            alert('Role criada!')
        } catch (error) {
            console.error('Error creating role:', error)
            alert('Erro ao criar role')
        }
    }

    // Endpoint: POST /admin/permissoes/novo
    const handleCreatePermission = async () => {
        const name = prompt('Nome da permissão:')
        if (!name) return

        try {
            await api.post('/admin/permissoes/novo', { name })
            fetchPermissions()
            alert('Permissão criada!')
        } catch (error) {
            console.error('Error creating permission:', error)
            alert('Erro ao criar permissão')
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
                title="Gerenciamento de Permissões"
                description="Configurar roles e permissões do sistema"
            />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Roles */}
                <div className="bg-white rounded-lg border border-gray-200">
                    <div className="p-6 border-b border-gray-200 flex items-center justify-between">
                        <h3 className="text-lg font-semibold text-gray-900">Roles</h3>
                        <button
                            onClick={handleCreateRole}
                            className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                        >
                            <Plus className="w-4 h-4" />
                            Nova Role
                        </button>
                    </div>

                    <div className="divide-y divide-gray-200">
                        {roles.map((role) => (
                            <div key={role.id} className="p-6 hover:bg-gray-50">
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex items-center gap-3">
                                        <Shield className="w-5 h-5 text-blue-600" />
                                        <div>
                                            <h4 className="font-semibold text-gray-900">{role.name}</h4>
                                            <p className="text-sm text-gray-600">{role.description}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button className="p-1 text-blue-600 hover:bg-blue-50 rounded">
                                            <Edit className="w-4 h-4" />
                                        </button>
                                        <button className="p-1 text-red-600 hover:bg-red-50 rounded">
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>

                                <div className="flex flex-wrap gap-2 mb-3">
                                    {role.permissions.map((perm, idx) => (
                                        <span
                                            key={idx}
                                            className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-medium"
                                        >
                                            {perm}
                                        </span>
                                    ))}
                                </div>

                                <p className="text-sm text-gray-500">
                                    {role.user_count} usuário(s) com esta role
                                </p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Permissions */}
                <div className="bg-white rounded-lg border border-gray-200">
                    <div className="p-6 border-b border-gray-200 flex items-center justify-between">
                        <h3 className="text-lg font-semibold text-gray-900">Permissões</h3>
                        <button
                            onClick={handleCreatePermission}
                            className="flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                        >
                            <Plus className="w-4 h-4" />
                            Nova Permissão
                        </button>
                    </div>

                    <div className="divide-y divide-gray-200">
                        {permissions.map((permission) => (
                            <div key={permission.id} className="p-6 hover:bg-gray-50">
                                <div className="flex items-start justify-between mb-2">
                                    <div>
                                        <h4 className="font-mono text-sm font-semibold text-gray-900">
                                            {permission.name}
                                        </h4>
                                        <p className="text-sm text-gray-600 mt-1">{permission.description}</p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button className="p-1 text-blue-600 hover:bg-blue-50 rounded">
                                            <Edit className="w-4 h-4" />
                                        </button>
                                        <button className="p-1 text-red-600 hover:bg-red-50 rounded">
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                                <span className="inline-block px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                                    {permission.category}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Áreas Jurídicas Permissions */}
            <div className="mt-6 bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Permissões por Área Jurídica
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                    Configure quais usuários podem acessar cada área do direito
                </p>
                <a
                    href="/admin/permissoes/areas-juridicas"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                    Gerenciar Áreas Jurídicas
                </a>
            </div>
        </AdminLayout>
    )
}
