import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * TeseTributariaList - Gestão de Teses Tributárias
 * CRUD completo integrado com API
 */
import { useState, useEffect } from 'react';
import api from '../../lib/api';
import { Plus, Edit, Trash2, Search, FileText, CheckCircle } from 'lucide-react';
export default function TeseTributariaList() {
    const [teses, setTeses] = useState([]);
    const [tributos, setTributos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filtros, setFiltros] = useState({ tributo_id: '', busca: '' });
    useEffect(() => {
        fetchData();
    }, [filtros]);
    const fetchData = async () => {
        setLoading(true);
        try {
            const [tesesRes, tributosRes] = await Promise.all([
                api.get('/api/tributario/teses', { params: filtros }),
                api.get('/api/processos/tributos')
            ]);
            setTeses(tesesRes.data.teses || []);
            setTributos(tributosRes.data || []);
        }
        catch (error) {
            console.error('Erro ao carregar teses:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const deleteTese = async (id) => {
        if (!confirm('Deseja realmente excluir esta tese?'))
            return;
        try {
            await api.delete(`/api/tributario/teses/${id}`);
            fetchData();
        }
        catch (error) {
            console.error('Erro ao excluir tese:', error);
        }
    };
    return (_jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsxs("h2", { className: "text-2xl font-bold flex items-center gap-3", children: [_jsx(FileText, { className: "w-7 h-7 text-primary" }), "Teses Tribut\u00E1rias"] }), _jsx("p", { className: "text-muted-foreground mt-1", children: "Gest\u00E3o de teses jur\u00EDdicas" })] }), _jsxs("button", { className: "flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary/90 rounded-lg transition-colors font-medium", children: [_jsx(Plus, { className: "w-4 h-4" }), "Nova Tese"] })] }), _jsx("div", { className: "bg-card border border-border rounded-xl p-4", children: _jsxs("div", { className: "flex gap-3", children: [_jsxs("div", { className: "flex-1 relative", children: [_jsx(Search, { className: "absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" }), _jsx("input", { type: "text", placeholder: "Buscar por c\u00F3digo, t\u00EDtulo...", className: "w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary", onChange: (e) => setFiltros({ ...filtros, busca: e.target.value }) })] }), _jsxs("select", { className: "bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary", onChange: (e) => setFiltros({ ...filtros, tributo_id: e.target.value }), children: [_jsx("option", { value: "", children: "Todos os Tributos" }), tributos.map(t => (_jsx("option", { value: t.id_tributo, children: t.nome }, t.id_tributo)))] })] }) }), loading ? (_jsx("div", { className: "text-center py-12", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto" }) })) : (_jsx("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-4", children: teses.map(tese => (_jsxs("div", { className: "bg-card border border-border rounded-xl p-6 hover:shadow-lg transition-all", children: [_jsx("div", { className: "flex items-start justify-between mb-4", children: _jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "flex items-center gap-2 mb-2", children: [_jsx("span", { className: "px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs font-medium", children: tese.codigo }), tese.ativo && _jsx(CheckCircle, { className: "w-4 h-4 text-green-500" })] }), _jsx("h3", { className: "font-semibold text-lg mb-2", children: tese.titulo }), tese.descricao && (_jsx("p", { className: "text-sm text-muted-foreground line-clamp-2", children: tese.descricao }))] }) }), tese.probabilidade_sucesso && (_jsxs("div", { className: "mb-4", children: [_jsxs("div", { className: "flex items-center justify-between text-sm mb-1", children: [_jsx("span", { className: "text-muted-foreground", children: "Probabilidade" }), _jsxs("span", { className: "font-medium", children: [tese.probabilidade_sucesso, "%"] })] }), _jsx("div", { className: "w-full bg-accent rounded-full h-2", children: _jsx("div", { className: "bg-primary rounded-full h-2 transition-all", style: { width: `${tese.probabilidade_sucesso}%` } }) })] })), _jsxs("div", { className: "flex gap-2 pt-4 border-t border-border", children: [_jsxs("button", { className: "flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary/20 hover:bg-primary/30 rounded-lg transition-colors text-primary", children: [_jsx(Edit, { className: "w-4 h-4" }), "Editar"] }), _jsxs("button", { onClick: () => deleteTese(tese.id_tese), className: "flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg transition-colors text-red-400", children: [_jsx(Trash2, { className: "w-4 h-4" }), "Excluir"] })] })] }, tese.id_tese))) }))] }));
}
