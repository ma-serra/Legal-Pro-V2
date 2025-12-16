import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { DataTable, SearchBar, PageHeader } from '../../components/ui/AdminComponents';
import { Plus, Eye, FileText } from 'lucide-react';
import api from '../../lib/api';
export default function ProcessosList() {
    const navigate = useNavigate();
    const [processos, setProcessos] = useState([]);
    const [filtered, setFiltered] = useState([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchProcessos();
    }, []);
    const fetchProcessos = async () => {
        try {
            const response = await api.get('/api/processos');
            setProcessos(response.data);
            setFiltered(response.data);
        }
        catch (error) {
            console.error('Error fetching processos:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const handleSearch = (query) => {
        const result = processos.filter(p => p.numero_processo.includes(query) ||
            p.client_name?.toLowerCase().includes(query.toLowerCase()) ||
            p.area_direito.toLowerCase().includes(query.toLowerCase()));
        setFiltered(result);
    };
    const columns = [
        {
            key: 'numero_processo',
            label: 'Número do Processo',
            render: (value) => (_jsx("div", { className: "font-mono text-sm font-medium", children: value }))
        },
        {
            key: 'client_name',
            label: 'Cliente',
        },
        {
            key: 'area_direito',
            label: 'Área',
            render: (value) => (_jsx("span", { className: "px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium", children: value }))
        },
        {
            key: 'status',
            label: 'Status',
            render: (value) => (_jsx("span", { className: `px-2 py-1 rounded-full text-xs font-medium ${value === 'ativo' ? 'bg-green-100 text-green-800' :
                    value === 'arquivado' ? 'bg-gray-100 text-gray-800' :
                        'bg-yellow-100 text-yellow-800'}`, children: value || 'Em andamento' }))
        },
        {
            key: 'data_distribuicao',
            label: 'Data Distribuição',
            render: (value) => value ? new Date(value).toLocaleDateString('pt-BR') : '-'
        },
        {
            key: 'actions',
            label: 'Ações',
            render: (_, row) => (_jsx("button", { onClick: (e) => {
                    e.stopPropagation();
                    navigate(`/processos/${row.id}`);
                }, className: "p-1 text-blue-600 hover:bg-blue-50 rounded", children: _jsx(Eye, { className: "w-4 h-4" }) }))
        },
    ];
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Processos Jur\u00EDdicos", description: `Gerenciar todos os processos - ${filtered.length} total`, action: _jsxs(Link, { to: "/processos/novo", className: "flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: [_jsx(Plus, { className: "w-4 h-4" }), "Novo Processo"] }) }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200", children: [_jsx("div", { className: "p-4 border-b border-gray-200", children: _jsx(SearchBar, { placeholder: "Buscar por n\u00FAmero, cliente ou \u00E1rea...", onSearch: handleSearch }) }), filtered.length > 0 ? (_jsxs(_Fragment, { children: [_jsx(DataTable, { columns: columns, data: filtered, onRowClick: (row) => navigate(`/processos/${row.id}`) }), _jsx("div", { className: "p-4 border-t border-gray-200 flex items-center justify-between", children: _jsxs("p", { className: "text-sm text-gray-600", children: ["Mostrando ", filtered.length, " de ", processos.length, " processos"] }) })] })) : (_jsxs("div", { className: "p-12 text-center", children: [_jsx(FileText, { className: "w-12 h-12 text-gray-400 mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-medium text-gray-900 mb-2", children: "Nenhum processo encontrado" }), _jsx("p", { className: "text-gray-600 mb-4", children: "Adicione processos para come\u00E7ar a gerenciar seus casos" }), _jsxs(Link, { to: "/processos/novo", className: "inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: [_jsx(Plus, { className: "w-4 h-4" }), "Adicionar Processo"] })] }))] })] }));
}
