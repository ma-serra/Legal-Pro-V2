import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Brain, RefreshCw, TrendingUp, Database, Zap, AlertCircle, CheckCircle2, BarChart3, LineChart as LineChartIcon } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import api from '../../lib/api';
export default function MLModelosDashboard() {
    const [modeloInfo, setModeloInfo] = useState(null);
    const [modelos, setModelos] = useState([]);
    const [dataStatus, setDataStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [retraining, setRetraining] = useState(false);
    const [erro, setErro] = useState(null);
    useEffect(() => {
        carregarDados();
    }, []);
    const carregarDados = async () => {
        setLoading(true);
        setErro(null);
        try {
            const [infoRes, modelsRes, statusRes] = await Promise.all([
                api.get('/api/ml/tributario/model-info'),
                api.get('/api/ml/tributario/models'),
                api.get('/api/ml/tributario/data-status')
            ]);
            setModeloInfo(infoRes.data);
            setModelos(modelsRes.data.models || []);
            setDataStatus(statusRes.data);
        }
        catch (error) {
            console.error('Erro ao carregar dados:', error);
            setErro(error.response?.data?.error || 'Erro ao carregar informações');
        }
        finally {
            setLoading(false);
        }
    };
    const handleRetreinar = async () => {
        if (!confirm('Deseja retreinar o modelo ML? Isso pode levar alguns minutos.')) {
            return;
        }
        setRetraining(true);
        try {
            const response = await api.post('/api/ml/tributario/retrain');
            alert(`Modelo retreinado com sucesso!\nNova versão: ${response.data.version}\nMAE: ${response.data.metrics.mae}\nR²: ${response.data.metrics.r2_score}`);
            await carregarDados();
        }
        catch (error) {
            console.error('Erro ao retreinar:', error);
            alert(error.response?.data?.error || 'Erro ao retreinar modelo');
        }
        finally {
            setRetraining(false);
        }
    };
    // Dados para gráficos
    const featureData = modeloInfo?.features_importantes.slice(0, 7).map(f => ({
        name: f.nome.replace(/_/g, ' '),
        importance: (f.importancia * 100).toFixed(1)
    })) || [];
    // Dados para histórico (invertendo para ordem cronológica)
    const historyData = [...modelos].reverse().map(m => ({
        versao: m.versao,
        r2: (m.r2 || 0) * 100,
        mae: m.mae || 0
    }));
    if (loading) {
        return (_jsx("div", { className: "flex items-center justify-center min-h-[60vh]", children: _jsxs("div", { className: "text-center space-y-4", children: [_jsx(RefreshCw, { className: "w-12 h-12 animate-spin text-primary mx-auto" }), _jsx("p", { className: "text-muted-foreground", children: "Carregando informa\u00E7\u00F5es ML..." })] }) }));
    }
    if (erro) {
        return (_jsx("div", { className: "p-6", children: _jsxs("div", { className: "bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-center", children: [_jsx(AlertCircle, { className: "w-12 h-12 text-red-400 mx-auto mb-4" }), _jsx("p", { className: "text-red-400 font-semibold", children: erro }), _jsx("button", { onClick: carregarDados, className: "mt-4 px-6 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors", children: "Tentar Novamente" })] }) }));
    }
    return (_jsxs("div", { className: "space-y-6 p-6", children: [_jsxs("div", { className: "flex flex-col md:flex-row md:items-center justify-between gap-4", children: [_jsxs("div", { children: [_jsxs("h1", { className: "text-3xl font-bold flex items-center gap-3", children: [_jsx(Brain, { className: "w-8 h-8 text-primary" }), "Dashboard Modelos ML"] }), _jsx("p", { className: "text-muted-foreground mt-1", children: "Gerenciamento e monitoramento de modelos de Machine Learning" })] }), _jsxs("div", { className: "flex gap-3", children: [_jsx("button", { onClick: carregarDados, className: "px-4 py-3 bg-accent hover:bg-accent/80 rounded-lg transition-colors", title: "Atualizar Dados", children: _jsx(RefreshCw, { className: `w-5 h-5 ${loading ? 'animate-spin' : ''}` }) }), _jsx("button", { onClick: handleRetreinar, disabled: retraining, className: "flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white rounded-lg font-semibold shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed", children: retraining ? (_jsxs(_Fragment, { children: [_jsx(RefreshCw, { className: "w-5 h-5 animate-spin" }), "Retreinando..."] })) : (_jsxs(_Fragment, { children: [_jsx(Zap, { className: "w-5 h-5" }), "Re-treinar Modelo"] })) })] })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-4 gap-6", children: [_jsxs("div", { className: "bg-card border border-border rounded-xl p-6 col-span-1 md:col-span-2", children: [_jsxs("div", { className: "flex items-center justify-between mb-4", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx(Brain, { className: "w-5 h-5 text-primary" }), _jsx("h3", { className: "font-semibold text-lg", children: "Modelo Ativo" })] }), _jsx("span", { className: "bg-green-500/20 text-green-600 text-xs px-2 py-1 rounded-full font-bold", children: modeloInfo?.modelo_atual })] }), _jsxs("div", { className: "grid grid-cols-3 gap-4 text-center", children: [_jsxs("div", { className: "p-3 bg-accent rounded-lg", children: [_jsx("div", { className: "text-sm text-muted-foreground", children: "R\u00B2 Score" }), _jsx("div", { className: "text-2xl font-bold text-blue-500", children: modeloInfo?.metricas.r2.toFixed(3) })] }), _jsxs("div", { className: "p-3 bg-accent rounded-lg", children: [_jsx("div", { className: "text-sm text-muted-foreground", children: "Erro M\u00E9dio (MAE)" }), _jsxs("div", { className: "text-2xl font-bold text-red-500", children: ["R$ ", modeloInfo?.metricas.mae.toFixed(0)] })] }), _jsxs("div", { className: "p-3 bg-accent rounded-lg", children: [_jsx("div", { className: "text-sm text-muted-foreground", children: "Treinado Em" }), _jsx("div", { className: "text-sm font-semibold mt-1", children: modelos.find(m => m.versao === modeloInfo?.modelo_atual)?.data_treinamento
                                                    ? new Date(modelos.find(m => m.versao === modeloInfo?.modelo_atual).data_treinamento).toLocaleDateString()
                                                    : '-' })] })] }), _jsxs("div", { className: "mt-4 pt-4 border-t border-border flex justify-between text-sm text-muted-foreground", children: [_jsxs("span", { children: ["Algoritmo: ", _jsx("strong", { children: modeloInfo?.algoritmo })] }), _jsxs("span", { children: ["Amostras Treino: ", _jsx("strong", { children: modeloInfo?.amostras_treino || '-' })] })] })] }), dataStatus && (_jsxs("div", { className: "bg-card border border-border rounded-xl p-6 col-span-1 md:col-span-2", children: [_jsxs("div", { className: "flex items-center gap-2 mb-4", children: [_jsx(Database, { className: "w-5 h-5 text-blue-500" }), _jsx("h3", { className: "font-semibold text-lg", children: "Sa\u00FAde dos Dados" })] }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsxs("div", { className: "flex justify-between text-sm mb-1", children: [_jsx("span", { children: "Cobertura de Conting\u00EAncia" }), _jsxs("span", { className: "font-bold", children: [((dataStatus.com_contingencia / dataStatus.total_processos) * 100).toFixed(0), "%"] })] }), _jsx("div", { className: "w-full bg-accent rounded-full h-2", children: _jsx("div", { className: "bg-blue-500 rounded-full h-2", style: { width: `${(dataStatus.com_contingencia / dataStatus.total_processos) * 100}%` } }) })] }), _jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("span", { className: "text-sm text-muted-foreground", children: "Total Processos" }), _jsx("div", { className: "text-xl font-bold", children: dataStatus.total_processos })] }), _jsxs("div", { children: [_jsx("span", { className: "text-sm text-muted-foreground", children: "Dataset Treino" }), _jsx("div", { className: "text-xl font-bold", children: dataStatus.com_contingencia })] })] })] })] }))] }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [_jsxs("div", { className: "bg-card border border-border rounded-xl p-6 min-h-[400px]", children: [_jsxs("h3", { className: "font-bold text-lg mb-6 flex items-center gap-2", children: [_jsx(LineChartIcon, { className: "w-5 h-5 text-primary" }), "Evolu\u00E7\u00E3o da Performance (R\u00B2)"] }), _jsx("div", { className: "h-[300px] w-full", children: _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(LineChart, { data: historyData, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", opacity: 0.3 }), _jsx(XAxis, { dataKey: "versao", tick: { fontSize: 12 } }), _jsx(YAxis, { domain: [0, 100] }), _jsx(Tooltip, { contentStyle: { borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' } }), _jsx(Line, { type: "monotone", dataKey: "r2", stroke: "#3b82f6", strokeWidth: 3, name: "R\u00B2 Score (%)", activeDot: { r: 8 } })] }) }) })] }), _jsxs("div", { className: "bg-card border border-border rounded-xl p-6 min-h-[400px]", children: [_jsxs("h3", { className: "font-bold text-lg mb-6 flex items-center gap-2", children: [_jsx(TrendingUp, { className: "w-5 h-5 text-orange-500" }), "Top Features de Impacto"] }), _jsx("div", { className: "h-[300px] w-full", children: _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(BarChart, { layout: "vertical", data: featureData, margin: { left: 20 }, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", opacity: 0.3, horizontal: false }), _jsx(XAxis, { type: "number", hide: true }), _jsx(YAxis, { dataKey: "name", type: "category", width: 150, tick: { fontSize: 11 } }), _jsx(Tooltip, { formatter: (value) => [`${value}%`, 'Importância'], contentStyle: { borderRadius: '8px' } }), _jsx(Bar, { dataKey: "importance", fill: "#f97316", radius: [0, 4, 4, 0], barSize: 20 })] }) }) })] })] }), _jsxs("div", { className: "bg-card border border-border rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center gap-3 mb-6", children: [_jsx(BarChart3, { className: "w-6 h-6 text-primary" }), _jsx("h3", { className: "font-semibold text-lg", children: "Hist\u00F3rico de Treinamentos" })] }), _jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full", children: [_jsx("thead", { className: "bg-accent border-b border-border", children: _jsxs("tr", { children: [_jsx("th", { className: "text-left py-3 px-4 text-sm font-medium", children: "Vers\u00E3o" }), _jsx("th", { className: "text-left py-3 px-4 text-sm font-medium", children: "Algoritmo" }), _jsx("th", { className: "text-center py-3 px-4 text-sm font-medium", children: "Data" }), _jsx("th", { className: "text-center py-3 px-4 text-sm font-medium", children: "MAE" }), _jsx("th", { className: "text-center py-3 px-4 text-sm font-medium", children: "R\u00B2" }), _jsx("th", { className: "text-center py-3 px-4 text-sm font-medium", children: "Status" })] }) }), _jsx("tbody", { children: modelos.map((modelo, index) => (_jsxs("tr", { className: "border-b border-border/50 hover:bg-accent/50", children: [_jsx("td", { className: "py-3 px-4 font-mono text-sm font-semibold", children: modelo.versao }), _jsx("td", { className: "py-3 px-4 text-sm", children: modelo.algoritmo }), _jsx("td", { className: "py-3 px-4 text-center text-sm text-muted-foreground", children: modelo.data_treinamento
                                                    ? new Date(modelo.data_treinamento).toLocaleDateString()
                                                    : (modelo.data_criacao ? new Date(modelo.data_criacao).toLocaleDateString() : '-') }), _jsxs("td", { className: "py-3 px-4 text-center text-sm font-semibold text-red-400", children: ["R$ ", modelo.mae.toFixed(0)] }), _jsx("td", { className: "py-3 px-4 text-center text-sm font-semibold text-blue-400", children: modelo.r2.toFixed(3) }), _jsx("td", { className: "py-3 px-4 text-center", children: modelo.versao === modeloInfo?.modelo_atual ? (_jsxs("span", { className: "inline-block px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-semibold", children: [_jsx(CheckCircle2, { className: "w-3 h-3 inline mr-1" }), "ATIVO"] })) : (_jsx("span", { className: "text-xs text-muted-foreground opacity-50", children: "Arquivado" })) })] }, index))) })] }) })] })] }));
}
