import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { DataTable, SearchBar, PageHeader } from '../../components/ui/AdminComponents'
import { Plus, FileText, Download, Edit, Trash2 } from 'lucide-react'
import api from '../../lib/api'

interface Template {
    id: number
    nome: string
    categoria: string
    descricao?: string
    tipo_arquivo: string
    num_usos: number
    created_at: string
}

export default function TemplatesList() {
    const navigate = useNavigate()
    const [templates, setTemplates] = useState<Template[]>([])
    const [filtered, setFiltered] = useState<Template[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchTemplates()
    }, [])

    // Endpoint: GET /api/templates

    const fetchTemplates = async () => {
        try {
            const response = await api.get('/api/templates')
            setTemplates(response.data)
            setFiltered(response.data)
        } catch (error) {
            console.error('Error fetching templates:', error)
        } finally {
            setLoading(false)
        }
    }

    // Endpoint: DELETE /api/templates/:id
    const handleDeleteTemplate = async (id: number) => {
        if (!confirm('Deseja excluir este template?')) return

        try {
            await api.delete(`/api/templates/${id}`)
            fetchTemplates()
            alert('Template excluído!')
        } catch (error) {
            console.error('Error deleting template:', error)
            alert('Erro ao excluir template')
        }
    }

    // Endpoint: GET /api/templates/:id/download
    const handleDownloadTemplate = async (id: number, nome: string) => {
        try {
            const response = await api.get(`/api/templates/${id}/download`, {
                responseType: 'blob'
            })

            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', nome)
            document.body.appendChild(link)
            link.click()
            link.remove()
        } catch (error) {
            console.error('Error downloading template:', error)
            alert('Erro ao baixar template')
        }
    }

    const handleSearch = (query: string) => {
        const result = templates.filter(t =>
            t.nome.toLowerCase().includes(query.toLowerCase()) ||
            t.categoria.toLowerCase().includes(query.toLowerCase()) ||
            t.descricao?.toLowerCase().includes(query.toLowerCase())
        )
        setFiltered(result)
    }

    const columns = [
        {
            key: 'nome',
            label: 'Nome',
            render: (value: string, row: Template) => (
                <div>
                    <div className="font-medium text-gray-900">{value}</div>
                    {row.descricao && (
                        <div className="text-sm text-gray-500">{row.descricao}</div>
                    )}
                </div>
            )
        },
        {
            key: 'categoria',
            label: 'Categoria',
            render: (value: string) => (
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                    {value}
                </span>
            )
        },
        {
            key: 'tipo_arquivo',
            label: 'Tipo',
            render: (value: string) => value.toUpperCase()
        },
        {
            key: 'num_usos',
            label: 'Usos',
        },
        {
            key: 'created_at',
            label: 'Criado em',
            render: (value: string) => new Date(value).toLocaleDateString('pt-BR')
        },
        {
            key: 'actions',
            label: 'Ações',
            render: (_: any, row: Template) => (
                <div className="flex items-center gap-2">
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            handleDownloadTemplate(row.id, row.nome)
                        }}
                        className="p-1 text-green-600 hover:bg-green-50 rounded"
                        title="Download"
                    >
                        <Download className="w-4 h-4" />
                    </button>
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            navigate(`/templates/${row.id}/edit`)
                        }}
                        className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        title="Editar"
                    >
                        <Edit className="w-4 h-4" />
                    </button>
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteTemplate(row.id)
                        }}
                        className="p-1 text-red-600 hover:bg-red-50 rounded"
                        title="Excluir"
                    >
                        <Trash2 className="w-4 h-4" />
                    </button>
                </div>
            )
        },
    ]

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
                title="Templates de Documentos"
                description={`${filtered.length} templates disponíveis`}
                action={
                    <button
                        onClick={() => navigate('/templates/novo')}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        <Plus className="w-4 h-4" />
                        Novo Template
                    </button>
                }
            />

            <div className="bg-white rounded-lg border border-gray-200">
                <div className="p-4 border-b border-gray-200">
                    <SearchBar
                        placeholder="Buscar por nome, categoria ou descrição..."
                        onSearch={handleSearch}
                    />
                </div>

                {filtered.length > 0 ? (
                    <>
                        <DataTable
                            columns={columns}
                            data={filtered}
                            onRowClick={(row) => handleDownloadTemplate(row.id, row.nome)}
                        />
                        <div className="p-4 border-t border-gray-200 flex items-center justify-between">
                            <p className="text-sm text-gray-600">
                                Mostrando {filtered.length} de {templates.length} templates
                            </p>
                        </div>
                    </>
                ) : (
                    <div className="p-12 text-center">
                        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">
                            Nenhum template encontrado
                        </h3>
                        <p className="text-gray-600 mb-4">
                            Crie templates para agilizar a criação de documentos
                        </p>
                        <button
                            onClick={() => navigate('/templates/novo')}
                            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                            <Plus className="w-4 h-4" />
                            Criar Template
                        </button>
                    </div>
                )}
            </div>
        </AdminLayout>
    )
}
