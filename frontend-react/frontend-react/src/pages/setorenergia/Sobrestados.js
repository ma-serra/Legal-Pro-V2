import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader, DataTable } from '../../components/ui/AdminComponents';
import { AlertTriangle, Eye, FileText, Clock, TrendingUp } from 'lucide-react';
import api from '../../lib/api';
export default function Sobrestados() {
    const navigate = useNavigate();
    const [processos, setProcessos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        total: 0,
        criticos: 0,
        valor_total: 0
    });
    useEffect(() => {
        fetchProcessos();
    }, []);
    const fetchProcessos = async () => {
        try {
            const response = await api.get('/setorenergia/sobrestados');
            setProcessos(response.data);
            //Calcular estatísticas
            const total = response.data.length;
            const criticos = response.data.filter((p) => p.acao_recomendada === 'urgente').length;
            const valor_total = response.data.reduce((sum, p) => sum + p.valor_causa, 0);
            setStats({ total, criticos, valor_total });
        }
        catch (error) {
            console.error('Error fetching sobrestados:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const columns = [
        {
            key: 'numero',
            label: 'Número do Processo',
            render: (value, row) => (_jsxs("div", { children: [_jsx("p", { className: "font-medium text-gray-900", children: value }), _jsx("p", { className: "text-sm text-gray-600", children: row.titulo })] }))
        },
        {
            key: 'motivo_sobrestamento',
            label: 'Motivo',
            render: (value) => (_jsx("span", { className: "text-sm text-gray-700", children: value }))
        },
        {
            key: 'data_sobrestamento',
            label: 'Data',
            render: (value) => (_jsx("span", { className: "text-sm text-gray-600", children: new Date(value).toLocaleDateString('pt-BR') }))
        },
        {
            key: 'prazo_estimado',
            label: 'Prazo Estimado',
            render: (value) => (_jsx("span", { className: "text-sm text-gray-600", children: value }))
        },
        {
            key: 'acao_recomendada',
            label: 'Ação',
            render: (value) => (_jsx("span", { className: `px-2 py-1 rounded-full text-xs font-medium ${value === 'urgente'
                    ? 'bg-red-100 text-red-800'
                    : value === 'monitorar'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-green-100 text-green-800'}`, children: value }))
        },
        {
            key: 'actions',
            label: 'Ações',
            render: (_, row) => (_jsx("button", { onClick: () => navigate(`/processos/${row.id}`), className: "p-1 text-blue-600 hover:bg-blue-50 rounded", title: "Ver detalhes", children: _jsx(Eye, { className: "w-4 h-4" }) }))
        }
    ];
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Processos Sobrestados", description: "Listagem e an\u00E1lise de processos com sobrestamento" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-6 mb-6", children: [_jsx("div", { className: "bg-white p-6 rounded-lg border border-gray-200", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-gray-600 mb-1", children: "Total Sobrestados" }), _jsx("p", { className: "text-3xl font-bold text-gray-900", children: stats.total })] }), _jsx(AlertTriangle, { className: "w-10 h-10 text-orange-600" })] }) }), _jsx("div", { className: "bg-white p-6 rounded-lg border border-gray-200", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-gray-600 mb-1", children: "Cr\u00EDticos" }), _jsx("p", { className: "text-3xl font-bold text-red-600", children: stats.criticos })] }), _jsx(FileText, { className: "w-10 h-10 text-red-600" })] }) }), _jsx("div", { className: "bg-white p-6 rounded-lg border border-gray-200", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-gray-600 mb-1", children: "Valor Total" }), _jsx("p", { className: "text-2xl font-bold text-gray-900", children: new Intl.NumberFormat('pt-BR', {
                                                style: 'currency',
                                                currency: 'BRL',
                                                notation: 'compact'
                                            }).format(stats.valor_total) })] }), _jsx(TrendingUp, { className: "w-10 h-10 text-green-600" })] }) })] }), _jsx("div", { className: "bg-white rounded-lg border border-gray-200", children: processos.length > 0 ? (_jsxs(_Fragment, { children: [_jsx(DataTable, { columns: columns, data: processos, onRowClick: (row) => navigate(`/processos/${row.id}`) }), _jsx("div", { className: "p-4 border-t border-gray-200", children: _jsxs("p", { className: "text-sm text-gray-600", children: ["Mostrando ", processos.length, " processos sobrestados"] }) })] })) : (_jsxs("div", { className: "p-12 text-center", children: [_jsx(Clock, { className: "w-16 h-16 text-gray-400 mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-medium text-gray-900 mb-2", children: "Nenhum processo sobrestado" }), _jsx("p", { className: "text-gray-600", children: "Todos os processos est\u00E3o em andamento normal" })] })) }), stats.criticos > 0 && (_jsx("div", { className: "mt-6 bg-red-50 border border-red-200 rounded-lg p-4", children: _jsxs("div", { className: "flex items-start gap-3", children: [_jsx(AlertTriangle, { className: "w-5 h-5 text-red-600 mt-0.5" }), _jsxs("div", { children: [_jsxs("h4", { className: "font-semibold text-red-900 mb-1", children: ["Aten\u00E7\u00E3o: ", stats.criticos, " processos cr\u00EDticos"] }), _jsx("p", { className: "text-sm text-red-700", children: "Estes processos requerem a\u00E7\u00E3o urgente devido ao tempo de sobrestamento prolongado." })] })] }) }))] }));
}
