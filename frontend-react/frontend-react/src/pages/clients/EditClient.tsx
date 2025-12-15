import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { ArrowLeft, Save } from 'lucide-react'
import api from '../../lib/api'

interface ClientForm {
    name: string
    legal_name: string
    document_number: string
    email: string
    phone: string
    address: string
    city: string
    state: string
    zipcode: string
    status: string
}

export default function EditClient() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [formData, setFormData] = useState<ClientForm>({
        name: '',
        legal_name: '',
        document_number: '',
        email: '',
        phone: '',
        address: '',
        city: '',
        state: '',
        zipcode: '',
        status: 'active'
    })

    useEffect(() => {
        if (id) {
            fetchClient()
        }
    }, [id])

    const fetchClient = async () => {
        try {
            const response = await api.get(`/api/clientes/${id}`)
            setFormData(response.data)
        } catch (error) {
            console.error('Error fetching client:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setSaving(true)

        try {
            await api.put(`/api/clientes/${id}`, formData)
            navigate(`/clientes/${id}`)
        } catch (error) {
            console.error('Error updating client:', error)
            alert('Erro ao atualizar cliente')
        } finally {
            setSaving(false)
        }
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target
        setFormData(prev => ({ ...prev, [name]: value }))
    }

    if (loading) {
        return (
            <AdminLayout>
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            </AdminLayout>
        )
    }

    return (
        <AdminLayout>
            <div className="mb-6">
                <Link
                    to={`/clientes/${id}`}
                    className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Voltar para detalhes
                </Link>

                <PageHeader
                    title="Editar Cliente"
                    description="Atualize as informações do cliente"
                />
            </div>

            <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Informações Básicas */}
                    <div className="md:col-span-2">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Informações Básicas</h3>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Nome / Nome Fantasia <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            required
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Razão Social
                        </label>
                        <input
                            type="text"
                            name="legal_name"
                            value={formData.legal_name}
                            onChange={handleChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            CPF/CNPJ <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            name="document_number"
                            value={formData.document_number}
                            onChange={handleChange}
                            required
                            placeholder="000.000.000-00"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Status <span className="text-red-500">*</span>
                        </label>
                        <select
                            name="status"
                            value={formData.status}
                            onChange={handleChange}
                            required
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                            <option value="active">Ativo</option>
                            <option value="inactive">Inativo</option>
                        </select>
                    </div>

                    {/* Contato */}
                    <div className="md:col-span-2 mt-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Contato</h3>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Email
                        </label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="cliente@email.com"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Telefone
                        </label>
                        <input
                            type="tel"
                            name="phone"
                            value={formData.phone}
                            onChange={handleChange}
                            placeholder="(00) 00000-0000"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>

                    {/* Endereço */}
                    <div className="md:col-span-2 mt-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Endereço</h3>
                    </div>

                    <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Logradouro
                        </label>
                        <input
                            type="text"
                            name="address"
                            value={formData.address}
                            onChange={handleChange}
                            placeholder="Rua, Avenida, etc."
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Cidade
                        </label>
                        <input
                            type="text"
                            name="city"
                            value={formData.city}
                            onChange={handleChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Estado
                        </label>
                        <input
                            type="text"
                            name="state"
                            value={formData.state}
                            onChange={handleChange}
                            placeholder="UF"
                            maxLength={2}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            CEP
                        </label>
                        <input
                            type="text"
                            name="zipcode"
                            value={formData.zipcode}
                            onChange={handleChange}
                            placeholder="00000-000"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>
                </div>

                {/* Ações */}
                <div className="flex justify-end gap-4 mt-8 pt-6 border-t border-gray-200">
                    <Link
                        to={`/clientes/${id}`}
                        className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                    >
                        Cancelar
                    </Link>
                    <button
                        type="submit"
                        disabled={saving}
                        className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Save className="w-4 h-4" />
                        {saving ? 'Salvando...' : 'Salvar Alterações'}
                    </button>
                </div>
            </form>
        </AdminLayout>
    )
}
