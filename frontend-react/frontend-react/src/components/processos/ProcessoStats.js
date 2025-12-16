import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * ProcessoStats - Dashboard de Estatísticas
 * Métricas e KPIs de processos
 */
import { useState, useEffect } from 'react';
import api from '../../lib/api';
import { Gavel, TrendingUp, DollarSign, AlertCircle, BarChart3, PieChart } from 'lucide-react';
export default function ProcessoStats() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchStats();
    }, []);
    const fetchStats = async () => {
        try {
            const response = await api.get('/api/processos/estatisticas');
            setStats(response.data || {});
        }
        catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
        }
        finally {
            setLoading(false);
        }
    };
    if (loading) {
        return (_jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4", children: [1, 2, 3, 4].map(i => (_jsx("div", { className: "animate-pulse bg-accent rounded-xl h-32" }, i))) }));
    }
    const cards = [
        {
            title: 'Total de Processos',
            value: stats?.total || 0,
            icon: Gavel,
            color: 'blue',
            trend: '+12%'
        },
        {
            title: 'Valor Total',
            value: new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL',
                notation: 'compact'
            }).format(stats?.valor_total || 0),
            icon: DollarSign,
            color: 'green',
            trend: '+8%'
        },
        {
            title: 'Processos Ativos',
            value: stats?.ativos || 0,
            icon: TrendingUp,
            color: 'orange',
            trend: '+5%'
        },
        {
            title: 'Alto Risco',
            value: stats?.alto_risco || 0,
            icon: AlertCircle,
            color: 'red',
            trend: '-3%'
        }
    ];
    return (_jsxs("div", { className: "space-y-6", children: [_jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4", children: cards.map((card, index) => (_jsxs("div", { className: `bg-gradient-to-br from-${card.color}-500/10 to-${card.color}-600/5 border border-${card.color}-500/20 rounded-xl p-6 hover:shadow-xl hover:scale-105 transition-all duration-300`, children: [_jsxs("div", { className: "flex items-start justify-between mb-4", children: [_jsx("div", { className: `p-3 bg-${card.color}-500/20 rounded-lg`, children: _jsx(card.icon, { className: `w-6 h-6 text-${card.color}-400` }) }), _jsx("span", { className: "px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs font-medium", children: card.trend })] }), _jsxs("div", { children: [_jsx("p", { className: "text-sm text-muted-foreground mb-1", children: card.title }), _jsx("p", { className: "text-3xl font-bold", children: card.value })] })] }, index))) }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-4", children: [_jsxs("div", { className: "bg-card border border-border rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center gap-3 mb-6", children: [_jsx(PieChart, { className: "w-5 h-5 text-primary" }), _jsx("h3", { className: "font-semibold", children: "Distribui\u00E7\u00E3o por Natureza" })] }), _jsx("div", { className: "space-y-4", children: [
                                    { natureza: 'Tributário', count: stats?.tributario || 0, color: 'blue' },
                                    { natureza: 'Trabalhista', count: stats?.trabalhista || 0, color: 'orange' },
                                    { natureza: 'Cível', count: stats?.civel || 0, color: 'purple' }
                                ].map(item => {
                                    const total = (stats?.tributario || 0) + (stats?.trabalhista || 0) + (stats?.civel || 0);
                                    const percentage = total > 0 ? (item.count / total * 100).toFixed(1) : '0';
                                    return (_jsxs("div", { children: [_jsxs("div", { className: "flex items-center justify-between mb-2", children: [_jsx("span", { className: "text-sm font-medium", children: item.natureza }), _jsxs("span", { className: "text-sm text-muted-foreground", children: [item.count, " (", percentage, "%)"] })] }), _jsx("div", { className: "w-full bg-accent rounded-full h-2", children: _jsx("div", { className: `bg-${item.color}-500 rounded-full h-2 transition-all duration-500`, style: { width: `${percentage}%` } }) })] }, item.natureza));
                                }) })] }), _jsxs("div", { className: "bg-card border border-border rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center gap-3 mb-6", children: [_jsx(BarChart3, { className: "w-5 h-5 text-primary" }), _jsx("h3", { className: "font-semibold", children: "Status dos Processos" })] }), _jsx("div", { className: "space-y-4", children: [
                                    { status: 'Ativos', count: stats?.ativos || 0, color: 'green' },
                                    { status: 'Arquivados', count: stats?.arquivados || 0, color: 'gray' },
                                    { status: 'Suspensos', count: stats?.suspensos || 0, color: 'yellow' }
                                ].map(item => {
                                    const total = (stats?.ativos || 0) + (stats?.arquivados || 0) + (stats?.suspensos || 0);
                                    const percentage = total > 0 ? (item.count / total * 100).toFixed(1) : '0';
                                    return (_jsxs("div", { children: [_jsxs("div", { className: "flex items-center justify-between mb-2", children: [_jsx("span", { className: "text-sm font-medium", children: item.status }), _jsxs("span", { className: "text-sm text-muted-foreground", children: [item.count, " (", percentage, "%)"] })] }), _jsx("div", { className: "w-full bg-accent rounded-full h-2", children: _jsx("div", { className: `bg-${item.color}-500 rounded-full h-2 transition-all duration-500`, style: { width: `${percentage}%` } }) })] }, item.status));
                                }) })] })] })] }));
}
