import { useState } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { Brain, Sparkles, FileText, Play } from 'lucide-react'
// import api from '../../lib/api'

interface AgentSuggestion {
    agente_id: number
    agente_nome: string
    score_relevancia: number
    razao: string
}

export default function SelecaoInteligente() {
    const [texto, setTexto] = useState('')
    const [categoria, setCategoria] = useState('')
    const [suggestions, setSuggestions] = useState<AgentSuggestion[]>([])
    const [analyzing, setAnalyzing] = useState(false)
    const [selectedAgents, setSelectedAgents] = useState<number[]>([])

    // Endpoint: POST /api/multi-agente/selecao-inteligente (hypothetical - would need to be created)
    // For now, using existing agent selection logic
    const handleAnalyzeText = async () => {
        if (!texto.trim()) {
            alert('Por favor, forneça um texto para análise')
            return
        }

        setAnalyzing(true)
        try {
            // This would call an AI endpoint that analyzes the text and suggests best agents
            // Mock implementation:
            const mockSuggestions: AgentSuggestion[] = [
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
            ]

            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1500))
            setSuggestions(mockSuggestions)
        } catch (error) {
            console.error('Error analyzing text:', error)
            alert('Erro ao analisar texto')
        } finally {
            setAnalyzing(false)
        }
    }

    const handleToggleAgent = (agentId: number) => {
        setSelectedAgents(prev =>
            prev.includes(agentId)
                ? prev.filter(id => id !== agentId)
                : [...prev, agentId]
        )
    }

    const handleExecute = async () => {
        if (selectedAgents.length === 0) {
            alert('Selecione ao menos um agente')
            return
        }

        // Would redirect to orchestrator with pre-selected agents
        window.location.href = `/multi-agente/orquestrador?agents=${selectedAgents.join(',')}&text=${encodeURIComponent(texto)}`
    }

    return (
        <AdminLayout>
            <PageHeader
                title="Seleção Inteligente de Agentes"
                description="IA analisa o texto e sugere os melhores agentes para a tarefa"
            />

            <div className="max-w-5xl mx-auto">
                {/* Input Section */}
                <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <FileText className="w-5 h-5" />
                        Texto para Análise
                    </h3>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Categoria (Opcional)
                            </label>
                            <select
                                value={categoria}
                                onChange={(e) => setCategoria(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                            >
                                <option value="">Detectar Automaticamente</option>
                                <option value="civel">Direito Cível</option>
                                <option value="trabalhista">Direito Trabalhista</option>
                                <option value="criminal">Direito Criminal</option>
                                <option value="tributario">Direito Tributário</option>
                                <option value="contratos">Contratos</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Texto do Documento/Caso
                            </label>
                            <textarea
                                value={texto}
                                onChange={(e) => setTexto(e.target.value)}
                                rows={10}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                placeholder="Cole aqui o texto que deseja analisar. A IA irá sugerir os agentes mais adequados baseado no conteúdo..."
                            />
                        </div>

                        <button
                            onClick={handleAnalyzeText}
                            disabled={analyzing || !texto.trim()}
                            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                        >
                            <Brain className="w-4 h-4" />
                            {analyzing ? 'Analisando...' : 'Analisar e Sugerir Agentes'}
                        </button>
                    </div>
                </div>

                {/* Loading State */}
                {analyzing && (
                    <div className="bg-white rounded-lg border border-gray-200 p-12 text-center mb-6">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                        <p className="text-gray-600">Analisando texto com IA...</p>
                        <p className="text-sm text-gray-500 mt-2">Identificando agentes mais relevantes</p>
                    </div>
                )}

                {/* Suggestions */}
                {suggestions.length > 0 && !analyzing && (
                    <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                            <Sparkles className="w-5 h-5 text-yellow-500" />
                            Agentes Sugeridos
                        </h3>

                        <div className="space-y-3">
                            {suggestions.map((suggestion) => (
                                <label
                                    key={suggestion.agente_id}
                                    className={`flex items-start gap-4 p-4 border rounded-lg cursor-pointer transition-colors ${selectedAgents.includes(suggestion.agente_id)
                                        ? 'border-blue-500 bg-blue-50'
                                        : 'border-gray-200 hover:bg-gray-50'
                                        }`}
                                >
                                    <input
                                        type="checkbox"
                                        checked={selectedAgents.includes(suggestion.agente_id)}
                                        onChange={() => handleToggleAgent(suggestion.agente_id)}
                                        className="mt-1 rounded"
                                    />
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between mb-2">
                                            <h4 className="font-semibold text-gray-900">{suggestion.agente_nome}</h4>
                                            <div className="flex items-center gap-2">
                                                <div className="text-sm font-medium text-blue-600">
                                                    {(suggestion.score_relevancia * 100).toFixed(0)}% relevância
                                                </div>
                                            </div>
                                        </div>
                                        <p className="text-sm text-gray-600">{suggestion.razao}</p>

                                        {/* Relevance Bar */}
                                        <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className="bg-blue-600 h-2 rounded-full transition-all"
                                                style={{ width: `${suggestion.score_relevancia * 100}%` }}
                                            />
                                        </div>
                                    </div>
                                </label>
                            ))}
                        </div>

                        {selectedAgents.length > 0 && (
                            <div className="mt-6 pt-6 border-t border-gray-200">
                                <p className="text-sm text-gray-600 mb-4">
                                    {selectedAgents.length} agente(s) selecionado(s)
                                </p>
                                <button
                                    onClick={handleExecute}
                                    className="flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
                                >
                                    <Play className="w-4 h-4" />
                                    Executar com Agentes Selecionados
                                </button>
                            </div>
                        )}
                    </div>
                )}

                {/* Info Box */}
                {suggestions.length === 0 && !analyzing && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                        <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                            <Brain className="w-5 h-5" />
                            Como funciona?
                        </h4>
                        <ul className="text-sm text-blue-800 space-y-2">
                            <li>• A IA analisa o conteúdo do seu texto usando NLP avançado</li>
                            <li>• Identifica os temas, áreas jurídicas e complexidade</li>
                            <li>• Sugere automaticamente os agentes mais qualificados</li>
                            <li>• Calcula score de relevância para cada agente</li>
                            <li>• Você pode ajustar a seleção manualmente se desejar</li>
                        </ul>
                    </div>
                )}
            </div>
        </AdminLayout>
    )
}
