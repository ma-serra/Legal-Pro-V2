import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { Send, Bot, User, Upload, Trash2, MessageSquare, Settings, ChevronLeft, X, FileText } from 'lucide-react';
import api from '../../lib/api';
// Modelos disponíveis por provider
const MODELS_BY_PROVIDER = {
    openai: ['gpt-5.2-thinking', 'gpt-5.2-instant', 'gpt-5.2-pro', 'gpt-5.1'],
    anthropic: ['claude-sonnet-4.5', 'claude-opus-4.5', 'claude-haiku-4.5'],
    google: ['gemini-3-pro-preview', 'gemini-2.5-pro', 'gemini-2.5-flash']
};
export default function AssistenteChat() {
    const { id } = useParams();
    const navigate = useNavigate();
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);
    // Estados
    const [assistente, setAssistente] = useState(null);
    const [conversas, setConversas] = useState([]);
    const [conversaAtiva, setConversaAtiva] = useState(null);
    const [mensagens, setMensagens] = useState([]);
    const [inputMensagem, setInputMensagem] = useState('');
    const [loading, setLoading] = useState(false);
    const [showHistory, setShowHistory] = useState(true);
    // Configurações customizadas
    const [provider, setProvider] = useState('anthropic');
    const [model, setModel] = useState('claude-sonnet-4.5');
    const [arquivos, setArquivos] = useState([]);
    // Carregar assistente e conversas
    useEffect(() => {
        if (id) {
            fetchAssistente();
            fetchConversas();
        }
    }, [id]);
    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [mensagens]);
    const fetchAssistente = async () => {
        try {
            const response = await api.get(`/api/assistentes/${id}`);
            setAssistente(response.data);
            // Setar provider/model padrão
            if (response.data.configuracoes) {
                setProvider(response.data.configuracoes.llm_provider || 'anthropic');
                setModel(response.data.configuracoes.llm_model || 'claude-sonnet-4.5');
            }
        }
        catch (error) {
            console.error('Erro ao carregar assistente:', error);
        }
    };
    const fetchConversas = async () => {
        try {
            const response = await api.get(`/api/assistentes/${id}/conversas`);
            setConversas(response.data.conversas || []);
        }
        catch (error) {
            console.error('Erro ao carregar conversas:', error);
        }
    };
    const criarNovaConversa = async () => {
        try {
            const response = await api.post(`/api/assistentes/${id}/conversas`, {
                titulo: `Conversa ${new Date().toLocaleString()}`,
                provider,
                modelo: model
            });
            const novaConversa = response.data;
            setConversas([novaConversa, ...conversas]);
            setConversaAtiva(novaConversa);
            setMensagens([]);
        }
        catch (error) {
            console.error('Erro ao criar conversa:', error);
        }
    };
    const carregarConversa = async (conversa) => {
        try {
            const response = await api.get(`/api/assistentes/${id}/conversas/${conversa.id}`);
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
        if (!confirm('Deseja realmente deletar esta conversa?'))
            return;
        try {
            await api.delete(`/api/assistentes/${id}/conversas/${conversaId}`);
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
        if (!inputMensagem.trim())
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
            const response = await api.post(`/api/assistentes/${id}/chat`, {
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
            // Atualizar conversa ativa
            if (conversaAtiva) {
                fetchConversas();
            }
        }
        catch (error) {
            console.error('Erro ao enviar mensagem:', error);
        }
        finally {
            setLoading(false);
        }
    };
    // Drag and drop
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
            await api.post(`/api/assistentes/${id}/conversas/${conversaAtiva.id}/upload`, formData);
            setArquivos(prev => prev.filter(f => f !== file));
            alert('Arquivo enviado com sucesso!');
        }
        catch (error) {
            console.error('Erro ao enviar arquivo:', error);
            alert('Erro ao enviar arquivo');
        }
    };
    if (!assistente) {
        return _jsx(AdminLayout, { children: _jsx("div", { className: "p-8", children: "Carregando..." }) });
    }
    return (_jsx(AdminLayout, { children: _jsxs("div", { className: "flex h-[calc(100vh-4rem)]", children: [showHistory && (_jsxs("div", { className: "w-80 bg-white border-r border-gray-200 flex flex-col", children: [_jsx("div", { className: "p-4 border-b border-gray-200", children: _jsxs("button", { onClick: criarNovaConversa, className: "w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2", children: [_jsx(MessageSquare, { className: "w-4 h-4" }), "Nova Conversa"] }) }), _jsx("div", { className: "flex-1 overflow-y-auto p-4 space-y-2", children: conversas.map(conversa => (_jsx("div", { className: `p-3 rounded-lg cursor-pointer hover:bg-gray-50 ${conversaAtiva?.id === conversa.id ? 'bg-blue-50 border border-blue-200' : 'border border-gray-200'}`, onClick: () => carregarConversa(conversa), children: _jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { className: "flex-1", children: [_jsx("p", { className: "font-medium text-sm", children: conversa.titulo }), _jsxs("p", { className: "text-xs text-gray-500 mt-1", children: [conversa.mensagens?.length || 0, " mensagens"] })] }), _jsx("button", { onClick: (e) => {
                                                e.stopPropagation();
                                                deletarConversa(conversa.id);
                                            }, className: "text-red-500 hover:text-red-700", children: _jsx(Trash2, { className: "w-4 h-4" }) })] }) }, conversa.id))) })] })), _jsxs("div", { className: "flex-1 flex flex-col", children: [_jsxs("div", { className: "bg-white border-b border-gray-200 p-4", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { className: "flex items-center gap-4", children: [_jsx("button", { onClick: () => navigate('/assistentes'), className: "text-gray-600 hover:text-gray-900", children: _jsx(ChevronLeft, { className: "w-5 h-5" }) }), _jsxs("div", { children: [_jsx("h1", { className: "text-xl font-bold", children: assistente.nome }), _jsx("p", { className: "text-sm text-gray-600", children: assistente.descricao })] })] }), _jsxs("button", { onClick: () => setShowHistory(!showHistory), className: "px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg", children: [showHistory ? 'Ocultar' : 'Mostrar', " Hist\u00F3rico"] })] }), _jsxs("div", { className: "mt-4 flex items-center gap-4", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx(Settings, { className: "w-4 h-4 text-gray-500" }), _jsxs("select", { value: provider, onChange: (e) => {
                                                        setProvider(e.target.value);
                                                        setModel(MODELS_BY_PROVIDER[e.target.value][0]);
                                                    }, className: "px-3 py-1 border border-gray-300 rounded-lg text-sm", children: [_jsx("option", { value: "openai", children: "OpenAI" }), _jsx("option", { value: "anthropic", children: "Anthropic" }), _jsx("option", { value: "google", children: "Google" })] })] }), _jsx("select", { value: model, onChange: (e) => setModel(e.target.value), className: "px-3 py-1 border border-gray-300 rounded-lg text-sm flex-1 max-w-xs", children: MODELS_BY_PROVIDER[provider].map(m => (_jsx("option", { value: m, children: m }, m))) })] })] }), _jsx("div", { className: "flex-1 overflow-y-auto p-6 bg-gray-50", children: mensagens.length === 0 ? (_jsx("div", { className: "flex items-center justify-center h-full text-gray-500", children: _jsxs("div", { className: "text-center", children: [_jsx(Bot, { className: "w-16 h-16 mx-auto mb-4 text-gray-400" }), _jsxs("p", { children: ["Inicie uma conversa com ", assistente.nome] })] }) })) : (_jsxs("div", { className: "space-y-4 max-w-4xl mx-auto", children: [mensagens.map((msg, idx) => (_jsxs("div", { className: `flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`, children: [msg.role === 'assistant' && (_jsx("div", { className: "w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0", children: _jsx(Bot, { className: "w-5 h-5 text-blue-600" }) })), _jsxs("div", { className: `max-w-2xl ${msg.role === 'user' ? 'order-first' : ''}`, children: [_jsx("div", { className: `p-4 rounded-lg ${msg.role === 'user'
                                                            ? 'bg-blue-600 text-white'
                                                            : 'bg-white border border-gray-200'}`, children: _jsx("p", { className: "whitespace-pre-wrap", children: msg.content }) }), msg.model && (_jsx("p", { className: "text-xs text-gray-500 mt-1", children: msg.model }))] }), msg.role === 'user' && (_jsx("div", { className: "w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0", children: _jsx(User, { className: "w-5 h-5 text-gray-600" }) }))] }, idx))), _jsx("div", { ref: messagesEndRef })] })) }), arquivos.length > 0 && (_jsx("div", { className: "bg-gray-100 border-t border-gray-200 p-3", children: _jsx("div", { className: "flex flex-wrap gap-2", children: arquivos.map((file, idx) => (_jsxs("div", { className: "flex items-center gap-2 bg-white px-3 py-2 rounded-lg border", children: [_jsx(FileText, { className: "w-4 h-4" }), _jsx("span", { className: "text-sm", children: file.name }), _jsx("button", { onClick: () => uploadArquivo(file), className: "text-blue-600 hover:text-blue-700 text-xs", children: "Enviar" }), _jsx("button", { onClick: () => setArquivos(prev => prev.filter((_, i) => i !== idx)), className: "text-red-500 hover:text-red-700", children: _jsx(X, { className: "w-4 h-4" }) })] }, idx))) }) })), _jsx("div", { className: "bg-white border-t border-gray-200 p-4", children: _jsxs("div", { onDrop: handleDrop, onDragOver: (e) => e.preventDefault(), className: "flex items-end gap-2", children: [_jsx("input", { type: "file", ref: fileInputRef, onChange: handleFileSelect, className: "hidden", multiple: true }), _jsx("button", { onClick: () => fileInputRef.current?.click(), className: "p-3 text-gray-600 hover:bg-gray-100 rounded-lg", children: _jsx(Upload, { className: "w-5 h-5" }) }), _jsx("textarea", { value: inputMensagem, onChange: (e) => setInputMensagem(e.target.value), onKeyPress: (e) => {
                                            if (e.key === 'Enter' && !e.shiftKey) {
                                                e.preventDefault();
                                                enviarMensagem();
                                            }
                                        }, placeholder: "Digite sua mensagem... (Arraste arquivos aqui)", className: "flex-1 px-4 py-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent", rows: 3 }), _jsx("button", { onClick: enviarMensagem, disabled: loading || !inputMensagem.trim(), className: "px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed", children: loading ? '...' : _jsx(Send, { className: "w-5 h-5" }) })] }) })] })] }) }));
}
