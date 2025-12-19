import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { Save, X, ArrowLeft } from 'lucide-react'
import api from '../../lib/api'

export default function EditProcesso() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
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
        autor: '',
        reu: '',
    })

    useEffect(() => {
        fetchProcesso()
    }, [id])

    // Endpoint: GET /api/processos/:processo_id
    const fetchProcesso = async () => {
        try {
            const response = await api.get(`/api/processos/${id}`)
            setFormData(response.data)
        } catch (error) {
            console.error('Error fetching processo:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        setFormData(prev => ({
            ...prev,
            [e.target.name]: e.target.value
        }))
    }

    // Endpoint: POST /api/processos/:processo_id/editar
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setSaving(true)

        try {
            const endpoint = `/api/processos/${id}` // Flask/REST standard often uses PUT on ID for update
            // But looking at backend routes might be specific... 
            // processes/routes.py uses @processos_bp.route('/<int:processo_id>', methods=['PUT'])
            await api.put(endpoint, { // Changed to PUT and cleaner path if backend supports it.
                ...formData,
                valor_causa: formData.valor_causa ? parseFloat(formData.valor_causa) : null
            })
            navigate(`/processos/${id}`)
        } catch (error) {
            console.error('Error updating processo:', error)
            alert('Erro ao atualizar processo')
        } finally {
            setSaving(false)
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
            <div className="mb-6">
                <button
                    onClick={() => navigate(`/processos/${id}`)}
                    className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Voltar
                </button>

                <PageHeader
                    title={`Editar Processo ${formData.numero_processo}`}
                    description="Atualizar informações do processo"
                />
            </div>

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

                    {/* Partes */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Partes</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Autor
                                </label>
                                <input
                                    type="text"
                                    name="autor"
                                    value={formData.autor}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Réu
                                </label>
                                <input
                                    type="text"
                                    name="reu"
                                    value={formData.reu}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Local */}
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
                        />
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3 pt-4 border-t border-gray-200">
                        <button
                            type="submit"
                            disabled={saving}
                            className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                        >
                            <Save className="w-4 h-4" />
                            {saving ? 'Salvando...' : 'Salvar Alterações'}
                        </button>
                        <button
                            type="button"
                            onClick={() => navigate(`/processos/${id}`)}
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
