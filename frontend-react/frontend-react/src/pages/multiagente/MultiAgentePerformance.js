import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader, StatCard } from '../../components/ui/AdminComponents';
import { TrendingUp, Clock, CheckCircle, XCircle, BarChart3 } from 'lucide-react';
import api from '../../lib/api';
export default function MultiAgentePerformance() {
    const [performance, setPerformance] = useState(null);
    const [agentStats, setAgentStats] = useState([]);
    const [loading, setLoading] = useState(true);
    const [period, setPeriod] = useState('30d');
    useEffect(() => {
        fetchPerformance();
    }, [period]);
    // Endpoint: GET /api/multi-agente-real/estatisticas (with period filter)
    const fetchPerformance = async () => {
        try {
            const response = await api.get('/api/multi-agente-real/estatisticas', {
                params: { periodo: period }
            });
            setPerformance(response.data);
            // Mock agent-specific performance data
            setAgentStats([
                { agente_nome: 'Agente Cível', num_execucoes: 145, taxa_sucesso: 0.94, tempo_medio: 12.3 },
                { agente_nome: 'Agente Trabalhista', num_execucoes: 89, taxa_sucesso: 0.91, tempo_medio: 10.7 },
                { agente_nome: 'Agente Criminal', num_execucoes: 67, taxa_sucesso: 0.88, tempo_medio: 15.2 },
                { agente_nome: 'Agente Tributário', num_execucoes: 54, taxa_sucesso: 0.93, tempo_medio: 11.5 },
            ]);
        }
        catch (error) {
            console.error('Error fetching performance:', error);
        }
        finally {
            setLoading(false);
        }
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Performance Multi-Agente", description: "Analytics e m\u00E9tricas de execu\u00E7\u00E3o" }), _jsxs("div", { className: "mb-6 flex items-center gap-4", children: [_jsx("label", { className: "text-sm font-medium text-gray-700", children: "Per\u00EDodo:" }), _jsxs("select", { value: period, onChange: (e) => setPeriod(e.target.value), className: "px-4 py-2 border border-gray-300 rounded-lg", children: [_jsx("option", { value: "7d", children: "\u00DAltimos 7 dias" }), _jsx("option", { value: "30d", children: "\u00DAltimos 30 dias" }), _jsx("option", { value: "90d", children: "\u00DAltimos 90 dias" }), _jsx("option", { value: "all", children: "Todos os tempos" })] })] }), performance && (_jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8", children: [_jsx(StatCard, { title: "Total Execu\u00E7\u00F5es", value: performance.total_execucoes.toString(), icon: BarChart3 }), _jsx(StatCard, { title: "Taxa de Sucesso", value: `${((performance.execucoes_sucesso / performance.total_execucoes) * 100).toFixed(1)}%`, icon: TrendingUp }), _jsx(StatCard, { title: "Tempo M\u00E9dio", value: `${performance.tempo_medio.toFixed(1)}s`, icon: Clock }), _jsx(StatCard, { title: "Sucesso/Erro", value: `${performance.execucoes_sucesso}/${performance.execucoes_erro}`, icon: CheckCircle })] })), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Performance por Agente" }), _jsx("div", { className: "space-y-4", children: agentStats.map((agent, idx) => (_jsxs("div", { className: "border-b border-gray-200 pb-4 last:border-0", children: [_jsxs("div", { className: "flex items-center justify-between mb-2", children: [_jsx("span", { className: "font-medium text-gray-900", children: agent.agente_nome }), _jsxs("span", { className: "text-sm text-gray-600", children: [agent.num_execucoes, " execu\u00E7\u00F5es"] })] }), _jsxs("div", { className: "grid grid-cols-2 gap-4 text-sm", children: [_jsxs("div", { children: [_jsx("span", { className: "text-gray-600", children: "Taxa Sucesso:" }), _jsxs("div", { className: "flex items-center gap-2 mt-1", children: [_jsx("div", { className: "flex-1 bg-gray-200 rounded-full h-2", children: _jsx("div", { className: "bg-green-500 h-2 rounded-full", style: { width: `${agent.taxa_sucesso * 100}%` } }) }), _jsxs("span", { className: "font-medium text-green-600", children: [(agent.taxa_sucesso * 100).toFixed(1), "%"] })] })] }), _jsxs("div", { children: [_jsx("span", { className: "text-gray-600", children: "Tempo M\u00E9dio:" }), _jsxs("div", { className: "font-medium text-blue-600 mt-1", children: [agent.tempo_medio.toFixed(1), "s"] })] })] })] }, idx))) })] }), performance && (_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Estat\u00EDsticas de Tempo" }), _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("label", { className: "text-sm text-gray-600", children: "Tempo M\u00E9dio de Execu\u00E7\u00E3o" }), _jsxs("p", { className: "text-3xl font-bold text-blue-600 mt-1", children: [performance.tempo_medio.toFixed(1), "s"] })] }), _jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "text-sm text-gray-600", children: "Mais R\u00E1pido" }), _jsxs("p", { className: "text-xl font-semibold text-green-600 mt-1", children: [performance.tempo_minimo.toFixed(1), "s"] })] }), _jsxs("div", { children: [_jsx("label", { className: "text-sm text-gray-600", children: "Mais Lento" }), _jsxs("p", { className: "text-xl font-semibold text-red-600 mt-1", children: [performance.tempo_maximo.toFixed(1), "s"] })] })] }), _jsxs("div", { className: "pt-4 border-t border-gray-200", children: [_jsx("label", { className: "text-sm text-gray-600 block mb-2", children: "Agente Mais Usado" }), _jsxs("div", { className: "flex items-center gap-2 text-purple-600", children: [_jsx(BarChart3, { className: "w-5 h-5" }), _jsx("span", { className: "font-semibold", children: performance.agente_mais_usado })] })] }), performance.melhor_combinacao && (_jsxs("div", { className: "pt-4 border-t border-gray-200", children: [_jsx("label", { className: "text-sm text-gray-600 block mb-2", children: "Melhor Combina\u00E7\u00E3o" }), _jsx("div", { className: "flex flex-wrap gap-2", children: performance.melhor_combinacao.map((agente, idx) => (_jsx("span", { className: "px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium", children: agente }, idx))) })] }))] })] }))] }), performance && (_jsxs("div", { className: "mt-6 bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Distribui\u00E7\u00E3o Sucesso/Erro" }), _jsxs("div", { className: "grid grid-cols-2 gap-6", children: [_jsxs("div", { className: "flex items-center gap-4 p-4 bg-green-50 rounded-lg", children: [_jsx(CheckCircle, { className: "w-8 h-8 text-green-600" }), _jsxs("div", { children: [_jsx("p", { className: "text-sm text-gray-600", children: "Execu\u00E7\u00F5es Bem-Sucedidas" }), _jsx("p", { className: "text-2xl font-bold text-green-600", children: performance.execucoes_sucesso })] })] }), _jsxs("div", { className: "flex items-center gap-4 p-4 bg-red-50 rounded-lg", children: [_jsx(XCircle, { className: "w-8 h-8 text-red-600" }), _jsxs("div", { children: [_jsx("p", { className: "text-sm text-gray-600", children: "Execu\u00E7\u00F5es com Erro" }), _jsx("p", { className: "text-2xl font-bold text-red-600", children: performance.execucoes_erro })] })] })] })] }))] }));
}
