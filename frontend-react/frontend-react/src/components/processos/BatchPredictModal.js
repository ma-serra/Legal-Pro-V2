import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { Brain, X, Download, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';
import api from '../../lib/api';
export default function BatchPredictModal({ processoIds, onClose, onSuccess }) {
    const [resultado, setResultado] = useState(null);
    const [analisando, setAnalisando] = useState(false);
    const [erro, setErro] = useState(null);
    const executarAnalise = async () => {
        setAnalisando(true);
        setErro(null);
        try {
            const response = await api.post('/api/ml/tributario/batch-predict', {
                processo_ids: processoIds
            });
            setResultado(response.data);
        }
        catch (error) {
            console.error('Erro batch predict:', error);
            setErro(error.response?.data?.error || 'Erro ao realizar análise em lote');
        }
        finally {
            setAnalisando(false);
        }
    };
    const exportarCSV = () => {
        if (!resultado)
            return;
        const headers = ['Processo ID', 'Pasta', 'Valor Predito', 'Confiança (%)', 'Risco'];
        const rows = resultado.predicoes.map(p => [
            p.processo_id,
            p.pasta || '-',
            p.valor_contingencia_predito.toFixed(2),
            (p.confianca * 100).toFixed(1),
            p.risco_predito || '-'
        ]);
        const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `batch_predict_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };
    const formatarMoeda = (valor) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
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
    const calcularMediaConfianca = () => {
        if (!resultado || resultado.predicoes.length === 0)
            return 0;
        const soma = resultado.predicoes.reduce((acc, p) => acc + p.confianca, 0);
        return (soma / resultado.predicoes.length) * 100;
    };
    return (_jsx("div", { className: "fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4", children: _jsxs("div", { className: "bg-card border border-border rounded-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col", children: [_jsx("div", { className: "bg-gradient-to-r from-primary/20 to-primary/5 border-b border-border p-6", children: _jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { children: [_jsxs("div", { className: "flex items-center gap-3 mb-2", children: [_jsx(Brain, { className: "w-6 h-6 text-primary" }), _jsx("h2", { className: "text-2xl font-bold", children: "An\u00E1lise ML em Lote" })] }), _jsxs("p", { className: "text-muted-foreground", children: [processoIds.length, " processo(s) selecionado(s)"] })] }), _jsx("button", { onClick: onClose, className: "p-2 hover:bg-accent rounded-lg transition-colors", children: _jsx(X, { className: "w-5 h-5" }) })] }) }), _jsxs("div", { className: "flex-1 overflow-y-auto p-6", children: [!resultado && !analisando && !erro && (_jsxs("div", { className: "text-center py-12", children: [_jsx(Brain, { className: "w-16 h-16 text-primary mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-semibold mb-2", children: "Pronto para Analisar" }), _jsxs("p", { className: "text-muted-foreground mb-6", children: ["Clique no bot\u00E3o abaixo para iniciar a an\u00E1lise ML de ", processoIds.length, " processo(s)."] }), _jsx("button", { onClick: executarAnalise, className: "px-6 py-3 bg-primary hover:bg-primary/90 text-white rounded-lg font-semibold transition-colors", children: "Iniciar An\u00E1lise" })] })), analisando && (_jsxs("div", { className: "text-center py-12", children: [_jsx(RefreshCw, { className: "w-16 h-16 text-primary animate-spin mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-semibold mb-2", children: "Processando..." }), _jsxs("p", { className: "text-muted-foreground", children: ["Analisando ", processoIds.length, " processo(s). Isso pode levar alguns segundos."] })] })), erro && (_jsxs("div", { className: "text-center py-12", children: [_jsx(AlertCircle, { className: "w-16 h-16 text-red-400 mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-semibold mb-2 text-red-400", children: "Erro na An\u00E1lise" }), _jsx("p", { className: "text-muted-foreground mb-6", children: erro }), _jsx("button", { onClick: executarAnalise, className: "px-6 py-3 bg-primary hover:bg-primary/90 text-white rounded-lg font-semibold transition-colors", children: "Tentar Novamente" })] })), resultado && (_jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "grid grid-cols-3 gap-4", children: [_jsxs("div", { className: "bg-green-500/10 border border-green-500/20 rounded-xl p-4 text-center", children: [_jsx(CheckCircle2, { className: "w-8 h-8 text-green-500 mx-auto mb-2" }), _jsx("div", { className: "text-2xl font-bold text-green-500", children: resultado.total_processados }), _jsx("div", { className: "text-sm text-muted-foreground", children: "Processados" })] }), _jsxs("div", { className: "bg-blue-500/10 border border-blue-500/20 rounded-xl p-4 text-center", children: [_jsx(Brain, { className: "w-8 h-8 text-blue-500 mx-auto mb-2" }), _jsxs("div", { className: "text-2xl font-bold text-blue-500", children: [calcularMediaConfianca().toFixed(1), "%"] }), _jsx("div", { className: "text-sm text-muted-foreground", children: "Confian\u00E7a M\u00E9dia" })] }), _jsxs("div", { className: "bg-purple-500/10 border border-purple-500/20 rounded-xl p-4 text-center", children: [_jsx(RefreshCw, { className: "w-8 h-8 text-purple-500 mx-auto mb-2" }), _jsx("div", { className: "text-2xl font-bold text-purple-500", children: resultado.tempo_processamento }), _jsx("div", { className: "text-sm text-muted-foreground", children: "Tempo" })] })] }), _jsx("div", { className: "bg-accent/30 border border-border rounded-xl overflow-hidden", children: _jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full", children: [_jsx("thead", { className: "bg-accent border-b border-border", children: _jsxs("tr", { children: [_jsx("th", { className: "text-left py-3 px-4 text-sm font-medium", children: "Processo" }), _jsx("th", { className: "text-right py-3 px-4 text-sm font-medium", children: "Valor Predito" }), _jsx("th", { className: "text-center py-3 px-4 text-sm font-medium", children: "Confian\u00E7a" }), _jsx("th", { className: "text-center py-3 px-4 text-sm font-medium", children: "Risco" })] }) }), _jsx("tbody", { children: resultado.predicoes.map((pred, index) => (_jsxs("tr", { className: "border-b border-border/50 hover:bg-accent/50", children: [_jsxs("td", { className: "py-3 px-4", children: [_jsxs("div", { className: "font-medium", children: ["#", pred.processo_id] }), pred.pasta && (_jsx("div", { className: "text-xs text-muted-foreground", children: pred.pasta }))] }), _jsx("td", { className: "py-3 px-4 text-right font-semibold text-primary", children: formatarMoeda(pred.valor_contingencia_predito) }), _jsx("td", { className: "py-3 px-4 text-center", children: _jsxs("div", { className: "inline-block px-3 py-1 bg-green-500/10 text-green-500 rounded-full text-sm font-semibold", children: [(pred.confianca * 100).toFixed(1), "%"] }) }), _jsx("td", { className: "py-3 px-4 text-center", children: pred.risco_predito && (_jsx("div", { className: `inline-block px-3 py-1 rounded-full text-sm font-semibold ${getRiscoColor(pred.risco_predito)}`, children: pred.risco_predito })) })] }, index))) })] }) }) })] }))] }), resultado && (_jsxs("div", { className: "border-t border-border p-6 flex items-center justify-between bg-accent/20", children: [_jsxs("button", { onClick: exportarCSV, className: "px-4 py-2 border border-border hover:bg-accent rounded-lg flex items-center gap-2 transition-colors", children: [_jsx(Download, { className: "w-4 h-4" }), "Exportar CSV"] }), _jsxs("div", { className: "flex gap-3", children: [_jsx("button", { onClick: onClose, className: "px-6 py-2 border border-border hover:bg-accent rounded-lg transition-colors", children: "Fechar" }), _jsx("button", { onClick: () => {
                                        onSuccess();
                                        onClose();
                                    }, className: "px-6 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg font-semibold transition-colors", children: "Concluir" })] })] }))] }) }));
}
