import { useState, useEffect } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { Settings, CheckCircle, XCircle, Loader } from 'lucide-react'
import api from '../../lib/api'

interface APIConfig {
    provider: string
    name: string
    status: 'active' | 'inactive' | 'error'
    api_key?: string
    endpoint?: string
    last_checked?: string
}

export default function APIConfiguration() {
    const [configs, setConfigs] = useState<APIConfig[]>([])
    const [loading, setLoading] = useState(true)
    const [testing, setTesting] = useState<string | null>(null)

    useEffect(() => {
        fetchConfigs()
    }, [])

    // Endpoint: GET /admin/apis
    const fetchConfigs = async () => {
        try {
            const response = await api.get('/admin/apis')
            setConfigs(response.data || [
                { provider: 'openai', name: 'OpenAI GPT-4', status: 'active' },
                { provider: 'anthropic', name: 'Claude', status: 'active' },
                { provider: 'google', name: 'Google AI', status: 'inactive' },
                { provider: 'azure', name: 'Azure OpenAI', status: 'active' },
            ])
        } catch (error) {
            console.error('Error fetching API configs:', error)
        } finally {
            setLoading(false)
        }
    }

    // Endpoint: POST /admin/apis/config
    const handleSaveConfig = async (provider: string, config: Partial<APIConfig>) => {
        try {
            await api.post('/admin/apis/config', {
                provider,
                ...config
            })
            fetchConfigs()
            alert('Configuração salva!')
        } catch (error) {
            console.error('Error saving config:', error)
            alert('Erro ao salvar configuração')
        }
    }

    // Endpoint: POST /admin/apis/test/:provider
    const handleTestAPI = async (provider: string) => {
        setTesting(provider)
        try {
            const response = await api.post(`/admin/apis/test/${provider}`)
            if (response.data.success) {
                alert(`✅ ${provider} funcionando corretamente!`)
            } else {
                alert(`❌ Erro ao testar ${provider}`)
            }
        } catch (error) {
            console.error('Error testing API:', error)
            alert('Erro no teste')
        } finally {
            setTesting(null)
        }
    }

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'active':
                return <CheckCircle className="w-5 h-5 text-green-600" />
            case 'error':
                return <XCircle className="w-5 h-5 text-red-600" />
            default:
                return <div className="w-5 h-5 rounded-full bg-gray-400" />
        }
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
            <PageHeader
                title="Configuração de APIs"
                description="Gerenciar integrações e APIs externas"
            />

            <div className="space-y-6">
                {configs.map((config) => (
                    <div key={config.provider} className="bg-white rounded-lg border border-gray-200 p-6">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                                {getStatusIcon(config.status)}
                                <div>
                                    <h3 className="font-semibold text-gray-900">{config.name}</h3>
                                    <p className="text-sm text-gray-500">{config.provider}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className={`px-3 py-1 rounded-full text-xs font-medium ${config.status === 'active' ? 'bg-green-100 text-green-800' :
                                        config.status === 'error' ? 'bg-red-100 text-red-800' :
                                            'bg-gray-100 text-gray-800'
                                    }`}>
                                    {config.status}
                                </span>
                                <button
                                    onClick={() => handleTestAPI(config.provider)}
                                    disabled={testing === config.provider}
                                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 flex items-center gap-2"
                                >
                                    {testing === config.provider ? (
                                        <>
                                            <Loader className="w-4 h-4 animate-spin" />
                                            Testando...
                                        </>
                                    ) : (
                                        'Testar'
                                    )}
                                </button>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    API Key
                                </label>
                                <input
                                    type="password"
                                    defaultValue={config.api_key}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                    placeholder="sk-..."
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Endpoint
                                </label>
                                <input
                                    type="text"
                                    defaultValue={config.endpoint}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                    placeholder="https://api.example.com"
                                />
                            </div>
                        </div>

                        {config.last_checked && (
                            <p className="text-sm text-gray-500 mt-4">
                                Último teste: {new Date(config.last_checked).toLocaleString('pt-BR')}
                            </p>
                        )}

                        <div className="flex gap-3 mt-4 pt-4 border-t border-gray-200">
                            <button
                                onClick={() => handleSaveConfig(config.provider, config)}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                            >
                                Salvar
                            </button>
                        </div>
                    </div>
                ))}

                {/* Add New API */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <div className="flex items-center gap-3">
                        <Settings className="w-6 h-6 text-blue-600" />
                        <div>
                            <h3 className="font-semibold text-blue-900">Adicionar Nova API</h3>
                            <p className="text-sm text-blue-700">
                                Configure integrações com novos provedores de IA e serviços externos
                            </p>
                        </div>
                    </div>
                    <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                        Adicionar API
                    </button>
                </div>
            </div>
        </AdminLayout>
    )
}
