import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Brain, TrendingUp, Target, Clock, RefreshCw, AlertCircle, Calculator, BarChart3 } from 'lucide-react';
import api from '../../lib/api';
import SimuladorPreditivo from '../../components/ml/SimuladorPreditivo';
import MLModelosDashboard from './MLModelosDashboard';
export default function MLAnaliseTributarioPage() {
    const [activeTab, setActiveTab] = useState('analise');
    // Estados Tab Análise
    const [processos, setProcessos] = useState([]);
    const [processoSelecionado, setProcessoSelecionado] = useState(null);
    const [predicao, setPredicao] = useState(null);
    const [historico, setHistorico] = useState([]);
    const [carregando, setCarregando] = useState(false);
    const [analisando, setAnalisando] = useState(false);
    useEffect(() => {
        carregarProcessos();
    }, []);
    useEffect(() => {
        if (processoSelecionado) {
            carregarHistorico(processoSelecionado);
        }
    }, [processoSelecionado]);
    const carregarProcessos = async () => {
        setCarregando(true);
        try {
            const response = await api.get('/api/processos', {
                params: { natureza_id: 1, per_page: 50 }
            });
            setProcessos(response.data.items || []);
        }
        catch (error) {
            console.error('Erro ao carregar processos:', error);
        }
        finally {
            setCarregando(false);
        }
    };
    const carregarHistorico = async (processoId) => {
        try {
            const response = await api.get(`/api/ml/tributario/historico/${processoId}`);
            setHistorico(response.data.predicoes || []);
            // Correcao: backend retorna { predicoes: [...] }
            if (response.data.predicoes && response.data.predicoes.length > 0) {
                setPredicao(response.data.predicoes[0]);
            }
        }
        catch (error) {
            console.error('Erro ao carregar histórico:', error);
            setHistorico([]);
        }
    };
    const analisarProcesso = async () => {
        if (!processoSelecionado)
            return;
        setAnalisando(true);
        try {
            const response = await api.post('/api/ml/tributario/predict', {
                processo_id: processoSelecionado
            });
            setPredicao(response.data);
            await carregarHistorico(processoSelecionado);
            alert('Análise ML concluída com sucesso!');
        }
        catch (error) {
            console.error('Erro na análise ML:', error);
            console.error('Erro na análise ML:', error);
            alert('Erro ao realizar análise. Verifique a conexão com o servidor.');
        }
        finally {
            setAnalisando(false);
        }
    };
    const formatarMoeda = (valor) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
    };
    const formatarData = (data) => {
        return new Date(data).toLocaleString('pt-BR');
    };
    const getRiscoColor = (risco) => {
        switch (risco?.toLowerCase()) {
            case 'baixo': return 'text-green-500';
            case 'medio':
            case 'médio': return 'text-yellow-500';
            case 'alto': return 'text-red-500';
            default: return 'text-gray-500';
        }
    };
    return (_jsxs("div", { className: "p-6 max-w-7xl mx-auto space-y-6", children: [_jsxs("div", { children: [_jsxs("h1", { className: "text-3xl font-bold flex items-center gap-3", children: [_jsx(Brain, { className: "w-8 h-8 text-primary" }), "An\u00E1lise ML - Tribut\u00E1rio"] }), _jsx("p", { className: "text-muted-foreground mt-2", children: "Intelig\u00EAncia Artificial aplicada \u00E0 gest\u00E3o de risco e previsibilidade processual" })] }), _jsxs("div", { className: "flex border-b border-border", children: [_jsxs("button", { onClick: () => setActiveTab('analise'), className: `px-6 py-3 font-medium text-sm flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'analise'
                            ? 'border-primary text-primary'
                            : 'border-transparent text-muted-foreground hover:text-foreground'}`, children: [_jsx(Target, { className: "w-4 h-4" }), "An\u00E1lise de Processo"] }), _jsxs("button", { onClick: () => setActiveTab('simulador'), className: `px-6 py-3 font-medium text-sm flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'simulador'
                            ? 'border-primary text-primary'
                            : 'border-transparent text-muted-foreground hover:text-foreground'}`, children: [_jsx(Calculator, { className: "w-4 h-4" }), "Simulador What-If"] }), _jsxs("button", { onClick: () => setActiveTab('dashboard'), className: `px-6 py-3 font-medium text-sm flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'dashboard'
                            ? 'border-primary text-primary'
                            : 'border-transparent text-muted-foreground hover:text-foreground'}`, children: [_jsx(BarChart3, { className: "w-4 h-4" }), "Performance Visual"] })] }), _jsxs("div", { className: "min-h-[500px]", children: [activeTab === 'analise' && (_jsxs("div", { className: "space-y-6 animate-in fade-in duration-300", children: [_jsxs("div", { className: "bg-card border border-border rounded-xl p-6", children: [_jsx("h2", { className: "text-xl font-bold mb-4", children: "Selecionar Processo" }), _jsxs("div", { className: "flex gap-4", children: [_jsxs("select", { value: processoSelecionado || '', onChange: (e) => {
                                                    const id = parseInt(e.target.value);
                                                    setProcessoSelecionado(id || null);
                                                    setPredicao(null);
                                                }, className: "flex-1 bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none", disabled: carregando, children: [_jsx("option", { value: "", children: carregando ? 'Carregando...' : 'Selecione um processo tributário...' }), processos.map(p => (_jsxs("option", { value: p.id_processo, children: [p.pasta, " - ", p.numero_cnj || p.titulo || 'Sem título'] }, p.id_processo)))] }), _jsx("button", { onClick: analisarProcesso, disabled: !processoSelecionado || analisando, className: "px-6 py-2.5 bg-primary hover:bg-primary/90 text-white rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed", children: analisando ? (_jsxs(_Fragment, { children: [_jsx(RefreshCw, { className: "w-4 h-4 animate-spin" }), "Analisando..."] })) : (_jsxs(_Fragment, { children: [_jsx(Brain, { className: "w-4 h-4" }), "Analisar com ML"] })) })] }), !processoSelecionado && (_jsxs("div", { className: "mt-4 flex items-start gap-3 text-sm text-muted-foreground bg-accent rounded-lg p-4", children: [_jsx(AlertCircle, { className: "w-5 h-5 mt-0.5 flex-shrink-0" }), _jsx("p", { children: "Selecione um processo tribut\u00E1rio para visualizar predi\u00E7\u00F5es existentes ou realizar uma nova an\u00E1lise ML. O modelo XGBoost analisa 19+ features para prever o valor de conting\u00EAncia." })] }))] }), predicao && (_jsxs("div", { className: "bg-gradient-to-br from-primary/10 to-primary/5 border-2 border-primary/30 rounded-xl p-6", children: [_jsxs("h2", { className: "text-xl font-bold mb-6 flex items-center gap-2", children: [_jsx(Target, { className: "w-6 h-6 text-primary" }), "Resultado da An\u00E1lise ML"] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-6", children: [_jsxs("div", { className: "bg-card border border-border rounded-lg p-6", children: [_jsx("div", { className: "text-sm text-muted-foreground mb-2", children: "Valor Conting\u00EAncia Predito" }), _jsx("div", { className: "text-3xl font-bold text-primary", children: formatarMoeda(predicao.valor_contingencia_predito) })] }), _jsxs("div", { className: "bg-card border border-border rounded-lg p-6", children: [_jsx("div", { className: "text-sm text-muted-foreground mb-2", children: "Confian\u00E7a do Modelo" }), _jsxs("div", { className: "text-3xl font-bold text-green-500", children: [(predicao.confianca * 100).toFixed(1), "%"] }), _jsx("div", { className: "w-full bg-accent rounded-full h-2 mt-3", children: _jsx("div", { className: "bg-green-500 rounded-full h-2 transition-all", style: { width: `${predicao.confianca * 100}%` } }) })] }), predicao.risco_predito && (_jsxs("div", { className: "bg-card border border-border rounded-lg p-6", children: [_jsx("div", { className: "text-sm text-muted-foreground mb-2", children: "Classifica\u00E7\u00E3o de Risco" }), _jsx("div", { className: `text-3xl font-bold ${getRiscoColor(predicao.risco_predito)}`, children: predicao.risco_predito })] }))] }), _jsx("div", { className: "mt-6 pt-6 border-t border-border text-sm text-muted-foreground", children: _jsxs("div", { className: "flex items-center gap-6 flex-wrap", children: [_jsxs("div", { children: [_jsx("strong", { children: "Modelo:" }), " ", predicao.modelo_algoritmo] }), _jsxs("div", { children: [_jsx("strong", { children: "Vers\u00E3o:" }), " ", predicao.modelo_versao] }), predicao.data_predicao && (_jsxs("div", { className: "flex items-center gap-1", children: [_jsx(Clock, { className: "w-4 h-4" }), formatarData(predicao.data_predicao)] }))] }) })] })), processoSelecionado && historico.length > 0 && (_jsxs("div", { className: "bg-card border border-border rounded-xl p-6", children: [_jsxs("h2", { className: "text-xl font-bold mb-4 flex items-center gap-2", children: [_jsx(TrendingUp, { className: "w-5 h-5" }), "Hist\u00F3rico de Predi\u00E7\u00F5es"] }), _jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full", children: [_jsx("thead", { children: _jsxs("tr", { className: "border-b border-border", children: [_jsx("th", { className: "text-left py-3 px-4 text-sm font-medium text-muted-foreground", children: "Data" }), _jsx("th", { className: "text-right py-3 px-4 text-sm font-medium text-muted-foreground", children: "Valor Predito" }), _jsx("th", { className: "text-center py-3 px-4 text-sm font-medium text-muted-foreground", children: "Confian\u00E7a" }), _jsx("th", { className: "text-center py-3 px-4 text-sm font-medium text-muted-foreground", children: "Modelo" })] }) }), _jsx("tbody", { children: historico.slice(0, 10).map((item, index) => (_jsxs("tr", { className: "border-b border-border/50 hover:bg-accent/50", children: [_jsx("td", { className: "py-3 px-4 text-sm", children: item.data_predicao ? formatarData(item.data_predicao) : '-' }), _jsx("td", { className: "py-3 px-4 text-sm text-right font-medium", children: formatarMoeda(item.valor_contingencia_predito) }), _jsxs("td", { className: "py-3 px-4 text-sm text-center", children: [(item.confianca * 100).toFixed(1), "%"] }), _jsx("td", { className: "py-3 px-4 text-sm text-center text-muted-foreground", children: item.modelo_versao })] }, index))) })] }) })] }))] })), activeTab === 'simulador' && (_jsxs("div", { className: "animate-in fade-in duration-300 py-6", children: [_jsxs("div", { className: "mb-6", children: [_jsx("h2", { className: "text-xl font-bold mb-2", children: "Simulador de Cen\u00E1rios Tribut\u00E1rios" }), _jsx("p", { className: "text-muted-foreground", children: "Simule varia\u00E7\u00F5es de comarca, juiz e valores para entender o impacto no risco de conting\u00EAncia. Os dados simulados n\u00E3o s\u00E3o salvos no hist\u00F3rico do processo." })] }), _jsx(SimuladorPreditivo, {})] })), activeTab === 'dashboard' && (_jsx("div", { className: "animate-in fade-in duration-300", children: _jsx(MLModelosDashboard, {}) }))] })] }));
}
