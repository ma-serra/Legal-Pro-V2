import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, DollarSign, Scale, Gavel, AlertTriangle, Calendar, Activity } from 'lucide-react';
import api from '../../lib/api';
// Cores do Sistema
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];
const NATUREZA_COLORS = {
    '1': '#3b82f6', // Tributário - Azul
    '2': '#f97316', // Trabalhista - Laranja
    '3': '#a855f7', // Cível - Roxo
};
export default function DashboardEstatisticas() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    useEffect(() => {
        carregarEstatisticas();
    }, []);
    const carregarEstatisticas = async () => {
        try {
            const response = await api.get('/api/processos/estatisticas');
            setStats(response.data);
        }
        catch (err) {
            console.error('Erro ao carregar estatísticas:', err);
            // Mock data for development if endpoint fails or is not ready
            setStats({
                total_processos: 1250,
                por_natureza: { '1': 450, '2': 300, '3': 500 },
                por_status: { '1': 800, '2': 400, '3': 50 },
                por_risco: { '1': 200, '2': 600, '3': 450 },
                valores_financeiros: {
                    total_valor_causa: 15400000.00,
                    total_valor_envolvido: 22000000.00,
                    total_contingencia: 8500000.00,
                    media_valor_causa: 12320.00
                },
                por_ano: { '2020': 100, '2021': 250, '2022': 300, '2023': 400, '2024': 200 }
            });
            setError('Usando dados demonstrativos (API indisponível)');
        }
        finally {
            setLoading(false);
        }
    };
    const formatCurrency = (value) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(value);
    };
    if (loading) {
        return (_jsx("div", { className: "flex items-center justify-center h-64", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent" }) }));
    }
    if (!stats)
        return null;
    // Transformação de dados para Recharts
    const dataNatureza = Object.entries(stats.por_natureza).map(([key, value]) => ({
        name: key === '1' ? 'Tributário' : key === '2' ? 'Trabalhista' : 'Cível',
        value: value,
        key: key
    }));
    const dataAno = Object.entries(stats.por_ano)
        .sort((a, b) => parseInt(a[0]) - parseInt(b[0]))
        .map(([ano, qtd]) => ({
        ano,
        processos: qtd
    }));
    const dataRisco = Object.entries(stats.por_risco).map(([key, value]) => ({
        name: key === '1' ? 'Provável' : key === '2' ? 'Possível' : 'Remoto',
        value: value
    }));
    return (_jsxs("div", { className: "space-y-6 animate-in fade-in duration-500", children: [error && (_jsxs("div", { className: "bg-yellow-500/10 border border-yellow-500/30 text-yellow-500 p-3 rounded-lg flex items-center gap-2 text-sm", children: [_jsx(AlertTriangle, { className: "w-4 h-4" }), error] })), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4", children: [_jsxs("div", { className: "bg-card border border-border p-6 rounded-xl hover:shadow-lg transition-all", children: [_jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm font-medium text-muted-foreground", children: "Total Processos" }), _jsx("h3", { className: "text-3xl font-bold mt-2", children: stats.total_processos })] }), _jsx("div", { className: "p-3 bg-blue-500/10 rounded-lg", children: _jsx(Scale, { className: "w-6 h-6 text-blue-500" }) })] }), _jsxs("div", { className: "mt-4 flex items-center gap-2 text-xs text-green-500", children: [_jsx(TrendingUp, { className: "w-3 h-3" }), _jsx("span", { children: "+12% este m\u00EAs" })] })] }), _jsxs("div", { className: "bg-card border border-border p-6 rounded-xl hover:shadow-lg transition-all", children: [_jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm font-medium text-muted-foreground", children: "Valor Total Causa" }), _jsx("h3", { className: "text-2xl font-bold mt-2 text-green-600", children: formatCurrency(stats.valores_financeiros.total_valor_causa) })] }), _jsx("div", { className: "p-3 bg-green-500/10 rounded-lg", children: _jsx(DollarSign, { className: "w-6 h-6 text-green-600" }) })] }), _jsx("div", { className: "mt-4 flex items-center gap-2 text-xs text-muted-foreground", children: _jsxs("span", { children: ["Ticket M\u00E9dio: ", formatCurrency(stats.valores_financeiros.media_valor_causa)] }) })] }), _jsxs("div", { className: "bg-card border border-border p-6 rounded-xl hover:shadow-lg transition-all", children: [_jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm font-medium text-muted-foreground", children: "Conting\u00EAncia" }), _jsx("h3", { className: "text-2xl font-bold mt-2 text-orange-600", children: formatCurrency(stats.valores_financeiros.total_contingencia) })] }), _jsx("div", { className: "p-3 bg-orange-500/10 rounded-lg", children: _jsx(Activity, { className: "w-6 h-6 text-orange-600" }) })] }), _jsx("div", { className: "mt-4 text-xs text-muted-foreground", children: _jsx("span", { children: "Recomendado provisionar" }) })] }), _jsxs("div", { className: "bg-card border border-border p-6 rounded-xl hover:shadow-lg transition-all", children: [_jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm font-medium text-muted-foreground", children: "Ativos" }), _jsx("h3", { className: "text-3xl font-bold mt-2", children: stats.por_status['1'] || 0 })] }), _jsx("div", { className: "p-3 bg-purple-500/10 rounded-lg", children: _jsx(Gavel, { className: "w-6 h-6 text-purple-600" }) })] }), _jsxs("p", { className: "mt-4 text-xs text-muted-foreground", children: [stats.por_status['2'] || 0, " Arquivados | ", stats.por_status['3'] || 0, " Suspensos"] })] })] }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [_jsxs("div", { className: "bg-card border border-border p-6 rounded-xl", children: [_jsxs("h3", { className: "font-semibold text-lg mb-6 flex items-center gap-2", children: [_jsx(Scale, { className: "w-5 h-5 text-primary" }), "Distribui\u00E7\u00E3o por Natureza"] }), _jsx("div", { className: "h-[300px] w-full", children: _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(PieChart, { children: [_jsx(Pie, { data: dataNatureza, cx: "50%", cy: "50%", labelLine: false, label: (props) => `${props.name} ${(props.percent * 100).toFixed(0)}%`, outerRadius: 100, fill: "#8884d8", dataKey: "value", children: dataNatureza.map((entry, index) => (_jsx(Cell, { fill: NATUREZA_COLORS[entry.key] || COLORS[index % COLORS.length] }, `cell-${index}`))) }), _jsx(Tooltip, { formatter: (value) => [value, 'Processos'] }), _jsx(Legend, {})] }) }) })] }), _jsxs("div", { className: "bg-card border border-border p-6 rounded-xl", children: [_jsxs("h3", { className: "font-semibold text-lg mb-6 flex items-center gap-2", children: [_jsx(Calendar, { className: "w-5 h-5 text-primary" }), "Evolu\u00E7\u00E3o de Processos (Ano)"] }), _jsx("div", { className: "h-[300px] w-full", children: _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(BarChart, { data: dataAno, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", vertical: false }), _jsx(XAxis, { dataKey: "ano" }), _jsx(YAxis, {}), _jsx(Tooltip, {}), _jsx(Legend, {}), _jsx(Bar, { dataKey: "processos", name: "Novos Processos", fill: "#3b82f6", radius: [4, 4, 0, 0] })] }) }) })] })] }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [_jsxs("div", { className: "bg-card border border-border p-6 rounded-xl", children: [_jsxs("h3", { className: "font-semibold text-lg mb-6 flex items-center gap-2", children: [_jsx(AlertTriangle, { className: "w-5 h-5 text-primary" }), "Classifica\u00E7\u00E3o de Risco"] }), _jsx("div", { className: "h-[250px] w-full", children: _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(BarChart, { data: dataRisco, layout: "vertical", children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", horizontal: true, vertical: false }), _jsx(XAxis, { type: "number" }), _jsx(YAxis, { dataKey: "name", type: "category", width: 100 }), _jsx(Tooltip, {}), _jsx(Legend, {}), _jsx(Bar, { dataKey: "value", name: "Processos", fill: "#f59e0b", radius: [0, 4, 4, 0] })] }) }) })] }), _jsxs("div", { className: "bg-gradient-to-br from-indigo-900 to-purple-900 p-6 rounded-xl text-white flex flex-col justify-center", children: [_jsx("h3", { className: "text-2xl font-bold mb-4", children: "Insights Financeiros" }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "flex justify-between items-center border-b border-white/10 pb-2", children: [_jsx("span", { className: "text-indigo-200", children: "Valor Envolvido Total" }), _jsx("span", { className: "font-semibold text-xl", children: formatCurrency(stats.valores_financeiros.total_valor_envolvido) })] }), _jsxs("div", { className: "flex justify-between items-center border-b border-white/10 pb-2", children: [_jsx("span", { className: "text-indigo-200", children: "Risco Financeiro (Conting\u00EAncia)" }), _jsx("span", { className: "font-semibold text-xl text-orange-300", children: formatCurrency(stats.valores_financeiros.total_contingencia) })] }), _jsxs("div", { className: "flex justify-between items-center pt-2", children: [_jsx("span", { className: "text-indigo-200", children: "Efici\u00EAncia Jur\u00EDdica" }), _jsx("span", { className: "px-3 py-1 bg-green-500/20 text-green-300 rounded-full text-sm font-medium", children: "Alta Performance" })] })] })] })] })] }));
}
