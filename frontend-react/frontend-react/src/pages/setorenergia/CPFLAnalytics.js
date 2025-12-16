import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader, StatCard } from '../../components/ui/AdminComponents';
import { Zap, TrendingUp, AlertTriangle, MapPin, FileText, BarChart3 } from 'lucide-react';
import api from '../../lib/api';
export default function CPFLAnalytics() {
    const [analytics, setAnalytics] = useState(null);
    const [predicoes, setPredicoes] = useState([]);
    const [alertas, setAlertas] = useState([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchAllData();
    }, []);
    const fetchAllData = async () => {
        await Promise.all([
            fetchAnalytics(),
            fetchPredicoes(),
            fetchAlertas()
        ]);
        setLoading(false);
    };
    // Endpoint: GET /setorenergia/analytics
    const fetchAnalytics = async () => {
        try {
            const response = await api.get('/setorenergia/analytics');
            setAnalytics(response.data);
        }
        catch (error) {
            console.error('Error fetching analytics:', error);
        }
    };
    // Endpoint: GET /setorenergia/predicoes
    const fetchPredicoes = async () => {
        try {
            const response = await api.get('/setorenergia/predicoes');
            setPredicoes(response.data.slice(0, 5)); // Top 5
        }
        catch (error) {
            console.error('Error fetching predictions:', error);
        }
    };
    // Endpoint: GET /setorenergia/alertas
    const fetchAlertas = async () => {
        try {
            const response = await api.get('/setorenergia/alertas');
            setAlertas(response.data.slice(0, 5)); // Latest 5
        }
        catch (error) {
            console.error('Error fetching alerts:', error);
        }
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "CPFL/RGE - Analytics do Setor de Energia", description: "Dashboard completo de an\u00E1lises e predi\u00E7\u00F5es" }), analytics && (_jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8", children: [_jsx(StatCard, { title: "Total de Processos", value: analytics.total_processos.toString(), icon: FileText }), _jsx(StatCard, { title: "Processos Ativos", value: analytics.processos_ativos.toString(), icon: Zap }), _jsx(StatCard, { title: "Taxa de Sucesso", value: `${analytics.taxa_sucesso.toFixed(1)}%`, icon: TrendingUp }), _jsx(StatCard, { title: "Valor Total", value: `R$ ${(analytics.valor_total / 1000000).toFixed(1)}M`, icon: BarChart3 })] })), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsxs("h3", { className: "text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2", children: [_jsx(TrendingUp, { className: "w-5 h-5 text-blue-600" }), "Predi\u00E7\u00F5es de Machine Learning"] }), _jsx("div", { className: "space-y-3", children: predicoes.map((pred, idx) => (_jsxs("div", { className: "p-4 border border-gray-200 rounded-lg hover:bg-gray-50", children: [_jsxs("div", { className: "flex items-center justify-between mb-2", children: [_jsx("span", { className: "font-mono text-sm font-medium", children: pred.numero_processo }), _jsxs("span", { className: `px-2 py-1 rounded-full text-xs font-medium ${pred.risco === 'baixo' ? 'bg-green-100 text-green-800' :
                                                        pred.risco === 'medio' ? 'bg-yellow-100 text-yellow-800' :
                                                            'bg-red-100 text-red-800'}`, children: ["Risco ", pred.risco.toUpperCase()] })] }), _jsxs("div", { className: "flex items-center gap-4 text-sm", children: [_jsxs("div", { children: [_jsx("span", { className: "text-gray-600", children: "Prob. Sucesso:" }), _jsxs("span", { className: "ml-2 font-medium", children: [(pred.probabilidade_sucesso * 100).toFixed(1), "%"] })] }), _jsxs("div", { children: [_jsx("span", { className: "text-gray-600", children: "Valor Est.:" }), _jsxs("span", { className: "ml-2 font-medium", children: ["R$ ", pred.valor_estimado.toLocaleString('pt-BR')] })] })] })] }, idx))) }), _jsx("button", { className: "w-full mt-4 px-4 py-2 text-center border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Ver Todas as Predi\u00E7\u00F5es" })] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsxs("h3", { className: "text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2", children: [_jsx(AlertTriangle, { className: "w-5 h-5 text-yellow-600" }), "Alertas Recentes"] }), _jsx("div", { className: "space-y-3", children: alertas.map((alerta) => (_jsx("div", { className: "p-4 border border-gray-200 rounded-lg", children: _jsxs("div", { className: "flex items-start gap-3", children: [_jsx(AlertTriangle, { className: `w-5 h-5 flex-shrink-0 ${alerta.severidade === 'alta' ? 'text-red-600' :
                                                    alerta.severidade === 'media' ? 'text-yellow-600' :
                                                        'text-blue-600'}` }), _jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "flex items-center justify-between mb-1", children: [_jsx("span", { className: "font-medium text-sm", children: alerta.tipo }), _jsx("span", { className: "text-xs text-gray-500", children: new Date(alerta.created_at).toLocaleDateString('pt-BR') })] }), _jsx("p", { className: "text-sm text-gray-600", children: alerta.mensagem })] })] }) }, alerta.id))) }), _jsx("button", { className: "w-full mt-4 px-4 py-2 text-center border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Ver Todos os Alertas" })] })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-6", children: [_jsxs("a", { href: "/setorenergia/mapa-risco", className: "bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow", children: [_jsx(MapPin, { className: "w-8 h-8 text-blue-600 mb-3" }), _jsx("h3", { className: "font-semibold text-gray-900 mb-2", children: "Mapa de Risco" }), _jsx("p", { className: "text-sm text-gray-600", children: "Visualiza\u00E7\u00E3o geogr\u00E1fica de riscos por regi\u00E3o" })] }), _jsxs("a", { href: "/setorenergia/sobrestados", className: "bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow", children: [_jsx(FileText, { className: "w-8 h-8 text-purple-600 mb-3" }), _jsx("h3", { className: "font-semibold text-gray-900 mb-2", children: "Sobrestados" }), _jsx("p", { className: "text-sm text-gray-600", children: "Processos sobrestados e an\u00E1lises" })] }), _jsxs("a", { href: "/setorenergia/relatorios", className: "bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow", children: [_jsx(BarChart3, { className: "w-8 h-8 text-green-600 mb-3" }), _jsx("h3", { className: "font-semibold text-gray-900 mb-2", children: "Relat\u00F3rios" }), _jsx("p", { className: "text-sm text-gray-600", children: "Relat\u00F3rios executivos e an\u00E1lises detalhadas" })] })] })] }));
}
