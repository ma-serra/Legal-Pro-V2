import { useState, useEffect } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { Plus, Edit, Trash2, FolderPlus, Folder } from 'lucide-react'
import api from '../../lib/api'

interface Category {
    id: number
    nome: string
    descricao: string
    parent_id: number | null
    total_templates: number
}

export default function TemplateCategories() {
    const [categories, setCategories] = useState<Category[]>([])
    const [loading, setLoading] = useState(true)
    const [isEditing, setIsEditing] = useState(false)
    const [currentCategory, setCurrentCategory] = useState<Partial<Category>>({})

    useEffect(() => {
        fetchCategories()
    }, [])

    const fetchCategories = async () => {
        try {
            const response = await api.get('/api/templates/categorias')
            setCategories(response.data)
        } catch (error) {
            console.error('Error fetching categories:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSave = async () => {
        try {
            if (currentCategory.id) {
                await api.put(`/api/templates/categorias/${currentCategory.id}`, currentCategory)
            } else {
                await api.post('/api/templates/categorias', currentCategory)
            }
            await fetchCategories()
            setIsEditing(false)
            setCurrentCategory({})
        } catch (error) {
            console.error('Error saving category:', error)
            alert('Erro ao salvar categoria')
        }
    }

    const handleDelete = async (id: number) => {
        if (!confirm('Tem certeza que deseja excluir esta categoria?')) return

        try {
            await api.delete(`/api/templates/categorias/${id}`)
            await fetchCategories()
        } catch (error) {
            console.error('Error deleting category:', error)
            alert('Erro ao excluir categoria. Verifique se não há templates vinculados.')
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
                title="Categorias de Templates"
                description="Organize os templates em categorias"
                action={
                    <button
                        onClick={() => {
                            setCurrentCategory({})
                            setIsEditing(true)
                        }}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        <Plus className="w-4 h-4" />
                        Nova Categoria
                    </button>
                }
            />

            {/* Editor de Categoria (Modal) */}
            {isEditing && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-lg max-w-md w-full">
                        <div className="p-6 border-b border-gray-200">
                            <h2 className="text-xl font-semibold text-gray-900">
                                {currentCategory.id ? 'Editar Categoria' : 'Nova Categoria'}
                            </h2>
                        </div>

                        <div className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Nome da Categoria
                                </label>
                                <input
                                    type="text"
                                    value={currentCategory.nome || ''}
                                    onChange={(e) => setCurrentCategory({ ...currentCategory, nome: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Descrição
                                </label>
                                <textarea
                                    value={currentCategory.descricao || ''}
                                    onChange={(e) => setCurrentCategory({ ...currentCategory, descricao: e.target.value })}
                                    rows={3}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Categoria Pai (Opcional)
                                </label>
                                <select
                                    value={currentCategory.parent_id || ''}
                                    onChange={(e) => setCurrentCategory({
                                        ...currentCategory,
                                        parent_id: e.target.value ? parseInt(e.target.value) : null
                                    })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="">Nenhuma (Categoria Raiz)</option>
                                    {categories.filter(c => c.id !== currentCategory.id).map((cat) => (
                                        <option key={cat.id} value={cat.id}>
                                            {cat.nome}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div className="p-6 border-t border-gray-200 flex justify-end gap-4">
                            <button
                                onClick={() => {
                                    setIsEditing(false)
                                    setCurrentCategory({})
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

            {/* Lista de Categorias */}
            {categories.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {categories.map((category) => (
                        <div
                            key={category.id}
                            className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    {category.parent_id ? (
                                        <FolderPlus className="w-8 h-8 text-blue-600" />
                                    ) : (
                                        <Folder className="w-8 h-8 text-blue-600" />
                                    )}
                                    <div>
                                        <h3 className="font-semibold text-gray-900">{category.nome}</h3>
                                        {category.parent_id && (
                                            <p className="text-xs text-gray-500">Subcategoria</p>
                                        )}
                                    </div>
                                </div>

                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => {
                                            setCurrentCategory(category)
                                            setIsEditing(true)
                                        }}
                                        className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                                        title="Editar"
                                    >
                                        <Edit className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={() => handleDelete(category.id)}
                                        className="p-1 text-red-600 hover:bg-red-50 rounded"
                                        title="Excluir"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            <p className="text-sm text-gray-600 mb-4">
                                {category.descricao || 'Sem descrição'}
                            </p>

                            <div className="pt-4 border-t border-gray-100">
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-gray-600">Templates:</span>
                                    <span className="font-semibold text-blue-600">
                                        {category.total_templates || 0}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                    <Folder className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Nenhuma categoria encontrada
                    </h3>
                    <p className="text-gray-600 mb-4">
                        Crie categorias para organizar seus templates
                    </p>
                    <button
                        onClick={() => {
                            setCurrentCategory({})
                            setIsEditing(true)
                        }}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        <Plus className="w-4 h-4" />
                        Criar Primeira Categoria
                    </button>
                </div>
            )}

            {/* Hierarquia de Categorias */}
            {categories.length > 0 && (
                <div className="mt-8 bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Hierarquia de Categorias</h3>
                    <div className="space-y-2">
                        {categories.filter(c => !c.parent_id).map((parent) => (
                            <div key={parent.id}>
                                <div className="flex items-center gap-2 text-gray-900 font-medium">
                                    <Folder className="w-4 h-4 text-blue-600" />
                                    <span>{parent.nome}</span>
                                    <span className="text-sm text-gray-500">({parent.total_templates})</span>
                                </div>
                                {categories.filter(c => c.parent_id === parent.id).length > 0 && (
                                    <div className="ml-6 mt-2 space-y-1">
                                        {categories.filter(c => c.parent_id === parent.id).map((child) => (
                                            <div key={child.id} className="flex items-center gap-2 text-sm text-gray-700">
                                                <FolderPlus className="w-3 h-3 text-blue-500" />
                                                <span>{child.nome}</span>
                                                <span className="text-xs text-gray-500">({child.total_templates})</span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </AdminLayout>
    )
}
