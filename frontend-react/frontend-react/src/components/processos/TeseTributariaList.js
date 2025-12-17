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
    const [showModal, setShowModal] = useState(false);
    const [editingTese, setEditingTese] = useState(null);
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
    return (_jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsxs("h2", { className: "text-2xl font-bold flex items-center gap-3", children: [_jsx(FileText, { className: "w-7 h-7 text-primary" }), "Teses Tribut\u00E1rias"] }), _jsx("p", { className: "text-muted-foreground mt-1", children: "Gest\u00E3o de teses jur\u00EDdicas" })] }), _jsxs("button", { onClick: () => {
                            setEditingTese(null);
                            setShowModal(true);
                        }, className: "flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary/90 rounded-lg transition-colors font-medium", children: [_jsx(Plus, { className: "w-4 h-4" }), "Nova Tese"] })] }), _jsx("div", { className: "bg-card border border-border rounded-xl p-4", children: _jsxs("div", { className: "flex gap-3", children: [_jsxs("div", { className: "flex-1 relative", children: [_jsx(Search, { className: "absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" }), _jsx("input", { type: "text", placeholder: "Buscar por c\u00F3digo, t\u00EDtulo...", className: "w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary", onChange: (e) => setFiltros({ ...filtros, busca: e.target.value }) })] }), _jsxs("select", { className: "bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary", onChange: (e) => setFiltros({ ...filtros, tributo_id: e.target.value }), children: [_jsx("option", { value: "", children: "Todos os Tributos" }), tributos.map(t => (_jsx("option", { value: t.id_tributo, children: t.nome }, t.id_tributo)))] })] }) }), loading ? (_jsx("div", { className: "text-center py-12", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto" }) })) : (_jsx("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-4", children: teses.map(tese => (_jsxs("div", { className: "bg-card border border-border rounded-xl p-6 hover:shadow-lg transition-all", children: [_jsx("div", { className: "flex items-start justify-between mb-4", children: _jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "flex items-center gap-2 mb-2", children: [_jsx("span", { className: "px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs font-medium", children: tese.codigo }), tese.ativo && _jsx(CheckCircle, { className: "w-4 h-4 text-green-500" })] }), _jsx("h3", { className: "font-semibold text-lg mb-2", children: tese.titulo }), tese.descricao && (_jsx("p", { className: "text-sm text-muted-foreground line-clamp-2", children: tese.descricao }))] }) }), tese.probabilidade_sucesso && (_jsxs("div", { className: "mb-4", children: [_jsxs("div", { className: "flex items-center justify-between text-sm mb-1", children: [_jsx("span", { className: "text-muted-foreground", children: "Probabilidade" }), _jsxs("span", { className: "font-medium", children: [tese.probabilidade_sucesso, "%"] })] }), _jsx("div", { className: "w-full bg-accent rounded-full h-2", children: _jsx("div", { className: "bg-primary rounded-full h-2 transition-all", style: { width: `${tese.probabilidade_sucesso}%` } }) })] })), _jsxs("div", { className: "flex gap-2 pt-4 border-t border-border", children: [_jsxs("button", { onClick: () => {
                                        setEditingTese(tese);
                                        setShowModal(true);
                                    }, className: "flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary/20 hover:bg-primary/30 rounded-lg transition-colors text-primary", children: [_jsx(Edit, { className: "w-4 h-4" }), "Editar"] }), _jsxs("button", { onClick: () => deleteTese(tese.id_tese), className: "flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg transition-colors text-red-400", children: [_jsx(Trash2, { className: "w-4 h-4" }), "Excluir"] })] })] }, tese.id_tese))) })), showModal && (_jsx(TeseModal, { tese: editingTese, tributos: tributos, onClose: () => {
                    setShowModal(false);
                    setEditingTese(null);
                }, onSave: () => {
                    setShowModal(false);
                    setEditingTese(null);
                    fetchData();
                } }))] }));
}
// Modal Component
function TeseModal({ tese, tributos, onClose, onSave }) {
    const [formData, setFormData] = useState({
        codigo: tese?.codigo || '',
        titulo: tese?.titulo || '',
        descricao: tese?.descricao || '',
        tributo_id: tese?.tributo_id || '',
        probabilidade_sucesso: tese?.probabilidade_sucesso || '',
        fundamentacao: tese?.fundamentacao || '',
        ativo: tese?.ativo ?? true
    });
    const [saving, setSaving] = useState(false);
    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            if (tese) {
                await api.put(`/api/tributario/teses/${tese.id_tese}`, formData);
            }
            else {
                await api.post('/api/tributario/teses', formData);
            }
            onSave();
        }
        catch (error) {
            console.error('Erro ao salvar tese:', error);
            alert('Erro ao salvar tese');
        }
        finally {
            setSaving(false);
        }
    };
    return (_jsx("div", { className: "fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4", children: _jsxs("div", { className: "bg-card border border-border rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto", children: [_jsx("div", { className: "p-6 border-b border-border", children: _jsx("h3", { className: "text-xl font-bold", children: tese ? 'Editar Tese' : 'Nova Tese' }) }), _jsxs("form", { onSubmit: handleSubmit, className: "p-6 space-y-4", children: [_jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "C\u00F3digo" }), _jsx("input", { type: "text", required: true, value: formData.codigo, onChange: (e) => setFormData({ ...formData, codigo: e.target.value }), className: "w-full bg-background border border-border rounded-lg px-4 py-2" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Tributo" }), _jsxs("select", { required: true, value: formData.tributo_id, onChange: (e) => setFormData({ ...formData, tributo_id: e.target.value }), className: "w-full bg-background border border-border rounded-lg px-4 py-2", children: [_jsx("option", { value: "", children: "Selecione..." }), tributos.map(t => (_jsx("option", { value: t.id_tributo, children: t.nome }, t.id_tributo)))] })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "T\u00EDtulo" }), _jsx("input", { type: "text", required: true, value: formData.titulo, onChange: (e) => setFormData({ ...formData, titulo: e.target.value }), className: "w-full bg-background border border-border rounded-lg px-4 py-2" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Descri\u00E7\u00E3o" }), _jsx("textarea", { rows: 3, value: formData.descricao, onChange: (e) => setFormData({ ...formData, descricao: e.target.value }), className: "w-full bg-background border border-border rounded-lg px-4 py-2" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Probabilidade Sucesso (%)" }), _jsx("input", { type: "number", min: "0", max: "100", value: formData.probabilidade_sucesso, onChange: (e) => setFormData({ ...formData, probabilidade_sucesso: e.target.value }), className: "w-full bg-background border border-border rounded-lg px-4 py-2" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Fundamenta\u00E7\u00E3o Legal" }), _jsx("textarea", { rows: 4, value: formData.fundamentacao, onChange: (e) => setFormData({ ...formData, fundamentacao: e.target.value }), className: "w-full bg-background border border-border rounded-lg px-4 py-2", placeholder: "Fundamenta\u00E7\u00E3o, jurisprud\u00EAncia, teses relacionadas..." })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("input", { type: "checkbox", id: "ativo", checked: formData.ativo, onChange: (e) => setFormData({ ...formData, ativo: e.target.checked }), className: "w-4 h-4 rounded border-border text-primary focus:ring-primary" }), _jsx("label", { htmlFor: "ativo", className: "text-sm font-medium", children: "Tese Ativa" })] }), _jsxs("div", { className: "flex gap-3 pt-4", children: [_jsx("button", { type: "button", onClick: onClose, className: "flex-1 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors", children: "Cancelar" }), _jsx("button", { type: "submit", disabled: saving, className: "flex-1 px-4 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors disabled:opacity-50", children: saving ? 'Salvando...' : 'Salvar' })] })] })] }) }));
}
