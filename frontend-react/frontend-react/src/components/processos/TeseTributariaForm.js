import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * TeseTributariaForm - CRUD de Teses
 * Modal para criar/editar teses tributárias
 */
import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import api from '../../lib/api';
import { X, Save, FileText, Percent } from 'lucide-react';
export default function TeseTributariaForm({ tese, onClose, onSave }) {
    const { register, handleSubmit, formState: { errors } } = useForm({
        defaultValues: tese || {}
    });
    const [tributos, setTributos] = useState([]);
    const [loading, setLoading] = useState(false);
    useEffect(() => {
        fetchTributos();
    }, []);
    const fetchTributos = async () => {
        try {
            const response = await api.get('/api/processos/tributos');
            setTributos(response.data || []);
        }
        catch (error) {
            console.error('Erro ao carregar tributos:', error);
        }
    };
    const onSubmit = async (data) => {
        setLoading(true);
        try {
            if (tese?.id_tese) {
                await api.put(`/api/tributario/teses/${tese.id_tese}`, data);
            }
            else {
                await api.post('/api/tributario/teses', data);
            }
            onSave();
            onClose();
        }
        catch (error) {
            console.error('Erro ao salvar tese:', error);
            alert('Erro ao salvar tese');
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsx("div", { className: "fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4", children: _jsxs("div", { className: "bg-card border border-border rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto", children: [_jsxs("div", { className: "sticky top-0 bg-card border-b border-border p-6 flex items-center justify-between", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "p-3 bg-blue-500/20 rounded-lg", children: _jsx(FileText, { className: "w-6 h-6 text-blue-400" }) }), _jsxs("div", { children: [_jsx("h2", { className: "text-2xl font-bold", children: tese ? 'Editar Tese' : 'Nova Tese Tributária' }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Cadastro de tese jur\u00EDdica" })] })] }), _jsx("button", { onClick: onClose, className: "p-2 hover:bg-accent rounded-lg transition-colors", children: _jsx(X, { className: "w-5 h-5" }) })] }), _jsxs("form", { onSubmit: handleSubmit(onSubmit), className: "p-6 space-y-6", children: [_jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsxs("label", { className: "block text-sm font-medium mb-2", children: ["C\u00F3digo * ", _jsx("span", { className: "text-muted-foreground text-xs", children: "(ex: TESE-001)" })] }), _jsx("input", { ...register('codigo', { required: 'Código é obrigatório' }), className: "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary", placeholder: "TESE-001" }), errors.codigo && _jsx("p", { className: "text-red-500 text-xs mt-1", children: errors.codigo.message })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Tributo" }), _jsxs("select", { ...register('tributo_id', { valueAsNumber: true }), className: "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary", children: [_jsx("option", { value: "", children: "Selecione..." }), tributos.map(t => (_jsx("option", { value: t.id_tributo, children: t.nome }, t.id_tributo)))] })] }), _jsxs("div", { className: "md:col-span-2", children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "T\u00EDtulo *" }), _jsx("input", { ...register('titulo', { required: 'Título é obrigatório' }), className: "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary", placeholder: "Descri\u00E7\u00E3o da tese" }), errors.titulo && _jsx("p", { className: "text-red-500 text-xs mt-1", children: errors.titulo.message })] }), _jsxs("div", { className: "md:col-span-2", children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Descri\u00E7\u00E3o" }), _jsx("textarea", { ...register('descricao'), rows: 3, className: "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary", placeholder: "Detalhes da tese..." })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Tema Repercuss\u00E3o Geral" }), _jsx("input", { ...register('tema_repercussao_geral'), className: "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary", placeholder: "Tema n\u00BA" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Tema Repetitivo" }), _jsx("input", { ...register('tema_repetitivo'), className: "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary", placeholder: "Tema n\u00BA" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Tribunal Origem" }), _jsxs("select", { ...register('tribunal_origem'), className: "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary", children: [_jsx("option", { value: "", children: "Selecione..." }), _jsx("option", { value: "STF", children: "STF" }), _jsx("option", { value: "STJ", children: "STJ" }), _jsx("option", { value: "TST", children: "TST" }), _jsx("option", { value: "TRF", children: "TRF" }), _jsx("option", { value: "TJ", children: "TJ" })] })] }), _jsxs("div", { children: [_jsxs("label", { className: "block text-sm font-medium mb-2 flex items-center gap-2", children: [_jsx(Percent, { className: "w-4 h-4" }), "Probabilidade de Sucesso"] }), _jsx("input", { type: "number", min: "0", max: "100", ...register('probabilidade_sucesso', { valueAsNumber: true }), className: "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary", placeholder: "0-100" })] }), _jsxs("div", { className: "md:col-span-2", children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Situa\u00E7\u00E3o" }), _jsxs("select", { ...register('situacao'), className: "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary", children: [_jsx("option", { value: "Pendente", children: "Pendente" }), _jsx("option", { value: "Favor\u00E1vel", children: "Favor\u00E1vel" }), _jsx("option", { value: "Desfavor\u00E1vel", children: "Desfavor\u00E1vel" }), _jsx("option", { value: "Parcial", children: "Parcial" })] })] }), _jsxs("div", { className: "md:col-span-2", children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Fundamenta\u00E7\u00E3o" }), _jsx("textarea", { ...register('fundamentacao'), rows: 4, className: "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary", placeholder: "Base legal e jurisprudencial..." })] })] }), _jsxs("div", { className: "flex gap-3 justify-end pt-6 border-t border-border", children: [_jsx("button", { type: "button", onClick: onClose, className: "px-6 py-2.5 bg-accent hover:bg-accent/80 rounded-lg transition-colors", children: "Cancelar" }), _jsxs("button", { type: "submit", disabled: loading, className: "flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary/90 rounded-lg transition-colors font-medium disabled:opacity-50", children: [_jsx(Save, { className: "w-4 h-4" }), loading ? 'Salvando...' : 'Salvar Tese'] })] })] })] }) }));
}
