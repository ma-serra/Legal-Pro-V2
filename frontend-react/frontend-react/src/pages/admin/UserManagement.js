import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { DataTable, SearchBar, PageHeader } from '../../components/ui/AdminComponents';
import { Plus, Edit, Trash2, Users } from 'lucide-react';
import api from '../../lib/api';
export default function UserManagement() {
    const [users, setUsers] = useState([]);
    const [filtered, setFiltered] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showNewUserModal, setShowNewUserModal] = useState(false);
    useEffect(() => {
        fetchUsers();
    }, []);
    // Endpoint: GET /admin/usuarios
    const fetchUsers = async () => {
        try {
            const response = await api.get('/admin/usuarios');
            setUsers(response.data);
            setFiltered(response.data);
        }
        catch (error) {
            console.error('Error fetching users:', error);
        }
        finally {
            setLoading(false);
        }
    };
    // Endpoint: POST /admin/usuarios/novo
    const handleCreateUser = async (userData) => {
        try {
            await api.post('/admin/usuarios/novo', userData);
            fetchUsers();
            setShowNewUserModal(false);
            alert('Usuário criado com sucesso!');
        }
        catch (error) {
            console.error('Error creating user:', error);
            alert('Erro ao criar usuário');
        }
    };
    // Endpoint: POST /admin/usuarios/:id/editar
    const handleEditUser = async (userId, userData) => {
        try {
            await api.post(`/admin/usuarios/${userId}/editar`, userData);
            fetchUsers();
            alert('Usuário atualizado!');
        }
        catch (error) {
            console.error('Error editing user:', error);
            alert('Erro ao editar usuário');
        }
    };
    // Endpoint: POST /admin/usuarios/:id/excluir
    const handleDeleteUser = async (userId) => {
        if (!confirm('Tem certeza que deseja excluir este usuário?'))
            return;
        try {
            await api.post(`/admin/usuarios/${userId}/excluir`);
            fetchUsers();
            alert('Usuário excluído!');
        }
        catch (error) {
            console.error('Error deleting user:', error);
            alert('Erro ao excluir usuário');
        }
    };
    const handleSearch = (query) => {
        const result = users.filter(u => u.email.toLowerCase().includes(query.toLowerCase()) ||
            u.name?.toLowerCase().includes(query.toLowerCase()) ||
            u.tenancy_name?.toLowerCase().includes(query.toLowerCase()));
        setFiltered(result);
    };
    const columns = [
        {
            key: 'name',
            label: 'Nome',
            render: (value, row) => (_jsxs("div", { children: [_jsx("div", { className: "font-medium text-gray-900", children: value || row.email }), _jsx("div", { className: "text-sm text-gray-500", children: row.email })] }))
        },
        {
            key: 'tenancy_name',
            label: 'Organização',
            render: (value) => value || '-'
        },
        {
            key: 'role',
            label: 'Função',
            render: (value) => (_jsx("span", { className: "px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium", children: value || 'member' }))
        },
        {
            key: 'is_active',
            label: 'Status',
            render: (value) => (_jsx("span", { className: `px-2 py-1 rounded-full text-xs font-medium ${value ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`, children: value ? 'Ativo' : 'Inativo' }))
        },
        {
            key: 'created_at',
            label: 'Criado em',
            render: (value) => new Date(value).toLocaleDateString('pt-BR')
        },
        {
            key: 'actions',
            label: 'Ações',
            render: (_, row) => (_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("button", { onClick: (e) => {
                            e.stopPropagation();
                            // Open edit modal
                        }, className: "p-1 text-blue-600 hover:bg-blue-50 rounded", title: "Editar", children: _jsx(Edit, { className: "w-4 h-4" }) }), _jsx("button", { onClick: (e) => {
                            e.stopPropagation();
                            handleDeleteUser(row.id);
                        }, className: "p-1 text-red-600 hover:bg-red-50 rounded", title: "Excluir", children: _jsx(Trash2, { className: "w-4 h-4" }) })] }))
        },
    ];
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Gerenciamento de Usu\u00E1rios", description: `Total de ${filtered.length} usuários`, action: _jsxs("button", { onClick: () => setShowNewUserModal(true), className: "flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: [_jsx(Plus, { className: "w-4 h-4" }), "Novo Usu\u00E1rio"] }) }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200", children: [_jsx("div", { className: "p-4 border-b border-gray-200", children: _jsx(SearchBar, { placeholder: "Buscar por nome, email ou organiza\u00E7\u00E3o...", onSearch: handleSearch }) }), filtered.length > 0 ? (_jsxs(_Fragment, { children: [_jsx(DataTable, { columns: columns, data: filtered, onRowClick: (row) => console.log('View user:', row.id) }), _jsx("div", { className: "p-4 border-t border-gray-200 flex items-center justify-between", children: _jsxs("p", { className: "text-sm text-gray-600", children: ["Mostrando ", filtered.length, " de ", users.length, " usu\u00E1rios"] }) })] })) : (_jsxs("div", { className: "p-12 text-center", children: [_jsx(Users, { className: "w-12 h-12 text-gray-400 mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-medium text-gray-900 mb-2", children: "Nenhum usu\u00E1rio encontrado" }), _jsx("p", { className: "text-gray-600 mb-4", children: "Crie um novo usu\u00E1rio para come\u00E7ar" }), _jsxs("button", { onClick: () => setShowNewUserModal(true), className: "inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: [_jsx(Plus, { className: "w-4 h-4" }), "Criar Usu\u00E1rio"] })] }))] }), showNewUserModal && (_jsx("div", { className: "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50", children: _jsxs("div", { className: "bg-white rounded-lg p-6 max-w-md w-full", children: [_jsx("h3", { className: "text-lg font-semibold mb-4", children: "Novo Usu\u00E1rio" }), _jsxs("form", { onSubmit: (e) => {
                                e.preventDefault();
                                const formData = new FormData(e.currentTarget);
                                handleCreateUser({
                                    email: formData.get('email'),
                                    name: formData.get('name'),
                                    password: formData.get('password'),
                                    role: formData.get('role')
                                });
                            }, children: [_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Email *" }), _jsx("input", { type: "email", name: "email", required: true, className: "w-full px-4 py-2 border border-gray-300 rounded-lg" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Nome" }), _jsx("input", { type: "text", name: "name", className: "w-full px-4 py-2 border border-gray-300 rounded-lg" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Senha *" }), _jsx("input", { type: "password", name: "password", required: true, className: "w-full px-4 py-2 border border-gray-300 rounded-lg" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Fun\u00E7\u00E3o" }), _jsxs("select", { name: "role", className: "w-full px-4 py-2 border border-gray-300 rounded-lg", children: [_jsx("option", { value: "member", children: "Member" }), _jsx("option", { value: "admin", children: "Admin" }), _jsx("option", { value: "owner", children: "Owner" })] })] })] }), _jsxs("div", { className: "flex gap-3 mt-6", children: [_jsx("button", { type: "submit", className: "flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: "Criar" }), _jsx("button", { type: "button", onClick: () => setShowNewUserModal(false), className: "flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Cancelar" })] })] })] }) }))] }));
}
