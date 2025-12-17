import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Brain, RefreshCw, AlertCircle } from 'lucide-react';
import api from '../../lib/api';
export default function QuickPredictCard({ processoId }) {
    const [predicao, setPredicao] = useState(null);
    const [loading, setLoading] = useState(true);
    const [atualizando, setAtualizando] = useState(false);
    const [erro, setErro] = useState(null);
    useEffect(() => {
        carregarPredicao();
    }, [processoId]);
    const carregarPredicao = async () => {
        setLoading(true);
        setErro(null);
        try {
            const response = await api.get(`/api/ml/tributario/quick-predict/${processoId}`);
            setPredicao(response.data);
        }
        catch (error) {
            console.error('Erro ao carregar predição:', error);
            if (error.response?.status === 404) {
                setErro('Nenhuma predição disponível');
            }
            else {
                setErro('Erro ao carregar predição');
            }
        }
        finally {
            setLoading(false);
        }
    };
    const atualizarPredicao = async () => {
        setAtualizando(true);
        try {
            const response = await api.post('/api/ml/tributario/predict', {
                processo_id: processoId
            });
            setPredicao(response.data);
            setErro(null);
        }
        catch (error) {
            console.error('Erro ao atualizar predição:', error);
            setErro(error.response?.data?.error || 'Erro ao gerar predição');
        }
        finally {
            setAtualizando(false);
        }
    };
    const formatarMoeda = (valor) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
    };
    const formatarData = (data) => {
        const date = new Date(data);
        const hoje = new Date();
        const diffDias = Math.floor((hoje.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
        if (diffDias === 0)
            return 'Hoje';
        if (diffDias === 1)
            return 'Ontem';
        if (diffDias < 7)
            return `${diffDias} dias atrás`;
        return date.toLocaleDateString('pt-BR');
    };
    const getRiscoColor = (risco) => {
        switch (risco?.toLowerCase()) {
            case 'baixo': return 'text-green-500 bg-green-500/10';
            case 'medio':
            case 'médio': return 'text-yellow-500 bg-yellow-500/10';
            case 'alto': return 'text-red-500 bg-red-500/10';
            default: return 'text-gray-500 bg-gray-500/10';
        }
    };
    if (loading) {
        return (_jsxs("div", { className: "bg-card border border-border rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center gap-2 mb-4", children: [_jsx(Brain, { className: "w-5 h-5 text-primary" }), _jsx("h3", { className: "font-semibold", children: "Predi\u00E7\u00E3o ML" })] }), _jsx("div", { className: "flex items-center justify-center py-8", children: _jsx(RefreshCw, { className: "w-6 h-6 animate-spin text-muted-foreground" }) })] }));
    }
    if (erro && !predicao) {
        return (_jsxs("div", { className: "bg-card border border-border rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center gap-2 mb-4", children: [_jsx(Brain, { className: "w-5 h-5 text-primary" }), _jsx("h3", { className: "font-semibold", children: "Predi\u00E7\u00E3o ML" })] }), _jsxs("div", { className: "text-center py-6", children: [_jsx(AlertCircle, { className: "w-12 h-12 text-muted-foreground mx-auto mb-3" }), _jsx("p", { className: "text-sm text-muted-foreground mb-4", children: erro }), _jsx("button", { onClick: atualizarPredicao, disabled: atualizando, className: "px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg text-sm transition-colors disabled:opacity-50", children: atualizando ? (_jsxs("span", { className: "flex items-center gap-2", children: [_jsx(RefreshCw, { className: "w-4 h-4 animate-spin" }), "Gerando..."] })) : ('Gerar Predição ML') })] })] }));
    }
    return (_jsxs("div", { className: "bg-gradient-to-br from-primary/5 to-primary/10 border border-primary/20 rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center justify-between mb-4", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx(Brain, { className: "w-5 h-5 text-primary" }), _jsx("h3", { className: "font-semibold", children: "Predi\u00E7\u00E3o ML" })] }), _jsx("button", { onClick: atualizarPredicao, disabled: atualizando, className: "p-2 hover:bg-primary/10 rounded-lg transition-colors disabled:opacity-50", title: "Atualizar predi\u00E7\u00E3o", children: _jsx(RefreshCw, { className: `w-4 h-4 ${atualizando ? 'animate-spin' : ''}` }) })] }), predicao && (_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsx("div", { className: "text-sm text-muted-foreground mb-1", children: "Valor Conting\u00EAncia" }), _jsx("div", { className: "text-2xl font-bold text-primary", children: formatarMoeda(predicao.valor_contingencia_predito) })] }), _jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("div", { className: "text-sm text-muted-foreground mb-1", children: "Confian\u00E7a" }), _jsxs("div", { className: "text-lg font-semibold text-green-500", children: [(predicao.confianca * 100).toFixed(1), "%"] }), _jsx("div", { className: "w-full bg-accent rounded-full h-2 mt-2", children: _jsx("div", { className: "bg-green-500 rounded-full h-2 transition-all", style: { width: `${predicao.confianca * 100}%` } }) })] }), predicao.risco_predito && (_jsxs("div", { children: [_jsx("div", { className: "text-sm text-muted-foreground mb-1", children: "Risco" }), _jsx("div", { className: `inline-block px-3 py-1 rounded-full text-sm font-semibold ${getRiscoColor(predicao.risco_predito)}`, children: predicao.risco_predito })] }))] }), _jsxs("div", { className: "pt-4 border-t border-border/50 text-xs text-muted-foreground flex items-center justify-between", children: [_jsxs("span", { children: ["Modelo ", predicao.modelo_versao] }), predicao.data_predicao && (_jsx("span", { children: formatarData(predicao.data_predicao) }))] })] }))] }));
}
