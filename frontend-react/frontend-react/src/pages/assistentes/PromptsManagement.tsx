import { useState, useEffect } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { Plus, Edit, Trash2, Copy, FileText } from 'lucide-react'
import api from '../../lib/api'

interface Prompt {
    id: number
    nome: string
    categoria: string
    area_juridica: string
    conteudo: string
    variables: string[]
    created_at: string
    created_by: string
}

export default function PromptsManagement() {
    const [prompts, setPrompts] = useState<Prompt[]>([])
    const [filteredPrompts, setFilteredPrompts] = useState<Prompt[]>([])
    const [loading, setLoading] = useState(true)
    const [selectedCategory, setSelectedCategory] = useState<string>('all')
    const [isEditing, setIsEditing] = useState(false)
    const [currentPrompt, setCurrentPrompt] = useState<Partial<Prompt>>({})

    useEffect(() => {
        fetchPrompts()
    }, [])

    useEffect(() => {
        filterPrompts()
    }, [selectedCategory, prompts])

    const fetchPrompts = async () => {
        try {
            const response = await api.get('/api/admin/prompts/listar')
            setPrompts(response.data)
        } catch (error) {
            console.error('Error fetching prompts:', error)
        } finally {
            setLoading(false)
        }
    }

    const filterPrompts = () => {
        if (selectedCategory === 'all') {
            setFilteredPrompts(prompts)
        } else {
            setFilteredPrompts(prompts.filter(p => p.categoria === selectedCategory))
        }
    }

    const handleSave = async () => {
        try {
            if (currentPrompt.id) {
                await api.put(`/api/admin/prompts/${currentPrompt.id}`, currentPrompt)
            } else {
                await api.post('/api/admin/prompts/salvar', currentPrompt)
            }
            await fetchPrompts()
            setIsEditing(false)
            setCurrentPrompt({})
        } catch (error) {
            console.error('Error saving prompt:', error)
            alert('Erro ao salvar prompt')
        }
    }

    const handleDelete = async (id: number) => {
        if (!confirm('Tem certeza que deseja excluir este prompt?')) return

        try {
            await api.delete(`/api/admin/prompts/excluir/${id}`)
            await fetchPrompts()
        } catch (error) {
            console.error('Error deleting prompt:', error)
            alert('Erro ao excluir prompt')
        }
    }

    const handleCopy = (content: string) => {
        navigator.clipboard.writeText(content)
        alert('Prompt copiado para área de transferência!')
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
                title="Gerenciamento de Prompts"
                description="Gerencie os prompts dos assistentes jurídicos"
                action={
                    <button
                        onClick={() => {
                            setCurrentPrompt({})
                            setIsEditing(true)
                        }}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        <Plus className="w-4 h-4" />
                        Novo Prompt
                    </button>
                }
            />

            {/* Editor de Prompt (Modal) */}
            {isEditing && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                        <div className="p-6 border-b border-gray-200">
                            <h2 className="text-xl font-semibold text-gray-900">
                                {currentPrompt.id ? 'Editar Prompt' : 'Novo Prompt'}
                            </h2>
                        </div>

                        <div className="p-6 space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Nome do Prompt
                                    </label>
                                    <input
                                        type="text"
                                        value={currentPrompt.nome || ''}
                                        onChange={(e) => setCurrentPrompt({ ...currentPrompt, nome: e.target.value })}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Categoria
                                    </label>
                                    <select
                                        value={currentPrompt.categoria || ''}
                                        onChange={(e) => setCurrentPrompt({ ...currentPrompt, categoria: e.target.value })}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="">Selecione...</option>
                                        <option value="system">System</option>
                                        <option value="user">User</option>
                                        <option value="assistant">Assistant</option>
                                        <option value="template">Template</option>
                                    </select>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Área Jurídica
                                </label>
                                <input
                                    type="text"
                                    value={currentPrompt.area_juridica || ''}
                                    onChange={(e) => setCurrentPrompt({ ...currentPrompt, area_juridica: e.target.value })}
                                    placeholder="Ex: Direito Penal, Empresarial, etc."
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Conteúdo do Prompt
                                </label>
                                <textarea
                                    value={currentPrompt.conteudo || ''}
                                    onChange={(e) => setCurrentPrompt({ ...currentPrompt, conteudo: e.target.value })}
                                    rows={12}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                                    placeholder="Digite o conteúdo do prompt... Use {variavel} para variáveis"
                                />
                                <p className="text-xs text-gray-500 mt-1">
                                    Use chaves para variáveis: {'{nome}'}, {'{area}'}, {'{contexto}'}
                                </p>
                            </div>
                        </div>

                        <div className="p-6 border-t border-gray-200 flex justify-end gap-4">
                            <button
                                onClick={() => {
                                    setIsEditing(false)
                                    setCurrentPrompt({})
                                }}
                                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleSave}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                            >
                                Salvar
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Filtros */}
            <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
                <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                    <option value="all">Todas as Categorias</option>
                    <option value="system">System</option>
                    <option value="user">User</option>
                    <option value="assistant">Assistant</option>
                    <option value="template">Template</option>
                </select>
            </div>

            {/* Lista de Prompts */}
            {filteredPrompts.length > 0 ? (
                <div className="grid grid-cols-1 gap-4">
                    {filteredPrompts.map((prompt) => (
                        <div key={prompt.id} className="bg-white rounded-lg border border-gray-200 p-6">
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <h3 className="text-lg font-semibold text-gray-900">
                                            {prompt.nome}
                                        </h3>
                                        <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded">
                                            {prompt.categoria}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-600 mb-3">
                                        {prompt.area_juridica}
                                    </p>
                                </div>

                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => handleCopy(prompt.conteudo)}
                                        className="p-2 text-gray-600 hover:bg-gray-100 rounded"
                                        title="Copiar"
                                    >
                                        <Copy className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={() => {
                                            setCurrentPrompt(prompt)
                                            setIsEditing(true)
                                        }}
                                        className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                                        title="Editar"
                                    >
                                        <Edit className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={() => handleDelete(prompt.id)}
                                        className="p-2 text-red-600 hover:bg-red-50 rounded"
                                        title="Excluir"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            <div className="bg-gray-50 rounded-lg p-4 font-mono text-sm text-gray-700 whitespace-pre-wrap">
                                {prompt.conteudo.substring(0, 300)}
                                {prompt.conteudo.length > 300 && '...'}
                            </div>

                            {prompt.variables && prompt.variables.length > 0 && (
                                <div className="mt-3 flex items-center gap-2">
                                    <span className="text-xs text-gray-500">Variáveis:</span>
                                    {prompt.variables.map((v, i) => (
                                        <span key={i} className="px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded">
                                            {v}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            ) : (
                <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                    <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Nenhum prompt encontrado
                    </h3>
                    <p className="text-gray-600 mb-4">
                        Crie seu primeiro prompt para começar
                    </p>
                    <button
                        onClick={() => {
                            setCurrentPrompt({})
                            setIsEditing(true)
                        }}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        <Plus className="w-4 h-4" />
                        Criar Primeiro Prompt
                    </button>
                </div>
            )}
        </AdminLayout>
    )
}
