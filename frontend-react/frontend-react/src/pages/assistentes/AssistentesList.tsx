import { useState, useEffect, useRef } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import {
    Bot, MessageSquare, Search, Filter, Send, Upload,
    Trash2, X, FileText, User, Settings
} from 'lucide-react'
import api from '../../lib/api'

interface Assistente {
    id: number
    nome: string
    area_juridica: string
    descricao: string
    tipo: string
    configuracoes_llm?: {
        llm_provider?: string
        llm_model?: string
    }
}

interface ChatMessage {
    role: 'user' | 'assistant'
    content: string
    timestamp: string
    provider?: string
    model?: string
}

interface Conversa {
    id: number
    titulo: string
    mensagens: ChatMessage[]
    provider_usado?: string
    modelo_usado?: string
}

const MODELS_BY_PROVIDER: Record<string, string[]> = {
    openai: ['gpt-5.2-thinking', 'gpt-5.2-instant', 'gpt-5.2-pro', 'gpt-5.1'],
    anthropic: ['claude-sonnet-4.5', 'claude-opus-4.5', 'claude-haiku-4.5'],
    google: ['gemini-3-pro-preview', 'gemini-2.5-pro', 'gemini-2.5-flash']
}

export default function AssistentesList() {
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)

    // Estados de lista
    const [assistentes, setAssistentes] = useState<Assistente[]>([])
    const [filteredAssistentes, setFilteredAssistentes] = useState<Assistente[]>([])
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedTipo, setSelectedTipo] = useState('all')

    // Estados de chat
    const [selectedAssistente, setSelectedAssistente] = useState<Assistente | null>(null)
    const [conversas, setConversas] = useState<Conversa[]>([])
    const [conversaAtiva, setConversaAtiva] = useState<Conversa | null>(null)
    const [mensagens, setMensagens] = useState<ChatMessage[]>([])
    const [inputMensagem, setInputMensagem] = useState('')
    const [loading, setLoading] = useState(false)
    const [provider, setProvider] = useState('anthropic')
    const [model, setModel] = useState('claude-sonnet-4.5')
    const [arquivos, setArquivos] = useState<File[]>([])

    useEffect(() => {
        fetchAssistentes()
    }, [])

    useEffect(() => {
        filterAssistentes()
    }, [searchQuery, selectedTipo, assistentes])

    useEffect(() => {
        if (selectedAssistente) {
            fetchConversas()
        }
    }, [selectedAssistente])

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [mensagens])

    const fetchAssistentes = async () => {
        try {
            const response = await api.get('/api/assistentes')
            setAssistentes(response.data.assistentes || [])
        } catch (error) {
            console.error('Erro ao carregar assistentes:', error)
        }
    }

    const filterAssistentes = () => {
        let filtered = assistentes

        if (searchQuery) {
            filtered = filtered.filter(a =>
                a.nome.toLowerCase().includes(searchQuery.toLowerCase()) ||
                a.descricao.toLowerCase().includes(searchQuery.toLowerCase())
            )
        }

        if (selectedTipo !== 'all') {
            filtered = filtered.filter(a => a.tipo === selectedTipo)
        }

        setFilteredAssistentes(filtered)
    }

    const fetchConversas = async () => {
        if (!selectedAssistente) return
        try {
            const response = await api.get(`/api/assistentes/${selectedAssistente.id}/conversas`)
            setConversas(response.data.conversas || [])
        } catch (error) {
            console.error('Erro ao carregar conversas:', error)
        }
    }

    const selecionarAssistente = (assistente: Assistente) => {
        setSelectedAssistente(assistente)
        setMensagens([])
        setConversaAtiva(null)
        if (assistente.configuracoes_llm) {
            setProvider(assistente.configuracoes_llm.llm_provider || 'anthropic')
            setModel(assistente.configuracoes_llm.llm_model || 'claude-sonnet-4.5')
        }
    }

    const criarNovaConversa = async () => {
        if (!selectedAssistente) return
        try {
            const response = await api.post(`/api/assistentes/${selectedAssistente.id}/conversas`, {
                titulo: `Conversa ${new Date().toLocaleString()}`,
                provider,
                modelo: model
            })
            setConversas([response.data, ...conversas])
            setConversaAtiva(response.data)
            setMensagens([])
        } catch (error) {
            console.error('Erro ao criar conversa:', error)
        }
    }

    const carregarConversa = async (conversa: Conversa) => {
        try {
            const response = await api.get(`/api/assistentes/${selectedAssistente?.id}/conversas/${conversa.id}`)
            setConversaAtiva(response.data)
            setMensagens(response.data.mensagens || [])
            if (response.data.provider_usado) setProvider(response.data.provider_usado)
            if (response.data.modelo_usado) setModel(response.data.modelo_usado)
        } catch (error) {
            console.error('Erro ao carregar conversa:', error)
        }
    }

    const deletarConversa = async (conversaId: number) => {
        if (!confirm('Deseja deletar esta conversa?')) return
        try {
            await api.delete(`/api/assistentes/${selectedAssistente?.id}/conversas/${conversaId}`)
            setConversas(conversas.filter(c => c.id !== conversaId))
            if (conversaAtiva?.id === conversaId) {
                setConversaAtiva(null)
                setMensagens([])
            }
        } catch (error) {
            console.error('Erro ao deletar conversa:', error)
        }
    }

    const enviarMensagem = async () => {
        if (!inputMensagem.trim() || !selectedAssistente) return

        const mensagemUser: ChatMessage = {
            role: 'user',
            content: inputMensagem,
            timestamp: new Date().toISOString()
        }

        setMensagens([...mensagens, mensagemUser])
        setInputMensagem('')
        setLoading(true)

        try {
            const response = await api.post(`/api/assistentes/${selectedAssistente.id}/chat`, {
                mensagem: inputMensagem,
                conversa_id: conversaAtiva?.id,
                provider,
                model
            })

            const mensagemAssistente: ChatMessage = {
                role: 'assistant',
                content: response.data.resposta,
                timestamp: response.data.timestamp,
                provider: response.data.provider,
                model: response.data.modelo_utilizado
            }

            setMensagens(prev => [...prev, mensagemAssistente])
            if (conversaAtiva) fetchConversas()
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        const files = Array.from(e.dataTransfer.files)
        setArquivos(prev => [...prev, ...files])
    }

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const files = Array.from(e.target.files)
            setArquivos(prev => [...prev, ...files])
        }
    }

    const uploadArquivo = async (file: File) => {
        if (!conversaAtiva) {
            alert('Crie uma conversa primeiro')
            return
        }

        const formData = new FormData()
        formData.append('file', file)

        try {
            await api.post(`/api/assistentes/${selectedAssistente?.id}/conversas/${conversaAtiva.id}/upload`, formData)
            setArquivos(prev => prev.filter(f => f !== file))
            alert('Arquivo enviado!')
        } catch (error) {
            console.error('Erro ao enviar arquivo:', error)
            alert('Erro ao enviar arquivo')
        }
    }

    return (
        <AdminLayout>
            <PageHeader
                title="Assistentes Jurídicos"
                subtitle={`${filteredAssistentes.length} assistentes disponíveis`}
                icon={Bot}
            />

            <div className="flex gap-4 h-[calc(100vh-200px)]">
                {/* Sidebar Esquerda - Lista de Assistentes */}
                <div className="w-80 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
                    {/* Filtros */}
                    <div className="p-4 border-b border-gray-200 space-y-3">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                            <input
                                type="text"
                                placeholder="Buscar assistentes..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        <select
                            value={selectedTipo}
                            onChange={(e) => setSelectedTipo(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="all">Todos os tipos</option>
                            <option value="juridico">Jurídico</option>
                            <option value="resumidor">Resumidor</option>
                            <option value="extrator">Extrator</option>
                            <option value="gerador">Gerador</option>
                        </select>
                    </div>

                    {/* Lista */}
                    <div className="flex-1 overflow-y-auto p-3 space-y-2">
                        {filteredAssistentes.map(assistente => (
                            <div
                                key={assistente.id}
                                onClick={() => selecionarAssistente(assistente)}
                                className={`p-3 rounded-lg cursor-pointer transition-colors ${selectedAssistente?.id === assistente.id
                                        ? 'bg-blue-50 border-2 border-blue-500'
                                        : 'bg-gray-50 hover:bg-gray-100 border border-gray-200'
                                    }`}
                            >
                                <div className="flex items-start gap-2">
                                    <Bot className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                                    <div className="flex-1 min-w-0">
                                        <p className="font-medium text-sm text-gray-900 truncate">{assistente.nome}</p>
                                        <p className="text-xs text-gray-500 mt-0.5">{assistente.area_juridica}</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Área Principal - Chat */}
                {selectedAssistente ? (
                    <div className="flex-1 bg-white rounded-lg shadow-sm border border-gray-200 flex">
                        {/* Histórico de Conversas */}
                        <div className="w-64 border-r border-gray-200 flex flex-col">
                            <div className="p-4 border-b border-gray-200">
                                <button
                                    onClick={criarNovaConversa}
                                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
                                >
                                    <MessageSquare className="w-4 h-4" />
                                    Nova Conversa
                                </button>
                            </div>

                            <div className="flex-1 overflow-y-auto p-2 space-y-1">
                                {conversas.map(conversa => (
                                    <div
                                        key={conversa.id}
                                        onClick={() => carregarConversa(conversa)}
                                        className={`p-2 rounded cursor-pointer ${conversaAtiva?.id === conversa.id ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50'
                                            }`}
                                    >
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1 min-w-0">
                                                <p className="text-xs font-medium truncate">{conversa.titulo}</p>
                                                <p className="text-xs text-gray-500">{conversa.mensagens?.length || 0} msgs</p>
                                            </div>
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation()
                                                    deletarConversa(conversa.id)
                                                }}
                                                className="text-red-500 hover:text-red-700"
                                            >
                                                <Trash2 className="w-3 h-3" />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Chat */}
                        <div className="flex-1 flex flex-col">
                            {/* Header */}
                            <div className="p-4 border-b border-gray-200">
                                <h2 className="text-lg font-bold">{selectedAssistente.nome}</h2>
                                <p className="text-sm text-gray-600">{selectedAssistente.descricao}</p>

                                {/* Seletores */}
                                <div className="mt-3 flex items-center gap-3">
                                    <Settings className="w-4 h-4 text-gray-500" />
                                    <select
                                        value={provider}
                                        onChange={(e) => {
                                            setProvider(e.target.value)
                                            setModel(MODELS_BY_PROVIDER[e.target.value][0])
                                        }}
                                        className="px-2 py-1 border border-gray-300 rounded text-sm"
                                    >
                                        <option value="openai">OpenAI</option>
                                        <option value="anthropic">Anthropic</option>
                                        <option value="google">Google</option>
                                    </select>

                                    <select
                                        value={model}
                                        onChange={(e) => setModel(e.target.value)}
                                        className="px-2 py-1 border border-gray-300 rounded text-sm flex-1"
                                    >
                                        {MODELS_BY_PROVIDER[provider].map(m => (
                                            <option key={m} value={m}>{m}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            {/* Mensagens */}
                            <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
                                {mensagens.length === 0 ? (
                                    <div className="flex items-center justify-center h-full text-gray-500">
                                        <div className="text-center">
                                            <Bot className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                                            <p>Inicie uma conversa</p>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="space-y-3">
                                        {mensagens.map((msg, idx) => (
                                            <div key={idx} className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                                                {msg.role === 'assistant' && (
                                                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                                                        <Bot className="w-5 h-5 text-blue-600" />
                                                    </div>
                                                )}
                                                <div className={`max-w-xl ${msg.role === 'user' ? 'order-first' : ''}`}>
                                                    <div className={`p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border border-gray-200'
                                                        }`}>
                                                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                                                    </div>
                                                    {msg.model && <p className="text-xs text-gray-500 mt-1">{msg.model}</p>}
                                                </div>
                                                {msg.role === 'user' && (
                                                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                                                        <User className="w-5 h-5 text-gray-600" />
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                        <div ref={messagesEndRef} />
                                    </div>
                                )}
                            </div>

                            {/* Arquivos Pendentes */}
                            {arquivos.length > 0 && (
                                <div className="bg-gray-100 border-t border-gray-200 p-2">
                                    <div className="flex flex-wrap gap-2">
                                        {arquivos.map((file, idx) => (
                                            <div key={idx} className="flex items-center gap-2 bg-white px-2 py-1 rounded border">
                                                <FileText className="w-4 h-4" />
                                                <span className="text-xs">{file.name}</span>
                                                <button onClick={() => uploadArquivo(file)} className="text-blue-600 text-xs">Enviar</button>
                                                <button onClick={() => setArquivos(prev => prev.filter((_, i) => i !== idx))}>
                                                    <X className="w-3 h-3" />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Input */}
                            <div
                                onDrop={handleDrop}
                                onDragOver={(e) => e.preventDefault()}
                                className="p-4 border-t border-gray-200"
                            >
                                <div className="flex items-end gap-2">
                                    <input
                                        type="file"
                                        ref={fileInputRef}
                                        onChange={handleFileSelect}
                                        className="hidden"
                                        multiple
                                    />
                                    <button
                                        onClick={() => fileInputRef.current?.click()}
                                        className="p-2 text-gray-600 hover:bg-gray-100 rounded"
                                    >
                                        <Upload className="w-5 h-5" />
                                    </button>

                                    <textarea
                                        value={inputMensagem}
                                        onChange={(e) => setInputMensagem(e.target.value)}
                                        onKeyPress={(e) => {
                                            if (e.key === 'Enter' && !e.shiftKey) {
                                                e.preventDefault()
                                                enviarMensagem()
                                            }
                                        }}
                                        placeholder="Digite sua mensagem..."
                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500"
                                        rows={2}
                                    />

                                    <button
                                        onClick={enviarMensagem}
                                        disabled={loading || !inputMensagem.trim()}
                                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300"
                                    >
                                        {loading ? '...' : <Send className="w-5 h-5" />}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="flex-1 bg-white rounded-lg shadow-sm border border-gray-200 flex items-center justify-center">
                        <div className="text-center text-gray-500">
                            <MessageSquare className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                            <p>Selecione um assistente para iniciar uma conversa</p>
                        </div>
                    </div>
                )}
            </div>
        </AdminLayout>
    )
}
