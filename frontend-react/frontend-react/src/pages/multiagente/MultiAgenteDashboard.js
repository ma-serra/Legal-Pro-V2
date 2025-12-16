import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader, StatCard } from '../../components/ui/AdminComponents';
import { Bot, Play, History, TrendingUp, Users } from 'lucide-react';
import api from '../../lib/api';
export default function MultiAgenteDashboard() {
    const [stats, setStats] = useState(null);
    const [recent, setRecent] = useState([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchData();
    }, []);
    const fetchData = async () => {
        await Promise.all([
            fetchStats(),
            fetchRecentExecutions()
        ]);
        setLoading(false);
    };
    // Endpoint: GET /api/multi-agente-real/estatisticas
    const fetchStats = async () => {
        try {
            const response = await api.get('/api/multi-agente-real/estatisticas');
            setStats(response.data);
        }
        catch (error) {
            console.error('Error fetching stats:', error);
        }
    };
    // Endpoint: GET /api/multi-agente-real/listar
    const fetchRecentExecutions = async () => {
        try {
            const response = await api.get('/api/multi-agente-real/listar');
            setRecent(response.data.slice(0, 10));
        }
        catch (error) {
            console.error('Error fetching executions:', error);
        }
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Multi-Agente Dashboard", description: "Sistema de orquestra\u00E7\u00E3o inteligente de m\u00FAltiplos agentes IA" }), stats && (_jsxs("div", { className: "grid grid-cols-1 md:grid-cols-4 gap-6 mb-8", children: [_jsx(StatCard, { title: "Total Execu\u00E7\u00F5es", value: stats.total_execucoes.toString(), icon: Play }), _jsx(StatCard, { title: "Taxa de Sucesso", value: `${((stats.execucoes_sucesso / stats.total_execucoes) * 100).toFixed(1)}%`, icon: TrendingUp }), _jsx(StatCard, { title: "M\u00E9dia Agentes/Exec", value: stats.media_agentes_por_execucao.toFixed(1), icon: Users }), _jsx(StatCard, { title: "Tempo M\u00E9dio", value: `${stats.tempo_medio_execucacao.toFixed(1)}s`, icon: Bot })] })), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [_jsx("div", { className: "space-y-6", children: _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "A\u00E7\u00F5es R\u00E1pidas" }), _jsxs("div", { className: "space-y-3", children: [_jsx("a", { href: "/multi-agente/orquestrador", className: "block p-4 border border-gray-200 rounded-lg hover:shadow-lg transition-shadow", children: _jsxs("div", { className: "flex items-center gap-4", children: [_jsx("div", { className: "p-3 bg-blue-100 rounded-lg", children: _jsx(Play, { className: "w-6 h-6 text-blue-600" }) }), _jsxs("div", { children: [_jsx("h4", { className: "font-semibold text-gray-900", children: "Orquestrador" }), _jsx("p", { className: "text-sm text-gray-600", children: "Executar an\u00E1lise multi-agente" })] })] }) }), _jsx("a", { href: "/multi-agente/selecao-inteligente", className: "block p-4 border border-gray-200 rounded-lg hover:shadow-lg transition-shadow", children: _jsxs("div", { className: "flex items-center gap-4", children: [_jsx("div", { className: "p-3 bg-purple-100 rounded-lg", children: _jsx(Bot, { className: "w-6 h-6 text-purple-600" }) }), _jsxs("div", { children: [_jsx("h4", { className: "font-semibold text-gray-900", children: "Sele\u00E7\u00E3o Inteligente" }), _jsx("p", { className: "text-sm text-gray-600", children: "IA escolhe melhores agentes" })] })] }) }), _jsx("a", { href: "/multi-agente/historico", className: "block p-4 border border-gray-200 rounded-lg hover:shadow-lg transition-shadow", children: _jsxs("div", { className: "flex items-center gap-4", children: [_jsx("div", { className: "p-3 bg-green-100 rounded-lg", children: _jsx(History, { className: "w-6 h-6 text-green-600" }) }), _jsxs("div", { children: [_jsx("h4", { className: "font-semibold text-gray-900", children: "Hist\u00F3rico" }), _jsx("p", { className: "text-sm text-gray-600", children: "Ver execu\u00E7\u00F5es anteriores" })] })] }) }), _jsx("a", { href: "/multi-agente/performance", className: "block p-4 border border-gray-200 rounded-lg hover:shadow-lg transition-shadow", children: _jsxs("div", { className: "flex items-center gap-4", children: [_jsx("div", { className: "p-3 bg-yellow-100 rounded-lg", children: _jsx(TrendingUp, { className: "w-6 h-6 text-yellow-600" }) }), _jsxs("div", { children: [_jsx("h4", { className: "font-semibold text-gray-900", children: "Performance" }), _jsx("p", { className: "text-sm text-gray-600", children: "Analytics e m\u00E9tricas" })] })] }) })] })] }) }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsxs("h3", { className: "text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2", children: [_jsx(History, { className: "w-5 h-5" }), "Execu\u00E7\u00F5es Recentes"] }), _jsxs("div", { className: "space-y-3", children: [recent.map((exec) => (_jsxs("div", { className: "p-4 border border-gray-200 rounded-lg hover:bg-gray-50", children: [_jsxs("div", { className: "flex items-center justify-between mb-2", children: [_jsx("span", { className: "font-medium text-sm", children: exec.tipo }), _jsx("span", { className: `px-2 py-1 rounded-full text-xs font-medium ${exec.status === 'sucesso' ? 'bg-green-100 text-green-800' :
                                                            exec.status === 'erro' ? 'bg-red-100 text-red-800' :
                                                                'bg-yellow-100 text-yellow-800'}`, children: exec.status })] }), _jsxs("div", { className: "flex items-center gap-4 text-sm text-gray-600", children: [_jsxs("span", { children: [exec.num_agentes, " agentes"] }), _jsx("span", { children: new Date(exec.created_at).toLocaleString('pt-BR') })] })] }, exec.id))), recent.length === 0 && (_jsx("p", { className: "text-sm text-gray-500 text-center py-8", children: "Nenhuma execu\u00E7\u00E3o recente" }))] }), _jsx("button", { className: "w-full mt-4 px-4 py-2 text-center border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Ver Hist\u00F3rico Completo" })] })] })] }));
}
