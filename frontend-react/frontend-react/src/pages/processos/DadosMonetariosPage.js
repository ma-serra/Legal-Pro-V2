import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * DadosMonetariosPage - Dashboard Completo BCB
 * Integração com APIs do Banco Central do Brasil
 * - SGS: Índices históricos
 * - Olinda PTAX: Cotações de câmbio
 * - Expectativas de Mercado (Focus)
 */
import { useState, useEffect } from 'react';
import { TrendingUp, DollarSign, Percent, RefreshCw, BarChart3, Globe, Target } from 'lucide-react';
import api from '../../lib/api';
export default function DadosMonetariosPage() {
    const [indices, setIndices] = useState([]);
    const [ptaxUSD, setPtaxUSD] = useState(null);
    const [ptaxEUR, setPtaxEUR] = useState(null);
    const [expectativas, setExpectativas] = useState({ selic: [], ipca: [], pib: [], cambio: [] });
    const [loading, setLoading] = useState(true);
    const [atualizando, setAtualizando] = useState(false);
    const [ultimaAtualizacao, setUltimaAtualizacao] = useState(null);
    useEffect(() => {
        carregarDados();
    }, []);
    const carregarDados = async () => {
        setLoading(true);
        try {
            // Carregar em paralelo
            const [indicesRes, ptaxUSDRes, ptaxEURRes, expectativasRes] = await Promise.allSettled([
                api.get('/api/atualizacao-monetaria/indices'),
                api.get('/api/bcb/ptax/hoje?moeda=USD'),
                api.get('/api/bcb/ptax/hoje?moeda=EUR'),
                api.get('/api/bcb/expectativas/resumo')
            ]);
            if (indicesRes.status === 'fulfilled') {
                setIndices(indicesRes.value.data);
            }
            if (ptaxUSDRes.status === 'fulfilled') {
                setPtaxUSD(ptaxUSDRes.value.data);
            }
            if (ptaxEURRes.status === 'fulfilled') {
                setPtaxEUR(ptaxEURRes.value.data);
            }
            if (expectativasRes.status === 'fulfilled') {
                setExpectativas(expectativasRes.value.data);
            }
            setUltimaAtualizacao(new Date());
        }
        catch (error) {
            console.error('Erro ao carregar dados:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const atualizarIndices = async () => {
        setAtualizando(true);
        try {
            await api.post('/api/atualizacao-monetaria/atualizar/recentes', { dias: 30 });
            await carregarDados();
        }
        catch (error) {
            console.error('Erro ao atualizar:', error);
        }
        finally {
            setAtualizando(false);
        }
    };
    // Formatadores padrão BCB
    const formatarMoeda = (valor, casas = 4) => {
        return valor.toLocaleString('pt-BR', {
            minimumFractionDigits: casas,
            maximumFractionDigits: casas
        });
    };
    const formatarPercentual = (valor, casas = 2) => {
        return `${valor.toLocaleString('pt-BR', {
            minimumFractionDigits: casas,
            maximumFractionDigits: casas
        })}%`;
    };
    const formatarData = (data) => {
        if (!data)
            return '-';
        return new Date(data).toLocaleDateString('pt-BR');
    };
    const formatarDataHora = (data) => {
        return data.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };
    // Converter valor baseado no tipo
    const formatarValorIndice = (valor, nome) => {
        if (valor === null)
            return '-';
        // SELIC/CDI: taxa diária → anual
        if (nome === 'SELIC' || nome === 'CDI' || nome === 'SELIC-EFETIVA') {
            const anual = valor * 252;
            return `${formatarMoeda(anual, 2)}% a.a.`;
        }
        // TJLP já vem anual
        if (nome === 'TJLP') {
            return `${formatarMoeda(valor, 2)}% a.a.`;
        }
        // Câmbio
        if (nome.includes('DOLAR') || nome.includes('EURO')) {
            return `R$ ${formatarMoeda(valor, 4)}`;
        }
        // Demais: percentual mensal
        return `${formatarMoeda(valor, 2)}%`;
    };
    if (loading) {
        return (_jsx("div", { className: "flex items-center justify-center min-h-screen", children: _jsxs("div", { className: "text-center", children: [_jsx(RefreshCw, { className: "w-12 h-12 animate-spin text-primary mx-auto mb-4" }), _jsx("p", { className: "text-muted-foreground", children: "Carregando dados do Banco Central..." })] }) }));
    }
    return (_jsxs("div", { className: "p-6 max-w-[1800px] mx-auto space-y-8", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsxs("h1", { className: "text-3xl font-bold flex items-center gap-3", children: [_jsx(BarChart3, { className: "w-8 h-8 text-primary" }), "Dados Monet\u00E1rios BCB"] }), _jsxs("p", { className: "text-muted-foreground mt-1", children: ["Dados oficiais do Banco Central do Brasil", ultimaAtualizacao && (_jsxs("span", { className: "ml-2 text-xs", children: ["\u2022 \u00DAltima atualiza\u00E7\u00E3o: ", formatarDataHora(ultimaAtualizacao)] }))] })] }), _jsxs("button", { onClick: atualizarIndices, disabled: atualizando, className: "px-5 py-2.5 bg-primary hover:bg-primary/90 text-white rounded-lg flex items-center gap-2 disabled:opacity-50", children: [_jsx(RefreshCw, { className: `w-4 h-4 ${atualizando ? 'animate-spin' : ''}` }), atualizando ? 'Atualizando...' : 'Atualizar Dados'] })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-6", children: [_jsxs("div", { className: "bg-gradient-to-br from-green-500/20 to-emerald-500/10 border border-green-500/30 rounded-2xl p-6", children: [_jsxs("div", { className: "flex items-center justify-between mb-4", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "p-3 bg-green-500/20 rounded-xl", children: _jsx(DollarSign, { className: "w-8 h-8 text-green-400" }) }), _jsxs("div", { children: [_jsx("h2", { className: "text-xl font-bold", children: "D\u00F3lar PTAX" }), _jsx("p", { className: "text-sm text-muted-foreground", children: ptaxUSD ? formatarData(ptaxUSD.data) : 'Carregando...' })] })] }), _jsx("span", { className: "px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-medium", children: "USD/BRL" })] }), ptaxUSD ? (_jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { className: "bg-background/50 rounded-xl p-4", children: [_jsx("p", { className: "text-sm text-muted-foreground mb-1", children: "Compra" }), _jsxs("p", { className: "text-3xl font-bold text-green-400", children: ["R$ ", formatarMoeda(ptaxUSD.cotacao_compra)] })] }), _jsxs("div", { className: "bg-background/50 rounded-xl p-4", children: [_jsx("p", { className: "text-sm text-muted-foreground mb-1", children: "Venda" }), _jsxs("p", { className: "text-3xl font-bold", children: ["R$ ", formatarMoeda(ptaxUSD.cotacao_venda)] })] })] })) : (_jsx("div", { className: "text-center py-8 text-muted-foreground", children: "Cota\u00E7\u00E3o n\u00E3o dispon\u00EDvel" }))] }), _jsxs("div", { className: "bg-gradient-to-br from-blue-500/20 to-indigo-500/10 border border-blue-500/30 rounded-2xl p-6", children: [_jsxs("div", { className: "flex items-center justify-between mb-4", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "p-3 bg-blue-500/20 rounded-xl", children: _jsx(Globe, { className: "w-8 h-8 text-blue-400" }) }), _jsxs("div", { children: [_jsx("h2", { className: "text-xl font-bold", children: "Euro PTAX" }), _jsx("p", { className: "text-sm text-muted-foreground", children: ptaxEUR ? formatarData(ptaxEUR.data) : 'Carregando...' })] })] }), _jsx("span", { className: "px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm font-medium", children: "EUR/BRL" })] }), ptaxEUR ? (_jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { className: "bg-background/50 rounded-xl p-4", children: [_jsx("p", { className: "text-sm text-muted-foreground mb-1", children: "Compra" }), _jsxs("p", { className: "text-3xl font-bold text-blue-400", children: ["R$ ", formatarMoeda(ptaxEUR.cotacao_compra)] })] }), _jsxs("div", { className: "bg-background/50 rounded-xl p-4", children: [_jsx("p", { className: "text-sm text-muted-foreground mb-1", children: "Venda" }), _jsxs("p", { className: "text-3xl font-bold", children: ["R$ ", formatarMoeda(ptaxEUR.cotacao_venda)] })] })] })) : (_jsx("div", { className: "text-center py-8 text-muted-foreground", children: "Cota\u00E7\u00E3o n\u00E3o dispon\u00EDvel" }))] })] }), _jsxs("div", { className: "bg-card border border-border rounded-2xl p-6", children: [_jsxs("div", { className: "flex items-center gap-3 mb-6", children: [_jsx("div", { className: "p-2 bg-primary/20 rounded-lg", children: _jsx(Target, { className: "w-6 h-6 text-primary" }) }), _jsxs("div", { children: [_jsx("h2", { className: "text-xl font-bold", children: "Expectativas de Mercado" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Relat\u00F3rio Focus - Proje\u00E7\u00F5es dos analistas" })] })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4", children: [_jsxs("div", { className: "bg-background border border-border rounded-xl p-4", children: [_jsxs("h3", { className: "font-semibold text-orange-400 mb-3 flex items-center gap-2", children: [_jsx(Percent, { className: "w-4 h-4" }), "SELIC"] }), expectativas.selic[0] ? (_jsxs(_Fragment, { children: [_jsxs("p", { className: "text-2xl font-bold", children: [formatarPercentual(expectativas.selic[0].mediana), " a.a."] }), _jsxs("p", { className: "text-sm text-muted-foreground", children: ["Ref: ", expectativas.selic[0].data_referencia] }), _jsxs("div", { className: "mt-2 text-xs text-muted-foreground", children: ["M\u00EDn: ", formatarPercentual(expectativas.selic[0].minimo), " | M\u00E1x: ", formatarPercentual(expectativas.selic[0].maximo)] })] })) : _jsx("p", { className: "text-muted-foreground", children: "Sem dados" })] }), _jsxs("div", { className: "bg-background border border-border rounded-xl p-4", children: [_jsxs("h3", { className: "font-semibold text-red-400 mb-3 flex items-center gap-2", children: [_jsx(TrendingUp, { className: "w-4 h-4" }), "IPCA"] }), expectativas.ipca[0] ? (_jsxs(_Fragment, { children: [_jsx("p", { className: "text-2xl font-bold", children: formatarPercentual(expectativas.ipca[0].mediana) }), _jsxs("p", { className: "text-sm text-muted-foreground", children: ["Ref: ", expectativas.ipca[0].data_referencia] }), _jsxs("div", { className: "mt-2 text-xs text-muted-foreground", children: ["M\u00EDn: ", formatarPercentual(expectativas.ipca[0].minimo), " | M\u00E1x: ", formatarPercentual(expectativas.ipca[0].maximo)] })] })) : _jsx("p", { className: "text-muted-foreground", children: "Sem dados" })] }), _jsxs("div", { className: "bg-background border border-border rounded-xl p-4", children: [_jsxs("h3", { className: "font-semibold text-green-400 mb-3 flex items-center gap-2", children: [_jsx(BarChart3, { className: "w-4 h-4" }), "PIB"] }), expectativas.pib[0] ? (_jsxs(_Fragment, { children: [_jsx("p", { className: "text-2xl font-bold", children: formatarPercentual(expectativas.pib[0].mediana) }), _jsxs("p", { className: "text-sm text-muted-foreground", children: ["Ref: ", expectativas.pib[0].data_referencia] }), _jsxs("div", { className: "mt-2 text-xs text-muted-foreground", children: ["M\u00EDn: ", formatarPercentual(expectativas.pib[0].minimo), " | M\u00E1x: ", formatarPercentual(expectativas.pib[0].maximo)] })] })) : _jsx("p", { className: "text-muted-foreground", children: "Sem dados" })] }), _jsxs("div", { className: "bg-background border border-border rounded-xl p-4", children: [_jsxs("h3", { className: "font-semibold text-blue-400 mb-3 flex items-center gap-2", children: [_jsx(DollarSign, { className: "w-4 h-4" }), "C\u00E2mbio (USD)"] }), expectativas.cambio[0] ? (_jsxs(_Fragment, { children: [_jsxs("p", { className: "text-2xl font-bold", children: ["R$ ", formatarMoeda(expectativas.cambio[0].mediana, 2)] }), _jsxs("p", { className: "text-sm text-muted-foreground", children: ["Ref: ", expectativas.cambio[0].data_referencia] }), _jsxs("div", { className: "mt-2 text-xs text-muted-foreground", children: ["M\u00EDn: R$ ", formatarMoeda(expectativas.cambio[0].minimo, 2), " | M\u00E1x: R$ ", formatarMoeda(expectativas.cambio[0].maximo, 2)] })] })) : _jsx("p", { className: "text-muted-foreground", children: "Sem dados" })] })] })] }), _jsxs("div", { className: "bg-card border border-border rounded-2xl p-6", children: [_jsxs("div", { className: "flex items-center justify-between mb-6", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "p-2 bg-primary/20 rounded-lg", children: _jsx(TrendingUp, { className: "w-6 h-6 text-primary" }) }), _jsxs("div", { children: [_jsx("h2", { className: "text-xl font-bold", children: "\u00CDndices Econ\u00F4micos (SGS)" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Sistema Gerenciador de S\u00E9ries Temporais" })] })] }), _jsx("a", { href: "/processos/indices", className: "text-primary hover:underline text-sm", children: "Ver hist\u00F3rico completo \u2192" })] }), _jsx("div", { className: "grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4", children: indices.map(indice => (_jsxs("div", { className: "bg-background border border-border rounded-xl p-4 hover:border-primary/50 transition-colors", children: [_jsx("h3", { className: "font-semibold text-sm mb-2 truncate", title: indice.nome, children: indice.nome }), _jsx("p", { className: "text-xl font-bold text-primary mb-1", children: formatarValorIndice(indice.ultimo_valor, indice.nome) }), _jsx("p", { className: "text-xs text-muted-foreground", children: indice.ultima_atualizacao ? formatarData(indice.ultima_atualizacao) : 'Sem dados' }), _jsxs("p", { className: "text-xs text-muted-foreground mt-1", children: [indice.total_registros, " registros"] })] }, indice.id))) })] }), _jsx("div", { className: "bg-blue-500/10 border border-blue-500/30 rounded-xl p-4", children: _jsxs("div", { className: "flex items-start gap-3", children: [_jsx(Globe, { className: "w-5 h-5 text-blue-400 mt-0.5" }), _jsxs("div", { className: "text-sm", children: [_jsx("p", { className: "font-medium text-blue-300 mb-1", children: "Fonte Oficial: Banco Central do Brasil" }), _jsx("p", { className: "text-blue-200/80", children: "Dados obtidos via APIs oficiais: SGS (S\u00E9ries Temporais) e Olinda (PTAX, Expectativas Focus). Os valores s\u00E3o fornecidos com a mesma precis\u00E3o das fontes originais." })] })] }) })] }));
}
