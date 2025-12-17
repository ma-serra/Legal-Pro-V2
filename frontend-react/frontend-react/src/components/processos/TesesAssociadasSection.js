import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Scale, Plus, Trash2, RefreshCw, AlertCircle } from 'lucide-react';
import api from '../../lib/api';
export default function TesesAssociadasSection({ processoId, tributoId }) {
    const [teses, setTeses] = useState([]);
    const [tesesdisponiveis, setTesesdisponiveis] = useState([]);
    const [loading, setLoading] = useState(true);
    const [loadingTeses, setLoadingTeses] = useState(false);
    const [selectedTeseId, setSelectedTeseId] = useState(null);
    const [adicionando, setAdicionando] = useState(false);
    useEffect(() => {
        carregarTesesAssociadas();
        if (tributoId) {
            carregarTesesDisponiveis();
        }
    }, [processoId, tributoId]);
    const carregarTesesAssociadas = async () => {
        setLoading(true);
        try {
            const response = await api.get(`/api/tributario/processos/${processoId}/teses`);
            setTeses(response.data || []);
        }
        catch (error) {
            console.error('Erro ao carregar teses associadas:', error);
            if (error.response?.status !== 404) {
                // Ignora 404 (sem teses)
            }
        }
        finally {
            setLoading(false);
        }
    };
    const carregarTesesDisponiveis = async () => {
        setLoadingTeses(true);
        try {
            const response = await api.get(`/api/tributario/teses`, {
                params: { tributo_id: tributoId }
            });
            setTesesdisponiveis(response.data || []);
        }
        catch (error) {
            console.error('Erro ao carregar teses disponíveis:', error);
        }
        finally {
            setLoadingTeses(false);
        }
    };
    const adicionarTese = async () => {
        if (!selectedTeseId)
            return;
        setAdicionando(true);
        try {
            await api.post(`/api/tributario/processos/${processoId}/teses`, {
                tese_id: selectedTeseId
            });
            await carregarTesesAssociadas();
            setSelectedTeseId(null);
        }
        catch (error) {
            console.error('Erro ao associar tese:', error);
            alert(error.response?.data?.error || 'Erro ao associar tese');
        }
        finally {
            setAdicionando(false);
        }
    };
    const removerTese = async (teseId) => {
        if (!confirm('Deseja remover esta tese do processo?'))
            return;
        try {
            await api.delete(`/api/tributario/processos/${processoId}/teses/${teseId}`);
            await carregarTesesAssociadas();
        }
        catch (error) {
            console.error('Erro ao remover tese:', error);
            alert(error.response?.data?.error || 'Erro ao remover tese');
        }
    };
    const formatarData = (data) => {
        return new Date(data).toLocaleDateString('pt-BR');
    };
    return (_jsxs("div", { className: "bg-card border border-border rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center gap-2 mb-6", children: [_jsx(Scale, { className: "w-5 h-5 text-primary" }), _jsx("h3", { className: "font-semibold text-lg", children: "Teses Associadas" })] }), tributoId && (_jsxs("div", { className: "mb-6 pb-6 border-b border-border", children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Adicionar Tese" }), _jsxs("div", { className: "flex gap-2", children: [_jsxs("select", { value: selectedTeseId || '', onChange: (e) => setSelectedTeseId(parseInt(e.target.value) || null), disabled: loadingTeses || adicionando, className: "flex-1 bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none disabled:opacity-50", children: [_jsx("option", { value: "", children: loadingTeses ? 'Carregando teses...' : 'Selecione uma tese...' }), tesesdisponiveis.map(tese => (_jsxs("option", { value: tese.id_tese, children: [tese.codigo ? `${tese.codigo} - ` : '', tese.titulo, tese.probabilidade_sucesso ? ` (${tese.probabilidade_sucesso}%)` : ''] }, tese.id_tese)))] }), _jsx("button", { onClick: adicionarTese, disabled: !selectedTeseId || adicionando, className: "px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed", children: adicionando ? (_jsxs(_Fragment, { children: [_jsx(RefreshCw, { className: "w-4 h-4 animate-spin" }), "Adicionando..."] })) : (_jsxs(_Fragment, { children: [_jsx(Plus, { className: "w-4 h-4" }), "Adicionar"] })) })] })] })), loading ? (_jsxs("div", { className: "text-center py-8", children: [_jsx(RefreshCw, { className: "w-6 h-6 animate-spin text-muted-foreground mx-auto mb-2" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Carregando teses..." })] })) : teses.length === 0 ? (_jsxs("div", { className: "text-center py-8", children: [_jsx(AlertCircle, { className: "w-12 h-12 text-muted-foreground mx-auto mb-3" }), _jsx("p", { className: "text-sm text-muted-foreground", children: tributoId ? 'Nenhuma tese associada ao processo' : 'Configure o tributo do processo para associar teses' })] })) : (_jsx("div", { className: "space-y-3", children: teses.map(tese => (_jsxs("div", { className: "flex items-start justify-between p-4 bg-accent/30 border border-border/50 rounded-lg hover:border-primary/30 transition-colors", children: [_jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "flex items-center gap-2 mb-1", children: [tese.codigo && (_jsx("span", { className: "px-2 py-0.5 bg-primary/20 text-primary rounded text-xs font-mono", children: tese.codigo })), _jsx("h4", { className: "font-medium", children: tese.titulo })] }), _jsxs("div", { className: "flex items-center gap-4 text-sm text-muted-foreground", children: [tese.probabilidade_sucesso !== undefined && (_jsxs("span", { className: "flex items-center gap-1", children: [_jsx("span", { className: "text-green-500", children: "\u2713" }), "Probabilidade: ", tese.probabilidade_sucesso, "%"] })), tese.data_associacao && (_jsxs("span", { children: ["Associada em ", formatarData(tese.data_associacao)] }))] })] }), _jsx("button", { onClick: () => removerTese(tese.id_tese), className: "p-2 hover:bg-red-500/10 text-red-400 rounded-lg transition-colors", title: "Remover tese", children: _jsx(Trash2, { className: "w-4 h-4" }) })] }, tese.id_tese))) }))] }));
}
