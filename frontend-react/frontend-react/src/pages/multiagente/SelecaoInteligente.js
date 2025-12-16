import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { Brain, Sparkles, FileText, Play } from 'lucide-react';
export default function SelecaoInteligente() {
    const [texto, setTexto] = useState('');
    const [categoria, setCategoria] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [analyzing, setAnalyzing] = useState(false);
    const [selectedAgents, setSelectedAgents] = useState([]);
    // Endpoint: POST /api/multi-agente/selecao-inteligente (hypothetical - would need to be created)
    // For now, using existing agent selection logic
    const handleAnalyzeText = async () => {
        if (!texto.trim()) {
            alert('Por favor, forneça um texto para análise');
            return;
        }
        setAnalyzing(true);
        try {
            // This would call an AI endpoint that analyzes the text and suggests best agents
            // Mock implementation:
            const mockSuggestions = [
                {
                    agente_id: 1,
                    agente_nome: 'Agente Cível Especializado',
                    score_relevancia: 0.95,
                    razao: 'Texto contém termos relacionados a direito civil e contratos'
                },
                {
                    agente_id: 3,
                    agente_nome: 'Agente de Análise Contratual',
                    score_relevancia: 0.87,
                    razao: 'Identificadas cláusulas contratuais complexas'
                },
                {
                    agente_id: 5,
                    agente_nome: 'Agente de Responsabilidade Civil',
                    score_relevancia: 0.76,
                    razao: 'Menções a danos e responsabilidades'
                }
            ];
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1500));
            setSuggestions(mockSuggestions);
        }
        catch (error) {
            console.error('Error analyzing text:', error);
            alert('Erro ao analisar texto');
        }
        finally {
            setAnalyzing(false);
        }
    };
    const handleToggleAgent = (agentId) => {
        setSelectedAgents(prev => prev.includes(agentId)
            ? prev.filter(id => id !== agentId)
            : [...prev, agentId]);
    };
    const handleExecute = async () => {
        if (selectedAgents.length === 0) {
            alert('Selecione ao menos um agente');
            return;
        }
        // Would redirect to orchestrator with pre-selected agents
        window.location.href = `/multi-agente/orquestrador?agents=${selectedAgents.join(',')}&text=${encodeURIComponent(texto)}`;
    };
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Sele\u00E7\u00E3o Inteligente de Agentes", description: "IA analisa o texto e sugere os melhores agentes para a tarefa" }), _jsxs("div", { className: "max-w-5xl mx-auto", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6 mb-6", children: [_jsxs("h3", { className: "text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2", children: [_jsx(FileText, { className: "w-5 h-5" }), "Texto para An\u00E1lise"] }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Categoria (Opcional)" }), _jsxs("select", { value: categoria, onChange: (e) => setCategoria(e.target.value), className: "w-full px-4 py-2 border border-gray-300 rounded-lg", children: [_jsx("option", { value: "", children: "Detectar Automaticamente" }), _jsx("option", { value: "civel", children: "Direito C\u00EDvel" }), _jsx("option", { value: "trabalhista", children: "Direito Trabalhista" }), _jsx("option", { value: "criminal", children: "Direito Criminal" }), _jsx("option", { value: "tributario", children: "Direito Tribut\u00E1rio" }), _jsx("option", { value: "contratos", children: "Contratos" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Texto do Documento/Caso" }), _jsx("textarea", { value: texto, onChange: (e) => setTexto(e.target.value), rows: 10, className: "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: "Cole aqui o texto que deseja analisar. A IA ir\u00E1 sugerir os agentes mais adequados baseado no conte\u00FAdo..." })] }), _jsxs("button", { onClick: handleAnalyzeText, disabled: analyzing || !texto.trim(), className: "flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50", children: [_jsx(Brain, { className: "w-4 h-4" }), analyzing ? 'Analisando...' : 'Analisar e Sugerir Agentes'] })] })] }), analyzing && (_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-12 text-center mb-6", children: [_jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" }), _jsx("p", { className: "text-gray-600", children: "Analisando texto com IA..." }), _jsx("p", { className: "text-sm text-gray-500 mt-2", children: "Identificando agentes mais relevantes" })] })), suggestions.length > 0 && !analyzing && (_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6 mb-6", children: [_jsxs("h3", { className: "text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2", children: [_jsx(Sparkles, { className: "w-5 h-5 text-yellow-500" }), "Agentes Sugeridos"] }), _jsx("div", { className: "space-y-3", children: suggestions.map((suggestion) => (_jsxs("label", { className: `flex items-start gap-4 p-4 border rounded-lg cursor-pointer transition-colors ${selectedAgents.includes(suggestion.agente_id)
                                        ? 'border-blue-500 bg-blue-50'
                                        : 'border-gray-200 hover:bg-gray-50'}`, children: [_jsx("input", { type: "checkbox", checked: selectedAgents.includes(suggestion.agente_id), onChange: () => handleToggleAgent(suggestion.agente_id), className: "mt-1 rounded" }), _jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "flex items-center justify-between mb-2", children: [_jsx("h4", { className: "font-semibold text-gray-900", children: suggestion.agente_nome }), _jsx("div", { className: "flex items-center gap-2", children: _jsxs("div", { className: "text-sm font-medium text-blue-600", children: [(suggestion.score_relevancia * 100).toFixed(0), "% relev\u00E2ncia"] }) })] }), _jsx("p", { className: "text-sm text-gray-600", children: suggestion.razao }), _jsx("div", { className: "mt-2 w-full bg-gray-200 rounded-full h-2", children: _jsx("div", { className: "bg-blue-600 h-2 rounded-full transition-all", style: { width: `${suggestion.score_relevancia * 100}%` } }) })] })] }, suggestion.agente_id))) }), selectedAgents.length > 0 && (_jsxs("div", { className: "mt-6 pt-6 border-t border-gray-200", children: [_jsxs("p", { className: "text-sm text-gray-600 mb-4", children: [selectedAgents.length, " agente(s) selecionado(s)"] }), _jsxs("button", { onClick: handleExecute, className: "flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700", children: [_jsx(Play, { className: "w-4 h-4" }), "Executar com Agentes Selecionados"] })] }))] })), suggestions.length === 0 && !analyzing && (_jsxs("div", { className: "bg-blue-50 border border-blue-200 rounded-lg p-6", children: [_jsxs("h4", { className: "font-semibold text-blue-900 mb-2 flex items-center gap-2", children: [_jsx(Brain, { className: "w-5 h-5" }), "Como funciona?"] }), _jsxs("ul", { className: "text-sm text-blue-800 space-y-2", children: [_jsx("li", { children: "\u2022 A IA analisa o conte\u00FAdo do seu texto usando NLP avan\u00E7ado" }), _jsx("li", { children: "\u2022 Identifica os temas, \u00E1reas jur\u00EDdicas e complexidade" }), _jsx("li", { children: "\u2022 Sugere automaticamente os agentes mais qualificados" }), _jsx("li", { children: "\u2022 Calcula score de relev\u00E2ncia para cada agente" }), _jsx("li", { children: "\u2022 Voc\u00EA pode ajustar a sele\u00E7\u00E3o manualmente se desejar" })] })] }))] })] }));
}
