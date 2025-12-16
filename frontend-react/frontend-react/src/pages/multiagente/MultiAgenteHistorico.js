import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { DataTable, SearchBar, PageHeader } from '../../components/ui/AdminComponents';
import { Eye, Trash2, Download, History } from 'lucide-react';
import api from '../../lib/api';
export default function MultiAgenteHistorico() {
    const navigate = useNavigate();
    const [historico, setHistorico] = useState([]);
    const [filtered, setFiltered] = useState([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchHistorico();
    }, []);
    // Endpoint: GET /historico-analises-multiagente
    const fetchHistorico = async () => {
        try {
            const response = await api.get('/historico-analises-multiagente');
            setHistorico(response.data);
            setFiltered(response.data);
        }
        catch (error) {
            console.error('Error fetching history:', error);
        }
        finally {
            setLoading(false);
        }
    };
    // Endpoint: GET /analise-multiagente/:analise_id/detalhes
    const handleViewDetails = (id) => {
        navigate(`/multi-agente/analise/${id}`);
    };
    // Endpoint: DELETE /api/analise-multiagente/:analise_id
    const handleDelete = async (id) => {
        if (!confirm('Deseja excluir esta análise?'))
            return;
        try {
            await api.delete(`/api/analise-multiagente/${id}`);
            fetchHistorico();
            alert('Análise excluída!');
        }
        catch (error) {
            console.error('Error deleting:', error);
            alert('Erro ao excluir análise');
        }
    };
    // Endpoint: POST /analise-multiagente/:analise_id/exportar-docx
    const handleExport = async (id) => {
        try {
            const response = await api.post(`/analise-multiagente/${id}/exportar-docx`, {}, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `analise-multiagente-${id}.docx`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        }
        catch (error) {
            console.error('Error exporting:', error);
            alert('Erro ao exportar análise');
        }
    };
    const handleSearch = (query) => {
        const result = historico.filter(item => item.tipo_analise.toLowerCase().includes(query.toLowerCase()) ||
            item.texto_preview.toLowerCase().includes(query.toLowerCase()));
        setFiltered(result);
    };
    const columns = [
        {
            key: 'tipo_analise',
            label: 'Tipo',
            render: (value) => (_jsx("span", { className: "font-medium text-gray-900", children: value }))
        },
        {
            key: 'num_agentes',
            label: 'Agentes',
            render: (value) => (_jsxs("span", { className: "px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium", children: [value, " agentes"] }))
        },
        {
            key: 'texto_preview',
            label: 'Texto',
            render: (value) => (_jsxs("span", { className: "text-sm text-gray-600 truncate max-w-xs block", children: [value.substring(0, 80), "..."] }))
        },
        {
            key: 'status',
            label: 'Status',
            render: (value) => (_jsx("span", { className: `px-2 py-1 rounded-full text-xs font-medium ${value === 'sucesso' ? 'bg-green-100 text-green-800' :
                    value === 'erro' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'}`, children: value }))
        },
        {
            key: 'created_at',
            label: 'Data',
            render: (value) => new Date(value).toLocaleString('pt-BR')
        },
        {
            key: 'actions',
            label: 'Ações',
            render: (_, row) => (_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("button", { onClick: (e) => {
                            e.stopPropagation();
                            handleViewDetails(row.id);
                        }, className: "p-1 text-blue-600 hover:bg-blue-50 rounded", title: "Ver detalhes", children: _jsx(Eye, { className: "w-4 h-4" }) }), _jsx("button", { onClick: (e) => {
                            e.stopPropagation();
                            handleExport(row.id);
                        }, className: "p-1 text-green-600 hover:bg-green-50 rounded", title: "Exportar", children: _jsx(Download, { className: "w-4 h-4" }) }), _jsx("button", { onClick: (e) => {
                            e.stopPropagation();
                            handleDelete(row.id);
                        }, className: "p-1 text-red-600 hover:bg-red-50 rounded", title: "Excluir", children: _jsx(Trash2, { className: "w-4 h-4" }) })] }))
        },
    ];
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Hist\u00F3rico Multi-Agente", description: `${filtered.length} execuções registradas` }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200", children: [_jsx("div", { className: "p-4 border-b border-gray-200", children: _jsx(SearchBar, { placeholder: "Buscar por tipo ou texto...", onSearch: handleSearch }) }), filtered.length > 0 ? (_jsxs(_Fragment, { children: [_jsx(DataTable, { columns: columns, data: filtered, onRowClick: (row) => handleViewDetails(row.id) }), _jsx("div", { className: "p-4 border-t border-gray-200 flex items-center justify-between", children: _jsxs("p", { className: "text-sm text-gray-600", children: ["Mostrando ", filtered.length, " de ", historico.length, " an\u00E1lises"] }) })] })) : (_jsxs("div", { className: "p-12 text-center", children: [_jsx(History, { className: "w-12 h-12 text-gray-400 mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-medium text-gray-900 mb-2", children: "Nenhuma an\u00E1lise encontrada" }), _jsx("p", { className: "text-gray-600", children: "Execute an\u00E1lises multi-agente para v\u00EA-las aqui" })] }))] })] }));
}
