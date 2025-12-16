import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader, StatCard } from '../../components/ui/AdminComponents';
import { TrendingUp, AlertTriangle, MapPin, Calendar, FileText, DollarSign, BarChart3 } from 'lucide-react';
import api from '../../lib/api';
export default function CPFLDashboard() {
    const navigate = useNavigate();
    const [stats, setStats] = useState({
        total_processos: 0,
        processos_ativos: 0,
        processos_sobrestados: 0,
        total_audiencias: 0,
        valor_total_causa: 0,
        taxa_sucesso: 0,
        proximas_audiencias: 0,
        alertas_pendentes: 0
    });
    const [recentProcesses, setRecentProcesses] = useState([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchDashboardData();
    }, []);
    const fetchDashboardData = async () => {
        try {
            const [statsRes, processesRes] = await Promise.all([
                api.get('/setorenergia/api/stats'),
                api.get('/setorenergia/api/processos?limit=5')
            ]);
            setStats(statsRes.data);
            setRecentProcesses(processesRes.data);
        }
        catch (error) {
            console.error('Error fetching dashboard data:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const formatCurrency = (value) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Setor Energia - Dashboard", description: "Vis\u00E3o geral dos processos CPFL e RGE" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6", children: [_jsx(StatCard, { title: "Total de Processos", value: stats.total_processos.toString(), icon: FileText, trend: { value: 5.2, isPositive: true } }), _jsx(StatCard, { title: "Processos Sobrestados", value: stats.processos_sobrestados.toString(), icon: AlertTriangle }), _jsx(StatCard, { title: "Valor Total em Causa", value: formatCurrency(stats.valor_total_causa), icon: DollarSign }), _jsx(StatCard, { title: "Taxa de Sucesso", value: `${stats.taxa_sucesso}%`, icon: TrendingUp, trend: { value: stats.taxa_sucesso, isPositive: stats.taxa_sucesso > 70 } })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6", children: [_jsxs("button", { onClick: () => navigate('/setorenergia/sobrestados'), className: "bg-white p-6 rounded-lg border border-gray-200 hover:border-orange-300 hover:shadow-md transition-all text-left", children: [_jsx(AlertTriangle, { className: "w-8 h-8 text-orange-600 mb-3" }), _jsx("h3", { className: "font-semibold text-gray-900 mb-1", children: "Sobrestados" }), _jsxs("p", { className: "text-sm text-gray-600", children: [stats.processos_sobrestados, " processos"] })] }), _jsxs("button", { onClick: () => navigate('/setorenergia/audiencias'), className: "bg-white p-6 rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all text-left", children: [_jsx(Calendar, { className: "w-8 h-8 text-blue-600 mb-3" }), _jsx("h3", { className: "font-semibold text-gray-900 mb-1", children: "Audi\u00EAncias" }), _jsxs("p", { className: "text-sm text-gray-600", children: [stats.proximas_audiencias, " pr\u00F3ximas"] })] }), _jsxs("button", { onClick: () => navigate('/setorenergia/mapa-risco'), className: "bg-white p-6 rounded-lg border border-gray-200 hover:border-red-300 hover:shadow-md transition-all text-left", children: [_jsx(MapPin, { className: "w-8 h-8 text-red-600 mb-3" }), _jsx("h3", { className: "font-semibold text-gray-900 mb-1", children: "Mapa de Risco" }), _jsx("p", { className: "text-sm text-gray-600", children: "Visualiza\u00E7\u00E3o geogr\u00E1fica" })] }), _jsxs("button", { onClick: () => navigate('/setorenergia/analytics'), className: "bg-white p-6 rounded-lg border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all text-left", children: [_jsx(BarChart3, { className: "w-8 h-8 text-purple-600 mb-3" }), _jsx("h3", { className: "font-semibold text-gray-900 mb-1", children: "Analytics" }), _jsx("p", { className: "text-sm text-gray-600", children: "An\u00E1lises detalhadas" })] })] }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Processos Recentes" }), _jsx("div", { className: "space-y-3", children: recentProcesses.map((process) => (_jsxs("div", { className: "flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer", onClick: () => navigate(`/processos/${process.id}`), children: [_jsxs("div", { className: "flex-1", children: [_jsx("p", { className: "font-medium text-gray-900 text-sm", children: process.titulo }), _jsxs("p", { className: "text-xs text-gray-600", children: ["N\u00BA ", process.numero] })] }), _jsxs("div", { className: "text-right", children: [_jsx("p", { className: "text-sm font-medium text-gray-900", children: formatCurrency(process.valor_causa) }), _jsx("span", { className: `text-xs px-2 py-1 rounded ${process.status === 'ativo' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`, children: process.status })] })] }, process.id))) }), _jsx("button", { onClick: () => navigate('/setorenergia/todos-processos'), className: "w-full mt-4 py-2 text-sm text-blue-600 hover:text-blue-700 font-medium", children: "Ver todos os processos \u2192" })] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Alertas & Notifica\u00E7\u00F5es" }), _jsx("div", { className: "space-y-3", children: stats.alertas_pendentes > 0 ? (_jsxs(_Fragment, { children: [_jsxs("div", { className: "flex items-start gap-3 p-3 bg-orange-50 rounded-lg", children: [_jsx(AlertTriangle, { className: "w-5 h-5 text-orange-600 mt-0.5" }), _jsxs("div", { children: [_jsxs("p", { className: "font-medium text-gray-900 text-sm", children: [stats.processos_sobrestados, " processos sobrestados"] }), _jsx("p", { className: "text-xs text-gray-600 mt-1", children: "Requerem an\u00E1lise e a\u00E7\u00E3o imediata" })] })] }), _jsxs("div", { className: "flex items-start gap-3 p-3 bg-blue-50 rounded-lg", children: [_jsx(Calendar, { className: "w-5 h-5 text-blue-600 mt-0.5" }), _jsxs("div", { children: [_jsxs("p", { className: "font-medium text-gray-900 text-sm", children: [stats.proximas_audiencias, " audi\u00EAncias pr\u00F3ximas"] }), _jsx("p", { className: "text-xs text-gray-600 mt-1", children: "Nos pr\u00F3ximos 7 dias" })] })] }), _jsxs("div", { className: "flex items-start gap-3 p-3 bg-green-50 rounded-lg", children: [_jsx(TrendingUp, { className: "w-5 h-5 text-green-600 mt-0.5" }), _jsxs("div", { children: [_jsx("p", { className: "font-medium text-gray-900 text-sm", children: "Taxa de sucesso em alta" }), _jsxs("p", { className: "text-xs text-gray-600 mt-1", children: [stats.taxa_sucesso, "% de decis\u00F5es favor\u00E1veis"] })] })] })] })) : (_jsxs("div", { className: "text-center py-8 text-gray-500", children: [_jsx(AlertTriangle, { className: "w-12 h-12 mx-auto mb-2 text-gray-400" }), _jsx("p", { className: "text-sm", children: "Nenhum alerta no momento" })] })) })] })] })] }));
}
