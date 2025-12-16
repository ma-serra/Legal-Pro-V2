import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { Play, FileText, Bot, AlertCircle } from 'lucide-react';
import api from '../../lib/api';
export default function MultiAgenteOrquestrador() {
    const navigate = useNavigate();
    const [selectedAgents, setSelectedAgents] = useState([]);
    const [texto, setTexto] = useState('');
    const [tipo, setTipo] = useState('completa');
    const [executing, setExecuting] = useState(false);
    const [resultado, setResultado] = useState(null);
    // Mock agents - would come from API
    const availableAgents = [
        { id: 1, nome: 'Agente Cível', especialidade: 'Direito Cível', disponivel: true },
        { id: 2, nome: 'Agente Trabalhista', especialidade: 'Direito Trabalhista', disponivel: true },
        { id: 3, nome: 'Agente Criminal', especialidade: 'Direito Criminal', disponivel: true },
        { id: 4, nome: 'Agente Tributário', especialidade: 'Direito Tributário', disponivel: true },
        { id: 5, nome: 'Agente Contratual', especialidade: 'Análise de Contratos', disponivel: true },
    ];
    const handleAgentToggle = (agentId) => {
        setSelectedAgents(prev => prev.includes(agentId)
            ? prev.filter(id => id !== agentId)
            : [...prev, agentId]);
    };
    // Endpoint: POST /api/multi-agente-real/analise-real
    const handleExecuteAnalysis = async () => {
        if (!texto.trim() || selectedAgents.length === 0) {
            alert('Selecione ao menos um agente e forneça um texto');
            return;
        }
        setExecuting(true);
        try {
            const response = await api.post('/api/multi-agente-real/analise-real', {
                texto,
                agentes_ids: selectedAgents,
                tipo_analise: tipo
            });
            setResultado(response.data);
        }
        catch (error) {
            console.error('Error executing analysis:', error);
            alert('Erro ao executar análise multi-agente');
        }
        finally {
            setExecuting(false);
        }
    };
    // Alternative endpoints:
    // POST /api/analise-multi-agente (older version)
    // POST /api/multi-agente-otimizada (optimized version)
    // POST /api/multi-agente-funcional (functional version)
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Orquestrador Multi-Agente", description: "Execute an\u00E1lises coordenadas com m\u00FAltiplos agentes IA" }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-3 gap-6", children: [_jsxs("div", { className: "lg:col-span-1 space-y-6", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsxs("h3", { className: "text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2", children: [_jsx(Bot, { className: "w-5 h-5" }), "Selecionar Agentes"] }), _jsx("div", { className: "space-y-2", children: availableAgents.map(agent => (_jsxs("label", { className: `flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${selectedAgents.includes(agent.id)
                                                ? 'border-blue-500 bg-blue-50'
                                                : 'border-gray-200 hover:bg-gray-50'}`, children: [_jsx("input", { type: "checkbox", checked: selectedAgents.includes(agent.id), onChange: () => handleAgentToggle(agent.id), className: "rounded" }), _jsxs("div", { className: "flex-1", children: [_jsx("div", { className: "font-medium text-sm", children: agent.nome }), _jsx("div", { className: "text-xs text-gray-500", children: agent.especialidade })] }), _jsx("div", { className: `w-2 h-2 rounded-full ${agent.disponivel ? 'bg-green-500' : 'bg-gray-300'}` })] }, agent.id))) }), _jsxs("div", { className: "mt-4 text-sm text-gray-600", children: [selectedAgents.length, " agente(s) selecionado(s)"] })] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Tipo de An\u00E1lise" }), _jsxs("select", { value: tipo, onChange: (e) => setTipo(e.target.value), className: "w-full px-4 py-2 border border-gray-300 rounded-lg", children: [_jsx("option", { value: "completa", children: "An\u00E1lise Completa" }), _jsx("option", { value: "resumida", children: "An\u00E1lise Resumida" }), _jsx("option", { value: "comparativa", children: "An\u00E1lise Comparativa" }), _jsx("option", { value: "consensual", children: "Busca Consenso" })] })] })] }), _jsxs("div", { className: "lg:col-span-2 space-y-6", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsxs("h3", { className: "text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2", children: [_jsx(FileText, { className: "w-5 h-5" }), "Texto para An\u00E1lise"] }), _jsx("textarea", { value: texto, onChange: (e) => setTexto(e.target.value), rows: 12, className: "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: "Cole aqui o texto, documento ou caso jur\u00EDdico para an\u00E1lise pelos agentes..." }), _jsxs("div", { className: "flex gap-3 mt-4", children: [_jsxs("button", { onClick: handleExecuteAnalysis, disabled: executing || !texto.trim() || selectedAgents.length === 0, className: "flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50", children: [_jsx(Play, { className: "w-4 h-4" }), executing ? 'Executando...' : 'Executar Análise'] }), resultado && (_jsx("button", { onClick: () => setResultado(null), className: "px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Nova An\u00E1lise" }))] })] }), resultado && (_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Resultados" }), resultado.analises?.map((analise, idx) => (_jsxs("div", { className: "mb-6 p-4 border border-gray-200 rounded-lg", children: [_jsxs("div", { className: "flex items-center justify-between mb-3", children: [_jsx("h4", { className: "font-semibold text-gray-900", children: analise.agente_nome }), _jsxs("span", { className: "text-sm text-gray-500", children: [analise.tempo_execucao, "s"] })] }), _jsx("div", { className: "prose prose-sm max-w-none", children: _jsx("p", { className: "text-gray-700", children: analise.resultado }) })] }, idx))), resultado.consenso && (_jsxs("div", { className: "mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg", children: [_jsxs("h4", { className: "font-semibold text-blue-900 mb-2 flex items-center gap-2", children: [_jsx(AlertCircle, { className: "w-5 h-5" }), "Consenso Multi-Agente"] }), _jsx("p", { className: "text-blue-800", children: resultado.consenso })] })), _jsxs("div", { className: "flex gap-3 mt-6 pt-6 border-t border-gray-200", children: [_jsx("button", { onClick: () => navigate(`/multi-agente/historico`), className: "px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Ver no Hist\u00F3rico" }), _jsx("button", { className: "px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Exportar Resultado" })] })] })), executing && (_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-12 text-center", children: [_jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" }), _jsxs("p", { className: "text-gray-600", children: ["Executando an\u00E1lise com ", selectedAgents.length, " agentes..."] }), _jsx("p", { className: "text-sm text-gray-500 mt-2", children: "Isso pode levar alguns segundos" })] }))] })] })] }));
}
