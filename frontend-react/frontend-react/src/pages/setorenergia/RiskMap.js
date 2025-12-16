import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { MapPin, AlertCircle, TrendingUp, Filter } from 'lucide-react';
import api from '../../lib/api';
export default function RiskMap() {
    const [riskData, setRiskData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedRisk, setSelectedRisk] = useState('all');
    useEffect(() => {
        fetchRiskData();
    }, []);
    const fetchRiskData = async () => {
        try {
            const response = await api.get('/setorenergia/mapa-risco');
            setRiskData(response.data);
        }
        catch (error) {
            console.error('Error fetching risk data:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const getRiskColor = (nivel) => {
        switch (nivel) {
            case 'baixo': return 'bg-green-500';
            case 'medio': return 'bg-yellow-500';
            case 'alto': return 'bg-orange-500';
            case 'critico': return 'bg-red-500';
            default: return 'bg-gray-500';
        }
    };
    const getRiskLabel = (nivel) => {
        switch (nivel) {
            case 'baixo': return 'Baixo';
            case 'medio': return 'Médio';
            case 'alto': return 'Alto';
            case 'critico': return 'Crítico';
            default: return 'Desconhecido';
        }
    };
    const filteredData = selectedRisk === 'all'
        ? riskData
        : riskData.filter(d => d.nivel_risco === selectedRisk);
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Mapa de Risco", description: "Visualiza\u00E7\u00E3o de risco por regi\u00E3o" }), _jsx("div", { className: "bg-white rounded-lg border border-gray-200 p-4 mb-6", children: _jsxs("div", { className: "flex items-center gap-4", children: [_jsx(Filter, { className: "w-5 h-5 text-gray-600" }), _jsxs("select", { value: selectedRisk, onChange: (e) => setSelectedRisk(e.target.value), className: "px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "all", children: "Todos os N\u00EDveis" }), _jsx("option", { value: "critico", children: "Cr\u00EDtico" }), _jsx("option", { value: "alto", children: "Alto" }), _jsx("option", { value: "medio", children: "M\u00E9dio" }), _jsx("option", { value: "baixo", children: "Baixo" })] })] }) }), _jsx("div", { className: "bg-white rounded-lg border border-gray-200 p-6 mb-6", children: _jsx("div", { className: "bg-gray-100 rounded-lg h-96 flex items-center justify-center", children: _jsxs("div", { className: "text-center", children: [_jsx(MapPin, { className: "w-16 h-16 text-gray-400 mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-medium text-gray-900 mb-2", children: "Mapa Interativo" }), _jsx("p", { className: "text-gray-600 mb-4", children: "Integra\u00E7\u00E3o com Google Maps/Leaflet ser\u00E1 adicionada" }), _jsx("p", { className: "text-sm text-gray-500", children: "Visualiza\u00E7\u00E3o geogr\u00E1fica dos n\u00EDveis de risco por comarca" })] }) }) }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6 mb-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Legenda de Risco" }), _jsxs("div", { className: "grid grid-cols-2 md:grid-cols-4 gap-4", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "w-4 h-4 rounded-full bg-green-500" }), _jsx("span", { className: "text-sm text-gray-700", children: "Baixo" })] }), _jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "w-4 h-4 rounded-full bg-yellow-500" }), _jsx("span", { className: "text-sm text-gray-700", children: "M\u00E9dio" })] }), _jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "w-4 h-4 rounded-full bg-orange-500" }), _jsx("span", { className: "text-sm text-gray-700", children: "Alto" })] }), _jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "w-4 h-4 rounded-full bg-red-500" }), _jsx("span", { className: "text-sm text-gray-700", children: "Cr\u00EDtico" })] })] })] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200", children: [_jsx("div", { className: "p-4 border-b border-gray-200", children: _jsx("h3", { className: "text-lg font-semibold text-gray-900", children: "Dados por Comarca" }) }), _jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full", children: [_jsx("thead", { className: "bg-gray-50", children: _jsxs("tr", { children: [_jsx("th", { className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase", children: "Comarca" }), _jsx("th", { className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase", children: "N\u00EDvel de Risco" }), _jsx("th", { className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase", children: "Processos" }), _jsx("th", { className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase", children: "Valor Total" }), _jsx("th", { className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase", children: "Taxa Sucesso" })] }) }), _jsx("tbody", { className: "divide-y divide-gray-200", children: filteredData.map((item, index) => (_jsxs("tr", { className: "hover:bg-gray-50", children: [_jsx("td", { className: "px-6 py-4 whitespace-nowrap", children: _jsxs("div", { className: "flex items-center gap-2", children: [_jsx(MapPin, { className: "w-4 h-4 text-gray-400" }), _jsx("span", { className: "text-sm font-medium text-gray-900", children: item.comarca })] }) }), _jsx("td", { className: "px-6 py-4 whitespace-nowrap", children: _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("div", { className: `w-3 h-3 rounded-full ${getRiskColor(item.nivel_risco)}` }), _jsx("span", { className: "text-sm text-gray-700", children: getRiskLabel(item.nivel_risco) })] }) }), _jsx("td", { className: "px-6 py-4 whitespace-nowrap text-sm text-gray-900", children: item.total_processos }), _jsx("td", { className: "px-6 py-4 whitespace-nowrap text-sm text-gray-900", children: new Intl.NumberFormat('pt-BR', {
                                                    style: 'currency',
                                                    currency: 'BRL',
                                                    notation: 'compact'
                                                }).format(item.valor_total) }), _jsx("td", { className: "px-6 py-4 whitespace-nowrap", children: _jsxs("div", { className: "flex items-center gap-2", children: [_jsx(TrendingUp, { className: `w-4 h-4 ${item.taxa_sucesso >= 70 ? 'text-green-600' : 'text-orange-600'}` }), _jsxs("span", { className: "text-sm text-gray-900", children: [item.taxa_sucesso, "%"] })] }) })] }, index))) })] }) })] }), _jsx("div", { className: "mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4", children: _jsxs("div", { className: "flex items-start gap-3", children: [_jsx(AlertCircle, { className: "w-5 h-5 text-blue-600 mt-0.5" }), _jsxs("div", { children: [_jsx("h4", { className: "font-semibold text-blue-900 mb-1", children: "Sobre o Mapa de Risco" }), _jsx("p", { className: "text-sm text-blue-700", children: "O n\u00EDvel de risco \u00E9 calculado com base no n\u00FAmero de processos, valor em causa, taxa de sucesso hist\u00F3rica e tempo m\u00E9dio de tramita\u00E7\u00E3o por comarca." })] })] }) })] }));
}
