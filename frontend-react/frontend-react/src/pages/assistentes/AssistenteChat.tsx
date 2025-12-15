import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import {
    Send, Bot, User, Upload, Trash2, Save,
    MessageSquare, Settings, ChevronLeft, X, FileText
} from 'lucide-react'
import api from '../../lib/api'

// Tipos
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
    arquivos_anexados?: any[]
    data_criacao?: string
    data_atualizacao?: string
}

interface Assistente {
    id: number
    nome: string
    tipo: string
    descricao: string
    configuracoes?: {
        llm_provider?: string
        llm_model?: string
        temperatura?: number
    }
}

// Modelos disponíveis por provider
const MODELS_BY_PROVIDER = {
    openai: ['gpt-5.2-thinking', 'gpt-5.2-instant', 'gpt-5.2-pro', 'gpt-5.1'],
    anthropic: ['claude-sonnet-4.5', 'claude-opus-4.5', 'claude-haiku-4.5'],
    google: ['gemini-3-pro-preview', 'gemini-2.5-pro', 'gemini-2.5-flash']
}

export default function AssistenteChat() {
    const { id } = useParams()
    const navigate = useNavigate()
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)

    // Estados
    const [assistente, setAssistente] = useState<Assistente | null>(null)
    const [conversas, setConversas] = useState<Conversa[]>([])
    const [conversaAtiva, setConversaAtiva] = useState<Conversa | null>(null)
    const [mensagens, setMensagens] = useState<ChatMessage[]>([])
    const [inputMensagem, setInputMensagem] = useState('')
    const [loading, setLoading] = useState(false)
    const [showHistory, setShowHistory] = useState(true)

    // Configurações customizadas
    const [provider, setProvider] = useState('anthropic')
    const [model, setModel] = useState('claude-sonnet-4.5')
    const [arquivos, setArquivos] = useState<File[]>([])

    // Carregar assistente e conversas
    useEffect(() => {
        if (id) {
            fetchAssistente()
            fetchConversas()
        }
    }, [id])

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [mensagens])

    const fetchAssistente = async () => {
        try {
            const response = await api.get(`/api/assistentes/${id}`)
            setAssistente(response.data)
            // Setar provider/model padrão
            if (response.data.configuracoes) {
                setProvider(response.data.configuracoes.llm_provider || 'anthropic')
                setModel(response.data.configuracoes.llm_model || 'claude-sonnet-4.5')
            }
        } catch (error) {
            console.error('Erro ao carregar assistente:', error)
        }
    }

    const fetchConversas = async () => {
        try {
            const response = await api.get(`/api/assistentes/${id}/conversas`)
            setConversas(response.data.conversas || [])
        } catch (error) {
            console.error('Erro ao carregar conversas:', error)
        }
    }

    const criarNovaConversa = async () => {
        try {
            const response = await api.post(`/api/assistentes/${id}/conversas`, {
                titulo: `Conversa ${new Date().toLocaleString()}`,
                provider,
                modelo: model
            })
            const novaConversa = response.data
            setConversas([novaConversa, ...conversas])
            setConversaAtiva(novaConversa)
            setMensagens([])
        } catch (error) {
            console.error('Erro ao criar conversa:', error)
        }
    }

    const carregarConversa = async (conversa: Conversa) => {
        try {
            const response = await api.get(`/api/assistentes/${id}/conversas/${conversa.id}`)
            setConversaAtiva(response.data)
            setMensagens(response.data.mensagens || [])
            if (response.data.provider_usado) setProvider(response.data.provider_usado)
            if (response.data.modelo_usado) setModel(response.data.modelo_usado)
        } catch (error) {
            console.error('Erro ao carregar conversa:', error)
        }
    }

    const deletarConversa = async (conversaId: number) => {
        if (!confirm('Deseja realmente deletar esta conversa?')) return

        try {
            await api.delete(`/api/assistentes/${id}/conversas/${conversaId}`)
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
        if (!inputMensagem.trim()) return

        const mensagemUser: ChatMessage = {
            role: 'user',
            content: inputMensagem,
            timestamp: new Date().toISOString()
        }

        setMensagens([...mensagens, mensagemUser])
        setInputMensagem('')
        setLoading(true)

        try {
            const response = await api.post(`/api/assistentes/${id}/chat`, {
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

            // Atualizar conversa ativa
            if (conversaAtiva) {
                fetchConversas()
            }
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error)
        } finally {
            setLoading(false)
        }
    }

    // Drag and drop
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
            await api.post(`/api/assistentes/${id}/conversas/${conversaAtiva.id}/upload`, formData)
            setArquivos(prev => prev.filter(f => f !== file))
            alert('Arquivo enviado com sucesso!')
        } catch (error) {
            console.error('Erro ao enviar arquivo:', error)
            alert('Erro ao enviar arquivo')
        }
    }

    if (!assistente) {
        return <AdminLayout><div className="p-8">Carregando...</div></AdminLayout>
    }

    return (
        <AdminLayout>
            <div className="flex h-[calc(100vh-4rem)]">
                {/* Sidebar - Histórico */}
                {showHistory && (
                    <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
                        <div className="p-4 border-b border-gray-200">
                            <button
                                onClick={criarNovaConversa}
                                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
                            >
                                <MessageSquare className="w-4 h-4" />
                                Nova Conversa
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto p-4 space-y-2">
                            {conversas.map(conversa => (
                                <div
                                    key={conversa.id}
                                    className={`p-3 rounded-lg cursor-pointer hover:bg-gray-50 ${conversaAtiva?.id === conversa.id ? 'bg-blue-50 border border-blue-200' : 'border border-gray-200'
                                        }`}
                                    onClick={() => carregarConversa(conversa)}
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <p className="font-medium text-sm">{conversa.titulo}</p>
                                            <p className="text-xs text-gray-500 mt-1">
                                                {conversa.mensagens_count || 0} mensagens
                                            </p>
                                        </div>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                deletarConversa(conversa.id)
                                            }}
                                            className="text-red-500 hover:text-red-700"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Chat Principal */}
                <div className="flex-1 flex flex-col">
                    {/* Header */}
                    <div className="bg-white border-b border-gray-200 p-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <button onClick={() => navigate('/assistentes')} className="text-gray-600 hover:text-gray-900">
                                    <ChevronLeft className="w-5 h-5" />
                                </button>
                                <div>
                                    <h1 className="text-xl font-bold">{assistente.nome}</h1>
                                    <p className="text-sm text-gray-600">{assistente.descricao}</p>
                                </div>
                            </div>

                            <button
                                onClick={() => setShowHistory(!showHistory)}
                                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                            >
                                {showHistory ? 'Ocultar' : 'Mostrar'} Histórico
                            </button>
                        </div>

                        {/* Seletores de Provider/Modelo */}
                        <div className="mt-4 flex items-center gap-4">
                            <div className="flex items-center gap-2">
                                <Settings className="w-4 h-4 text-gray-500" />
                                <select
                                    value={provider}
                                    onChange={(e) => {
                                        setProvider(e.target.value)
                                        setModel(MODELS_BY_PROVIDER[e.target.value as keyof typeof MODELS_BY_PROVIDER][0])
                                    }}
                                    className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
                                >
                                    <option value="openai">OpenAI</option>
                                    <option value="anthropic">Anthropic</option>
                                    <option value="google">Google</option>
                                </select>
                            </div>

                            <select
                                value={model}
                                onChange={(e) => setModel(e.target.value)}
                                className="px-3 py-1 border border-gray-300 rounded-lg text-sm flex-1 max-w-xs"
                            >
                                {MODELS_BY_PROVIDER[provider as keyof typeof MODELS_BY_PROVIDER].map(m => (
                                    <option key={m} value={m}>{m}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Mensagens */}
                    <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
                        {mensagens.length === 0 ? (
                            <div className="flex items-center justify-center h-full text-gray-500">
                                <div className="text-center">
                                    <Bot className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                                    <p>Inicie uma conversa com {assistente.nome}</p>
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-4 max-w-4xl mx-auto">
                                {mensagens.map((msg, idx) => (
                                    <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                                        {msg.role === 'assistant' && (
                                            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                                                <Bot className="w-5 h-5 text-blue-600" />
                                            </div>
                                        )}
                                        <div className={`max-w-2xl ${msg.role === 'user' ? 'order-first' : ''}`}>
                                            <div className={`p-4 rounded-lg ${msg.role === 'user'
                                                    ? 'bg-blue-600 text-white'
                                                    : 'bg-white border border-gray-200'
                                                }`}>
                                                <p className="whitespace-pre-wrap">{msg.content}</p>
                                            </div>
                                            {msg.model && (
                                                <p className="text-xs text-gray-500 mt-1">{msg.model}</p>
                                            )}
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
                        <div className="bg-gray-100 border-t border-gray-200 p-3">
                            <div className="flex flex-wrap gap-2">
                                {arquivos.map((file, idx) => (
                                    <div key={idx} className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg border">
                                        <FileText className="w-4 h-4" />
                                        <span className="text-sm">{file.name}</span>
                                        <button
                                            onClick={() => uploadArquivo(file)}
                                            className="text-blue-600 hover:text-blue-700 text-xs"
                                        >
                                            Enviar
                                        </button>
                                        <button
                                            onClick={() => setArquivos(prev => prev.filter((_, i) => i !== idx))}
                                            className="text-red-500 hover:text-red-700"
                                        >
                                            <X className="w-4 h-4" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Input */}
                    <div className="bg-white border-t border-gray-200 p-4">
                        <div
                            onDrop={handleDrop}
                            onDragOver={(e) => e.preventDefault()}
                            className="flex items-end gap-2"
                        >
                            <input
                                type="file"
                                ref={fileInputRef}
                                onChange={handleFileSelect}
                                className="hidden"
                                multiple
                            />
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                className="p-3 text-gray-600 hover:bg-gray-100 rounded-lg"
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
                                placeholder="Digite sua mensagem... (Arraste arquivos aqui)"
                                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                rows={3}
                            />

                            <button
                                onClick={enviarMensagem}
                                disabled={loading || !inputMensagem.trim()}
                                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                            >
                                {loading ? '...' : <Send className="w-5 h-5" />}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </AdminLayout>
    )
}
