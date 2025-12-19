import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Assistentes Jurídicos - Interface Completa
 * Features: Drag & Drop, Histórico, Salvar, Excluir
 */
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Upload, History, Save, Trash2, Download, Send, Paperclip, X, FileText, Clock, ChevronLeft } from 'lucide-react';
import api from '../lib/api';
const assistentes = [
    { id: 'direito_civil', nome: 'Assistente Cível', descricao: 'Direito Cível', cor: 'blue' },
    { id: 'direito_trabalhista', nome: 'Assistente Trabalhista', descricao: 'Direito Trabalhista', cor: 'green' },
    { id: 'direito_empresarial', nome: 'Assistente Empresarial', descricao: 'Direito Empresarial', cor: 'purple' },
    { id: 'direito_tributario', nome: 'Assistente Tributário', descricao: 'Direito Tributário', cor: 'orange' },
    { id: 'direito_previdenciario', nome: 'Assistente Previdenciário', descricao: 'Direito Previdenciário', cor: 'red' },
    { id: 'direito_penal', nome: 'Assistente Penal', descricao: 'Direito Penal', cor: 'red' },
    { id: 'direito_administrativo', nome: 'Assistente Administrativo', descricao: 'Direito Administrativo', cor: 'teal' },
    { id: 'direito_constitucional', nome: 'Assistente Constitucional', descricao: 'Direito Constitucional', cor: 'indigo' }
];
export default function Assistentes() {
    const navigate = useNavigate();
    const [assistenteSelecionado, setAssistenteSelecionado] = useState(null);
    const [conversaAtual, setConversaAtual] = useState(null);
    const [mensagens, setMensagens] = useState([]);
    const [inputMensagem, setInputMensagem] = useState('');
    const [enviando, setEnviando] = useState(false);
    const [historico, setHistorico] = useState([]);
    const [mostrarHistorico, setMostrarHistorico] = useState(false);
    const [arquivosSelecionados, setArquivosSelecionados] = useState([]);
    const [dragOver, setDragOver] = useState(false);
    const fileInputRef = useRef(null);
    const messagesEndRef = useRef(null);
    useEffect(() => {
        carregarHistorico();
    }, []);
    useEffect(() => {
        scrollToBottom();
    }, [mensagens]);
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };
    const carregarHistorico = async () => {
        try {
            const conversasSalvas = localStorage.getItem('conversas_assistentes');
            if (conversasSalvas) {
                setHistorico(JSON.parse(conversasSalvas));
            }
        }
        catch (error) {
            console.error('Erro ao carregar histórico:', error);
        }
    };
    const selecionarAssistente = (id) => {
        const idStr = String(id);
        setAssistenteSelecionado(idStr);
        setConversaAtual({
            id: Date.now().toString(),
            titulo: `Nova conversa - ${assistentes.find(a => a.id === idStr)?.nome}`,
            assistente_id: idStr,
            mensagens: [],
            criado_em: new Date(),
            atualizado_em: new Date()
        });
        setMensagens([]);
        setArquivosSelecionados([]);
    };
    const handleDragOver = (e) => {
        e.preventDefault();
        setDragOver(true);
    };
    const handleDragLeave = () => {
        setDragOver(false);
    };
    const handleDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        const files = Array.from(e.dataTransfer.files);
        setArquivosSelecionados(prev => [...prev, ...files]);
    };
    const handleFileSelect = (e) => {
        if (e.target.files) {
            const files = Array.from(e.target.files);
            setArquivosSelecionados(prev => [...prev, ...files]);
        }
    };
    const removerArquivo = (index) => {
        setArquivosSelecionados(prev => prev.filter((_, i) => i !== index));
    };
    const enviarMensagem = async () => {
        if (!inputMensagem.trim() && arquivosSelecionados.length === 0)
            return;
        if (!assistenteSelecionado)
            return;
        setEnviando(true);
        const novaMensagem = {
            id: Date.now().toString(),
            role: 'user',
            content: inputMensagem,
            timestamp: new Date(),
            arquivos: arquivosSelecionados.map(f => f.name)
        };
        setMensagens(prev => [...prev, novaMensagem]);
        setInputMensagem('');
        const arquivosTemp = [...arquivosSelecionados];
        setArquivosSelecionados([]);
        try {
            // Chamada real à API
            const response = await api.post('/api/assistentes/consultar', {
                area: assistenteSelecionado, // Enviando ID da área (ex: 'direito_civil')
                pergunta: inputMensagem,
                contexto: '', // Contexto adicional se necessário
                modelo: 'gpt-4o' // Modelo padrão ou selecionado nas preferências
            });
            const respostaTexto = response.data.resposta || response.data.content || "Não foi possível obter resposta.";
            const respostaAssistente = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: respostaTexto,
                timestamp: new Date()
            };
            setMensagens(prev => [...prev, respostaAssistente]);
            // Atualizar conversa atual
            if (conversaAtual) {
                const conversaAtualizada = {
                    ...conversaAtual,
                    mensagens: [...mensagens, novaMensagem, respostaAssistente],
                    atualizado_em: new Date()
                };
                setConversaAtual(conversaAtualizada);
            }
        }
        catch (error) {
            console.error('Erro ao enviar mensagem:', error);
        }
        finally {
            setEnviando(false);
        }
    };
    const salvarConversa = () => {
        if (!conversaAtual || mensagens.length === 0)
            return;
        const conversaParaSalvar = {
            ...conversaAtual,
            mensagens,
            atualizado_em: new Date()
        };
        const historicoAtualizado = [conversaParaSalvar, ...historico.filter(c => c.id !== conversaAtual.id)];
        setHistorico(historicoAtualizado);
        localStorage.setItem('conversas_assistentes', JSON.stringify(historicoAtualizado));
        alert('Conversa salva com sucesso!');
    };
    const carregarConversa = (conversa) => {
        setConversaAtual(conversa);
        setMensagens(conversa.mensagens);
        setAssistenteSelecionado(conversa.assistente_id);
        setMostrarHistorico(false);
    };
    const excluirConversa = (id) => {
        if (!confirm('Deseja realmente excluir esta conversa?'))
            return;
        const historicoAtualizado = historico.filter(c => c.id !== id);
        setHistorico(historicoAtualizado);
        localStorage.setItem('conversas_assistentes', JSON.stringify(historicoAtualizado));
        if (conversaAtual?.id === id) {
            setConversaAtual(null);
            setMensagens([]);
            setAssistenteSelecionado(null);
        }
    };
    const exportarConversa = () => {
        if (!conversaAtual || mensagens.length === 0)
            return;
        const conteudo = mensagens.map(m => `[${m.timestamp.toLocaleString('pt-BR')}] ${m.role === 'user' ? 'Você' : 'Assistente'}:\n${m.content}\n${m.arquivos ? `Arquivos: ${m.arquivos.join(', ')}\n` : ''}\n`).join('\n');
        const blob = new Blob([conteudo], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `conversa_${conversaAtual.id}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    };
    // View: Seleção de Assistente
    if (!assistenteSelecionado) {
        return (_jsxs("div", { className: "p-6 max-w-7xl mx-auto", children: [_jsxs("div", { className: "flex items-center justify-between mb-8", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold mb-2", children: "Assistentes Jur\u00EDdicos" }), _jsx("p", { className: "text-muted-foreground", children: "Escolha um assistente especializado" })] }), _jsxs("button", { onClick: () => setMostrarHistorico(!mostrarHistorico), className: "flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors", children: [_jsx(History, { className: "w-5 h-5" }), "Hist\u00F3rico (", historico.length, ")"] })] }), mostrarHistorico ? (_jsxs("div", { className: "space-y-4", children: [_jsxs("button", { onClick: () => setMostrarHistorico(false), className: "flex items-center gap-2 text-primary hover:underline mb-4", children: [_jsx(ChevronLeft, { className: "w-4 h-4" }), "Voltar para assistentes"] }), historico.length === 0 ? (_jsxs("div", { className: "text-center py-12 bg-card border border-border rounded-xl", children: [_jsx(History, { className: "w-12 h-12 mx-auto text-muted-foreground mb-4" }), _jsx("p", { className: "text-muted-foreground", children: "Nenhuma conversa salva" })] })) : (_jsx("div", { className: "grid gap-4", children: historico.map(conversa => (_jsx("div", { className: "bg-card border border-border rounded-xl p-6 hover:shadow-lg transition-all", children: _jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { className: "flex-1", children: [_jsx("h3", { className: "font-semibold mb-2", children: conversa.titulo }), _jsxs("p", { className: "text-sm text-muted-foreground mb-2", children: [conversa.mensagens.length, " mensagens"] }), _jsxs("p", { className: "text-xs text-muted-foreground", children: [_jsx(Clock, { className: "w-3 h-3 inline mr-1" }), new Date(conversa.atualizado_em).toLocaleString('pt-BR')] })] }), _jsxs("div", { className: "flex gap-2", children: [_jsx("button", { onClick: () => carregarConversa(conversa), className: "px-3 py-2 bg-primary hover:bg-primary/90 rounded-lg text-sm", children: "Abrir" }), _jsx("button", { onClick: () => excluirConversa(conversa.id), className: "px-3 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg", children: _jsx(Trash2, { className: "w-4 h-4" }) })] })] }) }, conversa.id))) }))] })) : (_jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4", children: assistentes.map(assistente => (_jsxs("button", { onClick: () => selecionarAssistente(assistente.id), className: "bg-card border border-border rounded-xl p-6 hover:shadow-xl hover:scale-105 transition-all text-left group", children: [_jsx("div", { className: `w-12 h-12 rounded-full bg-${assistente.cor}-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`, children: _jsx(MessageSquare, { className: `w-6 h-6 text-${assistente.cor}-400` }) }), _jsx("h3", { className: "font-semibold mb-2 group-hover:text-primary transition-colors", children: assistente.nome }), _jsx("p", { className: "text-sm text-muted-foreground", children: assistente.descricao })] }, assistente.id))) }))] }));
    }
    // View: Chat
    return (_jsxs("div", { className: "flex flex-col h-[calc(100vh-80px)]", children: [_jsxs("div", { className: "border-b border-border bg-card p-4 flex items-center justify-between", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("button", { onClick: () => setAssistenteSelecionado(null), className: "p-2 hover:bg-accent rounded-lg transition-colors", children: _jsx(ChevronLeft, { className: "w-5 h-5" }) }), _jsxs("div", { children: [_jsx("h2", { className: "font-semibold", children: assistentes.find(a => a.id === assistenteSelecionado)?.nome }), _jsxs("p", { className: "text-xs text-muted-foreground", children: [mensagens.length, " mensagens"] })] })] }), _jsxs("div", { className: "flex gap-2", children: [_jsx("button", { onClick: () => setMostrarHistorico(true), className: "p-2 hover:bg-accent rounded-lg transition-colors", title: "Hist\u00F3rico", children: _jsx(History, { className: "w-5 h-5" }) }), _jsx("button", { onClick: salvarConversa, disabled: mensagens.length === 0, className: "p-2 hover:bg-accent rounded-lg transition-colors disabled:opacity-50", title: "Salvar conversa", children: _jsx(Save, { className: "w-5 h-5" }) }), _jsx("button", { onClick: exportarConversa, disabled: mensagens.length === 0, className: "p-2 hover:bg-accent rounded-lg transition-colors disabled:opacity-50", title: "Exportar", children: _jsx(Download, { className: "w-5 h-5" }) })] })] }), _jsxs("div", { className: "flex-1 overflow-y-auto p-6 space-y-4 bg-background", children: [mensagens.length === 0 ? (_jsxs("div", { className: "text-center py-12", children: [_jsx(MessageSquare, { className: "w-16 h-16 mx-auto text-muted-foreground mb-4" }), _jsx("p", { className: "text-lg font-medium mb-2", children: "Inicie uma conversa" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Envie uma mensagem ou anexe arquivos para an\u00E1lise" })] })) : (mensagens.map(mensagem => (_jsx("div", { className: `flex ${mensagem.role === 'user' ? 'justify-end' : 'justify-start'}`, children: _jsxs("div", { className: `max-w-[70%] rounded-xl p-4 ${mensagem.role === 'user'
                                ? 'bg-primary text-white'
                                : 'bg-card border border-border'}`, children: [_jsx("p", { className: "whitespace-pre-wrap", children: mensagem.content }), mensagem.arquivos && mensagem.arquivos.length > 0 && (_jsx("div", { className: "mt-3 pt-3 border-t border-white/20 space-y-1", children: mensagem.arquivos.map((arquivo, idx) => (_jsxs("div", { className: "flex items-center gap-2 text-xs", children: [_jsx(Paperclip, { className: "w-3 h-3" }), _jsx("span", { children: arquivo })] }, idx))) })), _jsx("p", { className: `text-xs mt-2 ${mensagem.role === 'user' ? 'text-white/70' : 'text-muted-foreground'}`, children: new Date(mensagem.timestamp).toLocaleTimeString('pt-BR') })] }) }, mensagem.id)))), _jsx("div", { ref: messagesEndRef })] }), _jsxs("div", { className: `border-t border-border bg-card p-4 ${dragOver ? 'bg-primary/10' : ''}`, onDragOver: handleDragOver, onDragLeave: handleDragLeave, onDrop: handleDrop, children: [arquivosSelecionados.length > 0 && (_jsx("div", { className: "mb-3 flex flex-wrap gap-2", children: arquivosSelecionados.map((arquivo, index) => (_jsxs("div", { className: "flex items-center gap-2 bg-accent px-3 py-2 rounded-lg text-sm", children: [_jsx(FileText, { className: "w-4 h-4" }), _jsx("span", { children: arquivo.name }), _jsx("button", { onClick: () => removerArquivo(index), className: "hover:text-red-400", children: _jsx(X, { className: "w-4 h-4" }) })] }, index))) })), _jsxs("div", { className: "flex gap-2", children: [_jsx("input", { type: "file", ref: fileInputRef, onChange: handleFileSelect, multiple: true, className: "hidden" }), _jsx("button", { onClick: () => fileInputRef.current?.click(), className: "p-3 hover:bg-accent rounded-lg transition-colors", title: "Anexar arquivos", children: _jsx(Paperclip, { className: "w-5 h-5" }) }), _jsx("input", { type: "text", value: inputMensagem, onChange: (e) => setInputMensagem(e.target.value), onKeyPress: (e) => e.key === 'Enter' && !e.shiftKey && enviarMensagem(), placeholder: "Digite sua mensagem...", disabled: enviando, className: "flex-1 bg-background border border-border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50" }), _jsxs("button", { onClick: enviarMensagem, disabled: enviando || (!inputMensagem.trim() && arquivosSelecionados.length === 0), className: "px-6 py-3 bg-primary hover:bg-primary/90 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2", children: [_jsx(Send, { className: "w-5 h-5" }), _jsx("span", { className: "hidden sm:inline", children: "Enviar" })] })] }), dragOver && (_jsx("div", { className: "absolute inset-0 bg-primary/20 border-2 border-dashed border-primary rounded-lg flex items-center justify-center pointer-events-none", children: _jsxs("div", { className: "text-center", children: [_jsx(Upload, { className: "w-12 h-12 mx-auto mb-2 text-primary" }), _jsx("p", { className: "text-lg font-semibold text-primary", children: "Solte os arquivos aqui" })] }) }))] })] }));
}
