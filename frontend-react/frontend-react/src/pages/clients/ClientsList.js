import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { DataTable, SearchBar, PageHeader } from '../../components/ui/AdminComponents';
import { Plus, Edit, Eye, Building2 } from 'lucide-react';
import api from '../../lib/api';
export default function ClientsList() {
    const { slug } = useParams();
    const navigate = useNavigate();
    const [clients, setClients] = useState([]);
    const [filteredClients, setFilteredClients] = useState([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchClients();
    }, [slug]);
    const fetchClients = async () => {
        try {
            const response = await api.get(`/api/saas/tenancy/${slug}/clients`);
            setClients(response.data);
            setFilteredClients(response.data);
        }
        catch (error) {
            console.error('Error fetching clients:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const handleSearch = (query) => {
        const filtered = clients.filter(client => client.name.toLowerCase().includes(query.toLowerCase()) ||
            client.document_number.includes(query) ||
            client.email?.toLowerCase().includes(query.toLowerCase()));
        setFilteredClients(filtered);
    };
    const columns = [
        {
            key: 'name',
            label: 'Nome',
            render: (value, row) => (_jsxs("div", { children: [_jsx("div", { className: "font-medium text-gray-900", children: value }), row.legal_name && (_jsx("div", { className: "text-sm text-gray-500", children: row.legal_name }))] }))
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
            render: (value) => (_jsx("span", { className: `px-2 py-1 rounded-full text-xs font-medium ${value === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`, children: value === 'active' ? 'Ativo' : 'Inativo' })),
        },
        {
            key: 'actions',
            label: 'Ações',
            render: (_, row) => (_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("button", { onClick: (e) => {
                            e.stopPropagation();
                            navigate(`/org/${slug}/clients/${row.id}`);
                        }, className: "p-1 text-blue-600 hover:bg-blue-50 rounded", title: "Ver detalhes", children: _jsx(Eye, { className: "w-4 h-4" }) }), _jsx("button", { onClick: (e) => {
                            e.stopPropagation();
                            navigate(`/org/${slug}/clients/${row.id}/edit`);
                        }, className: "p-1 text-gray-600 hover:bg-gray-50 rounded", title: "Editar", children: _jsx(Edit, { className: "w-4 h-4" }) })] })),
        },
    ];
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Clientes Atendidos", description: `Gerenciar clientes da organização - ${filteredClients.length} total`, action: _jsxs(Link, { to: `/org/${slug}/clients/new`, className: "flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: [_jsx(Plus, { className: "w-4 h-4" }), "Novo Cliente"] }) }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200", children: [_jsx("div", { className: "p-4 border-b border-gray-200", children: _jsx(SearchBar, { placeholder: "Buscar por nome, CPF/CNPJ ou email...", onSearch: handleSearch }) }), filteredClients.length > 0 ? (_jsxs(_Fragment, { children: [_jsx(DataTable, { columns: columns, data: filteredClients, onRowClick: (row) => navigate(`/org/${slug}/clients/${row.id}`) }), _jsx("div", { className: "p-4 border-t border-gray-200 flex items-center justify-between", children: _jsxs("p", { className: "text-sm text-gray-600", children: ["Mostrando ", filteredClients.length, " de ", clients.length, " clientes"] }) })] })) : (_jsxs("div", { className: "p-12 text-center", children: [_jsx(Building2, { className: "w-12 h-12 text-gray-400 mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-medium text-gray-900 mb-2", children: "Nenhum cliente encontrado" }), _jsx("p", { className: "text-gray-600 mb-4", children: "Comece adicionando seus primeiros clientes ao sistema" }), _jsxs(Link, { to: `/org/${slug}/clients/new`, className: "inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: [_jsx(Plus, { className: "w-4 h-4" }), "Adicionar Primeiro Cliente"] })] }))] })] }));
}
