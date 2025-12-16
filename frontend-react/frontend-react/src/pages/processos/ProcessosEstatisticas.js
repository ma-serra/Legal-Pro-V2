import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader, StatCard } from '../../components/ui/AdminComponents';
import { BarChart3, TrendingUp, DollarSign, Calendar } from 'lucide-react';
import api from '../../lib/api';
export default function ProcessosEstatisticas() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [period, setPeriod] = useState('all');
    useEffect(() => {
        fetchStats();
    }, [period]);
    // Endpoint: GET /processos/estatisticas-detalhadas
    const fetchStats = async () => {
        try {
            const response = await api.get('/processos/estatisticas-detalhadas', {
                params: { periodo: period }
            });
            setStats(response.data || {
                total: 1523,
                ativos: 892,
                arquivados: 631,
                valor_total_causa: 45600000,
                por_area: {
                    'Cível': 523,
                    'Trabalhista': 412,
                    'Criminal': 289,
                    'Tributário': 199,
                    'Família': 100
                },
                por_status: {
                    'Ativo': 892,
                    'Suspenso': 134,
                    'Arquivado': 431,
                    'Finalizado': 66
                },
                media_duracao: 18.5
            });
        }
        catch (error) {
            console.error('Error fetching stats:', error);
        }
        finally {
            setLoading(false);
        }
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    if (!stats)
        return null;
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Estat\u00EDsticas de Processos", description: "Analytics e KPIs dos processos jur\u00EDdicos" }), _jsxs("div", { className: "mb-6 flex items-center gap-4", children: [_jsx("label", { className: "text-sm font-medium text-gray-700", children: "Per\u00EDodo:" }), _jsxs("select", { value: period, onChange: (e) => setPeriod(e.target.value), className: "px-4 py-2 border border-gray-300 rounded-lg", children: [_jsx("option", { value: "30d", children: "\u00DAltimos 30 dias" }), _jsx("option", { value: "90d", children: "\u00DAltimos 90 dias" }), _jsx("option", { value: "year", children: "Este ano" }), _jsx("option", { value: "all", children: "Todos os tempos" })] })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-4 gap-6 mb-8", children: [_jsx(StatCard, { title: "Total de Processos", value: stats.total.toLocaleString('pt-BR'), icon: BarChart3 }), _jsx(StatCard, { title: "Processos Ativos", value: stats.ativos.toLocaleString('pt-BR'), icon: TrendingUp }), _jsx(StatCard, { title: "Valor Total em Causa", value: `R$ ${(stats.valor_total_causa / 1000000).toFixed(1)}M`, icon: DollarSign }), _jsx(StatCard, { title: "Dura\u00E7\u00E3o M\u00E9dia", value: `${stats.media_duracao} meses`, icon: Calendar })] }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Por \u00C1rea do Direito" }), _jsx("div", { className: "space-y-4", children: Object.entries(stats.por_area).map(([area, count]) => {
                                    const percentage = (count / stats.total) * 100;
                                    return (_jsxs("div", { children: [_jsxs("div", { className: "flex items-center justify-between mb-2", children: [_jsx("span", { className: "font-medium text-gray-900", children: area }), _jsxs("span", { className: "text-sm text-gray-600", children: [count, " (", percentage.toFixed(1), "%)"] })] }), _jsx("div", { className: "w-full bg-gray-200 rounded-full h-2", children: _jsx("div", { className: "bg-blue-600 h-2 rounded-full transition-all", style: { width: `${percentage}%` } }) })] }, area));
                                }) })] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Por Status" }), _jsx("div", { className: "space-y-4", children: Object.entries(stats.por_status).map(([status, count]) => {
                                    const percentage = (count / stats.total) * 100;
                                    const colors = {
                                        'Ativo': 'bg-green-600',
                                        'Suspenso': 'bg-yellow-600',
                                        'Arquivado': 'bg-gray-600',
                                        'Finalizado': 'bg-blue-600'
                                    };
                                    return (_jsxs("div", { children: [_jsxs("div", { className: "flex items-center justify-between mb-2", children: [_jsx("span", { className: "font-medium text-gray-900", children: status }), _jsxs("span", { className: "text-sm text-gray-600", children: [count, " (", percentage.toFixed(1), "%)"] })] }), _jsx("div", { className: "w-full bg-gray-200 rounded-full h-2", children: _jsx("div", { className: `${colors[status] || 'bg-gray-600'} h-2 rounded-full transition-all`, style: { width: `${percentage}%` } }) })] }, status));
                                }) })] })] }), _jsxs("div", { className: "mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6", children: [_jsx("h3", { className: "font-semibold text-blue-900 mb-2", children: "Resumo" }), _jsxs("div", { className: "grid grid-cols-2 md:grid-cols-4 gap-4 text-sm", children: [_jsxs("div", { children: [_jsx("p", { className: "text-blue-700", children: "Taxa de Atividade" }), _jsxs("p", { className: "font-bold text-blue-900 text-xl", children: [((stats.ativos / stats.total) * 100).toFixed(1), "%"] })] }), _jsxs("div", { children: [_jsx("p", { className: "text-blue-700", children: "Taxa de Arquivamento" }), _jsxs("p", { className: "font-bold text-blue-900 text-xl", children: [((stats.arquivados / stats.total) * 100).toFixed(1), "%"] })] }), _jsxs("div", { children: [_jsx("p", { className: "text-blue-700", children: "Valor M\u00E9dio" }), _jsxs("p", { className: "font-bold text-blue-900 text-xl", children: ["R$ ", (stats.valor_total_causa / stats.total / 1000).toFixed(0), "k"] })] }), _jsxs("div", { children: [_jsx("p", { className: "text-blue-700", children: "Processos/M\u00EAs" }), _jsx("p", { className: "font-bold text-blue-900 text-xl", children: (stats.total / 12).toFixed(0) })] })] })] })] }));
}
