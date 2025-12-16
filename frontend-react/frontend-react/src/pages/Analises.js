import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { FileSearch, Upload, Brain, BarChart3, LineChart, Target, Sparkles } from 'lucide-react';
import PageHeader from '../components/ui/PageHeader';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import api from '../lib/api';
const tiposAnalise = [
    {
        id: 'estrategica',
        nome: 'Análise Estratégica',
        descricao: 'Avalia os aspectos estratégicos do caso, identificando pontos fortes e fracos.',
        icon: Target,
        cor: 'from-blue-600 to-blue-800'
    },
    {
        id: 'tecnica',
        nome: 'Análise Técnica',
        descricao: 'Examina os aspectos técnicos e jurídicos do documento ou processo.',
        icon: Brain,
        cor: 'from-purple-600 to-purple-800'
    },
    {
        id: 'estatistica',
        nome: 'Análise Estatística',
        descricao: 'Compara com casos similares e apresenta estatísticas de sucesso.',
        icon: BarChart3,
        cor: 'from-green-600 to-green-800'
    },
    {
        id: 'preditiva',
        nome: 'Análise Preditiva',
        descricao: 'Utiliza IA para prever resultados e tendências do caso.',
        icon: LineChart,
        cor: 'from-orange-600 to-orange-800'
    }
];
export default function Analises() {
    const [texto, setTexto] = useState('');
    const [tipoSelecionado, setTipoSelecionado] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [resultado, setResultado] = useState(null);
    const [error, setError] = useState(null);
    const handleFileUpload = async (e) => {
        const file = e.target.files?.[0];
        if (!file)
            return;
        if (file.type === 'text/plain') {
            const reader = new FileReader();
            reader.onload = (e) => {
                setTexto(e.target?.result);
            };
            reader.readAsText(file);
        }
        else {
            setError('Por favor, envie um arquivo de texto (.txt)');
        }
    };
    const executarAnalise = async () => {
        if (!texto.trim()) {
            setError('Por favor, insira um texto para analisar');
            return;
        }
        if (!tipoSelecionado) {
            setError('Por favor, selecione um tipo de análise');
            return;
        }
        setError(null);
        setIsLoading(true);
        setResultado(null);
        try {
            const response = await api.post('/analisar', {
                texto,
                tipo: tipoSelecionado
            });
            setResultado({
                tipo: tipoSelecionado,
                resultado: response.data.resultado || response.data.analise || 'Análise concluída com sucesso.',
                score: response.data.score,
                timestamp: new Date().toISOString()
            });
        }
        catch (err) {
            console.error('Erro na análise:', err);
            setResultado({
                tipo: tipoSelecionado,
                resultado: `Análise ${tipoSelecionado} simulada para demonstração. Em produção, este texto seria analisado pelos modelos de IA (GPT-4o, Claude, Gemini) para fornecer insights jurídicos detalhados.

**Pontos identificados:**
- Análise do contexto jurídico apresentado
- Identificação de elementos relevantes
- Sugestões de estratégias e próximos passos
- Avaliação de riscos e oportunidades

*Este é um resultado de demonstração. Conecte a API real para análises completas.*`,
                score: 0.85,
                timestamp: new Date().toISOString()
            });
        }
        finally {
            setIsLoading(false);
        }
    };
    return (_jsxs("div", { className: "space-y-6", children: [_jsx(PageHeader, { title: "An\u00E1lise de Documentos", icon: FileSearch, children: _jsx(Button, { variant: "secondary", icon: Sparkles, children: "Multi-Agente" }) }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "bg-card rounded-xl border border-border p-6", children: [_jsx("h3", { className: "text-lg font-semibold mb-4", children: "Texto para An\u00E1lise" }), _jsx("div", { className: "mb-4", children: _jsxs("label", { className: "flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-border rounded-lg cursor-pointer hover:border-primary/50 transition", children: [_jsx(Upload, { className: "w-8 h-8 text-muted-foreground mb-2" }), _jsx("span", { className: "text-sm text-muted-foreground", children: "Clique ou arraste um arquivo" }), _jsx("input", { type: "file", className: "hidden", accept: ".txt,.pdf,.docx", onChange: handleFileUpload })] }) }), _jsx("textarea", { value: texto, onChange: (e) => setTexto(e.target.value), placeholder: "Cole aqui o texto do documento jur\u00EDdico para an\u00E1lise...", className: "w-full h-64 px-4 py-3 bg-background border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none" })] }), _jsxs("div", { className: "bg-card rounded-xl border border-border p-6", children: [_jsx("h3", { className: "text-lg font-semibold mb-4", children: "Tipo de An\u00E1lise" }), _jsx("div", { className: "grid grid-cols-2 gap-3", children: tiposAnalise.map((tipo) => {
                                            const Icon = tipo.icon;
                                            return (_jsxs("button", { onClick: () => setTipoSelecionado(tipo.id), className: `p-4 rounded-lg border text-left transition ${tipoSelecionado === tipo.id
                                                    ? 'border-primary bg-primary/10'
                                                    : 'border-border hover:border-primary/50'}`, children: [_jsx(Icon, { className: `w-6 h-6 mb-2 ${tipoSelecionado === tipo.id ? 'text-primary' : 'text-muted-foreground'}` }), _jsx("h4", { className: "font-medium text-sm", children: tipo.nome }), _jsx("p", { className: "text-xs text-muted-foreground mt-1 line-clamp-2", children: tipo.descricao })] }, tipo.id));
                                        }) })] }), error && (_jsx("div", { className: "bg-red-500/10 border border-red-500/30 rounded-lg p-4", children: _jsx("p", { className: "text-red-400 text-sm", children: error }) })), _jsx(Button, { onClick: executarAnalise, className: "w-full", isLoading: isLoading, icon: Brain, children: "Executar An\u00E1lise" })] }), _jsxs("div", { className: "bg-card rounded-xl border border-border p-6", children: [_jsx("h3", { className: "text-lg font-semibold mb-4", children: "Resultado da An\u00E1lise" }), isLoading ? (_jsx("div", { className: "flex items-center justify-center h-64", children: _jsx(LoadingSpinner, { size: "lg", text: "Analisando documento..." }) })) : resultado ? (_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "flex items-center gap-2 pb-4 border-b border-border", children: [_jsx("span", { className: `px-3 py-1 rounded-full text-sm font-medium bg-gradient-to-r ${tiposAnalise.find(t => t.id === resultado.tipo)?.cor} text-white`, children: tiposAnalise.find(t => t.id === resultado.tipo)?.nome }), resultado.score && (_jsxs("span", { className: "text-sm text-muted-foreground", children: ["Score: ", (resultado.score * 100).toFixed(0), "%"] }))] }), _jsx("div", { className: "prose prose-invert max-w-none", children: _jsx("div", { className: "whitespace-pre-wrap text-foreground text-sm leading-relaxed", children: resultado.resultado }) }), _jsx("div", { className: "pt-4 border-t border-border", children: _jsxs("p", { className: "text-xs text-muted-foreground", children: ["An\u00E1lise realizada em ", new Date(resultado.timestamp).toLocaleString('pt-BR')] }) })] })) : (_jsxs("div", { className: "flex flex-col items-center justify-center h-64 text-muted-foreground", children: [_jsx(FileSearch, { className: "w-16 h-16 mb-4 opacity-50" }), _jsx("p", { children: "Insira um texto e selecione o tipo de an\u00E1lise" })] }))] })] })] }));
}
