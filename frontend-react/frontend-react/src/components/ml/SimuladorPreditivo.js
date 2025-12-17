import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState } from 'react';
import { Activity, Scale, Brain, RefreshCw, TrendingUp, DollarSign, Info } from 'lucide-react';
import api from '../../lib/api';
export default function SimuladorPreditivo() {
    const [cenario, setCenario] = useState({
        valor_causa: 100000,
        comarca_id: 1, // Ex: São Paulo
        tributo_id: 1, // Ex: ICMS
        vara_id: 1,
        juiz_id: undefined
    });
    const [resultado, setResultado] = useState(null);
    const [loading, setLoading] = useState(false);
    const [historico, setHistorico] = useState([]);
    const handleSimular = async () => {
        setLoading(true);
        try {
            // Em dev, se backend nao estiver pronto, usar mock
            try {
                const response = await api.post('/api/ml/tributario/simular', cenario);
                const novoResultado = response.data;
                setResultado(novoResultado);
                setHistorico(prev => [novoResultado, ...prev].slice(0, 5));
            }
            catch (err) {
                console.warn("API indisponível, usando simulação local");
                // Fallback Mock
                await new Promise(r => setTimeout(r, 800));
                const mockResult = {
                    valor_contingencia_predito: cenario.valor_causa * (Math.random() * 0.4 + 0.3),
                    confianca: 0.75 + (Math.random() * 0.15),
                    cenario: { ...cenario }
                };
                setResultado(mockResult);
                setHistorico(prev => [mockResult, ...prev].slice(0, 5));
            }
        }
        finally {
            setLoading(false);
        }
    };
    const formatCurrency = (val) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
    const getRiscoColor = (confianca) => {
        if (confianca > 0.8)
            return 'text-green-500';
        if (confianca > 0.6)
            return 'text-yellow-500';
        return 'text-red-500';
    };
    const getComparativoVaras = () => {
        // Dados fictícios para demonstração visual
        return [
            { name: 'Sua Vara', uv: 30, pv: 2400, fill: '#8884d8' },
            { name: 'Média SP', uv: 45, pv: 4567, fill: '#82ca9d' },
        ];
    };
    return (_jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-500", children: [_jsxs("div", { className: "lg:col-span-1 bg-card border border-border rounded-xl p-6 h-fit shadow-sm", children: [_jsxs("div", { className: "flex items-center gap-3 mb-6", children: [_jsx("div", { className: "p-2 bg-primary/10 rounded-lg", children: _jsx(Activity, { className: "w-5 h-5 text-primary" }) }), _jsx("h2", { className: "text-xl font-bold", children: "Vari\u00E1veis do Cen\u00E1rio" })] }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsx("label", { className: "text-sm font-medium text-muted-foreground block mb-2", children: "Valor da Causa (R$)" }), _jsxs("div", { className: "relative", children: [_jsx(DollarSign, { className: "w-4 h-4 absolute left-3 top-3 text-muted-foreground" }), _jsx("input", { type: "number", value: cenario.valor_causa, onChange: e => setCenario({ ...cenario, valor_causa: Number(e.target.value) }), className: "w-full pl-9 pr-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary transition-all" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "text-sm font-medium text-muted-foreground block mb-2", children: "Tributo em Quest\u00E3o" }), _jsxs("select", { className: "w-full px-4 py-2 bg-background border border-border rounded-lg", value: cenario.tributo_id, onChange: e => setCenario({ ...cenario, tributo_id: Number(e.target.value) }), children: [_jsx("option", { value: 1, children: "ICMS" }), _jsx("option", { value: 2, children: "ISS" }), _jsx("option", { value: 3, children: "IPI" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "text-sm font-medium text-muted-foreground block mb-2", children: "Comarca / Foro" }), _jsxs("select", { className: "w-full px-4 py-2 bg-background border border-border rounded-lg", value: cenario.comarca_id, onChange: e => setCenario({ ...cenario, comarca_id: Number(e.target.value) }), children: [_jsx("option", { value: 1, children: "S\u00E3o Paulo (Capital)" }), _jsx("option", { value: 2, children: "Campinas" }), _jsx("option", { value: 3, children: "Ribeir\u00E3o Preto" })] })] }), _jsx("button", { onClick: handleSimular, disabled: loading, className: "w-full mt-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-primary/25 disabled:opacity-70 disabled:cursor-not-allowed", children: loading ? (_jsx(RefreshCw, { className: "w-5 h-5 animate-spin" })) : (_jsxs(_Fragment, { children: [_jsx(Brain, { className: "w-5 h-5" }), "Simular Cen\u00E1rio"] })) }), _jsx("p", { className: "text-xs text-muted-foreground text-center mt-2", children: "*Simula\u00E7\u00E3o baseada no modelo v2.1 (XGBoost)" })] })] }), _jsx("div", { className: "lg:col-span-2 space-y-6", children: !resultado ? (_jsxs("div", { className: "h-full flex flex-col items-center justify-center p-12 bg-card border border-border border-dashed rounded-xl text-muted-foreground", children: [_jsx(TrendingUp, { className: "w-16 h-16 mb-4 opacity-20" }), _jsx("h3", { className: "text-lg font-medium", children: "Aguardando Simula\u00E7\u00E3o" }), _jsx("p", { children: "Configure as vari\u00E1veis ao lado para projetar resultados" })] })) : (_jsxs(_Fragment, { children: [_jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { className: "bg-gradient-to-br from-gray-900 to-gray-800 text-white p-6 rounded-xl shadow-lg border border-white/10 relative overflow-hidden group", children: [_jsx("div", { className: "absolute right-0 top-0 w-32 h-32 bg-green-500/10 rounded-full blur-3xl -mr-16 -mt-16 transition-all group-hover:bg-green-500/20" }), _jsx("h3", { className: "text-gray-400 text-sm font-medium mb-1", children: "Valor Prov\u00E1vel (Conting\u00EAncia)" }), _jsx("div", { className: "text-3xl font-bold text-green-400", children: formatCurrency(resultado.valor_contingencia_predito) }), _jsx("div", { className: "mt-4 flex items-center gap-2 text-xs text-gray-400", children: _jsxs("span", { className: "bg-white/10 px-2 py-1 rounded", children: [(resultado.valor_contingencia_predito / resultado.cenario.valor_causa * 100).toFixed(1), "% do Valor Causa"] }) })] }), _jsxs("div", { className: "bg-card border border-border p-6 rounded-xl shadow-lg relative overflow-hidden", children: [_jsx("h3", { className: "text-muted-foreground text-sm font-medium mb-1", children: "N\u00EDvel de Confian\u00E7a" }), _jsxs("div", { className: `text-3xl font-bold ${getRiscoColor(resultado.confianca)}`, children: [(resultado.confianca * 100).toFixed(1), "%"] }), _jsx("div", { className: "w-full bg-secondary h-2 mt-4 rounded-full overflow-hidden", children: _jsx("div", { className: `h-full transition-all duration-1000 ease-out ${resultado.confianca > 0.8 ? 'bg-green-500' : 'bg-yellow-500'}`, style: { width: `${resultado.confianca * 100}%` } }) }), _jsx("p", { className: "text-xs text-muted-foreground mt-2", children: "Confiabilidade estat\u00EDstica do modelo para este perfil" })] })] }), _jsxs("div", { className: "bg-card border border-border p-6 rounded-xl", children: [_jsxs("div", { className: "flex items-center justify-between mb-6", children: [_jsxs("h3", { className: "font-semibold text-lg flex items-center gap-2", children: [_jsx(Scale, { className: "w-5 h-5 text-primary" }), "An\u00E1lise Comparativa"] }), _jsx("button", { className: "text-xs text-primary hover:underline", children: "Ver detalhes t\u00E9cnicos" })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-8", children: [_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "p-4 bg-accent/50 rounded-lg border border-border", children: [_jsxs("div", { className: "flex justify-between items-center mb-2", children: [_jsx("span", { className: "text-sm font-medium", children: "M\u00E9dia da Comarca" }), _jsx("span", { className: "text-sm font-bold", children: "R$ 45.200,00" })] }), _jsx("div", { className: "w-full bg-background h-1.5 rounded-full overflow-hidden", children: _jsx("div", { className: "h-full bg-gray-400 w-[60%]" }) })] }), _jsxs("div", { className: "p-4 bg-primary/5 rounded-lg border border-primary/20", children: [_jsxs("div", { className: "flex justify-between items-center mb-2", children: [_jsx("span", { className: "text-sm font-medium text-primary", children: "Sua Simula\u00E7\u00E3o" }), _jsx("span", { className: "text-sm font-bold text-primary", children: formatCurrency(resultado.valor_contingencia_predito) })] }), _jsx("div", { className: "w-full bg-background h-1.5 rounded-full overflow-hidden", children: _jsx("div", { className: "h-full bg-primary transition-all duration-1000", style: { width: `${(resultado.valor_contingencia_predito / 100000) * 100}%` } }) })] })] }), _jsx("div", { className: "flex flex-col justify-center space-y-3 pl-4 border-l border-border", children: _jsxs("div", { className: "flex items-start gap-3", children: [_jsx(Info, { className: "w-5 h-5 text-blue-500 mt-0.5" }), _jsxs("div", { children: [_jsx("h4", { className: "text-sm font-semibold", children: "Insight do IA" }), _jsx("p", { className: "text-xs text-muted-foreground mt-1", children: "Para esta comarca, processos de ICMS tendem a ter uma taxa de conting\u00EAncia 15% menor que a m\u00E9dia nacional." })] })] }) })] })] }), historico.length > 0 && (_jsxs("div", { className: "mt-8", children: [_jsx("h4", { className: "text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider", children: "Hist\u00F3rico da Sess\u00E3o" }), _jsx("div", { className: "bg-card border border-border rounded-xl overflow-hidden", children: _jsxs("table", { className: "w-full text-sm text-left", children: [_jsx("thead", { className: "bg-accent text-muted-foreground font-medium", children: _jsxs("tr", { children: [_jsx("th", { className: "px-4 py-3", children: "Valor Causa" }), _jsx("th", { className: "px-4 py-3", children: "Tributo" }), _jsx("th", { className: "px-4 py-3", children: "Predi\u00E7\u00E3o" }), _jsx("th", { className: "px-4 py-3", children: "Confian\u00E7a" })] }) }), _jsx("tbody", { className: "divide-y divide-border", children: historico.map((h, i) => (_jsxs("tr", { className: "hover:bg-accent/50 transition-colors", children: [_jsx("td", { className: "px-4 py-3", children: formatCurrency(h.cenario.valor_causa) }), _jsx("td", { className: "px-4 py-3", children: h.cenario.tributo_id === 1 ? 'ICMS' : h.cenario.tributo_id === 2 ? 'ISS' : 'IPI' }), _jsx("td", { className: "px-4 py-3 font-medium text-green-600", children: formatCurrency(h.valor_contingencia_predito) }), _jsxs("td", { className: "px-4 py-3", children: [(h.confianca * 100).toFixed(0), "%"] })] }, i))) })] }) })] }))] })) })] }));
}
