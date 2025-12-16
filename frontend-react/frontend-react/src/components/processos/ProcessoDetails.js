import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * ProcessoDetails - Visualização Completa do Processo
 * Tabs: Geral, Específico, Prognóstico, Histórico
 */
import { useState, useEffect } from 'react';
import api from '../../lib/api';
import { FileText, DollarSign, Building2, TrendingUp, X } from 'lucide-react';
export default function ProcessoDetails({ processoId, onClose }) {
    const [processo, setProcesso] = useState(null);
    const [activeTab, setActiveTab] = useState('geral');
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchProcesso();
    }, [processoId]);
    const fetchProcesso = async () => {
        try {
            const response = await api.get(`/api/processos/${processoId}`);
            setProcesso(response.data);
        }
        catch (error) {
            console.error('Erro ao carregar processo:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const formatCurrency = (value) => {
        if (!value)
            return 'R$ 0,00';
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };
    const formatDate = (dateString) => {
        if (!dateString)
            return '-';
        return new Date(dateString).toLocaleDateString('pt-BR');
    };
    if (loading) {
        return (_jsx("div", { className: "fixed inset-0 bg-black/50 flex items-center justify-center z-50", children: _jsx("div", { className: "bg-card rounded-xl p-8", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto" }) }) }));
    }
    if (!processo)
        return null;
    const tabs = [
        { id: 'geral', label: 'Geral', icon: FileText },
        { id: 'valores', label: 'Valores', icon: DollarSign },
        { id: 'especifico', label: 'Específico', icon: Building2 },
        { id: 'prognostico', label: 'Prognóstico', icon: TrendingUp }
    ];
    return (_jsx("div", { className: "fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4", children: _jsxs("div", { className: "bg-card border border-border rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col", children: [_jsx("div", { className: "bg-gradient-to-r from-primary/20 to-primary/5 border-b border-border p-6", children: _jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "flex items-center gap-3 mb-2", children: [_jsx("div", { className: "p-2 bg-primary/20 rounded-lg", children: _jsx(FileText, { className: "w-5 h-5 text-primary" }) }), _jsx("span", { className: "px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs font-medium", children: processo.natureza_id === 1 ? 'Tributário' : processo.natureza_id === 2 ? 'Trabalhista' : 'Cível' })] }), _jsx("h2", { className: "text-2xl font-bold mb-1", children: processo.titulo || processo.pasta }), _jsxs("p", { className: "text-muted-foreground text-sm", children: ["Pasta: ", processo.pasta] }), processo.numero_cnj && (_jsxs("p", { className: "text-muted-foreground text-sm font-mono", children: ["CNJ: ", processo.numero_cnj] }))] }), _jsx("button", { onClick: onClose, className: "p-2 hover:bg-accent rounded-lg transition-colors", children: _jsx(X, { className: "w-5 h-5" }) })] }) }), _jsx("div", { className: "border-b border-border px-6", children: _jsx("div", { className: "flex gap-1", children: tabs.map(tab => (_jsxs("button", { onClick: () => setActiveTab(tab.id), className: `flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${activeTab === tab.id
                                ? 'border-primary text-primary font-medium'
                                : 'border-transparent text-muted-foreground hover:text-foreground'}`, children: [_jsx(tab.icon, { className: "w-4 h-4" }), tab.label] }, tab.id))) }) }), _jsxs("div", { className: "flex-1 overflow-y-auto p-6", children: [activeTab === 'geral' && (_jsx("div", { className: "space-y-6", children: _jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "text-sm text-muted-foreground", children: "Status" }), _jsx("p", { className: "font-medium", children: "Ativo" })] }), _jsxs("div", { children: [_jsx("label", { className: "text-sm text-muted-foreground", children: "Data Cria\u00E7\u00E3o" }), _jsx("p", { className: "font-medium", children: formatDate(processo.data_criacao) })] }), processo.data_distribuicao && (_jsxs("div", { children: [_jsx("label", { className: "text-sm text-muted-foreground", children: "Data Distribui\u00E7\u00E3o" }), _jsx("p", { className: "font-medium", children: formatDate(processo.data_distribuicao) })] }))] }) })), activeTab === 'valores' && (_jsx("div", { className: "space-y-4", children: _jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { className: "bg-green-500/10 border border-green-500/20 rounded-xl p-4", children: [_jsx("label", { className: "text-sm text-muted-foreground", children: "Valor da Causa" }), _jsx("p", { className: "text-2xl font-bold text-green-400", children: formatCurrency(processo.valor_causa) })] }), _jsxs("div", { className: "bg-blue-500/10 border border-blue-500/20 rounded-xl p-4", children: [_jsx("label", { className: "text-sm text-muted-foreground", children: "Conting\u00EAncia" }), _jsx("p", { className: "text-2xl font-bold text-blue-400", children: formatCurrency(processo.contingencia) })] })] }) })), activeTab === 'especifico' && (_jsx("div", { className: "text-center py-8 text-muted-foreground", children: "Dados espec\u00EDficos por natureza aparecer\u00E3o aqui" })), activeTab === 'prognostico' && (_jsx("div", { className: "text-center py-8 text-muted-foreground", children: "Progn\u00F3stico do processo aparecer\u00E1 aqui" }))] })] }) }));
}
