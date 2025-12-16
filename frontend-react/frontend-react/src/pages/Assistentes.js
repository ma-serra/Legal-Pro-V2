import { jsxs as _jsxs, jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
import { useState } from 'react';
import { Users, MessageCircle, Send, Sparkles } from 'lucide-react';
import PageHeader from '../components/ui/PageHeader';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import api from '../lib/api';
const assistentes = [
    { id: 'civil', nome: 'Assistente Civil', area: 'Direito Civil', descricao: 'Especialista em contratos, responsabilidade civil e obrigações.', cor: 'bg-blue-600' },
    { id: 'trabalhista', nome: 'Assistente Trabalhista', area: 'Direito Trabalhista', descricao: 'Expert em CLT, relações de trabalho e direitos do trabalhador.', cor: 'bg-green-600' },
    { id: 'empresarial', nome: 'Assistente Empresarial', area: 'Direito Empresarial', descricao: 'Focado em sociedades, contratos comerciais e recuperação judicial.', cor: 'bg-purple-600' },
    { id: 'tributario', nome: 'Assistente Tributário', area: 'Direito Tributário', descricao: 'Especializado em tributos, planejamento fiscal e contencioso.', cor: 'bg-yellow-600' },
    { id: 'previdenciario', nome: 'Assistente Previdenciário', area: 'Direito Previdenciário', descricao: 'Expert em aposentadoria, benefícios e INSS.', cor: 'bg-orange-600' },
    { id: 'penal', nome: 'Assistente Penal', area: 'Direito Penal', descricao: 'Focado em crimes, processo penal e execução penal.', cor: 'bg-red-600' },
    { id: 'imobiliario', nome: 'Assistente Imobiliário', area: 'Direito Imobiliário', descricao: 'Especialista em compra/venda, locação e registros.', cor: 'bg-teal-600' },
    { id: 'consumidor', nome: 'Assistente do Consumidor', area: 'Direito do Consumidor', descricao: 'Expert em CDC, relações de consumo e proteção.', cor: 'bg-pink-600' },
    { id: 'familia', nome: 'Assistente de Família', area: 'Direito de Família', descricao: 'Focado em divórcio, guarda, pensão e sucessões.', cor: 'bg-indigo-600' },
    { id: 'digital', nome: 'Assistente Digital', area: 'Direito Digital', descricao: 'Especializado em LGPD, crimes cibernéticos e contratos digitais.', cor: 'bg-cyan-600' },
    { id: 'ambiental', nome: 'Assistente Ambiental', area: 'Direito Ambiental', descricao: 'Expert em licenciamento, crimes ambientais e sustentabilidade.', cor: 'bg-emerald-600' },
    { id: 'administrativo', nome: 'Assistente Administrativo', area: 'Direito Administrativo', descricao: 'Focado em licitações, servidores públicos e atos administrativos.', cor: 'bg-slate-600' }
];
export default function Assistentes() {
    const [assistenteSelecionado, setAssistenteSelecionado] = useState(null);
    const [mensagem, setMensagem] = useState('');
    const [mensagens, setMensagens] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const enviarMensagem = async () => {
        if (!mensagem.trim() || !assistenteSelecionado)
            return;
        const novaMensagem = {
            role: 'user',
            content: mensagem,
            timestamp: new Date()
        };
        setMensagens(prev => [...prev, novaMensagem]);
        setMensagem('');
        setIsLoading(true);
        try {
            const response = await api.post('/assistente/chat', {
                assistente: assistenteSelecionado.id,
                mensagem: mensagem,
                historico: mensagens
            });
            const respostaAssistente = {
                role: 'assistant',
                content: response.data.resposta || response.data.message || 'Resposta recebida.',
                timestamp: new Date()
            };
            setMensagens(prev => [...prev, respostaAssistente]);
        }
        catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            const respostaDemo = {
                role: 'assistant',
                content: `Olá! Sou o ${assistenteSelecionado.nome}, especializado em ${assistenteSelecionado.area}. 

Como posso ajudá-lo hoje? Posso auxiliar com:
- Análise de casos e documentos
- Estratégias jurídicas
- Pesquisa de jurisprudência
- Elaboração de peças processuais
- Orientações sobre procedimentos

*Esta é uma resposta de demonstração. Em produção, a resposta viria dos modelos de IA integrados.*`,
                timestamp: new Date()
            };
            setMensagens(prev => [...prev, respostaDemo]);
        }
        finally {
            setIsLoading(false);
        }
    };
    const selecionarAssistente = (assistente) => {
        setAssistenteSelecionado(assistente);
        setMensagens([{
                role: 'assistant',
                content: `Olá! Sou o ${assistente.nome}, especializado em ${assistente.area}. ${assistente.descricao} Como posso ajudá-lo hoje?`,
                timestamp: new Date()
            }]);
    };
    return (_jsxs("div", { className: "space-y-6", children: [_jsx(PageHeader, { title: "Assistentes Jur\u00EDdicos", icon: Users, children: _jsxs(Button, { variant: "secondary", icon: Sparkles, children: [assistentes.length, " Assistentes"] }) }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-3 gap-6", children: [_jsxs("div", { className: "lg:col-span-1 space-y-4", children: [_jsx("h3", { className: "font-semibold text-foreground", children: "Escolha um Assistente" }), _jsx("div", { className: "space-y-2 max-h-[600px] overflow-y-auto pr-2", children: assistentes.map((assistente) => (_jsx("button", { onClick: () => selecionarAssistente(assistente), className: `w-full p-4 rounded-lg border text-left transition ${assistenteSelecionado?.id === assistente.id
                                        ? 'border-primary bg-primary/10'
                                        : 'border-border hover:border-primary/50 bg-card'}`, children: _jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: `w-10 h-10 rounded-full ${assistente.cor} flex items-center justify-center`, children: _jsx(Users, { className: "w-5 h-5 text-white" }) }), _jsxs("div", { children: [_jsx("h4", { className: "font-medium text-foreground", children: assistente.nome }), _jsx("p", { className: "text-xs text-muted-foreground", children: assistente.area })] })] }) }, assistente.id))) })] }), _jsx("div", { className: "lg:col-span-2 bg-card rounded-xl border border-border flex flex-col h-[650px]", children: assistenteSelecionado ? (_jsxs(_Fragment, { children: [_jsxs("div", { className: "p-4 border-b border-border flex items-center gap-3", children: [_jsx("div", { className: `w-10 h-10 rounded-full ${assistenteSelecionado.cor} flex items-center justify-center`, children: _jsx(Users, { className: "w-5 h-5 text-white" }) }), _jsxs("div", { children: [_jsx("h3", { className: "font-semibold text-foreground", children: assistenteSelecionado.nome }), _jsx("p", { className: "text-sm text-muted-foreground", children: assistenteSelecionado.area })] })] }), _jsxs("div", { className: "flex-1 overflow-y-auto p-4 space-y-4", children: [mensagens.map((msg, idx) => (_jsx("div", { className: `flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`, children: _jsxs("div", { className: `max-w-[80%] p-3 rounded-lg ${msg.role === 'user'
                                                    ? 'bg-primary text-primary-foreground'
                                                    : 'bg-background border border-border'}`, children: [_jsx("p", { className: "text-sm whitespace-pre-wrap", children: msg.content }), _jsx("p", { className: "text-xs opacity-70 mt-1", children: msg.timestamp.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) })] }) }, idx))), isLoading && (_jsx("div", { className: "flex justify-start", children: _jsx("div", { className: "bg-background border border-border p-3 rounded-lg", children: _jsx(LoadingSpinner, { size: "sm" }) }) }))] }), _jsx("div", { className: "p-4 border-t border-border", children: _jsxs("div", { className: "flex gap-2", children: [_jsx("input", { type: "text", value: mensagem, onChange: (e) => setMensagem(e.target.value), onKeyDown: (e) => e.key === 'Enter' && !e.shiftKey && enviarMensagem(), placeholder: "Digite sua mensagem...", className: "flex-1 px-4 py-2 bg-background border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary" }), _jsx(Button, { onClick: enviarMensagem, icon: Send, disabled: !mensagem.trim() || isLoading, children: "Enviar" })] }) })] })) : (_jsxs("div", { className: "flex-1 flex flex-col items-center justify-center text-muted-foreground", children: [_jsx(MessageCircle, { className: "w-16 h-16 mb-4 opacity-50" }), _jsx("p", { className: "text-lg", children: "Selecione um assistente" }), _jsx("p", { className: "text-sm", children: "para iniciar uma conversa" })] })) })] })] }));
}
