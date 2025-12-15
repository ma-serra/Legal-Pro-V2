import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import {
    Save, Plus, Home, Send, Paperclip, Globe, FileText,
    MessageSquare
} from 'lucide-react'
import api from '../../lib/api'
import type { ChatConfig, ChatMessage, Conversa } from '../../types/assistente'
import { DEFAULT_CHAT_CONFIG } from '../../types/assistente'

export default function AssistenteChat() {
    const { id } = useParams()
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [conversas, setConversas] = useState<Conversa[]>([])
    const [currentConversa, setCurrentConversa] = useState<string | null>(null)
    const [userInput, setUserInput] = useState('')
    const [config, setConfig] = useState<ChatConfig>(DEFAULT_CHAT_CONFIG)
    const [assistenteNome, setAssistenteNome] = useState('Assistente Jurídico IA')
    const [assistenteDesc, setAssistenteDesc] = useState('Especialista em questões jurídicas')
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (id) {
            fetchAssistente()
            fetchConversas()
        }
    }, [id])

    const fetchAssistente = async () => {
        try {
            const response = await api.get(`/api/assistentes/${id}`)
            setAssistenteNome(response.data.nome)
            setAssistenteDesc(response.data.descricao)
        } catch (error) {
            console.error('Error fetching assistente:', error)
        }
    }

    const fetchConversas = async () => {
        try {
            const response = await api.get(`/api/assistentes/${id}/conversas`)
            setConversas(response.data)
        } catch (error) {
            console.error('Error fetching conversas:', error)
        }
    }

    const handleSaveConfig = (e: React.FormEvent) => {
        e.preventDefault()
        // Salvar configurações
        console.log('Config salva:', config)
    }

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!userInput.trim()) return

        const newMessage: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: userInput,
            timestamp: new Date(),
            config_usada: config
        }

        setMessages([...messages, newMessage])
        setUserInput('')
        setLoading(true)

        try {
            // Simular resposta do assistente
            setTimeout(() => {
                const assistantMessage: ChatMessage = {
                    id: (Date.now() + 1).toString(),
                    role: 'assistant',
                    content: `Essa é uma resposta simulada usando:\n\nModelo: ${config.modelo_llm}\nPersonalidade: ${config.personalidade}\nTom: ${config.tom_voz}\nPesquisa Web: ${config.usar_pesquisa_web ? 'Sim' : 'Não'}\nDocumentos: ${config.usar_documentos ? 'Sim' : 'Não'}`,
                    timestamp: new Date()
                }
                setMessages(prev => [...prev, assistantMessage])
                setLoading(false)
            }, 1000)
        } catch (error) {
            console.error('Error sending message:', error)
            setLoading(false)
        }
    }

    const handleNovaConversa = () => {
        setMessages([])
        setCurrentConversa(null)
    }

    return (
        <AdminLayout>
            <div className="container-fluid h-[calc(100vh-120px)] p-0 mt-2">
                <div className="row h-full">
                    {/* Sidebar - Histórico de Conversas */}
                    <div className="col-md-3 h-full bg-gray-900 border-r border-gray-700 rounded-l-lg p-4 overflow-hidden flex flex-col">
                        <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-700">
                            <h5 className="text-white font-semibold m-0">Histórico</h5>
                            <div className="flex gap-2">
                                <a href="/" className="btn btn-sm btn-secondary">
                                    <Home className="w-4 h-4" />
                                </a>
                                <button
                                    onClick={handleNovaConversa}
                                    className="btn btn-sm btn-primary"
                                >
                                    <Plus className="w-4 h-4" />
                                </button>
                            </div>
                        </div>

                        <div className="flex-1 overflow-y-auto">
                            {conversas.length > 0 ? (
                                conversas.map((conversa) => (
                                    <button
                                        key={conversa.id}
                                        onClick={() => setCurrentConversa(conversa.id)}
                                        className={`w-full text-left p-3 mb-2 rounded-lg transition-colors ${currentConversa === conversa.id
                                                ? 'bg-blue-600 text-white'
                                                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                                            }`}
                                    >
                                        <div className="font-medium text-sm truncate">{conversa.titulo}</div>
                                        <div className="text-xs opacity-70 mt-1">
                                            {new Date(conversa.created_at).toLocaleDateString('pt-BR')}
                                        </div>
                                    </button>
                                ))
                            ) : (
                                <div className="text-center text-gray-500 py-8">
                                    <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
                                    <p className="text-sm">Nenhuma conversa encontrada.</p>
                                    <p className="text-xs mt-1">Clique em "+" para começar.</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Área Principal */}
                    <div className="col-md-9 h-full bg-gray-800 rounded-r-lg p-4 flex flex-col">
                        {/* Header do Assistente */}
                        <div className="bg-gray-900 rounded-lg p-4 mb-4 border border-gray-700">
                            <h4 className="text-blue-400 font-semibold mb-1">{assistenteNome}</h4>
                            <p className="text-gray-400 text-sm m-0">{assistenteDesc}</p>
                        </div>

                        {/* Card de Configurações Sempre Visível */}
                        <div className="bg-gray-900 rounded-lg p-4 mb-4 border border-gray-700">
                            <h5 className="text-white mb-3 font-semibold">Configurações do Assistente</h5>
                            <form onSubmit={handleSaveConfig} className="row g-3">
                                {/* Linha 1: Dropdowns */}
                                <div className="col-md-4">
                                    <label className="form-label text-gray-400 text-sm">
                                        <Globe className="w-4 h-4 inline mr-1" />
                                        Modelo de Linguagem
                                    </label>
                                    <select
                                        className="form-select form-select-sm bg-gray-800 text-white border-gray-700"
                                        value={config.modelo_llm}
                                        onChange={(e) => setConfig({ ...config, modelo_llm: e.target.value })}
                                    >
                                        <option value="openai/gpt-4o">GPT-4o</option>
                                        <option value="anthropic/claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                                        <option value="deepseek/deepseek-chat">DeepSeek Chat</option>
                                    </select>
                                </div>

                                <div className="col-md-4">
                                    <label className="form-label text-gray-400 text-sm">
                                        <MessageSquare className="w-4 h-4 inline mr-1" />
                                        Personalidade Jurídica
                                    </label>
                                    <select
                                        className="form-select form-select-sm bg-gray-800 text-white border-gray-700"
                                        value={config.personalidade}
                                        onChange={(e) => setConfig({ ...config, personalidade: e.target.value as any })}
                                    >
                                        <option value="advogado">Advogado</option>
                                        <option value="juiz">Juiz</option>
                                        <option value="promotor">Promotor</option>
                                    </select>
                                </div>

                                <div className="col-md-4">
                                    <label className="form-label text-gray-400 text-sm">
                                        <FileText className="w-4 h-4 inline mr-1" />
                                        Tom de Voz
                                    </label>
                                    <select
                                        className="form-select form-select-sm bg-gray-800 text-white border-gray-700"
                                        value={config.tom_voz}
                                        onChange={(e) => setConfig({ ...config, tom_voz: e.target.value as any })}
                                    >
                                        <option value="formal">Formal</option>
                                        <option value="natural">Natural</option>
                                        <option value="simples">Simplificado</option>
                                    </select>
                                </div>

                                {/* Linha 2: Toggles */}
                                <div className="col-md-6">
                                    <div className="form-check form-switch">
                                        <input
                                            className="form-check-input"
                                            type="checkbox"
                                            id="usar_pesquisa_web"
                                            checked={config.usar_pesquisa_web}
                                            onChange={(e) => setConfig({ ...config, usar_pesquisa_web: e.target.checked })}
                                        />
                                        <label className="form-check-label text-gray-300 text-sm" htmlFor="usar_pesquisa_web">
                                            <Globe className="w-4 h-4 inline mr-1 text-blue-400" />
                                            Usar Pesquisa Web
                                        </label>
                                    </div>
                                </div>

                                <div className="col-md-6">
                                    <div className="form-check form-switch">
                                        <input
                                            className="form-check-input"
                                            type="checkbox"
                                            id="usar_documentos"
                                            checked={config.usar_documentos}
                                            onChange={(e) => setConfig({ ...config, usar_documentos: e.target.checked })}
                                        />
                                        <label className="form-check-label text-gray-300 text-sm" htmlFor="usar_documentos">
                                            <FileText className="w-4 h-4 inline mr-1 text-blue-400" />
                                            Usar Documentos Enviados
                                        </label>
                                    </div>
                                </div>

                                <div className="col-12 text-end">
                                    <button type="submit" className="btn btn-primary btn-sm">
                                        <Save className="w-4 h-4 inline mr-1" />
                                        Salvar Configurações
                                    </button>
                                </div>
                            </form>
                        </div>

                        {/* Área de Mensagens */}
                        <div className="flex-1 flex flex-col overflow-hidden">
                            <div className="flex-1 overflow-y-auto mb-3 p-3 space-y-4">
                                {messages.length > 0 ? (
                                    messages.map((message) => (
                                        <div
                                            key={message.id}
                                            className={`p-3 rounded-lg max-w-[80%] ${message.role === 'user'
                                                    ? 'bg-blue-600 text-white ml-auto'
                                                    : 'bg-gray-700 text-white mr-auto'
                                                }`}
                                        >
                                            <div className="whitespace-pre-wrap">{message.content}</div>
                                        </div>
                                    ))
                                ) : (
                                    <div className="text-center text-gray-400 py-12">
                                        <h3 className="text-blue-400 text-xl mb-3">Assistente AI</h3>
                                        <p className="mb-2">Bem-vindo ao seu assistente especializado!</p>
                                        <p className="text-sm">Você pode fazer perguntas, enviar documentos e obter respostas baseadas em conhecimento jurídico.</p>
                                        <p className="text-sm mt-2">Utilize as configurações acima para ajustar o modelo, personalidade e tom das respostas.</p>
                                    </div>
                                )}
                                {loading && (
                                    <div className="p-3 rounded-lg max-w-[80%] bg-gray-700 text-white mr-auto">
                                        <div className="flex items-center gap-2">
                                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                            <span>Pensando...</span>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Formulário de Mensagem */}
                            <form onSubmit={handleSendMessage}>
                                <div className="input-group">
                                    <button
                                        className="btn btn-outline-success dropdown-toggle"
                                        type="button"
                                        data-bs-toggle="dropdown"
                                        style={{ backgroundColor: '#1f5981', color: 'white', borderColor: '#25a56a' }}
                                    >
                                        <Paperclip className="w-4 h-4" />
                                    </button>
                                    <ul className="dropdown-menu">
                                        <li>
                                            <label className="dropdown-item" htmlFor="fileUpload">
                                                <FileText className="w-4 h-4 inline mr-2" />
                                                Enviar Arquivo
                                            </label>
                                            <input id="fileUpload" type="file" style={{ display: 'none' }} />
                                        </li>
                                    </ul>
                                    <textarea
                                        id="userInput"
                                        className="form-control bg-gray-700 text-white border-gray-600"
                                        placeholder="Digite sua mensagem aqui..."
                                        rows={1}
                                        value={userInput}
                                        onChange={(e) => setUserInput(e.target.value)}
                                        onKeyPress={(e) => {
                                            if (e.key === 'Enter' && !e.shiftKey) {
                                                e.preventDefault()
                                                handleSendMessage(e)
                                            }
                                        }}
                                    />
                                    <button className="btn btn-primary" type="submit">
                                        <Send className="w-4 h-4" />
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <style>{`
        .assistente-chat-container {
          height: calc(100vh - 120px);
        }
        
        .form-check-input:checked {
          background-color: #0d6efd;
          border-color: #0d6efd;
        }
        
        @media (max-width: 768px) {
          .col-md-3 {
            height: auto;
            max-height: 200px;
          }
        }
      `}</style>
        </AdminLayout>
    )
}
