import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * PrognosticoTributarioPanel - Painel de Prognóstico
 * 3 Cenários: Provável, Possível, Remoto
 */
import { useState, useEffect } from 'react';
import api from '../../lib/api';
import { TrendingUp, DollarSign } from 'lucide-react';
export default function PrognosticoTributarioPanel({ processoId }) {
    const [prognostico, setPrognostico] = useState(null);
    const [editing, setEditing] = useState(false);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchPrognostico();
    }, [processoId]);
    const fetchPrognostico = async () => {
        try {
            const response = await api.get(`/api/tributario/processos/${processoId}/prognostico`);
            setPrognostico(response.data);
        }
        catch (error) {
            console.error('Erro ao carregar prognóstico:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const savePrognostico = async (data) => {
        try {
            await api.post(`/api/tributario/processos/${processoId}/prognostico`, data);
            fetchPrognostico();
            setEditing(false);
        }
        catch (error) {
            console.error('Erro ao salvar prognóstico:', error);
        }
    };
    const formatCurrency = (value) => {
        if (!value)
            return 'R$ 0,00';
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };
    if (loading) {
        return _jsx("div", { className: "animate-pulse bg-accent rounded-xl h-64" });
    }
    const cenarios = [
        {
            tipo: 'provavel',
            label: 'Provável',
            color: 'green',
            data: prognostico?.provavel
        },
        {
            tipo: 'possivel',
            label: 'Possível',
            color: 'yellow',
            data: prognostico?.possivel
        },
        {
            tipo: 'remoto',
            label: 'Remoto',
            color: 'red',
            data: prognostico?.remoto
        }
    ];
    return (_jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "p-3 bg-primary/20 rounded-lg", children: _jsx(TrendingUp, { className: "w-6 h-6 text-primary" }) }), _jsxs("div", { children: [_jsx("h3", { className: "text-xl font-bold", children: "Progn\u00F3stico Tribut\u00E1rio" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "An\u00E1lise de cen\u00E1rios" })] })] }), !editing && (_jsx("button", { onClick: () => setEditing(true), className: "px-4 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors", children: prognostico ? 'Editar' : 'Criar Prognóstico' }))] }), _jsx("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-4", children: cenarios.map(cenario => (_jsxs("div", { className: `bg-${cenario.color}-500/10 border border-${cenario.color}-500/20 rounded-xl p-6 hover:shadow-lg transition-all`, children: [_jsxs("div", { className: "flex items-center gap-2 mb-4", children: [_jsx("div", { className: `p-2 bg-${cenario.color}-500/20 rounded-lg`, children: _jsx(TrendingUp, { className: `w-5 h-5 text-${cenario.color}-400` }) }), _jsx("h4", { className: `font-semibold text-${cenario.color}-400`, children: cenario.label })] }), cenario.data ? (_jsxs("div", { className: "space-y-3", children: [_jsxs("div", { children: [_jsx("label", { className: "text-xs text-muted-foreground", children: "Valor" }), _jsx("p", { className: "text-2xl font-bold", children: formatCurrency(cenario.data.valor) })] }), _jsxs("div", { children: [_jsx("label", { className: "text-xs text-muted-foreground", children: "Percentual" }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("div", { className: "flex-1 bg-accent rounded-full h-2", children: _jsx("div", { className: `bg-${cenario.color}-500 rounded-full h-2 transition-all`, style: { width: `${cenario.data.percentual}%` } }) }), _jsxs("span", { className: "text-sm font-medium", children: [cenario.data.percentual, "%"] })] })] })] })) : (_jsx("p", { className: "text-sm text-muted-foreground", children: "N\u00E3o configurado" }))] }, cenario.tipo))) }), prognostico && (_jsx("div", { className: "bg-gradient-to-r from-primary/20 to-primary/5 border border-primary/20 rounded-xl p-6", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("h4", { className: "text-sm text-muted-foreground mb-1", children: "Valor Esperado (Ponderado)" }), _jsx("p", { className: "text-3xl font-bold text-primary", children: "Calcular via API" })] }), _jsx(DollarSign, { className: "w-12 h-12 text-primary/50" })] }) }))] }));
}
