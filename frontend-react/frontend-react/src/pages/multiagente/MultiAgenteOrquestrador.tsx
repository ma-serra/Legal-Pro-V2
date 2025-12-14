import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { Play, FileText, Bot, AlertCircle } from 'lucide-react'
import api from '../../lib/api'

interface AgentOption {
    id: number
    nome: string
    especialidade: string
    disponivel: boolean
}

export default function MultiAgenteOrquestrador() {
    const navigate = useNavigate()
    const [selectedAgents, setSelectedAgents] = useState<number[]>([])
    const [texto, setTexto] = useState('')
    const [tipo, setTipo] = useState('completa')
    const [executing, setExecuting] = useState(false)
    const [resultado, setResultado] = useState<any>(null)

    // Mock agents - would come from API
    const availableAgents: AgentOption[] = [
        { id: 1, nome: 'Agente Cível', especialidade: 'Direito Cível', disponivel: true },
        { id: 2, nome: 'Agente Trabalhista', especialidade: 'Direito Trabalhista', disponivel: true },
        { id: 3, nome: 'Agente Criminal', especialidade: 'Direito Criminal', disponivel: true },
        { id: 4, nome: 'Agente Tributário', especialidade: 'Direito Tributário', disponivel: true },
        { id: 5, nome: 'Agente Contratual', especialidade: 'Análise de Contratos', disponivel: true },
    ]

    const handleAgentToggle = (agentId: number) => {
        setSelectedAgents(prev =>
            prev.includes(agentId)
                ? prev.filter(id => id !== agentId)
                : [...prev, agentId]
        )
    }

    // Endpoint: POST /api/multi-agente-real/analise-real
    const handleExecuteAnalysis = async () => {
        if (!texto.trim() || selectedAgents.length === 0) {
            alert('Selecione ao menos um agente e forneça um texto')
            return
        }

        setExecuting(true)
        try {
            const response = await api.post('/api/multi-agente-real/analise-real', {
                texto,
                agentes_ids: selectedAgents,
                tipo_analise: tipo
            })

            setResultado(response.data)
        } catch (error) {
            console.error('Error executing analysis:', error)
            alert('Erro ao executar análise multi-agente')
        } finally {
            setExecuting(false)
        }
    }

    // Alternative endpoints:
    // POST /api/analise-multi-agente (older version)
    // POST /api/multi-agente-otimizada (optimized version)
    // POST /api/multi-agente-funcional (functional version)

    return (
        <AdminLayout>
            <PageHeader
                title="Orquestrador Multi-Agente"
                description="Execute análises coordenadas com múltiplos agentes IA"
            />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Configuration Panel */}
                <div className="lg:col-span-1 space-y-6">
                    {/* Agent Selection */}
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                            <Bot className="w-5 h-5" />
                            Selecionar Agentes
                        </h3>

                        <div className="space-y-2">
                            {availableAgents.map(agent => (
                                <label
                                    key={agent.id}
                                    className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${selectedAgents.includes(agent.id)
                                            ? 'border-blue-500 bg-blue-50'
                                            : 'border-gray-200 hover:bg-gray-50'
                                        }`}
                                >
                                    <input
                                        type="checkbox"
                                        checked={selectedAgents.includes(agent.id)}
                                        onChange={() => handleAgentToggle(agent.id)}
                                        className="rounded"
                                    />
                                    <div className="flex-1">
                                        <div className="font-medium text-sm">{agent.nome}</div>
                                        <div className="text-xs text-gray-500">{agent.especialidade}</div>
                                    </div>
                                    <div className={`w-2 h-2 rounded-full ${agent.disponivel ? 'bg-green-500' : 'bg-gray-300'
                                        }`} />
                                </label>
                            ))}
                        </div>

                        <div className="mt-4 text-sm text-gray-600">
                            {selectedAgents.length} agente(s) selecionado(s)
                        </div>
                    </div>

                    {/* Analysis Type */}
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Tipo de Análise</h3>
                        <select
                            value={tipo}
                            onChange={(e) => setTipo(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                        >
                            <option value="completa">Análise Completa</option>
                            <option value="resumida">Análise Resumida</option>
                            <option value="comparativa">Análise Comparativa</option>
                            <option value="consensual">Busca Consenso</option>
                        </select>
                    </div>
                </div>

                {/* Main Panel */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Input */}
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                            <FileText className="w-5 h-5" />
                            Texto para Análise
                        </h3>

                        <textarea
                            value={texto}
                            onChange={(e) => setTexto(e.target.value)}
                            rows={12}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="Cole aqui o texto, documento ou caso jurídico para análise pelos agentes..."
                        />

                        <div className="flex gap-3 mt-4">
                            <button
                                onClick={handleExecuteAnalysis}
                                disabled={executing || !texto.trim() || selectedAgents.length === 0}
                                className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                            >
                                <Play className="w-4 h-4" />
                                {executing ? 'Executando...' : 'Executar Análise'}
                            </button>

                            {resultado && (
                                <button
                                    onClick={() => setResultado(null)}
                                    className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                >
                                    Nova Análise
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Results */}
                    {resultado && (
                        <div className="bg-white rounded-lg border border-gray-200 p-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Resultados</h3>

                            {resultado.analises?.map((analise: any, idx: number) => (
                                <div key={idx} className="mb-6 p-4 border border-gray-200 rounded-lg">
                                    <div className="flex items-center justify-between mb-3">
                                        <h4 className="font-semibold text-gray-900">{analise.agente_nome}</h4>
                                        <span className="text-sm text-gray-500">{analise.tempo_execucao}s</span>
                                    </div>
                                    <div className="prose prose-sm max-w-none">
                                        <p className="text-gray-700">{analise.resultado}</p>
                                    </div>
                                </div>
                            ))}

                            {resultado.consenso && (
                                <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                    <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                                        <AlertCircle className="w-5 h-5" />
                                        Consenso Multi-Agente
                                    </h4>
                                    <p className="text-blue-800">{resultado.consenso}</p>
                                </div>
                            )}

                            <div className="flex gap-3 mt-6 pt-6 border-t border-gray-200">
                                <button
                                    onClick={() => navigate(`/multi-agente/historico`)}
                                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                >
                                    Ver no Histórico
                                </button>
                                <button
                                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                >
                                    Exportar Resultado
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Loading State */}
                    {executing && (
                        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                            <p className="text-gray-600">Executando análise com {selectedAgents.length} agentes...</p>
                            <p className="text-sm text-gray-500 mt-2">Isso pode levar alguns segundos</p>
                        </div>
                    )}
                </div>
            </div>
        </AdminLayout>
    )
}
