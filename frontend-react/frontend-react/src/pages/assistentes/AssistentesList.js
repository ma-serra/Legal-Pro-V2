import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect, useRef } from 'react';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { Bot, MessageSquare, Search, Send, Upload, Trash2, X, FileText, User, Settings } from 'lucide-react';
import api from '../../lib/api';
const MODELS_BY_PROVIDER = {
    openai: ['gpt-5.2-thinking', 'gpt-5.2-instant', 'gpt-5.2-pro', 'gpt-5.1'],
    anthropic: ['claude-sonnet-4.5', 'claude-opus-4.5', 'claude-haiku-4.5'],
    google: ['gemini-3-pro-preview', 'gemini-2.5-pro', 'gemini-2.5-flash']
};
export default function AssistentesList() {
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);
    // Estados de lista
    const [assistentes, setAssistentes] = useState([]);
    const [filteredAssistentes, setFilteredAssistentes] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedTipo, setSelectedTipo] = useState('all');
    // Estados de chat
    const [selectedAssistente, setSelectedAssistente] = useState(null);
    const [conversas, setConversas] = useState([]);
    const [conversaAtiva, setConversaAtiva] = useState(null);
    const [mensagens, setMensagens] = useState([]);
    const [inputMensagem, setInputMensagem] = useState('');
    const [loading, setLoading] = useState(false);
    const [provider, setProvider] = useState('anthropic');
    const [model, setModel] = useState('claude-sonnet-4.5');
    const [arquivos, setArquivos] = useState([]);
    useEffect(() => {
        fetchAssistentes();
    }, []);
    useEffect(() => {
        filterAssistentes();
    }, [searchQuery, selectedTipo, assistentes]);
    useEffect(() => {
        if (selectedAssistente) {
            fetchConversas();
        }
    }, [selectedAssistente]);
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [mensagens]);
    const fetchAssistentes = async () => {
        try {
            const response = await api.get('/api/assistentes');
            setAssistentes(response.data.assistentes || []);
        }
        catch (error) {
            console.error('Erro ao carregar assistentes:', error);
        }
    };
    const filterAssistentes = () => {
        let filtered = assistentes;
        if (searchQuery) {
            filtered = filtered.filter(a => a.nome.toLowerCase().includes(searchQuery.toLowerCase()) ||
                a.descricao.toLowerCase().includes(searchQuery.toLowerCase()));
        }
        if (selectedTipo !== 'all') {
            filtered = filtered.filter(a => a.tipo === selectedTipo);
        }
        setFilteredAssistentes(filtered);
    };
    const fetchConversas = async () => {
        if (!selectedAssistente)
            return;
        try {
            const response = await api.get(`/api/assistentes/${selectedAssistente.id}/conversas`);
            setConversas(response.data.conversas || []);
        }
        catch (error) {
            console.error('Erro ao carregar conversas:', error);
        }
    };
    const selecionarAssistente = (assistente) => {
        setSelectedAssistente(assistente);
        setMensagens([]);
        setConversaAtiva(null);
        if (assistente.configuracoes_llm) {
            setProvider(assistente.configuracoes_llm.llm_provider || 'anthropic');
            setModel(assistente.configuracoes_llm.llm_model || 'claude-sonnet-4.5');
        }
    };
    const criarNovaConversa = async () => {
        if (!selectedAssistente)
            return;
        try {
            const response = await api.post(`/api/assistentes/${selectedAssistente.id}/conversas`, {
                titulo: `Conversa ${new Date().toLocaleString()}`,
                provider,
                modelo: model
            });
            setConversas([response.data, ...conversas]);
            setConversaAtiva(response.data);
            setMensagens([]);
        }
        catch (error) {
            console.error('Erro ao criar conversa:', error);
        }
    };
    const carregarConversa = async (conversa) => {
        try {
            const response = await api.get(`/api/assistentes/${selectedAssistente?.id}/conversas/${conversa.id}`);
            setConversaAtiva(response.data);
            setMensagens(response.data.mensagens || []);
            if (response.data.provider_usado)
                setProvider(response.data.provider_usado);
            if (response.data.modelo_usado)
                setModel(response.data.modelo_usado);
        }
        catch (error) {
            console.error('Erro ao carregar conversa:', error);
        }
    };
    const deletarConversa = async (conversaId) => {
        if (!confirm('Deseja deletar esta conversa?'))
            return;
        try {
            await api.delete(`/api/assistentes/${selectedAssistente?.id}/conversas/${conversaId}`);
            setConversas(conversas.filter(c => c.id !== conversaId));
            if (conversaAtiva?.id === conversaId) {
                setConversaAtiva(null);
                setMensagens([]);
            }
        }
        catch (error) {
            console.error('Erro ao deletar conversa:', error);
        }
    };
    const enviarMensagem = async () => {
        if (!inputMensagem.trim() || !selectedAssistente)
            return;
        const mensagemUser = {
            role: 'user',
            content: inputMensagem,
            timestamp: new Date().toISOString()
        };
        setMensagens([...mensagens, mensagemUser]);
        setInputMensagem('');
        setLoading(true);
        try {
            const response = await api.post(`/api/assistentes/${selectedAssistente.id}/chat`, {
                mensagem: inputMensagem,
                conversa_id: conversaAtiva?.id,
                provider,
                model
            });
            const mensagemAssistente = {
                role: 'assistant',
                content: response.data.resposta,
                timestamp: response.data.timestamp,
                provider: response.data.provider,
                model: response.data.modelo_utilizado
            };
            setMensagens(prev => [...prev, mensagemAssistente]);
            if (conversaAtiva)
                fetchConversas();
        }
        catch (error) {
            console.error('Erro ao enviar mensagem:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const handleDrop = (e) => {
        e.preventDefault();
        const files = Array.from(e.dataTransfer.files);
        setArquivos(prev => [...prev, ...files]);
    };
    const handleFileSelect = (e) => {
        if (e.target.files) {
            const files = Array.from(e.target.files);
            setArquivos(prev => [...prev, ...files]);
        }
    };
    const uploadArquivo = async (file) => {
        if (!conversaAtiva) {
            alert('Crie uma conversa primeiro');
            return;
        }
        const formData = new FormData();
        formData.append('file', file);
        try {
            await api.post(`/api/assistentes/${selectedAssistente?.id}/conversas/${conversaAtiva.id}/upload`, formData);
            setArquivos(prev => prev.filter(f => f !== file));
            alert('Arquivo enviado!');
        }
        catch (error) {
            console.error('Erro ao enviar arquivo:', error);
            alert('Erro ao enviar arquivo');
        }
    };
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Assistentes Jur\u00EDdicos", description: `${filteredAssistentes.length} assistentes disponíveis` }), _jsxs("div", { className: "flex gap-4 h-[calc(100vh-200px)]", children: [_jsxs("div", { className: "w-80 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col", children: [_jsxs("div", { className: "p-4 border-b border-gray-200 space-y-3", children: [_jsxs("div", { className: "relative", children: [_jsx(Search, { className: "absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" }), _jsx("input", { type: "text", placeholder: "Buscar assistentes...", value: searchQuery, onChange: (e) => setSearchQuery(e.target.value), className: "w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] }), _jsxs("select", { value: selectedTipo, onChange: (e) => setSelectedTipo(e.target.value), className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "all", children: "Todos os tipos" }), _jsx("option", { value: "juridico", children: "Jur\u00EDdico" }), _jsx("option", { value: "resumidor", children: "Resumidor" }), _jsx("option", { value: "extrator", children: "Extrator" }), _jsx("option", { value: "gerador", children: "Gerador" })] })] }), _jsx("div", { className: "flex-1 overflow-y-auto p-3 space-y-2", children: filteredAssistentes.map(assistente => (_jsx("div", { onClick: () => selecionarAssistente(assistente), className: `p-3 rounded-lg cursor-pointer transition-colors ${selectedAssistente?.id === assistente.id
                                        ? 'bg-blue-50 border-2 border-blue-500'
                                        : 'bg-gray-50 hover:bg-gray-100 border border-gray-200'}`, children: _jsxs("div", { className: "flex items-start gap-2", children: [_jsx(Bot, { className: "w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" }), _jsxs("div", { className: "flex-1 min-w-0", children: [_jsx("p", { className: "font-medium text-sm text-gray-900 truncate", children: assistente.nome }), _jsx("p", { className: "text-xs text-gray-500 mt-0.5", children: assistente.area_juridica })] })] }) }, assistente.id))) })] }), selectedAssistente ? (_jsxs("div", { className: "flex-1 bg-white rounded-lg shadow-sm border border-gray-200 flex", children: [_jsxs("div", { className: "w-64 border-r border-gray-200 flex flex-col", children: [_jsx("div", { className: "p-4 border-b border-gray-200", children: _jsxs("button", { onClick: criarNovaConversa, className: "w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2", children: [_jsx(MessageSquare, { className: "w-4 h-4" }), "Nova Conversa"] }) }), _jsx("div", { className: "flex-1 overflow-y-auto p-2 space-y-1", children: conversas.map(conversa => (_jsx("div", { onClick: () => carregarConversa(conversa), className: `p-2 rounded cursor-pointer ${conversaAtiva?.id === conversa.id ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50'}`, children: _jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { className: "flex-1 min-w-0", children: [_jsx("p", { className: "text-xs font-medium truncate", children: conversa.titulo }), _jsxs("p", { className: "text-xs text-gray-500", children: [conversa.mensagens?.length || 0, " msgs"] })] }), _jsx("button", { onClick: (e) => {
                                                            e.stopPropagation();
                                                            deletarConversa(conversa.id);
                                                        }, className: "text-red-500 hover:text-red-700", children: _jsx(Trash2, { className: "w-3 h-3" }) })] }) }, conversa.id))) })] }), _jsxs("div", { className: "flex-1 flex flex-col", children: [_jsxs("div", { className: "p-4 border-b border-gray-200", children: [_jsx("h2", { className: "text-lg font-bold", children: selectedAssistente.nome }), _jsx("p", { className: "text-sm text-gray-600", children: selectedAssistente.descricao }), _jsxs("div", { className: "mt-3 flex items-center gap-3", children: [_jsx(Settings, { className: "w-4 h-4 text-gray-500" }), _jsxs("select", { value: provider, onChange: (e) => {
                                                            setProvider(e.target.value);
                                                            setModel(MODELS_BY_PROVIDER[e.target.value][0]);
                                                        }, className: "px-2 py-1 border border-gray-300 rounded text-sm", children: [_jsx("option", { value: "openai", children: "OpenAI" }), _jsx("option", { value: "anthropic", children: "Anthropic" }), _jsx("option", { value: "google", children: "Google" })] }), _jsx("select", { value: model, onChange: (e) => setModel(e.target.value), className: "px-2 py-1 border border-gray-300 rounded text-sm flex-1", children: MODELS_BY_PROVIDER[provider].map(m => (_jsx("option", { value: m, children: m }, m))) })] })] }), _jsx("div", { className: "flex-1 overflow-y-auto p-4 bg-gray-50", children: mensagens.length === 0 ? (_jsx("div", { className: "flex items-center justify-center h-full text-gray-500", children: _jsxs("div", { className: "text-center", children: [_jsx(Bot, { className: "w-16 h-16 mx-auto mb-4 text-gray-400" }), _jsx("p", { children: "Inicie uma conversa" })] }) })) : (_jsxs("div", { className: "space-y-3", children: [mensagens.map((msg, idx) => (_jsxs("div", { className: `flex gap-2 ${msg.role === 'user' ? 'justify-end' : ''}`, children: [msg.role === 'assistant' && (_jsx("div", { className: "w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0", children: _jsx(Bot, { className: "w-5 h-5 text-blue-600" }) })), _jsxs("div", { className: `max-w-xl ${msg.role === 'user' ? 'order-first' : ''}`, children: [_jsx("div", { className: `p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border border-gray-200'}`, children: _jsx("p", { className: "text-sm whitespace-pre-wrap", children: msg.content }) }), msg.model && _jsx("p", { className: "text-xs text-gray-500 mt-1", children: msg.model })] }), msg.role === 'user' && (_jsx("div", { className: "w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0", children: _jsx(User, { className: "w-5 h-5 text-gray-600" }) }))] }, idx))), _jsx("div", { ref: messagesEndRef })] })) }), arquivos.length > 0 && (_jsx("div", { className: "bg-gray-100 border-t border-gray-200 p-2", children: _jsx("div", { className: "flex flex-wrap gap-2", children: arquivos.map((file, idx) => (_jsxs("div", { className: "flex items-center gap-2 bg-white px-2 py-1 rounded border", children: [_jsx(FileText, { className: "w-4 h-4" }), _jsx("span", { className: "text-xs", children: file.name }), _jsx("button", { onClick: () => uploadArquivo(file), className: "text-blue-600 text-xs", children: "Enviar" }), _jsx("button", { onClick: () => setArquivos(prev => prev.filter((_, i) => i !== idx)), children: _jsx(X, { className: "w-3 h-3" }) })] }, idx))) }) })), _jsx("div", { onDrop: handleDrop, onDragOver: (e) => e.preventDefault(), className: "p-4 border-t border-gray-200", children: _jsxs("div", { className: "flex items-end gap-2", children: [_jsx("input", { type: "file", ref: fileInputRef, onChange: handleFileSelect, className: "hidden", multiple: true }), _jsx("button", { onClick: () => fileInputRef.current?.click(), className: "p-2 text-gray-600 hover:bg-gray-100 rounded", children: _jsx(Upload, { className: "w-5 h-5" }) }), _jsx("textarea", { value: inputMensagem, onChange: (e) => setInputMensagem(e.target.value), onKeyPress: (e) => {
                                                        if (e.key === 'Enter' && !e.shiftKey) {
                                                            e.preventDefault();
                                                            enviarMensagem();
                                                        }
                                                    }, placeholder: "Digite sua mensagem...", className: "flex-1 px-3 py-2 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500", rows: 2 }), _jsx("button", { onClick: enviarMensagem, disabled: loading || !inputMensagem.trim(), className: "px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300", children: loading ? '...' : _jsx(Send, { className: "w-5 h-5" }) })] }) })] })] })) : (_jsx("div", { className: "flex-1 bg-white rounded-lg shadow-sm border border-gray-200 flex items-center justify-center", children: _jsxs("div", { className: "text-center text-gray-500", children: [_jsx(MessageSquare, { className: "w-16 h-16 mx-auto mb-4 text-gray-400" }), _jsx("p", { children: "Selecione um assistente para iniciar uma conversa" })] }) }))] })] }));
}
