import { useState, useEffect } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { MapPin, Navigation, Filter, Layers } from 'lucide-react'
import api from '../../lib/api'

interface ProcessLocation {
    id: number
    numero: string
    titulo: string
    comarca: string
    endereco: string
    latitude: number
    longitude: number
    status: string
    valor_causa: number
    nivel_prioridade: 'baixo' | 'medio' | 'alto'
}

export default function Geolocation() {
    const [locations, setLocations] = useState<ProcessLocation[]>([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState<string>('all')
    const [selectedLocation, setSelectedLocation] = useState<ProcessLocation | null>(null)

    useEffect(() => {
        fetchLocations()
    }, [])

    const fetchLocations = async () => {
        try {
            const response = await api.get('/setorenergia/geolocalizacao')
            setLocations(response.data)
        } catch (error) {
            console.error('Error fetching locations:', error)
        } finally {
            setLoading(false)
        }
    }

    const filteredLocations = filter === 'all'
        ? locations
        : locations.filter(l => l.nivel_prioridade === filter)

    const getPriorityColor = (nivel: string) => {
        switch (nivel) {
            case 'alto': return 'bg-red-500'
            case 'medio': return 'bg-yellow-500'
            case 'baixo': return 'bg-green-500'
            default: return 'bg-gray-500'
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
                title="Geolocalização de Processos"
                description="Visualização geográfica dos processos por localização"
            />

            {/* Filtros e Controles */}
            <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Filter className="w-5 h-5 text-gray-600" />
                        <select
                            value={filter}
                            onChange={(e) => setFilter(e.target.value)}
                            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="all">Todas as Prioridades</option>
                            <option value="alto">Alta</option>
                            <option value="medio">Média</option>
                            <option value="baixo">Baixa</option>
                        </select>
                    </div>
                    <div className="flex items-center gap-2">
                        <Layers className="w-5 h-5 text-gray-600" />
                        <span className="text-sm text-gray-600">{filteredLocations.length} localizações</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Mapa (Placeholder) */}
                <div className="lg:col-span-2">
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <div className="bg-gray-100 rounded-lg h-[600px] flex items-center justify-center">
                            <div className="text-center">
                                <MapPin className="w-20 h-20 text-gray-400 mx-auto mb-4" />
                                <h3 className="text-xl font-medium text-gray-900 mb-3">
                                    Mapa Interativo
                                </h3>
                                <p className="text-gray-600 mb-6 max-w-md mx-auto">
                                    Integração com Google Maps ou Leaflet será adicionada para visualização
                                    interativa dos processos por localização geográfica
                                </p>
                                <div className="flex justify-center gap-4">
                                    <div className="flex items-center gap-2">
                                        <div className="w-3 h-3 rounded-full bg-red-500"></div>
                                        <span className="text-sm text-gray-700">Alta Prioridade</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                                        <span className="text-sm text-gray-700">Média Prioridade</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-3 h-3 rounded-full bg-green-500"></div>
                                        <span className="text-sm text-gray-700">Baixa Prioridade</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Lista de Localizações */}
                <div className="lg:col-span-1">
                    <div className="bg-white rounded-lg border border-gray-200">
                        <div className="p-4 border-b border-gray-200">
                            <h3 className="font-semibold text-gray-900">Processos</h3>
                        </div>
                        <div className="max-h-[600px] overflow-y-auto">
                            {filteredLocations.map((location) => (
                                <div
                                    key={location.id}
                                    className={`p-4 border-b border-gray-100 cursor-pointer transition-colors ${selectedLocation?.id === location.id ? 'bg-blue-50' : 'hover:bg-gray-50'
                                        }`}
                                    onClick={() => setSelectedLocation(location)}
                                >
                                    <div className="flex items-start gap-3">
                                        <div className={`w-3 h-3 rounded-full mt-1.5 flex-shrink-0 ${getPriorityColor(location.nivel_prioridade)}`}></div>
                                        <div className="flex-1 min-w-0">
                                            <p className="font-medium text-gray-900 text-sm truncate">
                                                {location.titulo}
                                            </p>
                                            <p className="text-xs text-gray-600 mb-1">
                                                Nº {location.numero}
                                            </p>
                                            <div className="flex items-center gap-1 text-xs text-gray-500">
                                                <MapPin className="w-3 h-3" />
                                                <span className="truncate">{location.comarca}</span>
                                            </div>
                                            <p className="text-xs text-gray-900 mt-1 font-medium">
                                                {new Intl.NumberFormat('pt-BR', {
                                                    style: 'currency',
                                                    currency: 'BRL',
                                                    notation: 'compact'
                                                }).format(location.valor_causa)}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Detalhes do Processo Selecionado */}
                    {selectedLocation && (
                        <div className="mt-4 bg-white rounded-lg border border-gray-200 p-4">
                            <h4 className="font-semibold text-gray-900 mb-3">Detalhes</h4>
                            <div className="space-y-3 text-sm">
                                <div>
                                    <span className="text-gray-600">Número:</span>
                                    <p className="font-medium text-gray-900">{selectedLocation.numero}</p>
                                </div>
                                <div>
                                    <span className="text-gray-600">Comarca:</span>
                                    <p className="font-medium text-gray-900">{selectedLocation.comarca}</p>
                                </div>
                                <div>
                                    <span className="text-gray-600">Endereço:</span>
                                    <p className="font-medium text-gray-900">{selectedLocation.endereco}</p>
                                </div>
                                <div>
                                    <span className="text-gray-600">Status:</span>
                                    <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                                        {selectedLocation.status}
                                    </span>
                                </div>
                                <div>
                                    <span className="text-gray-600">Coordenadas:</span>
                                    <p className="font-mono text-xs text-gray-700">
                                        {selectedLocation.latitude}, {selectedLocation.longitude}
                                    </p>
                                </div>
                                <button className="w-full mt-2 px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2">
                                    <Navigation className="w-4 h-4" />
                                    Abrir no Maps
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Estatísticas por Região */}
            <div className="mt-6 bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Estatísticas por Região</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {['Porto Alegre', 'Caxias do Sul', 'Pelotas', 'Santa Maria'].map((cidade) => {
                        const count = locations.filter(l => l.comarca.includes(cidade)).length
                        const total = locations.filter(l => l.comarca.includes(cidade))
                            .reduce((sum, l) => sum + l.valor_causa, 0)

                        return (
                            <div key={cidade} className="bg-gray-50 rounded-lg p-4">
                                <h4 className="font-medium text-gray-900 mb-2">{cidade}</h4>
                                <p className="text-2xl font-bold text-blue-600 mb-1">{count}</p>
                                <p className="text-xs text-gray-600">
                                    {new Intl.NumberFormat('pt-BR', {
                                        style: 'currency',
                                        currency: 'BRL',
                                        notation: 'compact'
                                    }).format(total)}
                                </p>
                            </div>
                        )
                    })}
                </div>
            </div>
        </AdminLayout>
    )
}
