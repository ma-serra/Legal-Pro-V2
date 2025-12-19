import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { ArrowLeft, Save, Bot, Sliders, Zap } from 'lucide-react'
import api from '../../lib/api'

interface AssistenteConfig {
    id: number
    nome: string
    area_juridica: string
    model: string
    temperature: number
    max_tokens: number
    top_p: number
    frequency_penalty: number
    presence_penalty: number
    system_prompt: string
    context_window: number
    response_format: string
}

export default function ConfigureAssistant() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [config, setConfig] = useState<AssistenteConfig>({
        id: 0,
        nome: '',
        area_juridica: '',
        model: 'gpt-4-turbo-preview',
        temperature: 0.7,
        max_tokens: 2000,
        top_p: 1.0,
        frequency_penalty: 0.0,
        presence_penalty: 0.0,
        system_prompt: '',
        context_window: 8000,
        response_format: 'text'
    })

    useEffect(() => {
        if (id) {
            fetchConfig()
        }
    }, [id])

    const fetchConfig = async () => {
        try {
            // GET /api/assistentes/:id
            const response = await api.get(`/api/assistentes/${id}`)
            const data = response.data

            // Adapt Backend (Nested) -> Frontend (Flat)
            setConfig({
                id: data.id,
                nome: data.nome,
                area_juridica: data.area_juridica || '',
                // Map legacy/nested fields
                model: data.configuracoes?.llm_model || data.modelo_ai || 'gpt-4-turbo-preview',
                temperature: data.configuracoes?.temperatura ?? data.temperatura ?? 0.7,
                max_tokens: data.configuracoes?.max_tokens ?? data.max_tokens ?? 2000,
                // Extra fields stored in configuracoes
                top_p: data.configuracoes?.top_p ?? 1.0,
                frequency_penalty: data.configuracoes?.frequency_penalty ?? 0.0,
                presence_penalty: data.configuracoes?.presence_penalty ?? 0.0,
                context_window: data.configuracoes?.context_window ?? 8000,
                response_format: data.configuracoes?.response_format || 'text',

                system_prompt: data.prompt_template || data.template_prompt || ''
            })
        } catch (error) {
            console.error('Error fetching config:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setSaving(true)

        try {
            // Adapt Frontend (Flat) -> Backend (Nested)
            // PUT /api/assistentes/:id
            const payload = {
                prompt_template: config.system_prompt,
                configuracoes: {
                    llm_model: config.model,
                    temperatura: config.temperature,
                    max_tokens: config.max_tokens,
                    top_p: config.top_p,
                    frequency_penalty: config.frequency_penalty,
                    presence_penalty: config.presence_penalty,
                    context_window: config.context_window,
                    response_format: config.response_format,
                    // Preserve other keys if needed? For now replace.
                }
            }

            await api.put(`/api/assistentes/${id}`, payload)
            alert('Configuração salva com sucesso!')
            navigate('/assistentes')
        } catch (error) {
            console.error('Error saving config:', error)
            alert('Erro ao salvar configuração')
        } finally {
            setSaving(false)
        }
    }

    const handleChange = (field: string, value: any) => {
        setConfig(prev => ({ ...prev, [field]: value }))
    }

    if (loading) {
        return (
            <AdminLayout>
                <div className="flex items-center justify-center h-96">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
            </AdminLayout>
        )
    }

    return (
        <AdminLayout>
            <div className="mb-6">
                <Link
                    to="/assistentes"
                    className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Voltar para assistentes
                </Link>

                <PageHeader
                    title={`Configurar: ${config.nome}`}
                    description={config.area_juridica}
                />
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Modelo de IA */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <Bot className="w-5 h-5 text-blue-600" />
                        <h3 className="text-lg font-semibold text-gray-900">Modelo de IA</h3>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Modelo
                            </label>
                            <select
                                value={config.model}
                                onChange={(e) => handleChange('model', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="gpt-4-turbo-preview">GPT-4 Turbo</option>
                                <option value="gpt-4">GPT-4</option>
                                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                <option value="claude-3-opus">Claude 3 Opus</option>
                                <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Formato de Resposta
                            </label>
                            <select
                                value={config.response_format}
                                onChange={(e) => handleChange('response_format', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="text">Texto</option>
                                <option value="json">JSON</option>
                                <option value="markdown">Markdown</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Parâmetros Avançados */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <Sliders className="w-5 h-5 text-blue-600" />
                        <h3 className="text-lg font-semibold text-gray-900">Parâmetros Avançados</h3>
                    </div>

                    <div className="space-y-6">
                        {/* Temperature */}
                        <div>
                            <div className="flex justify-between mb-2">
                                <label className="text-sm font-medium text-gray-700">
                                    Temperature
                                </label>
                                <span className="text-sm text-gray-600">{config.temperature}</span>
                            </div>
                            <input
                                type="range"
                                min="0"
                                max="2"
                                step="0.1"
                                value={config.temperature}
                                onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
                                className="w-full"
                            />
                            <p className="text-xs text-gray-500 mt-1">
                                Controla a criatividade. 0 = mais preciso, 2 = mais criativo
                            </p>
                        </div>

                        {/* Max Tokens */}
                        <div>
                            <div className="flex justify-between mb-2">
                                <label className="text-sm font-medium text-gray-700">
                                    Máximo de Tokens
                                </label>
                                <span className="text-sm text-gray-600">{config.max_tokens}</span>
                            </div>
                            <input
                                type="range"
                                min="100"
                                max="4000"
                                step="100"
                                value={config.max_tokens}
                                onChange={(e) => handleChange('max_tokens', parseInt(e.target.value))}
                                className="w-full"
                            />
                            <p className="text-xs text-gray-500 mt-1">
                                Tamanho máximo da resposta
                            </p>
                        </div>

                        {/* Top P */}
                        <div>
                            <div className="flex justify-between mb-2">
                                <label className="text-sm font-medium text-gray-700">
                                    Top P
                                </label>
                                <span className="text-sm text-gray-600">{config.top_p}</span>
                            </div>
                            <input
                                type="range"
                                min="0"
                                max="1"
                                step="0.1"
                                value={config.top_p}
                                onChange={(e) => handleChange('top_p', parseFloat(e.target.value))}
                                className="w-full"
                            />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Frequency Penalty */}
                            <div>
                                <div className="flex justify-between mb-2">
                                    <label className="text-sm font-medium text-gray-700">
                                        Frequency Penalty
                                    </label>
                                    <span className="text-sm text-gray-600">{config.frequency_penalty}</span>
                                </div>
                                <input
                                    type="range"
                                    min="-2"
                                    max="2"
                                    step="0.1"
                                    value={config.frequency_penalty}
                                    onChange={(e) => handleChange('frequency_penalty', parseFloat(e.target.value))}
                                    className="w-full"
                                />
                            </div>

                            {/* Presence Penalty */}
                            <div>
                                <div className="flex justify-between mb-2">
                                    <label className="text-sm font-medium text-gray-700">
                                        Presence Penalty
                                    </label>
                                    <span className="text-sm text-gray-600">{config.presence_penalty}</span>
                                </div>
                                <input
                                    type="range"
                                    min="-2"
                                    max="2"
                                    step="0.1"
                                    value={config.presence_penalty}
                                    onChange={(e) => handleChange('presence_penalty', parseFloat(e.target.value))}
                                    className="w-full"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                {/* System Prompt */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <Zap className="w-5 h-5 text-blue-600" />
                        <h3 className="text-lg font-semibold text-gray-900">System Prompt</h3>
                    </div>

                    <textarea
                        value={config.system_prompt}
                        onChange={(e) => handleChange('system_prompt', e.target.value)}
                        rows={10}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                        placeholder="Digite o prompt do sistema..."
                    />
                    <p className="text-xs text-gray-500 mt-2">
                        Define o comportamento e personalidade do assistente
                    </p>
                </div>

                {/* Ações */}
                <div className="flex justify-end gap-4">
                    <Link
                        to="/assistentes"
                        className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                    >
                        Cancelar
                    </Link>
                    <button
                        type="submit"
                        disabled={saving}
                        className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    >
                        <Save className="w-4 h-4" />
                        {saving ? 'Salvando...' : 'Salvar Configuração'}
                    </button>
                </div>
            </form>
        </AdminLayout>
    )
}
