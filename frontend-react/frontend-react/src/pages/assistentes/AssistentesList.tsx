import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { Bot, MessageSquare, Search, Filter, ChevronRight } from 'lucide-react'
import api from '../../lib/api'

interface Assistente {
    id: number
    nome: string
    area_juridica: string
    categoria: string
    descricao: string
    tipo: string
    status: string
    total_conversas?: number
}

interface AreaJuridica {
    id: number
    nome: string
    total_assistentes: number
}

export default function AssistentesList() {
    const navigate = useNavigate()
    const [assistentes, setAssistentes] = useState<Assistente[]>([])
    const [areas, setAreas] = useState<AreaJuridica[]>([])
    const [filteredAssistentes, setFilteredAssistentes] = useState<Assistente[]>([])
    const [loading, setLoading] = useState(true)
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedArea, setSelectedArea] = useState<string>('all')
    const [selectedTipo, setSelectedTipo] = useState<string>('all')

    useEffect(() => {
        fetchAssistentes()
        fetchAreas()
    }, [])

    useEffect(() => {
        filterAssistentes()
    }, [searchQuery, selectedArea, selectedTipo, assistentes])

    const fetchAssistentes = async () => {
        try {
            const response = await api.get('/api/assistentes')
            setAssistentes(response.data.assistentes || [])  // FIX: acessar .assistentes
        } catch (error) {
            console.error('Error fetching assistentes:', error)
        } finally {
            setLoading(false)
        }
    }

    const fetchAreas = async () => {
        try {
            const response = await api.get('/api/areas-juridicas')
            setAreas(response.data)
        } catch (error) {
            console.error('Error fetching areas:', error)
        }
    }

    const filterAssistentes = () => {
        let filtered = assistentes

        // Filtro por busca
        if (searchQuery) {
            filtered = filtered.filter(a =>
                a.nome.toLowerCase().includes(searchQuery.toLowerCase()) ||
                a.area_juridica.toLowerCase().includes(searchQuery.toLowerCase()) ||
                a.descricao.toLowerCase().includes(searchQuery.toLowerCase())
            )
        }

        // Filtro por área
        if (selectedArea !== 'all') {
            filtered = filtered.filter(a => a.area_juridica === selectedArea)
        }

        // Filtro por tipo
        if (selectedTipo !== 'all') {
            filtered = filtered.filter(a => a.tipo === selectedTipo)
        }

        setFilteredAssistentes(filtered)
    }

    const getIconColor = (tipo: string) => {
        switch (tipo) {
            case 'juridico': return 'text-blue-600 bg-blue-100'
            case 'resumidor': return 'text-green-600 bg-green-100'
            case 'sentimento': return 'text-purple-600 bg-purple-100'
            case 'extrator': return 'text-orange-600 bg-orange-100'
            case 'tradutor': return 'text-pink-600 bg-pink-100'
            case 'classificador': return 'text-yellow-600 bg-yellow-100'
            case 'gerador': return 'text-indigo-600 bg-indigo-100'
            case 'sintetizador': return 'text-cyan-600 bg-cyan-100'
            case 'formatador': return 'text-teal-600 bg-teal-100'
            default: return 'text-gray-600 bg-gray-100'
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
                title="Assistentes Jurídicos IA"
                description={`${filteredAssistentes.length} assistentes especializados disponíveis`}
            />

            {/* Filtros */}
            <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
                <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
                    {/* Busca */}
                    <div className="md:col-span-5">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                            <input
                                type="text"
                                placeholder="Buscar assistentes..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                    </div>

                    {/* Filtro por Área */}
                    <div className="md:col-span-4">
                        <select
                            value={selectedArea}
                            onChange={(e) => setSelectedArea(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                            <option value="all">Todas as Áreas</option>
                            {areas.map((area) => (
                                <option key={area.id} value={area.nome}>
                                    {area.nome} ({area.total_assistentes})
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Filtro por Tipo */}
                    <div className="md:col-span-3">
                        <select
                            value={selectedTipo}
                            onChange={(e) => setSelectedTipo(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                            <option value="all">Todos os Tipos</option>
                            <option value="juridico">Jurídico</option>
                            <option value="resumidor">Resumidor</option>
                            <option value="sentimento">Análise de Sentimento</option>
                            <option value="extrator">Extrator</option>
                            <option value="tradutor">Tradutor</option>
                            <option value="classificador">Classificador</option>
                            <option value="gerador">Gerador</option>
                            <option value="sintetizador">Sintetizador</option>
                            <option value="formatador">Formatador</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Grid de Assistentes */}
            {filteredAssistentes.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredAssistentes.map((assistente) => (
                        <div
                            key={assistente.id}
                            className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow cursor-pointer"
                            onClick={() => navigate(`/assistentes/${assistente.id}/chat`)}
                        >
                            {/* Header */}
                            <div className="flex items-start justify-between mb-4">
                                <div className={`p-3 rounded-lg ${getIconColor(assistente.tipo)}`}>
                                    <Bot className="w-6 h-6" />
                                </div>
                                <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                                    {assistente.tipo}
                                </span>
                            </div>

                            {/* Conteúdo */}
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                {assistente.nome}
                            </h3>
                            <p className="text-sm text-blue-600 mb-3">
                                {assistente.area_juridica}
                            </p>
                            <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                                {assistente.descricao}
                            </p>

                            {/* Footer */}
                            <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                                <div className="flex items-center gap-1 text-sm text-gray-500">
                                    <MessageSquare className="w-4 h-4" />
                                    <span>{assistente.total_conversas || 0} conversas</span>
                                </div>
                                <ChevronRight className="w-5 h-5 text-gray-400" />
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                    <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Nenhum assistente encontrado
                    </h3>
                    <p className="text-gray-600 mb-4">
                        Tente ajustar os filtros de busca
                    </p>
                    <button
                        onClick={() => {
                            setSearchQuery('')
                            setSelectedArea('all')
                            setSelectedTipo('all')
                        }}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        Limpar Filtros
                    </button>
                </div>
            )}

            {/* Estatísticas */}
            {filteredAssistentes.length > 0 && (
                <div className="mt-6 bg-blue-50 rounded-lg border border-blue-200 p-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-blue-700">
                            <Filter className="w-5 h-5" />
                            <span className="font-medium">
                                Mostrando {filteredAssistentes.length} de {assistentes.length} assistentes
                            </span>
                        </div>
                        <Link
                            to="/admin/agents"
                            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                        >
                            Gerenciar assistentes →
                        </Link>
                    </div>
                </div>
            )}
        </AdminLayout>
    )
}
