import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { ArrowLeft, Save } from 'lucide-react'
import api from '../../lib/api'

interface TemplateForm {
    id: number
    nome: string
    categoria: string
    area_juridica: string
    descricao: string
    conteudo: string
    campos_variaveis: string[]
}

export default function EditTemplate() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [formData, setFormData] = useState<TemplateForm>({
        id: 0,
        nome: '',
        categoria: '',
        area_juridica: '',
        descricao: '',
        conteudo: '',
        campos_variaveis: []
    })
    const [newVariable, setNewVariable] = useState('')

    useEffect(() => {
        if (id) {
            fetchTemplate()
        }
    }, [id])

    const fetchTemplate = async () => {
        try {
            const response = await api.get(`/api/templates/${id}`)
            setFormData(response.data)
        } catch (error) {
            console.error('Error fetching template:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setSaving(true)

        try {
            await api.put(`/api/templates/${id}`, formData)
            navigate('/templates')
        } catch (error) {
            console.error('Error updating template:', error)
            alert('Erro ao atualizar template')
        } finally {
            setSaving(false)
        }
    }

    const handleAddVariable = () => {
        if (newVariable && !formData.campos_variaveis.includes(newVariable)) {
            setFormData(prev => ({
                ...prev,
                campos_variaveis: [...prev.campos_variaveis, newVariable]
            }))
            setNewVariable('')
        }
    }

    const handleRemoveVariable = (variable: string) => {
        setFormData(prev => ({
            ...prev,
            campos_variaveis: prev.campos_variaveis.filter(v => v !== variable)
        }))
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
                    to="/templates"
                    className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Voltar para templates
                </Link>

                <PageHeader
                    title="Editar Template"
                    description={formData.nome}
                />
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Informações Básicas */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Informações Básicas</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Nome do Template <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="text"
                                value={formData.nome}
                                onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                                required
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Categoria <span className="text-red-500">*</span>
                            </label>
                            <select
                                value={formData.categoria}
                                onChange={(e) => setFormData({ ...formData, categoria: e.target.value })}
                                required
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="peticoes">Petições</option>
                                <option value="contratos">Contratos</option>
                                <option value="pareceres">Pareceres</option>
                                <option value="recursos">Recursos</option>
                                <option value="outros">Outros</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Área Jurídica <span className="text-red-500">*</span>
                            </label>
                            <select
                                value={formData.area_juridica}
                                onChange={(e) => setFormData({ ...formData, area_juridica: e.target.value })}
                                required
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="penal">Direito Penal</option>
                                <option value="civil">Direito Civil</option>
                                <option value="trabalhista">Direito Trabalhista</option>
                                <option value="empresarial">Direito Empresarial</option>
                                <option value="consumidor">Direito do Consumidor</option>
                                <option value="tributario">Direito Tributário</option>
                            </select>
                        </div>

                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Descrição
                            </label>
                            <textarea
                                value={formData.descricao}
                                onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                                rows={3}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                    </div>
                </div>

                {/* Campos Variáveis */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Campos Variáveis</h3>

                    <div className="flex gap-2 mb-4">
                        <input
                            type="text"
                            value={newVariable}
                            onChange={(e) => setNewVariable(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddVariable())}
                            placeholder="Nome da variável"
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                        <button
                            type="button"
                            onClick={handleAddVariable}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                            Adicionar
                        </button>
                    </div>

                    {formData.campos_variaveis.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                            {formData.campos_variaveis.map((variable) => (
                                <div
                                    key={variable}
                                    className="flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-lg"
                                >
                                    <span className="text-sm font-mono">{`{${variable}}`}</span>
                                    <button
                                        type="button"
                                        onClick={() => handleRemoveVariable(variable)}
                                        className="text-blue-600 hover:text-blue-800"
                                    >
                                        ×
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Conteúdo do Template */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Conteúdo do Template</h3>
                    <textarea
                        value={formData.conteudo}
                        onChange={(e) => setFormData({ ...formData, conteudo: e.target.value })}
                        required
                        rows={20}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                    />
                </div>

                {/* Ações */}
                <div className="flex justify-end gap-4">
                    <Link
                        to="/templates"
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
                        {saving ? 'Salvando...' : 'Salvar Alterações'}
                    </button>
                </div>
            </form>
        </AdminLayout>
    )
}
