import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { Brain, Clock, CheckCircle2 } from 'lucide-react';
export default function AnalysisHub() {
    const navigate = useNavigate();
    const [analyses] = useState([
        {
            id: 1,
            name: 'Análise de Risco Processual',
            description: 'Avalia probabilidade de sucesso e riscos do processo',
            category: 'Processo',
            estimatedTime: '5-10 min',
            complexity: 'high'
        },
        {
            id: 2,
            name: 'Análise de Contratos',
            description: 'Identifica cláusulas abusivas e riscos contratuais',
            category: 'Contratos',
            estimatedTime: '3-7 min',
            complexity: 'medium'
        },
        {
            id: 3,
            name: 'Análise de Jurisprudência',
            description: 'Busca precedentes relevantes e tendências',
            category: 'Pesquisa',
            estimatedTime: '10-15 min',
            complexity: 'high'
        },
        {
            id: 4,
            name: 'Análise de Documentos',
            description: 'Extrai informações-chave de documentos',
            category: 'Documentos',
            estimatedTime: '2-5 min',
            complexity: 'low'
        },
        {
            id: 5,
            name: 'Análise de Timeline',
            description: 'Organiza eventos cronologicamente',
            category: 'Processo',
            estimatedTime: '3-8 min',
            complexity: 'medium'
        },
        {
            id: 6,
            name: 'Análise de Partes',
            description: 'Identifica e categoriza partes envolvidas',
            category: 'Processo',
            estimatedTime: '2-4 min',
            complexity: 'low'
        }
    ]);
    const [selectedCategory, setSelectedCategory] = useState('all');
    const categories = ['all', 'Processo', 'Contratos', 'Pesquisa', 'Documentos'];
    const filteredAnalyses = selectedCategory === 'all'
        ? analyses
        : analyses.filter(a => a.category === selectedCategory);
    const getComplexityColor = (level) => {
        switch (level) {
            case 'low': return 'bg-green-100 text-green-800';
            case 'medium': return 'bg-yellow-100 text-yellow-800';
            case 'high': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Central de An\u00E1lises", description: "Escolha o tipo de an\u00E1lise que deseja realizar" }), _jsx("div", { className: "flex gap-2 mb-6", children: categories.map(cat => (_jsx("button", { onClick: () => setSelectedCategory(cat), className: `px-4 py-2 rounded-lg font-medium transition-colors ${selectedCategory === cat
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'}`, children: cat === 'all' ? 'Todas' : cat }, cat))) }), _jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6", children: filteredAnalyses.map(analysis => (_jsxs("div", { onClick: () => navigate(`/analises/new?type=${analysis.id}`), className: "bg-white rounded-lg border border-gray-200 p-6 cursor-pointer hover:shadow-lg transition-shadow", children: [_jsxs("div", { className: "flex items-start justify-between mb-4", children: [_jsx("div", { className: "p-3 bg-blue-100 rounded-lg", children: _jsx(Brain, { className: "w-6 h-6 text-blue-600" }) }), _jsx("span", { className: `px-2 py-1 rounded-full text-xs font-medium ${getComplexityColor(analysis.complexity)}`, children: analysis.complexity === 'low' ? 'Simples' :
                                        analysis.complexity === 'medium' ? 'Médio' : 'Avançado' })] }), _jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-2", children: analysis.name }), _jsx("p", { className: "text-sm text-gray-600 mb-4", children: analysis.description }), _jsxs("div", { className: "flex items-center gap-4 text-sm text-gray-500", children: [_jsxs("div", { className: "flex items-center gap-1", children: [_jsx(Clock, { className: "w-4 h-4" }), analysis.estimatedTime] }), _jsxs("div", { className: "flex items-center gap-1", children: [_jsx(CheckCircle2, { className: "w-4 h-4" }), analysis.category] })] })] }, analysis.id))) })] }));
}
