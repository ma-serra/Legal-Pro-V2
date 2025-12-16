import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { Shield, Plus, Edit, Trash2 } from 'lucide-react';
import api from '../../lib/api';
export default function PermissionsManagement() {
    const [roles, setRoles] = useState([]);
    const [permissions, setPermissions] = useState([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchData();
    }, []);
    const fetchData = async () => {
        await Promise.all([
            fetchRoles(),
            fetchPermissions()
        ]);
        setLoading(false);
    };
    // Endpoint: GET /admin/roles
    const fetchRoles = async () => {
        try {
            const response = await api.get('/admin/roles');
            setRoles(response.data || [
                { id: 1, name: 'Admin', description: 'Administrador do sistema', permissions: ['all'], user_count: 5 },
                { id: 2, name: 'Manager', description: 'Gerente', permissions: ['read', 'write'], user_count: 12 },
                { id: 3, name: 'Viewer', description: 'Visualizador', permissions: ['read'], user_count: 45 },
            ]);
        }
        catch (error) {
            console.error('Error fetching roles:', error);
        }
    };
    // Endpoint: GET /admin/permissoes
    const fetchPermissions = async () => {
        try {
            const response = await api.get('/admin/permissoes');
            setPermissions(response.data || [
                { id: 1, name: 'processos.read', description: 'Visualizar processos', category: 'Processos' },
                { id: 2, name: 'processos.write', description: 'Criar/editar processos', category: 'Processos' },
                { id: 3, name: 'clientes.read', description: 'Visualizar clientes', category: 'Clientes' },
                { id: 4, name: 'admin.all', description: 'Admin total', category: 'Admin' },
            ]);
        }
        catch (error) {
            console.error('Error fetching permissions:', error);
        }
    };
    // Endpoint: POST /admin/roles/novo
    const handleCreateRole = async () => {
        const name = prompt('Nome da role:');
        if (!name)
            return;
        try {
            await api.post('/admin/roles/novo', { name });
            fetchRoles();
            alert('Role criada!');
        }
        catch (error) {
            console.error('Error creating role:', error);
            alert('Erro ao criar role');
        }
    };
    // Endpoint: POST /admin/permissoes/novo
    const handleCreatePermission = async () => {
        const name = prompt('Nome da permissão:');
        if (!name)
            return;
        try {
            await api.post('/admin/permissoes/novo', { name });
            fetchPermissions();
            alert('Permissão criada!');
        }
        catch (error) {
            console.error('Error creating permission:', error);
            alert('Erro ao criar permissão');
        }
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Gerenciamento de Permiss\u00F5es", description: "Configurar roles e permiss\u00F5es do sistema" }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200", children: [_jsxs("div", { className: "p-6 border-b border-gray-200 flex items-center justify-between", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900", children: "Roles" }), _jsxs("button", { onClick: handleCreateRole, className: "flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm", children: [_jsx(Plus, { className: "w-4 h-4" }), "Nova Role"] })] }), _jsx("div", { className: "divide-y divide-gray-200", children: roles.map((role) => (_jsxs("div", { className: "p-6 hover:bg-gray-50", children: [_jsxs("div", { className: "flex items-start justify-between mb-3", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx(Shield, { className: "w-5 h-5 text-blue-600" }), _jsxs("div", { children: [_jsx("h4", { className: "font-semibold text-gray-900", children: role.name }), _jsx("p", { className: "text-sm text-gray-600", children: role.description })] })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("button", { className: "p-1 text-blue-600 hover:bg-blue-50 rounded", children: _jsx(Edit, { className: "w-4 h-4" }) }), _jsx("button", { className: "p-1 text-red-600 hover:bg-red-50 rounded", children: _jsx(Trash2, { className: "w-4 h-4" }) })] })] }), _jsx("div", { className: "flex flex-wrap gap-2 mb-3", children: role.permissions.map((perm, idx) => (_jsx("span", { className: "px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-medium", children: perm }, idx))) }), _jsxs("p", { className: "text-sm text-gray-500", children: [role.user_count, " usu\u00E1rio(s) com esta role"] })] }, role.id))) })] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200", children: [_jsxs("div", { className: "p-6 border-b border-gray-200 flex items-center justify-between", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900", children: "Permiss\u00F5es" }), _jsxs("button", { onClick: handleCreatePermission, className: "flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm", children: [_jsx(Plus, { className: "w-4 h-4" }), "Nova Permiss\u00E3o"] })] }), _jsx("div", { className: "divide-y divide-gray-200", children: permissions.map((permission) => (_jsxs("div", { className: "p-6 hover:bg-gray-50", children: [_jsxs("div", { className: "flex items-start justify-between mb-2", children: [_jsxs("div", { children: [_jsx("h4", { className: "font-mono text-sm font-semibold text-gray-900", children: permission.name }), _jsx("p", { className: "text-sm text-gray-600 mt-1", children: permission.description })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("button", { className: "p-1 text-blue-600 hover:bg-blue-50 rounded", children: _jsx(Edit, { className: "w-4 h-4" }) }), _jsx("button", { className: "p-1 text-red-600 hover:bg-red-50 rounded", children: _jsx(Trash2, { className: "w-4 h-4" }) })] })] }), _jsx("span", { className: "inline-block px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs", children: permission.category })] }, permission.id))) })] })] }), _jsxs("div", { className: "mt-6 bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Permiss\u00F5es por \u00C1rea Jur\u00EDdica" }), _jsx("p", { className: "text-sm text-gray-600 mb-4", children: "Configure quais usu\u00E1rios podem acessar cada \u00E1rea do direito" }), _jsx("a", { href: "/admin/permissoes/areas-juridicas", className: "inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: "Gerenciar \u00C1reas Jur\u00EDdicas" })] })] }));
}
