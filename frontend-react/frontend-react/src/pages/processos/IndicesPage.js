import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * Dashboard Profissional - Índices Econômicos
 * Integração completa com API BACEN
 * Atualização diária automática
 */
import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Calendar, RefreshCw, BarChart3, Download, Clock } from 'lucide-react';
import api from '../../lib/api';
import IndicesChart from '../../components/processos/IndicesChart';
export default function IndicesEconomicosPage() {
    const [indices, setIndices] = useState([]);
    const [indiceSelecionado, setIndiceSelecionado] = useState(null);
    const [historico, setHistorico] = useState([]);
    const [carregando, setCarregando] = useState(true);
    const [atualizando, setAtualizando] = useState(false);
    const [filtroTempo, setFiltroTempo] = useState('30d');
    useEffect(() => {
        carregarIndices();
    }, []);
    useEffect(() => {
        if (indiceSelecionado) {
            carregarHistorico(indiceSelecionado);
        }
    }, [indiceSelecionado, filtroTempo]);
    const carregarIndices = async () => {
        setCarregando(true);
        try {
            const response = await api.get('/api/atualizacao-monetaria/indices');
            setIndices(response.data);
            // Selecionar SELIC por padrão
            const selic = response.data.find((i) => i.nome === 'SELIC');
            if (selic) {
                setIndiceSelecionado(selic.id);
            }
        }
        catch (error) {
            console.error('Erro ao carregar índices:', error);
        }
        finally {
            setCarregando(false);
        }
    };
    const carregarHistorico = async (indiceId) => {
        try {
            const params = { limite: 365 };
            // Filtrar por período
            const hoje = new Date();
            let dataInicio = new Date();
            if (filtroTempo === '30d') {
                dataInicio.setDate(dataInicio.getDate() - 30);
            }
            else if (filtroTempo === '90d') {
                dataInicio.setDate(dataInicio.getDate() - 90);
            }
            else if (filtroTempo === '1y') {
                dataInicio.setFullYear(dataInicio.getFullYear() - 1);
            }
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
            await carregarIndices();
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
    const calcularVariacao = (valores) => {
        if (valores.length < 2)
            return null;
        const atual = valores[0].valor;
        const anterior = valores[1].valor;
        const variacao = ((atual - anterior) / anterior) * 100;
        return variacao;
    };
    const formatarData = (data) => {
        return new Date(data).toLocaleDateString('pt-BR');
    };
    const formatarValor = (valor, indice) => {
        if (indice.includes('Taxa') || indice.includes('SELIC') || indice.includes('CDI')) {
            return `${valor.toFixed(2)}% a.a.`;
        }
        return `${valor.toFixed(2)}%`;
    };
    if (carregando) {
        return (_jsx("div", { className: "flex items-center justify-center min-h-screen", children: _jsx(RefreshCw, { className: "w-8 h-8 animate-spin text-primary" }) }));
    }
    const indiceInfo = indices.find(i => i.id === indiceSelecionado);
    return (_jsxs("div", { className: "p-6 max-w-[1600px] mx-auto space-y-6", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsxs("h1", { className: "text-3xl font-bold flex items-center gap-3", children: [_jsx(BarChart3, { className: "w-8 h-8 text-primary" }), "\u00CDndices Econ\u00F4micos"] }), _jsx("p", { className: "text-muted-foreground mt-2", children: "Dados oficiais do Banco Central - Atualiza\u00E7\u00E3o di\u00E1ria autom\u00E1tica" })] }), _jsxs("button", { onClick: atualizarIndices, disabled: atualizando, className: "px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50", children: [_jsx(RefreshCw, { className: `w-4 h-4 ${atualizando ? 'animate-spin' : ''}` }), atualizando ? 'Atualizando...' : 'Atualizar Índices'] })] }), _jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4", children: indices.map((indice) => {
                    const variacao = calcularVariacao(historico.filter(h => true));
                    const estaEmAlta = variacao && variacao > 0;
                    return (_jsxs("button", { onClick: () => setIndiceSelecionado(indice.id), className: `bg-card border-2 rounded-xl p-4 text-left transition-all hover: shadow-lg ${indiceSelecionado === indice.id
                            ? 'border-primary shadow-lg scale-105'
                            : 'border-border hover:border-primary/50'}`, children: [_jsxs("div", { className: "flex items-start justify-between mb-3", children: [_jsxs("div", { children: [_jsx("h3", { className: "font-bold text-lg", children: indice.nome }), _jsx("p", { className: "text-xs text-muted-foreground", children: indice.descricao })] }), indice.ultimo_valor && estaEmAlta !== null && (estaEmAlta ? (_jsx(TrendingUp, { className: "w-5 h-5 text-green-500" })) : (_jsx(TrendingDown, { className: "w-5 h-5 text-red-500" })))] }), indice.ultimo_valor ? (_jsxs(_Fragment, { children: [_jsx("div", { className: "text-2xl font-bold text-primary mb-1", children: formatarValor(indice.ultimo_valor, indice.nome) }), variacao !== null && (_jsxs("div", { className: `text-sm font-medium ${estaEmAlta ? 'text-green-500' : 'text-red-500'}`, children: [estaEmAlta ? '+' : '', variacao.toFixed(2), "% m\u00EAs"] })), _jsxs("div", { className: "flex items-center gap-1 text-xs text-muted-foreground mt-2", children: [_jsx(Clock, { className: "w-3 h-3" }), indice.ultima_atualizacao && formatarData(indice.ultima_atualizacao)] })] })) : (_jsx("div", { className: "text-sm text-muted-foreground", children: "Sem dados" })), _jsxs("div", { className: "text-xs text-muted-foreground mt-2 pt-2 border-t border-border", children: [indice.total_registros, " registros"] })] }, indice.id));
                }) }), indiceInfo && (_jsxs("div", { className: "bg-card border border-border rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center justify-between mb-6", children: [_jsxs("div", { children: [_jsxs("h2", { className: "text-2xl font-bold flex items-center gap-2", children: [indiceInfo.nome, _jsx("span", { className: "text-sm font-normal text-muted-foreground", children: indiceInfo.descricao })] }), _jsxs("p", { className: "text-sm text-muted-foreground mt-1", children: ["Fonte: ", indiceInfo.fonte_oficial] })] }), _jsxs("div", { className: "flex items-center gap-2", children: [['30d', '90d', '1y', 'all'].map((periodo) => (_jsxs("button", { onClick: () => setFiltroTempo(periodo), className: `px-3 py-1.5 rounded-lg text-sm transition-colors ${filtroTempo === periodo
                                            ? 'bg-primary text-white'
                                            : 'bg-accent hover:bg-accent/80'}`, children: [periodo === '30d' && '30 dias', periodo === '90d' && '90 dias', periodo === '1y' && '1 ano', periodo === 'all' && 'Tudo'] }, periodo))), _jsx("button", { className: "p-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors", children: _jsx(Download, { className: "w-4 h-4" }) })] })] }), historico.length > 0 ? (_jsx("div", { className: "h-[400px]", children: _jsx(IndicesChart, { indiceId: indiceInfo.id, indiceName: indiceInfo.nome }) })) : (_jsx("div", { className: "h-[400px] flex items-center justify-center text-muted-foreground", children: "Sem dados dispon\u00EDveis para o per\u00EDodo selecionado" })), _jsxs("div", { className: "mt-6 pt-6 border-t border-border", children: [_jsx("h3", { className: "font-bold mb-4", children: "\u00DAltimos 10 Registros" }), _jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full", children: [_jsx("thead", { children: _jsxs("tr", { className: "border-b border-border", children: [_jsx("th", { className: "text-left py-2 px-4 text-sm font-medium text-muted-foreground", children: "Data" }), _jsx("th", { className: "text-right py-2 px-4 text-sm font-medium text-muted-foreground", children: "Valor" }), _jsx("th", { className: "text-right py-2 px-4 text-sm font-medium text-muted-foreground", children: "Varia\u00E7\u00E3o" })] }) }), _jsx("tbody", { children: historico.slice(0, 10).map((item, index) => {
                                                const variacaoItem = index < historico.length - 1
                                                    ? ((item.valor - historico[index + 1].valor) / historico[index + 1].valor) * 100
                                                    : null;
                                                const estaEmAlta = variacaoItem && variacaoItem > 0;
                                                return (_jsxs("tr", { className: "border-b border-border/50 hover:bg-accent/50", children: [_jsx("td", { className: "py-3 px-4 text-sm", children: formatarData(item.data_referencia) }), _jsx("td", { className: "py-3 px-4 text-sm text-right font-medium", children: formatarValor(item.valor, indiceInfo.nome) }), _jsx("td", { className: "py-3 px-4 text-sm text-right", children: variacaoItem !== null ? (_jsxs("span", { className: estaEmAlta ? 'text-green-500' : 'text-red-500', children: [estaEmAlta ? '+' : '', variacaoItem.toFixed(2), "%"] })) : (_jsx("span", { className: "text-muted-foreground", children: "-" })) })] }, item.data_referencia));
                                            }) })] }) })] })] })), _jsx("div", { className: "bg-blue-500/10 border border-blue-500/30 rounded-xl p-4", children: _jsxs("div", { className: "flex items-start gap-3", children: [_jsx(Calendar, { className: "w-5 h-5 text-blue-400 mt-0.5" }), _jsxs("div", { className: "text-sm", children: [_jsx("p", { className: "font-medium text-blue-300 mb-1", children: "Atualiza\u00E7\u00E3o Autom\u00E1tica Di\u00E1ria" }), _jsx("p", { className: "text-blue-200/80", children: "Os \u00EDndices s\u00E3o atualizados automaticamente todos os dias \u00E0s 8h da manh\u00E3, buscando os dados mais recentes diretamente do Sistema Gerenciador de S\u00E9ries Temporais (SGS) do Banco Central do Brasil." })] })] }) })] }));
}
