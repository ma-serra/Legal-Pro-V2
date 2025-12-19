import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * Dashboard Completo - Índices Econômicos e Dados BCB
 * Integração com APIs do Banco Central:
 * - SGS: Séries Temporais (SELIC, IPCA, INPC, etc.)
 * - Olinda PTAX: Cotações de Câmbio
 * - Expectativas de Mercado (Focus)
 */
import { useState, useEffect } from 'react';
import { Calendar, RefreshCw, DollarSign, BarChart3, Clock, Globe, Target } from 'lucide-react';
import api from '../../lib/api';
import IndicesChart from '../../components/processos/IndicesChart';
export default function IndicesEconomicosPage() {
    const [indices, setIndices] = useState([]);
    const [indiceSelecionado, setIndiceSelecionado] = useState(null);
    const [historico, setHistorico] = useState([]);
    const [carregando, setCarregando] = useState(true);
    const [atualizando, setAtualizando] = useState(false);
    const [filtroTempo, setFiltroTempo] = useState('30d');
    // Novos estados para PTAX e Expectativas
    const [ptaxUSD, setPtaxUSD] = useState(null);
    const [ptaxEUR, setPtaxEUR] = useState(null);
    const [expectativas, setExpectativas] = useState({ selic: [], ipca: [], pib: [], cambio: [] });
    const [abaAtiva, setAbaAtiva] = useState('indices');
    useEffect(() => {
        carregarTodosDados();
    }, []);
    useEffect(() => {
        if (indiceSelecionado) {
            carregarHistorico(indiceSelecionado);
        }
    }, [indiceSelecionado, filtroTempo]);
    const carregarTodosDados = async () => {
        setCarregando(true);
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
                const selic = indicesRes.value.data.find((i) => i.nome === 'SELIC');
                if (selic)
                    setIndiceSelecionado(selic.id);
            }
            if (ptaxUSDRes.status === 'fulfilled' && !ptaxUSDRes.value.data.erro) {
                setPtaxUSD(ptaxUSDRes.value.data);
            }
            if (ptaxEURRes.status === 'fulfilled' && !ptaxEURRes.value.data.erro) {
                setPtaxEUR(ptaxEURRes.value.data);
            }
            if (expectativasRes.status === 'fulfilled') {
                setExpectativas(expectativasRes.value.data);
            }
        }
        catch (error) {
            console.error('Erro ao carregar dados:', error);
        }
        finally {
            setCarregando(false);
        }
    };
    const carregarHistorico = async (indiceId) => {
        try {
            const params = { limite: 365 };
            const hoje = new Date();
            let dataInicio = new Date();
            if (filtroTempo === '30d')
                dataInicio.setDate(dataInicio.getDate() - 30);
            else if (filtroTempo === '90d')
                dataInicio.setDate(dataInicio.getDate() - 90);
            else if (filtroTempo === '1y')
                dataInicio.setFullYear(dataInicio.getFullYear() - 1);
            if (filtroTempo !== 'all') {
                params.data_inicio = dataInicio.toISOString().split('T')[0];
            }
            const response = await api.get(`/api/atualizacao-monetaria/indices/${indiceId}/historico`, { params });
            setHistorico(response.data);
        }
        catch (error) {
            console.error('Erro ao carregar histórico:', error);
        }
    };
    const atualizarIndices = async () => {
        setAtualizando(true);
        try {
            await api.post('/api/atualizacao-monetaria/atualizar/recentes', { dias: 30 });
            await carregarTodosDados();
            alert('Índices atualizados com sucesso!');
        }
        catch (error) {
            console.error('Erro ao atualizar índices:', error);
            alert('Erro ao atualizar índices');
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
    const formatarData = (data) => {
        if (!data)
            return '-';
        return new Date(data).toLocaleDateString('pt-BR');
    };
    const formatarValor = (valor, indice) => {
        if (indice === 'SELIC' || indice === 'CDI' || indice === 'SELIC-EFETIVA') {
            const taxaAnual = valor * 252;
            return `${taxaAnual.toFixed(2)}% a.a.`;
        }
        if (indice === 'TJLP')
            return `${valor.toFixed(2)}% a.a.`;
        if (indice.includes('DOLAR') || indice.includes('EURO'))
            return `R$ ${formatarMoeda(valor)}`;
        return `${valor.toFixed(2)}% mês`;
    };
    if (carregando) {
        return (_jsx("div", { className: "flex items-center justify-center min-h-screen", children: _jsxs("div", { className: "text-center", children: [_jsx(RefreshCw, { className: "w-12 h-12 animate-spin text-primary mx-auto mb-4" }), _jsx("p", { className: "text-muted-foreground", children: "Carregando dados do Banco Central..." })] }) }));
    }
    const indiceInfo = indices.find(i => i.id === indiceSelecionado);
    return (_jsxs("div", { className: "p-6 max-w-[1600px] mx-auto space-y-6", children: [_jsxs("div", { className: "flex items-center justify-between flex-wrap gap-4", children: [_jsxs("div", { children: [_jsxs("h1", { className: "text-3xl font-bold flex items-center gap-3", children: [_jsx(BarChart3, { className: "w-8 h-8 text-primary" }), "Dados Monet\u00E1rios BCB"] }), _jsx("p", { className: "text-muted-foreground mt-1", children: "Dados oficiais do Banco Central do Brasil - Atualiza\u00E7\u00E3o em tempo real" })] }), _jsxs("button", { onClick: atualizarIndices, disabled: atualizando, className: "px-5 py-2.5 bg-primary hover:bg-primary/90 text-white rounded-lg flex items-center gap-2 disabled:opacity-50", children: [_jsx(RefreshCw, { className: `w-4 h-4 ${atualizando ? 'animate-spin' : ''}` }), atualizando ? 'Atualizando...' : 'Atualizar Dados'] })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { className: "bg-gradient-to-br from-green-500/20 to-emerald-500/10 border border-green-500/30 rounded-xl p-5", children: [_jsxs("div", { className: "flex items-center justify-between mb-3", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx(DollarSign, { className: "w-6 h-6 text-green-400" }), _jsx("h2", { className: "font-bold", children: "D\u00F3lar PTAX" })] }), _jsx("span", { className: "text-xs text-muted-foreground", children: ptaxUSD ? formatarData(ptaxUSD.data) : '-' })] }), ptaxUSD ? (_jsxs("div", { className: "grid grid-cols-2 gap-3", children: [_jsxs("div", { children: [_jsx("p", { className: "text-xs text-muted-foreground", children: "Compra" }), _jsxs("p", { className: "text-2xl font-bold text-green-400", children: ["R$ ", formatarMoeda(ptaxUSD.cotacao_compra)] })] }), _jsxs("div", { children: [_jsx("p", { className: "text-xs text-muted-foreground", children: "Venda" }), _jsxs("p", { className: "text-2xl font-bold", children: ["R$ ", formatarMoeda(ptaxUSD.cotacao_venda)] })] })] })) : (_jsx("p", { className: "text-muted-foreground", children: "Cota\u00E7\u00E3o n\u00E3o dispon\u00EDvel" }))] }), _jsxs("div", { className: "bg-gradient-to-br from-blue-500/20 to-indigo-500/10 border border-blue-500/30 rounded-xl p-5", children: [_jsxs("div", { className: "flex items-center justify-between mb-3", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx(Globe, { className: "w-6 h-6 text-blue-400" }), _jsx("h2", { className: "font-bold", children: "Euro PTAX" })] }), _jsx("span", { className: "text-xs text-muted-foreground", children: ptaxEUR ? formatarData(ptaxEUR.data) : '-' })] }), ptaxEUR ? (_jsxs("div", { className: "grid grid-cols-2 gap-3", children: [_jsxs("div", { children: [_jsx("p", { className: "text-xs text-muted-foreground", children: "Compra" }), _jsxs("p", { className: "text-2xl font-bold text-blue-400", children: ["R$ ", formatarMoeda(ptaxEUR.cotacao_compra)] })] }), _jsxs("div", { children: [_jsx("p", { className: "text-xs text-muted-foreground", children: "Venda" }), _jsxs("p", { className: "text-2xl font-bold", children: ["R$ ", formatarMoeda(ptaxEUR.cotacao_venda)] })] })] })) : (_jsx("p", { className: "text-muted-foreground", children: "Cota\u00E7\u00E3o n\u00E3o dispon\u00EDvel" }))] })] }), _jsxs("div", { className: "bg-card border border-border rounded-xl p-5", children: [_jsxs("div", { className: "flex items-center gap-2 mb-4", children: [_jsx(Target, { className: "w-5 h-5 text-primary" }), _jsx("h2", { className: "font-bold", children: "Expectativas de Mercado (Focus)" })] }), _jsx("div", { className: "grid grid-cols-2 md:grid-cols-4 gap-3", children: [
                            { key: 'selic', label: 'SELIC', cor: 'orange', sufixo: '% a.a.' },
                            { key: 'ipca', label: 'IPCA', cor: 'red', sufixo: '%' },
                            { key: 'pib', label: 'PIB', cor: 'green', sufixo: '%' },
                            { key: 'cambio', label: 'Câmbio', cor: 'blue', prefixo: 'R$ ' }
                        ].map(({ key, label, cor, sufixo, prefixo }) => {
                            const dados = expectativas[key]?.[0];
                            return (_jsxs("div", { className: "bg-background border border-border rounded-lg p-3", children: [_jsx("h3", { className: `font-semibold text-${cor}-400 text-sm mb-2`, children: label }), dados ? (_jsxs(_Fragment, { children: [_jsxs("p", { className: "text-xl font-bold", children: [prefixo || '', formatarMoeda(dados.mediana, 2), sufixo || ''] }), _jsx("p", { className: "text-xs text-muted-foreground", children: dados.data_referencia })] })) : _jsx("p", { className: "text-muted-foreground text-sm", children: "Sem dados" })] }, key));
                        }) })] }), _jsx("div", { className: "grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6 gap-3", children: indices.map((indice) => (_jsxs("button", { onClick: () => setIndiceSelecionado(indice.id), className: `bg-card border-2 rounded-xl p-4 text-left transition-all hover:shadow-lg ${indiceSelecionado === indice.id
                        ? 'border-primary shadow-lg'
                        : 'border-border hover:border-primary/50'}`, children: [_jsx("h3", { className: "font-bold text-sm truncate", children: indice.nome }), _jsx("p", { className: "text-xs text-muted-foreground truncate mb-2", children: indice.descricao }), indice.ultimo_valor ? (_jsxs(_Fragment, { children: [_jsx("p", { className: "text-lg font-bold text-primary", children: formatarValor(indice.ultimo_valor, indice.nome) }), _jsxs("p", { className: "text-xs text-muted-foreground flex items-center gap-1 mt-1", children: [_jsx(Clock, { className: "w-3 h-3" }), formatarData(indice.ultima_atualizacao || '')] })] })) : (_jsx("p", { className: "text-sm text-muted-foreground", children: "Sem dados" }))] }, indice.id))) }), indiceInfo && (_jsxs("div", { className: "bg-card border border-border rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center justify-between mb-4 flex-wrap gap-4", children: [_jsxs("div", { children: [_jsx("h2", { className: "text-xl font-bold", children: indiceInfo.nome }), _jsxs("p", { className: "text-sm text-muted-foreground", children: ["Fonte: ", indiceInfo.fonte_oficial] })] }), _jsx("div", { className: "flex items-center gap-2", children: ['30d', '90d', '1y', 'all'].map((periodo) => (_jsxs("button", { onClick: () => setFiltroTempo(periodo), className: `px-3 py-1.5 rounded-lg text-sm transition-colors ${filtroTempo === periodo
                                        ? 'bg-primary text-white'
                                        : 'bg-accent hover:bg-accent/80'}`, children: [periodo === '30d' && '30 dias', periodo === '90d' && '90 dias', periodo === '1y' && '1 ano', periodo === 'all' && 'Tudo'] }, periodo))) })] }), _jsx(IndicesChart, { indiceId: indiceInfo.id, indiceName: indiceInfo.nome }), _jsxs("div", { className: "mt-6 pt-6 border-t border-border", children: [_jsx("h3", { className: "font-bold mb-4", children: "\u00DAltimos 10 Registros" }), _jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full", children: [_jsx("thead", { children: _jsxs("tr", { className: "border-b border-border", children: [_jsx("th", { className: "text-left py-2 px-4 text-sm font-medium text-muted-foreground", children: "Data" }), _jsx("th", { className: "text-right py-2 px-4 text-sm font-medium text-muted-foreground", children: "Valor" }), _jsx("th", { className: "text-right py-2 px-4 text-sm font-medium text-muted-foreground", children: "Varia\u00E7\u00E3o" })] }) }), _jsx("tbody", { children: historico.slice(0, 10).map((item, index) => {
                                                const variacaoItem = index < historico.length - 1
                                                    ? ((item.valor - historico[index + 1].valor) / historico[index + 1].valor) * 100
                                                    : null;
                                                const estaEmAlta = variacaoItem && variacaoItem > 0;
                                                return (_jsxs("tr", { className: "border-b border-border/50 hover:bg-accent/50", children: [_jsx("td", { className: "py-3 px-4 text-sm", children: formatarData(item.data_referencia) }), _jsx("td", { className: "py-3 px-4 text-sm text-right font-medium", children: formatarValor(item.valor, indiceInfo.nome) }), _jsx("td", { className: "py-3 px-4 text-sm text-right", children: variacaoItem !== null ? (_jsxs("span", { className: estaEmAlta ? 'text-green-500' : 'text-red-500', children: [estaEmAlta ? '+' : '', variacaoItem.toFixed(2), "%"] })) : (_jsx("span", { className: "text-muted-foreground", children: "-" })) })] }, item.data_referencia));
                                            }) })] }) })] })] })), _jsx("div", { className: "bg-blue-500/10 border border-blue-500/30 rounded-xl p-4", children: _jsxs("div", { className: "flex items-start gap-3", children: [_jsx(Calendar, { className: "w-5 h-5 text-blue-400 mt-0.5" }), _jsxs("div", { className: "text-sm", children: [_jsx("p", { className: "font-medium text-blue-300 mb-1", children: "Fonte: Banco Central do Brasil" }), _jsx("p", { className: "text-blue-200/80", children: "APIs: SGS (S\u00E9ries Temporais), Olinda PTAX (C\u00E2mbio), Expectativas Focus. Dados atualizados diariamente \u00E0s 8h ou sob demanda." })] })] }) })] }));
}
