import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Save, AlertCircle, Calculator, RefreshCw } from 'lucide-react';
import api from '../../lib/api';
export default function PrognosticoTab({ processoId }) {
    const [prognostico, setPrognostico] = useState({});
    const [valorEsperado, setValorEsperado] = useState(null);
    const [loading, setLoading] = useState(true);
    const [salvando, setSalvando] = useState(false);
    const [erro, setErro] = useState(null);
    useEffect(() => {
        carregarPrognostico();
    }, [processoId]);
    useEffect(() => {
        calcularValorEsperado();
    }, [prognostico]);
    const carregarPrognostico = async () => {
        setLoading(true);
        try {
            const response = await api.get(`/api/tributario/processos/${processoId}/prognostico`);
            setPrognostico(response.data || {});
            // Carregar valor esperado
            try {
                const veResponse = await api.get(`/api/tributario/processos/${processoId}/valor-esperado`);
                setValorEsperado(veResponse.data?.valor_esperado);
            }
            catch {
                // Ignorar erro valor esperado
            }
        }
        catch (error) {
            if (error.response?.status !== 404) {
                console.error('Erro ao carregar prognóstico:', error);
            }
        }
        finally {
            setLoading(false);
        }
    };
    const calcularValorEsperado = () => {
        const probProv = prognostico.probabilidade_provavel || 0;
        const probPoss = prognostico.probabilidade_possivel || 0;
        const probRem = prognostico.probabilidade_remota || 0;
        const valProv = prognostico.valor_provavel || 0;
        const valPoss = prognostico.valor_possivel || 0;
        const valRem = prognostico.valor_remoto || 0;
        if (probProv === 0 && probPoss === 0 && probRem === 0) {
            setValorEsperado(null);
            return;
        }
        const ve = (probProv * valProv + probPoss * valPoss + probRem * valRem) / 100;
        setValorEsperado(ve);
    };
    const handleChange = (field, value) => {
        setPrognostico(prev => ({
            ...prev,
            [field]: value
        }));
    };
    const validarPrognostico = () => {
        const probProv = prognostico.probabilidade_provavel || 0;
        const probPoss = prognostico.probabilidade_possivel || 0;
        const probRem = prognostico.probabilidade_remota || 0;
        const soma = probProv + probPoss + probRem;
        if (soma > 100) {
            setErro('A soma das probabilidades não pode exceder 100%');
            return false;
        }
        if (soma === 0) {
            setErro('Preencha pelo menos uma probabilidade');
            return false;
        }
        setErro(null);
        return true;
    };
    const salvarPrognostico = async () => {
        if (!validarPrognostico())
            return;
        setSalvando(true);
        try {
            await api.post(`/api/tributario/processos/${processoId}/prognostico`, prognostico);
            // Recarregar valor esperado do backend
            const response = await api.get(`/api/tributario/processos/${processoId}/valor-esperado`);
            setValorEsperado(response.data?.valor_esperado);
            alert('Prognóstico salvo com sucesso!');
        }
        catch (error) {
            console.error('Erro ao salvar prognóstico:', error);
            setErro(error.response?.data?.error || 'Erro ao salvar prognóstico');
        }
        finally {
            setSalvando(false);
        }
    };
    const formatarMoeda = (valor) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
    };
    if (loading) {
        return (_jsx("div", { className: "flex items-center justify-center py-12", children: _jsx(RefreshCw, { className: "w-6 h-6 animate-spin text-muted-foreground" }) }));
    }
    return (_jsxs("div", { className: "space-y-6", children: [erro && (_jsxs("div", { className: "bg-red-500/10 border border-red-500/20 rounded-lg p-4 flex items-start gap-3", children: [_jsx(AlertCircle, { className: "w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" }), _jsx("p", { className: "text-sm text-red-400", children: erro })] })), _jsxs("div", { className: "bg-green-500/5 border border-green-500/20 rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center gap-2 mb-4", children: [_jsx("div", { className: "w-2 h-2 bg-green-500 rounded-full" }), _jsx("h3", { className: "font-semibold text-lg", children: "Cen\u00E1rio Prov\u00E1vel" })] }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Tese/Descri\u00E7\u00E3o" }), _jsx("textarea", { value: prognostico.tese_provavel || '', onChange: (e) => handleChange('tese_provavel', e.target.value), className: "w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none", rows: 3, placeholder: "Descreva a tese..." })] }), _jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Probabilidade (%)" }), _jsx("input", { type: "range", min: "0", max: "100", value: prognostico.probabilidade_provavel || 0, onChange: (e) => handleChange('probabilidade_provavel', parseInt(e.target.value)), className: "w-full mb-2" }), _jsxs("div", { className: "text-center text-2xl font-bold text-green-500", children: [prognostico.probabilidade_provavel || 0, "%"] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Valor (R$)" }), _jsx("input", { type: "number", value: prognostico.valor_provavel || '', onChange: (e) => handleChange('valor_provavel', parseFloat(e.target.value) || 0), className: "w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none", placeholder: "0,00", step: "0.01" })] })] })] })] }), _jsxs("div", { className: "bg-yellow-500/5 border border-yellow-500/20 rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center gap-2 mb-4", children: [_jsx("div", { className: "w-2 h-2 bg-yellow-500 rounded-full" }), _jsx("h3", { className: "font-semibold text-lg", children: "Cen\u00E1rio Poss\u00EDvel" })] }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Tese/Descri\u00E7\u00E3o" }), _jsx("textarea", { value: prognostico.tese_possivel || '', onChange: (e) => handleChange('tese_possivel', e.target.value), className: "w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none", rows: 3, placeholder: "Descreva a tese..." })] }), _jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Probabilidade (%)" }), _jsx("input", { type: "range", min: "0", max: "100", value: prognostico.probabilidade_possivel || 0, onChange: (e) => handleChange('probabilidade_possivel', parseInt(e.target.value)), className: "w-full mb-2" }), _jsxs("div", { className: "text-center text-2xl font-bold text-yellow-500", children: [prognostico.probabilidade_possivel || 0, "%"] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Valor (R$)" }), _jsx("input", { type: "number", value: prognostico.valor_possivel || '', onChange: (e) => handleChange('valor_possivel', parseFloat(e.target.value) || 0), className: "w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none", placeholder: "0,00", step: "0.01" })] })] })] })] }), _jsxs("div", { className: "bg-red-500/5 border border-red-500/20 rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center gap-2 mb-4", children: [_jsx("div", { className: "w-2 h-2 bg-red-500 rounded-full" }), _jsx("h3", { className: "font-semibold text-lg", children: "Cen\u00E1rio Remoto" })] }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Tese/Descri\u00E7\u00E3o" }), _jsx("textarea", { value: prognostico.tese_remota || '', onChange: (e) => handleChange('tese_remota', e.target.value), className: "w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none", rows: 3, placeholder: "Descreva a tese..." })] }), _jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Probabilidade (%)" }), _jsx("input", { type: "range", min: "0", max: "100", value: prognostico.probabilidade_remota || 0, onChange: (e) => handleChange('probabilidade_remota', parseInt(e.target.value)), className: "w-full mb-2" }), _jsxs("div", { className: "text-center text-2xl font-bold text-red-500", children: [prognostico.probabilidade_remota || 0, "%"] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "Valor (R$)" }), _jsx("input", { type: "number", value: prognostico.valor_remoto || '', onChange: (e) => handleChange('valor_remoto', parseFloat(e.target.value) || 0), className: "w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none", placeholder: "0,00", step: "0.01" })] })] })] })] }), valorEsperado !== null && (_jsxs("div", { className: "bg-gradient-to-br from-primary/10 to-primary/5 border-2 border-primary/30 rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center gap-3 mb-4", children: [_jsx(Calculator, { className: "w-6 h-6 text-primary" }), _jsx("h3", { className: "font-semibold text-lg", children: "Valor Esperado Calculado" })] }), _jsxs("div", { className: "text-center", children: [_jsx("div", { className: "text-4xl font-bold text-primary mb-4", children: formatarMoeda(valorEsperado) }), _jsxs("div", { className: "text-sm text-muted-foreground space-y-1", children: [_jsx("p", { children: "C\u00E1lculo: (Prob \u00D7 Valor) de cada cen\u00E1rio" }), _jsxs("p", { className: "font-mono text-xs", children: ["= (", prognostico.probabilidade_provavel || 0, "% \u00D7 ", formatarMoeda(prognostico.valor_provavel || 0), ") + (", prognostico.probabilidade_possivel || 0, "% \u00D7 ", formatarMoeda(prognostico.valor_possivel || 0), ") + (", prognostico.probabilidade_remota || 0, "% \u00D7 ", formatarMoeda(prognostico.valor_remoto || 0), ")"] })] })] })] })), _jsx("div", { className: "flex justify-end pt-4", children: _jsx("button", { onClick: salvarPrognostico, disabled: salvando, className: "px-6 py-3 bg-primary hover:bg-primary/90 text-white rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 font-semibold", children: salvando ? (_jsxs(_Fragment, { children: [_jsx(RefreshCw, { className: "w-5 h-5 animate-spin" }), "Salvando..."] })) : (_jsxs(_Fragment, { children: [_jsx(Save, { className: "w-5 h-5" }), "Salvar Progn\u00F3stico"] })) }) })] }));
}
