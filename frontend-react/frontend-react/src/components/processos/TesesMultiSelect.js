import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * TesesMultiSelect - Componente para seleção múltipla de teses
 * Para uso no formulário de criação de processo
 */
import { useState, useEffect } from 'react';
import { X, Plus, Scale } from 'lucide-react';
import api from '../../lib/api';
export default function TesesMultiSelect({ tributoId, selectedTeses, onChange, disabled }) {
    const [tesesDisponiveis, setTesesDisponiveis] = useState([]);
    const [loading, setLoading] = useState(false);
    const [dropdownOpen, setDropdownOpen] = useState(false);
    useEffect(() => {
        if (tributoId) {
            carregarTeses();
        }
        else {
            setTesesDisponiveis([]);
        }
    }, [tributoId]);
    const carregarTeses = async () => {
        setLoading(true);
        try {
            const response = await api.get('/api/tributario/teses', {
                params: { tributo_id: tributoId }
            });
            setTesesDisponiveis(response.data || []);
        }
        catch (error) {
            console.error('Erro ao carregar teses:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const adicionarTese = (teseId) => {
        if (!selectedTeses.includes(teseId)) {
            onChange([...selectedTeses, teseId]);
        }
        setDropdownOpen(false);
    };
    const removerTese = (teseId) => {
        onChange(selectedTeses.filter(id => id !== teseId));
    };
    const tesesSelecionadasInfo = tesesDisponiveis.filter(t => selectedTeses.includes(t.id_tese));
    const tesesNaoSelecionadas = tesesDisponiveis.filter(t => !selectedTeses.includes(t.id_tese));
    return (_jsxs("div", { className: "space-y-3", children: [_jsxs("label", { className: "block text-sm font-medium mb-2 flex items-center gap-2", children: [_jsx(Scale, { className: "w-4 h-4 text-primary" }), "Teses Envolvidas"] }), _jsx("div", { className: "flex flex-wrap gap-2 min-h-[40px] p-2 bg-background border border-border rounded-lg", children: tesesSelecionadasInfo.length === 0 ? (_jsx("span", { className: "text-muted-foreground text-sm", children: tributoId ? 'Nenhuma tese selecionada' : 'Selecione um tributo primeiro' })) : (tesesSelecionadasInfo.map(tese => (_jsxs("span", { className: "inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary/20 text-primary rounded-full text-sm", children: [tese.codigo && _jsx("span", { className: "font-mono text-xs", children: tese.codigo }), tese.titulo, !disabled && (_jsx("button", { type: "button", onClick: () => removerTese(tese.id_tese), className: "hover:bg-primary/30 rounded-full p-0.5", children: _jsx(X, { className: "w-3 h-3" }) }))] }, tese.id_tese)))) }), tributoId && !disabled && (_jsxs("div", { className: "relative", children: [_jsxs("button", { type: "button", onClick: () => setDropdownOpen(!dropdownOpen), disabled: loading || tesesNaoSelecionadas.length === 0, className: "flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors", children: [_jsx(Plus, { className: "w-4 h-4" }), loading ? 'Carregando...' : 'Adicionar Tese'] }), dropdownOpen && tesesNaoSelecionadas.length > 0 && (_jsxs(_Fragment, { children: [_jsx("div", { className: "fixed inset-0 z-10", onClick: () => setDropdownOpen(false) }), _jsx("div", { className: "absolute top-full left-0 mt-1 w-96 max-h-60 overflow-y-auto bg-card border border-border rounded-lg shadow-xl z-20", children: tesesNaoSelecionadas.map(tese => (_jsxs("button", { type: "button", onClick: () => adicionarTese(tese.id_tese), className: "w-full text-left px-4 py-3 hover:bg-accent border-b border-border/50 last:border-0 transition-colors", children: [_jsxs("div", { className: "flex items-center gap-2", children: [tese.codigo && (_jsx("span", { className: "px-2 py-0.5 bg-primary/20 text-primary rounded text-xs font-mono", children: tese.codigo })), _jsx("span", { className: "font-medium", children: tese.titulo })] }), tese.probabilidade_sucesso !== undefined && (_jsxs("div", { className: "text-xs text-muted-foreground mt-1", children: ["Probabilidade de sucesso: ", tese.probabilidade_sucesso, "%"] }))] }, tese.id_tese))) })] }))] })), tributoId && !loading && tesesDisponiveis.length === 0 && (_jsx("p", { className: "text-xs text-yellow-500", children: "\u26A0\uFE0F Nenhuma tese cadastrada para este tributo. Cadastre teses em Processos \u2192 Teses Tribut\u00E1rias." }))] }));
}
