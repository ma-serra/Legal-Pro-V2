import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { Send, Save, Trash2, MessageSquare, Bot } from 'lucide-react'
import api from '../../lib/api'

interface Message {
    role: 'user' | 'assistant'
    content: string
    timestamp: Date
}

interface Conversation {
    id: number
    titulo: string
    created_at: string
}

export default function AssistenteChat() {
    const { agente_id } = useParams()
    const [messages, setMessages] = useState<Message[]>([])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [conversations, setConversations] = useState<Conversation[]>([])
    const [currentConversationId, setCurrentConversationId] = useState<number | null>(null)

    useEffect(() => {
        fetchConversations()
    }, [agente_id])

    // Endpoint: GET /agentes/:agente_id/conversas
    const fetchConversations = async () => {
        try {
            const response = await api.get(`/agentes/${agente_id}/conversas`)
            setConversations(response.data)
        } catch (error) {
            console.error('Error fetching conversations:', error)
        }
    }

    // Endpoint: GET /agentes/:agente_id/conversa/:conversa_id
    const loadConversation = async (conversaId: number) => {
        try {
            const response = await api.get(`/agentes/${agente_id}/conversa/${conversaId}`)
            setMessages(response.data.messages || [])
            setCurrentConversationId(conversaId)
        } catch (error) {
            console.error('Error loading conversation:', error)
        }
    }

    // Endpoint: POST /agentes/:agente_id/chat
    const handleSendMessage = async () => {
        if (!input.trim()) return

        const userMessage: Message = {
            role: 'user',
            content: input,
            timestamp: new Date()
        }

        setMessages(prev => [...prev, userMessage])
        setInput('')
        setLoading(true)

        try {
            const response = await api.post(`/agentes/${agente_id}/chat`, {
                message: input,
                conversation_id: currentConversationId
            })

            const assistantMessage: Message = {
                role: 'assistant',
                content: response.data.response,
                timestamp: new Date()
            }

            setMessages(prev => [...prev, assistantMessage])

            // Update conversation ID if new conversation was created
            if (response.data.conversation_id && !currentConversationId) {
                setCurrentConversationId(response.data.conversation_id)
                fetchConversations()
            }
        } catch (error) {
            console.error('Error sending message:', error)
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Desculpe, ocorreu um erro ao processar sua mensagem.',
                timestamp: new Date()
            }])
        } finally {
            setLoading(false)
        }
    }

    // Endpoint: POST /agentes/:agente_id/salvar-conversa
    const handleSaveConversation = async () => {
        if (messages.length === 0) return

        try {
            await api.post(`/agentes/${agente_id}/salvar-conversa`, {
                messages,
                titulo: `Conversa ${new Date().toLocaleString('pt-BR')}`
            })
            fetchConversations()
            alert('Conversa salva com sucesso!')
        } catch (error) {
            console.error('Error saving conversation:', error)
            alert('Erro ao salvar conversa')
        }
    }

    // Endpoint: DELETE /agentes/:agente_id/conversa/:conversa_id
    const handleDeleteConversation = async (conversaId: number) => {
        if (!confirm('Deseja excluir esta conversa?')) return

        try {
            await api.delete(`/agentes/${agente_id}/conversa/${conversaId}`)
            fetchConversations()
            if (currentConversationId === conversaId) {
                setMessages([])
                setCurrentConversationId(null)
            }
            alert('Conversa excluída!')
        } catch (error) {
            console.error('Error deleting conversation:', error)
            alert('Erro ao excluir conversa')
        }
    }

    const handleNewChat = () => {
        setMessages([])
        setCurrentConversationId(null)
    }

    return (
        <AdminLayout>
            <PageHeader
                title="Chat com Assistente"
                description={`Agente #${agente_id}`}
                action={
                    <button
                        onClick={handleNewChat}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        <MessageSquare className="w-4 h-4" />
                        Nova Conversa
                    </button>
                }
            />

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Conversations Sidebar */}
                <div className="lg:col-span-1">
                    <div className="bg-white rounded-lg border border-gray-200 p-4">
                        <h3 className="font-semibold text-gray-900 mb-4">Conversas Salvas</h3>
                        <div className="space-y-2">
                            {conversations.map(conv => (
                                <div
                                    key={conv.id}
                                    className={`p-3 rounded-lg border cursor-pointer hover:bg-gray-50 ${currentConversationId === conv.id ? 'bg-blue-50 border-blue-300' : 'border-gray-200'
                                        }`}
                                >
                                    <div className="flex items-start justify-between">
                                        <div
                                            onClick={() => loadConversation(conv.id)}
                                            className="flex-1"
                                        >
                                            <p className="font-medium text-sm text-gray-900">{conv.titulo}</p>
                                            <p className="text-xs text-gray-500">
                                                {new Date(conv.created_at).toLocaleDateString('pt-BR')}
                                            </p>
                                        </div>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                handleDeleteConversation(conv.id)
                                            }}
                                            className="text-red-600 hover:bg-red-50 p-1 rounded"
                                        >
                                            <Trash2 className="w-3 h-3" />
                                        </button>
                                    </div>
                                </div>
                            ))}

                            {conversations.length === 0 && (
                                <p className="text-sm text-gray-500 text-center py-4">
                                    Nenhuma conversa salva
                                </p>
                            )}
                        </div>
                    </div>
                </div>

                {/* Chat Area */}
                <div className="lg:col-span-3">
                    <div className="bg-white rounded-lg border border-gray-200 h-[600px] flex flex-col">
                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-6 space-y-4">
                            {messages.length === 0 && (
                                <div className="flex items-center justify-center h-full text-center">
                                    <div>
                                        <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                                        <h3 className="text-lg font-medium text-gray-900 mb-2">
                                            Começe uma conversa
                                        </h3>
                                        <p className="text-gray-600">
                                            Digite sua mensagem abaixo para começar
                                        </p>
                                    </div>
                                </div>
                            )}

                            {messages.map((msg, idx) => (
                                <div
                                    key={idx}
                                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-[70%] rounded-lg px-4 py-3 ${msg.role === 'user'
                                                ? 'bg-blue-600 text-white'
                                                : 'bg-gray-100 text-gray-900'
                                            }`}
                                    >
                                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                                        <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                                            }`}>
                                            {msg.timestamp.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                                        </p>
                                    </div>
                                </div>
                            ))}

                            {loading && (
                                <div className="flex justify-start">
                                    <div className="bg-gray-100 rounded-lg px-4 py-3">
                                        <div className="flex gap-2">
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Input Area */}
                        <div className="border-t border-gray-200 p-4">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                                    placeholder="Digite sua mensagem..."
                                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    disabled={loading}
                                />
                                {messages.length > 0 && (
                                    <button
                                        onClick={handleSaveConversation}
                                        className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                        title="Salvar Conversa"
                                    >
                                        <Save className="w-4 h-4" />
                                    </button>
                                )}
                                <button
                                    onClick={handleSendMessage}
                                    disabled={loading || !input.trim()}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                                >
                                    <Send className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </AdminLayout>
    )
}
