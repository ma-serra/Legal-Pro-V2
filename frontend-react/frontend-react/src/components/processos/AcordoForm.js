import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * AcordoForm - Registro de Acordos (Trabalhista/Cível)
 * Componente genérico para ambas naturezas
 */
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import api from '../../lib/api';
import { X, Save, DollarSign, Calendar, AlertCircle } from 'lucide-react';
export default function AcordoForm({ processoId, natureza, tolerancia, onClose, onSave }) {
    const { register, handleSubmit, watch, formState: { errors } } = useForm();
    const [loading, setLoading] = useState(false);
    const [viabilidade, setViabilidade] = useState(null);
    const valorProposta = watch('valor_acordo');
    const verificarViabilidade = async () => {
        if (!valorProposta)
            return;
        try {
            const response = await api.post(`/api/${natureza}/processos/${processoId}/acordo/viabilidade`, { valor_proposta: parseFloat(valorProposta) });
            setViabilidade(response.data);
        }
        catch (error) {
            console.error('Erro ao verificar viabilidade:', error);
        }
    };
    const onSubmit = async (data) => {
        setLoading(true);
        try {
            await api.post(`/api/${natureza}/processos/${processoId}/acordo`, {
                valor_acordo: parseFloat(data.valor_acordo),
                data_acordo: data.data_acordo,
                observacoes: data.observacoes
            });
            onSave();
            onClose();
        }
        catch (error) {
            console.error('Erro ao registrar acordo:', error);
            alert('Erro ao registrar acordo');
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsx("div", { className: "fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4", children: _jsxs("div", { className: "bg-card border border-border rounded-2xl max-w-2xl w-full", children: [_jsxs("div", { className: "p-6 border-b border-border flex items-center justify-between", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "p-3 bg-green-500/20 rounded-lg", children: _jsx(DollarSign, { className: "w-6 h-6 text-green-400" }) }), _jsxs("div", { children: [_jsx("h2", { className: "text-2xl font-bold", children: "Registrar Acordo" }), _jsx("p", { className: "text-sm text-muted-foreground capitalize", children: natureza })] })] }), _jsx("button", { onClick: onClose, className: "p-2 hover:bg-accent rounded-lg transition-colors", children: _jsx(X, { className: "w-5 h-5" }) })] }), _jsxs("form", { onSubmit: handleSubmit(onSubmit), className: "p-6 space-y-6", children: [tolerancia && (_jsx("div", { className: "bg-blue-500/10 border border-blue-500/20 rounded-xl p-4", children: _jsxs("div", { className: "flex items-start gap-3", children: [_jsx(AlertCircle, { className: "w-5 h-5 text-blue-400 mt-0.5" }), _jsxs("div", { children: [_jsx("h4", { className: "font-semibold text-blue-400 mb-1", children: "Toler\u00E2ncia Configurada" }), _jsxs("p", { className: "text-sm text-muted-foreground", children: ["Valor m\u00E1ximo aceit\u00E1vel: ", new Intl.NumberFormat('pt-BR', {
                                                        style: 'currency',
                                                        currency: 'BRL'
                                                    }).format(tolerancia)] })] })] }) })), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsxs("label", { className: "block text-sm font-medium mb-2", children: ["Valor do Acordo * ", _jsx("span", { className: "text-muted-foreground text-xs", children: "(R$)" })] }), _jsxs("div", { className: "relative", children: [_jsx(DollarSign, { className: "absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" }), _jsx("input", { type: "number", step: "0.01", ...register('valor_acordo', { required: 'Valor é obrigatório' }), onBlur: verificarViabilidade, className: "w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary", placeholder: "0.00" })] }), errors.valor_acordo && (_jsx("p", { className: "text-red-500 text-xs mt-1", children: errors.valor_acordo.message }))] }), viabilidade && (_jsxs("div", { className: `${viabilidade.viavel
                                        ? 'bg-green-500/10 border-green-500/20'
                                        : 'bg-red-500/10 border-red-500/20'} border rounded-xl p-4`, children: [_jsx("p", { className: `font-semibold ${viabilidade.viavel ? 'text-green-400' : 'text-red-400'}`, children: viabilidade.mensagem }), viabilidade.percentual_tolerancia && (_jsxs("p", { className: "text-sm text-muted-foreground mt-1", children: [viabilidade.percentual_tolerancia.toFixed(1), "% da toler\u00E2ncia"] }))] })), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Data do Acordo *" }), _jsxs("div", { className: "relative", children: [_jsx(Calendar, { className: "absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" }), _jsx("input", { type: "date", ...register('data_acordo', { required: 'Data é obrigatória' }), className: "w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary" })] }), errors.data_acordo && (_jsx("p", { className: "text-red-500 text-xs mt-1", children: errors.data_acordo.message }))] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Observa\u00E7\u00F5es" }), _jsx("textarea", { ...register('observacoes'), rows: 3, className: "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary", placeholder: "Detalhes do acordo..." })] })] }), _jsxs("div", { className: "flex gap-3 justify-end pt-6 border-t border-border", children: [_jsx("button", { type: "button", onClick: onClose, className: "px-6 py-2.5 bg-accent hover:bg-accent/80 rounded-lg transition-colors", children: "Cancelar" }), _jsxs("button", { type: "submit", disabled: loading || (viabilidade && !viabilidade.viavel), className: "flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary/90 rounded-lg transition-colors font-medium disabled:opacity-50", children: [_jsx(Save, { className: "w-4 h-4" }), loading ? 'Salvando...' : 'Registrar Acordo'] })] })] })] }) }));
}
