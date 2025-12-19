import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * IndicesChart - Gráfico de Histórico de Índices
 * Visualização temporal com Recharts
 */
import { useState, useEffect } from 'react';
import api from '../../lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Calendar } from 'lucide-react';
export default function IndicesChart({ indiceId, indiceName }) {
    const [historico, setHistorico] = useState([]);
    const [loading, setLoading] = useState(true);
    const [periodo, setPeriodo] = useState(90); // dias
    useEffect(() => {
        fetchHistorico();
    }, [indiceId, periodo]);
    const fetchHistorico = async () => {
        setLoading(true);
        try {
            const dataInicio = new Date();
            dataInicio.setDate(dataInicio.getDate() - periodo);
            const response = await api.get(`/api/atualizacao-monetaria/indices/${indiceId}/historico`, {
                params: {
                    data_inicio: dataInicio.toISOString().split('T')[0],
                    limite: 100
                }
            });
            setHistorico((response.data || []).reverse());
        }
        catch (error) {
            console.error('Erro ao carregar histórico:', error);
        }
        finally {
            setLoading(false);
        }
    };
    // Função para converter valor baseado no tipo de índice
    const converterValor = (valor) => {
        // SELIC e CDI vêm como taxa diária - converter para anual
        if (indiceName === 'SELIC' || indiceName === 'CDI' || indiceName === 'SELIC-EFETIVA') {
            return valor * 252; // Taxa diária * 252 dias úteis
        }
        return valor;
    };
    const formatarLabel = () => {
        if (indiceName === 'SELIC' || indiceName === 'CDI' || indiceName === 'SELIC-EFETIVA' || indiceName === 'TJLP') {
            return '% a.a.';
        }
        if (indiceName.includes('DOLAR') || indiceName.includes('EURO')) {
            return 'R$';
        }
        return '% mês';
    };
    const chartData = historico.map(h => ({
        data: new Date(h.data_referencia).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
        valor: converterValor(parseFloat(h.valor.toString()))
    }));
    const media = chartData.length > 0 ? chartData.reduce((acc, d) => acc + d.valor, 0) / chartData.length : 0;
    const minimo = chartData.length > 0 ? Math.min(...chartData.map(d => d.valor)) : 0;
    const maximo = chartData.length > 0 ? Math.max(...chartData.map(d => d.valor)) : 0;
    return (_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "flex items-center justify-between flex-wrap gap-4", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "p-2 bg-primary/20 rounded-lg", children: _jsx(TrendingUp, { className: "w-5 h-5 text-primary" }) }), _jsxs("div", { children: [_jsxs("h3", { className: "font-semibold", children: ["Hist\u00F3rico ", indiceName] }), _jsxs("p", { className: "text-sm text-muted-foreground", children: ["\u00DAltimos ", periodo, " dias"] })] })] }), _jsx("div", { className: "flex gap-2", children: [30, 90, 180, 365].map(dias => (_jsxs("button", { onClick: () => setPeriodo(dias), className: `px-3 py-1.5 rounded-lg text-sm transition-colors ${periodo === dias
                                ? 'bg-primary text-white'
                                : 'bg-accent hover:bg-accent/80'}`, children: [dias, "d"] }, dias))) })] }), loading ? (_jsx("div", { className: "animate-pulse bg-accent rounded-xl h-80" })) : chartData.length === 0 ? (_jsxs("div", { className: "bg-accent rounded-xl p-12 text-center", children: [_jsx(Calendar, { className: "w-12 h-12 text-muted-foreground mx-auto mb-4" }), _jsx("p", { className: "text-muted-foreground", children: "Sem dados para o per\u00EDodo selecionado" })] })) : (_jsxs("div", { className: "bg-card border border-border rounded-xl p-4", children: [_jsx("div", { style: { width: '100%', height: 300 }, children: _jsx(ResponsiveContainer, { children: _jsxs(LineChart, { data: chartData, margin: { top: 10, right: 30, left: 10, bottom: 10 }, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", stroke: "#333" }), _jsx(XAxis, { dataKey: "data", stroke: "#888", style: { fontSize: '11px' }, tickMargin: 10 }), _jsx(YAxis, { stroke: "#888", style: { fontSize: '11px' }, tickFormatter: (value) => `${value.toFixed(2)}`, domain: ['auto', 'auto'], width: 60 }), _jsx(Tooltip, { contentStyle: {
                                            backgroundColor: '#1f1f1f',
                                            border: '1px solid #333',
                                            borderRadius: '8px'
                                        }, formatter: (value) => [`${parseFloat(value).toFixed(2)} ${formatarLabel()}`, indiceName] }), _jsx(Legend, {}), _jsx(Line, { type: "monotone", dataKey: "valor", name: indiceName, stroke: "#3b82f6", strokeWidth: 2, dot: { fill: '#3b82f6', r: 2 }, activeDot: { r: 5 } })] }) }) }), _jsxs("div", { className: "grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-border", children: [_jsxs("div", { className: "text-center", children: [_jsx("p", { className: "text-xs text-muted-foreground mb-1", children: "M\u00E9dia" }), _jsxs("p", { className: "text-lg font-bold text-primary", children: [media.toFixed(2), " ", formatarLabel()] })] }), _jsxs("div", { className: "text-center", children: [_jsx("p", { className: "text-xs text-muted-foreground mb-1", children: "M\u00EDnima" }), _jsxs("p", { className: "text-lg font-bold text-green-400", children: [minimo.toFixed(2), " ", formatarLabel()] })] }), _jsxs("div", { className: "text-center", children: [_jsx("p", { className: "text-xs text-muted-foreground mb-1", children: "M\u00E1xima" }), _jsxs("p", { className: "text-lg font-bold text-red-400", children: [maximo.toFixed(2), " ", formatarLabel()] })] })] })] }))] }));
}
