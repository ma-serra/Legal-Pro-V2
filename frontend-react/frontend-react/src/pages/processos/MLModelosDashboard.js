import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Brain, RefreshCw, TrendingUp, Database, Zap, AlertCircle, CheckCircle2, BarChart3 } from 'lucide-react';
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
            setModelos(modelsRes.data || []);
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
            alert(`Modelo retreinado com sucesso!\nNova versão: ${response.data.nova_versao}\nMAE: ${response.data.metricas.mae}\nR²: ${response.data.metricas.r2}`);
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
    if (loading) {
        return (_jsx("div", { className: "flex items-center justify-center min-h-[60vh]", children: _jsxs("div", { className: "text-center space-y-4", children: [_jsx(RefreshCw, { className: "w-12 h-12 animate-spin text-primary mx-auto" }), _jsx("p", { className: "text-muted-foreground", children: "Carregando informa\u00E7\u00F5es ML..." })] }) }));
    }
    if (erro) {
        return (_jsx("div", { className: "p-6", children: _jsxs("div", { className: "bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-center", children: [_jsx(AlertCircle, { className: "w-12 h-12 text-red-400 mx-auto mb-4" }), _jsx("p", { className: "text-red-400 font-semibold", children: erro }), _jsx("button", { onClick: carregarDados, className: "mt-4 px-6 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors", children: "Tentar Novamente" })] }) }));
    }
    return (_jsxs("div", { className: "space-y-6 p-6", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsxs("h1", { className: "text-3xl font-bold flex items-center gap-3", children: [_jsx(Brain, { className: "w-8 h-8 text-primary" }), "Dashboard Modelos ML"] }), _jsx("p", { className: "text-muted-foreground mt-1", children: "Gerenciamento e monitoramento de modelos de Machine Learning" })] }), _jsx("button", { onClick: handleRetreinar, disabled: retraining, className: "flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white rounded-lg font-semibold shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed", children: retraining ? (_jsxs(_Fragment, { children: [_jsx(RefreshCw, { className: "w-5 h-5 animate-spin" }), "Retreinando..."] })) : (_jsxs(_Fragment, { children: [_jsx(Zap, { className: "w-5 h-5" }), "Re-treinar Modelo"] })) })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-6", children: [dataStatus && (_jsxs("div", { className: "bg-gradient-to-br from-blue-500/10 to-blue-600/5 border border-blue-500/20 rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center gap-3 mb-4", children: [_jsx(Database, { className: "w-6 h-6 text-blue-400" }), _jsx("h3", { className: "font-semibold text-lg", children: "Status dos Dados" })] }), _jsxs("div", { className: "space-y-3", children: [_jsxs("div", { className: "flex justify-between items-center", children: [_jsx("span", { className: "text-sm text-muted-foreground", children: "Total Processos" }), _jsx("span", { className: "text-2xl font-bold text-blue-400", children: dataStatus.total_processos })] }), _jsxs("div", { className: "flex justify-between items-center", children: [_jsx("span", { className: "text-sm text-muted-foreground", children: "Com Conting\u00EAncia" }), _jsx("span", { className: "text-xl font-semibold", children: dataStatus.com_contingencia })] }), _jsxs("div", { className: "flex justify-between items-center", children: [_jsx("span", { className: "text-sm text-muted-foreground", children: "Features Completas" }), _jsx("span", { className: "text-xl font-semibold", children: dataStatus.com_features_completas })] }), _jsx("div", { className: "pt-3 border-t border-border", children: _jsx("div", { className: `inline-block px-3 py-1 rounded-full text-sm font-semibold ${dataStatus.status === 'OK'
                                                ? 'bg-green-500/20 text-green-400'
                                                : 'bg-yellow-500/20 text-yellow-400'}`, children: dataStatus.status }) })] })] })), modeloInfo && (_jsxs("div", { className: "bg-gradient-to-br from-purple-500/10 to-purple-600/5 border border-purple-500/20 rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center gap-3 mb-4", children: [_jsx(Brain, { className: "w-6 h-6 text-purple-400" }), _jsx("h3", { className: "font-semibold text-lg", children: "Modelo Atual" })] }), _jsxs("div", { className: "space-y-3", children: [_jsxs("div", { children: [_jsx("span", { className: "text-sm text-muted-foreground", children: "Vers\u00E3o" }), _jsx("div", { className: "text-2xl font-bold text-purple-400", children: modeloInfo.modelo_atual })] }), _jsxs("div", { children: [_jsx("span", { className: "text-sm text-muted-foreground", children: "Algoritmo" }), _jsx("div", { className: "text-lg font-semibold", children: modeloInfo.algoritmo })] }), _jsxs("div", { className: "pt-3 border-t border-border grid grid-cols-3 gap-2 text-center", children: [_jsxs("div", { children: [_jsx("div", { className: "text-xs text-muted-foreground", children: "MAE" }), _jsx("div", { className: "text-sm font-bold text-green-400", children: modeloInfo.metricas.mae.toFixed(0) })] }), _jsxs("div", { children: [_jsx("div", { className: "text-xs text-muted-foreground", children: "R\u00B2" }), _jsx("div", { className: "text-sm font-bold text-blue-400", children: modeloInfo.metricas.r2.toFixed(3) })] }), _jsxs("div", { children: [_jsx("div", { className: "text-xs text-muted-foreground", children: "RMSE" }), _jsx("div", { className: "text-sm font-bold text-purple-400", children: modeloInfo.metricas.rmse.toFixed(0) })] })] })] })] })), modeloInfo && modeloInfo.features_importantes.length > 0 && (_jsxs("div", { className: "bg-gradient-to-br from-orange-500/10 to-orange-600/5 border border-orange-500/20 rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center gap-3 mb-4", children: [_jsx(TrendingUp, { className: "w-6 h-6 text-orange-400" }), _jsx("h3", { className: "font-semibold text-lg", children: "Features Importantes" })] }), _jsx("div", { className: "space-y-3", children: modeloInfo.features_importantes.slice(0, 5).map((feature, index) => (_jsxs("div", { children: [_jsxs("div", { className: "flex justify-between items-center mb-1", children: [_jsx("span", { className: "text-sm text-muted-foreground truncate", children: feature.nome.replace(/_/g, ' ') }), _jsxs("span", { className: "text-xs font-semibold text-orange-400", children: [(feature.importancia * 100).toFixed(1), "%"] })] }), _jsx("div", { className: "w-full bg-accent rounded-full h-2", children: _jsx("div", { className: "bg-gradient-to-r from-orange-500 to-yellow-500 rounded-full h-2 transition-all", style: { width: `${feature.importancia * 100}%` } }) })] }, index))) })] }))] }), modelos.length > 0 && (_jsxs("div", { className: "bg-card border border-border rounded-xl p-6", children: [_jsxs("div", { className: "flex items-center gap-3 mb-6", children: [_jsx(BarChart3, { className: "w-6 h-6 text-primary" }), _jsx("h3", { className: "font-semibold text-lg", children: "Hist\u00F3rico de Modelos" })] }), _jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full", children: [_jsx("thead", { className: "bg-accent border-b border-border", children: _jsxs("tr", { children: [_jsx("th", { className: "text-left py-3 px-4 text-sm font-medium", children: "Vers\u00E3o" }), _jsx("th", { className: "text-left py-3 px-4 text-sm font-medium", children: "Algoritmo" }), _jsx("th", { className: "text-center py-3 px-4 text-sm font-medium", children: "MAE" }), _jsx("th", { className: "text-center py-3 px-4 text-sm font-medium", children: "R\u00B2" }), _jsx("th", { className: "text-center py-3 px-4 text-sm font-medium", children: "RMSE" }), _jsx("th", { className: "text-center py-3 px-4 text-sm font-medium", children: "Status" })] }) }), _jsx("tbody", { children: modelos.map((modelo, index) => (_jsxs("tr", { className: "border-b border-border/50 hover:bg-accent/50", children: [_jsx("td", { className: "py-3 px-4 font-mono text-sm font-semibold", children: modelo.versao }), _jsx("td", { className: "py-3 px-4 text-sm", children: modelo.algoritmo }), _jsx("td", { className: "py-3 px-4 text-center text-sm font-semibold text-green-400", children: modelo.mae.toFixed(0) }), _jsx("td", { className: "py-3 px-4 text-center text-sm font-semibold text-blue-400", children: modelo.r2.toFixed(3) }), _jsx("td", { className: "py-3 px-4 text-center text-sm font-semibold text-purple-400", children: modelo.rmse ? modelo.rmse.toFixed(0) : '-' }), _jsx("td", { className: "py-3 px-4 text-center", children: modelo.versao === modeloInfo?.modelo_atual ? (_jsxs("span", { className: "inline-block px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-semibold", children: [_jsx(CheckCircle2, { className: "w-3 h-3 inline mr-1" }), "ATIVO"] })) : (_jsx("span", { className: "text-xs text-muted-foreground", children: "-" })) })] }, index))) })] }) })] }))] }));
}
