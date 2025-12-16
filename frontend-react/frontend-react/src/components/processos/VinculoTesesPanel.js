import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * VinculoTesesPanel - Vinculação Tese-Processo
 * Gerencia teses vinculadas a um processo
 */
import { useState, useEffect } from 'react';
import api from '../../lib/api';
import { Plus, X, Check, Link as LinkIcon } from 'lucide-react';
export default function VinculoTesesPanel({ processoId }) {
    const [tesVinculadas, setTesesVinculadas] = useState([]);
    const [tesesDisponiveis, setTesesDisponiveis] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchTeses();
    }, [processoId]);
    const fetchTeses = async () => {
        setLoading(true);
        try {
            const [vinculadasRes, disponiveisRes] = await Promise.all([
                api.get(`/api/tributario/processos/${processoId}/teses`),
                api.get('/api/tributario/teses')
            ]);
            setTesesVinculadas(vinculadasRes.data || []);
            setTesesDisponiveis(disponiveisRes.data.teses || []);
        }
        catch (error) {
            console.error('Erro ao carregar teses:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const vincularTese = async (teseId) => {
        try {
            await api.post(`/api/tributario/processos/${processoId}/teses`, {
                tese_id: teseId,
                ordem: tesVinculadas.length + 1
            });
            fetchTeses();
            setShowModal(false);
        }
        catch (error) {
            console.error('Erro ao vincular tese:', error);
            alert('Erro ao vincular tese');
        }
    };
    const desvincularTese = async (teseId) => {
        if (!confirm('Deseja desvincular esta tese?'))
            return;
        try {
            await api.delete(`/api/tributario/processos/${processoId}/teses/${teseId}`);
            fetchTeses();
        }
        catch (error) {
            console.error('Erro ao desvincular:', error);
        }
    };
    const atualizarStatus = async (teseId, novoStatus) => {
        try {
            await api.put(`/api/tributario/processos/${processoId}/teses/${teseId}/status`, {
                status: novoStatus
            });
            fetchTeses();
        }
        catch (error) {
            console.error('Erro ao atualizar status:', error);
        }
    };
    if (loading) {
        return _jsx("div", { className: "animate-pulse bg-accent rounded-xl h-64" });
    }
    return (_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx(LinkIcon, { className: "w-5 h-5 text-primary" }), _jsx("h3", { className: "font-semibold", children: "Teses Vinculadas" }), _jsx("span", { className: "px-2 py-1 bg-primary/20 text-primary rounded-full text-xs", children: tesVinculadas.length })] }), _jsxs("button", { onClick: () => setShowModal(true), className: "flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors text-sm", children: [_jsx(Plus, { className: "w-4 h-4" }), "Vincular Tese"] })] }), tesVinculadas.length === 0 ? (_jsx("div", { className: "bg-accent rounded-xl p-8 text-center", children: _jsx("p", { className: "text-muted-foreground", children: "Nenhuma tese vinculada" }) })) : (_jsx("div", { className: "space-y-3", children: tesVinculadas.map((vinculo, index) => (_jsx("div", { className: "bg-card border border-border rounded-xl p-4 hover:shadow-lg transition-all", children: _jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "flex items-center gap-2 mb-2", children: [_jsxs("span", { className: "px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs font-medium", children: ["#", vinculo.ordem] }), _jsx("span", { className: "px-2 py-1 bg-primary/20 text-primary rounded text-xs", children: vinculo.tese.codigo }), _jsxs("select", { value: vinculo.status, onChange: (e) => atualizarStatus(vinculo.tese.id_tese, e.target.value), className: "px-2 py-1 bg-background border border-border rounded text-xs focus:outline-none focus:ring-2 focus:ring-primary", children: [_jsx("option", { value: "Aguardando", children: "Aguardando" }), _jsx("option", { value: "Em an\u00E1lise", children: "Em an\u00E1lise" }), _jsx("option", { value: "Aceita", children: "Aceita" }), _jsx("option", { value: "Rejeitada", children: "Rejeitada" })] })] }), _jsx("p", { className: "font-medium mb-1", children: vinculo.tese.titulo }), vinculo.tese.probabilidade_sucesso && (_jsxs("p", { className: "text-sm text-muted-foreground", children: ["Probabilidade: ", vinculo.tese.probabilidade_sucesso, "%"] }))] }), _jsx("button", { onClick: () => desvincularTese(vinculo.tese.id_tese), className: "p-2 hover:bg-red-500/20 rounded-lg transition-colors text-red-400", children: _jsx(X, { className: "w-4 h-4" }) })] }) }, vinculo.tese.id_tese))) })), showModal && (_jsx("div", { className: "fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4", children: _jsxs("div", { className: "bg-card border border-border rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col", children: [_jsxs("div", { className: "p-6 border-b border-border flex items-center justify-between", children: [_jsx("h3", { className: "text-xl font-bold", children: "Selecionar Tese" }), _jsx("button", { onClick: () => setShowModal(false), className: "p-2 hover:bg-accent rounded-lg", children: _jsx(X, { className: "w-5 h-5" }) })] }), _jsx("div", { className: "flex-1 overflow-y-auto p-6 space-y-3", children: tesesDisponiveis.filter((t) => !tesVinculadas.some(v => v.tese.id_tese === t.id_tese)).map((tese) => (_jsx("div", { className: "bg-background border border-border rounded-lg p-4 hover:border-primary transition-colors cursor-pointer", onClick: () => vincularTese(tese.id_tese), children: _jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "flex items-center gap-2 mb-2", children: [_jsx("span", { className: "px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs", children: tese.codigo }), tese.probabilidade_sucesso && (_jsxs("span", { className: "text-xs text-muted-foreground", children: [tese.probabilidade_sucesso, "% sucesso"] }))] }), _jsx("p", { className: "font-medium", children: tese.titulo })] }), _jsx(Check, { className: "w-5 h-5 text-primary" })] }) }, tese.id_tese))) })] }) }))] }));
}
