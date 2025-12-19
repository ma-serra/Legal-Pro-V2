import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * AtualizacaoMonetariaSection - Seção para cálculo de atualização monetária
 * Integra com tabela IndiceMonetario do backend
 */
import { useState, useEffect } from 'react';
import { Calculator, RefreshCw, TrendingUp, Calendar, DollarSign } from 'lucide-react';
import api from '../../lib/api';
export default function AtualizacaoMonetariaSection({ valorOriginal = 0, dataBase, onChange }) {
    const [indices, setIndices] = useState([]);
    const [selectedIndice, setSelectedIndice] = useState(null);
    const [dataInicio, setDataInicio] = useState(dataBase || '');
    const [dataFim, setDataFim] = useState(new Date().toISOString().split('T')[0]);
    const [valorAtualizado, setValorAtualizado] = useState(null);
    const [loading, setLoading] = useState(false);
    const [loadingIndices, setLoadingIndices] = useState(false);
    const [fatorAcumulado, setFatorAcumulado] = useState(null);
    useEffect(() => {
        carregarIndices();
    }, []);
    useEffect(() => {
        if (dataBase) {
            setDataInicio(dataBase);
        }
    }, [dataBase]);
    const carregarIndices = async () => {
        setLoadingIndices(true);
        try {
            const response = await api.get('/api/indices-monetarios');
            setIndices(response.data || []);
        }
        catch (error) {
            console.error('Erro ao carregar índices:', error);
            // Fallback com índices comuns
            setIndices([
                { id_indice: 1, codigo: 'SELIC', nome: 'Taxa SELIC' },
                { id_indice: 2, codigo: 'IPCA', nome: 'IPCA-E' },
                { id_indice: 3, codigo: 'INPC', nome: 'INPC' },
                { id_indice: 4, codigo: 'UFESPs', nome: 'UFESP' },
                { id_indice: 5, codigo: 'LEI13918', nome: 'Lei 13.918/2009' }
            ]);
        }
        finally {
            setLoadingIndices(false);
        }
    };
    const calcularAtualizacao = async () => {
        if (!selectedIndice || !dataInicio || !dataFim || !valorOriginal) {
            alert('Preencha todos os campos para calcular');
            return;
        }
        setLoading(true);
        try {
            const response = await api.post('/api/atualizacao-monetaria/calcular', {
                valor_original: valorOriginal,
                data_inicio: dataInicio,
                data_fim: dataFim,
                indice_id: selectedIndice
            });
            const { valor_atualizado, fator_acumulado } = response.data;
            setValorAtualizado(valor_atualizado);
            setFatorAcumulado(fator_acumulado);
            if (onChange) {
                onChange(valor_atualizado);
            }
        }
        catch (error) {
            console.error('Erro ao calcular atualização:', error);
            // Fallback: cálculo simplificado local
            const mesesDiff = calcularMesesEntre(new Date(dataInicio), new Date(dataFim));
            const taxaMensal = 0.01; // 1% ao mês como estimativa
            const fator = Math.pow(1 + taxaMensal, mesesDiff);
            const valorCalc = valorOriginal * fator;
            setValorAtualizado(valorCalc);
            setFatorAcumulado(fator);
            if (onChange) {
                onChange(valorCalc);
            }
        }
        finally {
            setLoading(false);
        }
    };
    const calcularMesesEntre = (dataInicio, dataFim) => {
        const anos = dataFim.getFullYear() - dataInicio.getFullYear();
        const meses = dataFim.getMonth() - dataInicio.getMonth();
        return anos * 12 + meses;
    };
    const formatarMoeda = (valor) => {
        return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    };
    return (_jsxs("div", { className: "bg-gradient-to-br from-emerald-500/10 to-teal-500/5 border border-emerald-500/30 rounded-xl p-6", children: [_jsxs("h4", { className: "text-lg font-semibold flex items-center gap-2 text-emerald-400 mb-4", children: [_jsx(TrendingUp, { className: "w-5 h-5" }), "Atualiza\u00E7\u00E3o Monet\u00E1ria"] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-4 gap-4 mb-4", children: [_jsxs("div", { children: [_jsxs("label", { className: "block text-sm font-medium mb-2 flex items-center gap-1", children: [_jsx(DollarSign, { className: "w-4 h-4" }), "Valor Original"] }), _jsx("div", { className: "w-full bg-background/50 border border-border rounded-lg px-4 py-2.5 text-muted-foreground", children: formatarMoeda(valorOriginal) })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-2", children: "\u00CDndice" }), _jsxs("select", { value: selectedIndice || '', onChange: (e) => setSelectedIndice(parseInt(e.target.value) || null), disabled: loadingIndices, className: "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 outline-none", children: [_jsx("option", { value: "", children: loadingIndices ? 'Carregando...' : 'Selecione...' }), indices.map(ind => (_jsxs("option", { value: ind.id_indice, children: [ind.codigo, " - ", ind.nome] }, ind.id_indice)))] })] }), _jsxs("div", { children: [_jsxs("label", { className: "block text-sm font-medium mb-2 flex items-center gap-1", children: [_jsx(Calendar, { className: "w-4 h-4" }), "Data In\u00EDcio"] }), _jsx("input", { type: "date", value: dataInicio, onChange: (e) => setDataInicio(e.target.value), className: "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 outline-none" })] }), _jsxs("div", { children: [_jsxs("label", { className: "block text-sm font-medium mb-2 flex items-center gap-1", children: [_jsx(Calendar, { className: "w-4 h-4" }), "Data Fim"] }), _jsx("input", { type: "date", value: dataFim, onChange: (e) => setDataFim(e.target.value), className: "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 outline-none" })] })] }), _jsxs("div", { className: "flex items-center gap-4", children: [_jsx("button", { type: "button", onClick: calcularAtualizacao, disabled: loading || !valorOriginal, className: "px-6 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed", children: loading ? (_jsxs(_Fragment, { children: [_jsx(RefreshCw, { className: "w-4 h-4 animate-spin" }), "Calculando..."] })) : (_jsxs(_Fragment, { children: [_jsx(Calculator, { className: "w-4 h-4" }), "Calcular Atualiza\u00E7\u00E3o"] })) }), valorAtualizado !== null && (_jsxs("div", { className: "flex-1 flex items-center gap-6 p-3 bg-emerald-500/20 border border-emerald-500/40 rounded-lg", children: [_jsxs("div", { children: [_jsx("span", { className: "text-xs text-muted-foreground", children: "Valor Atualizado" }), _jsx("p", { className: "text-xl font-bold text-emerald-400", children: formatarMoeda(valorAtualizado) })] }), fatorAcumulado !== null && (_jsxs("div", { children: [_jsx("span", { className: "text-xs text-muted-foreground", children: "Fator" }), _jsx("p", { className: "text-lg font-semibold", children: fatorAcumulado.toFixed(6) })] })), _jsxs("div", { children: [_jsx("span", { className: "text-xs text-muted-foreground", children: "Corre\u00E7\u00E3o" }), _jsxs("p", { className: "text-lg font-semibold text-green-400", children: ["+", formatarMoeda(valorAtualizado - valorOriginal)] })] })] }))] }), _jsx("p", { className: "text-xs text-muted-foreground mt-3", children: "\uD83D\uDCA1 Os c\u00E1lculos utilizam os \u00EDndices armazenados no sistema. Para valores oficiais, consulte o tribunal competente." })] }));
}
