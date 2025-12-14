import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { Save, X } from 'lucide-react'
import api from '../../lib/api'

export default function NovoProcesso() {
    const navigate = useNavigate()
    const [loading, setLoading] = useState(false)
    const [formData, setFormData] = useState({
        numero_processo: '',
        client_id: '',
        area_direito: 'civel',
        status: 'ativo',
        valor_causa: '',
        data_distribuicao: '',
        vara: '',
        comarca: '',
        descricao: '',
    })

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        setFormData(prev => ({
            ...prev,
            [e.target.name]: e.target.value
        }))
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)

        try {
            await api.post('/api/processos', {
                ...formData,
                valor_causa: formData.valor_causa ? parseFloat(formData.valor_causa) : null
            })
            navigate('/processos')
        } catch (error) {
            console.error('Error creating processo:', error)
            alert('Erro ao criar processo')
        } finally {
            setLoading(false)
        }
    }

    return (
        <AdminLayout>
            <PageHeader title="Novo Processo" description="Cadastrar novo processo jurídico" />

            <form onSubmit={handleSubmit} className="max-w-4xl">
                <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
                    {/* Basic Info */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Informações Básicas</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Número do Processo *
                                </label>
                                <input
                                    type="text"
                                    name="numero_processo"
                                    value={formData.numero_processo}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    placeholder="0000000-00.0000.0.00.0000"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Área do Direito *
                                </label>
                                <select
                                    name="area_direito"
                                    value={formData.area_direito}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="civel">Cível</option>
                                    <option value="trabalhista">Trabalhista</option>
                                    <option value="criminal">Criminal</option>
                                    <option value="tributario">Tributário</option>
                                    <option value="familia">Família</option>
                                    <option value="empresarial">Empresarial</option>
                                    <option value="imobiliario">Imobiliário</option>
                                    <option value="consumidor">Consumidor</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Status
                                </label>
                                <select
                                    name="status"
                                    value={formData.status}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="ativo">Ativo</option>
                                    <option value="suspenso">Suspenso</option>
                                    <option value="arquivado">Arquivado</option>
                                    <option value="finalizado">Finalizado</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Valor da Causa
                                </label>
                                <input
                                    type="number"
                                    name="valor_causa"
                                    value={formData.valor_causa}
                                    onChange={handleChange}
                                    step="0.01"
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    placeholder="R$ 0,00"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Data de Distribuição
                                </label>
                                <input
                                    type="date"
                                    name="data_distribuicao"
                                    value={formData.data_distribuicao}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Local Info */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Localização</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Vara
                                </label>
                                <input
                                    type="text"
                                    name="vara"
                                    value={formData.vara}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    placeholder="1ª Vara Cível"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Comarca
                                </label>
                                <input
                                    type="text"
                                    name="comarca"
                                    value={formData.comarca}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    placeholder="São Paulo"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Description */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Descrição/Observações
                        </label>
                        <textarea
                            name="descricao"
                            value={formData.descricao}
                            onChange={handleChange}
                            rows={4}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="Informações adicionais sobre o processo..."
                        />
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3 pt-4 border-t border-gray-200">
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                        >
                            <Save className="w-4 h-4" />
                            {loading ? 'Salvando...' : 'Salvar Processo'}
                        </button>
                        <button
                            type="button"
                            onClick={() => navigate('/processos')}
                            className="flex items-center gap-2 px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                        >
                            <X className="w-4 h-4" />
                            Cancelar
                        </button>
                    </div>
                </div>
            </form>
        </AdminLayout>
    )
}
