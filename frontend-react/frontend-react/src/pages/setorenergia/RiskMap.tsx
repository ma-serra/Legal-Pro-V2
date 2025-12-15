import { useState, useEffect } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { MapPin, AlertCircle, TrendingUp, Filter } from 'lucide-react'
import api from '../../lib/api'

interface RiskData {
    comarca: string
    total_processos: number
    nivel_risco: 'baixo' | 'medio' | 'alto' | 'critico'
    valor_total: number
    taxa_sucesso: number
    latitude: number
    longitude: number
}

export default function RiskMap() {
    const [riskData, setRiskData] = useState<RiskData[]>([])
    const [loading, setLoading] = useState(true)
    const [selectedRisk, setSelectedRisk] = useState<string>('all')

    useEffect(() => {
        fetchRiskData()
    }, [])

    const fetchRiskData = async () => {
        try {
            const response = await api.get('/setorenergia/mapa-risco')
            setRiskData(response.data)
        } catch (error) {
            console.error('Error fetching risk data:', error)
        } finally {
            setLoading(false)
        }
    }

    const getRiskColor = (nivel: string) => {
        switch (nivel) {
            case 'baixo': return 'bg-green-500'
            case 'medio': return 'bg-yellow-500'
            case 'alto': return 'bg-orange-500'
            case 'critico': return 'bg-red-500'
            default: return 'bg-gray-500'
        }
    }

    const getRiskLabel = (nivel: string) => {
        switch (nivel) {
            case 'baixo': return 'Baixo'
            case 'medio': return 'Médio'
            case 'alto': return 'Alto'
            case 'critico': return 'Crítico'
            default: return 'Desconhecido'
        }
    }

    const filteredData = selectedRisk === 'all'
        ? riskData
        : riskData.filter(d => d.nivel_risco === selectedRisk)

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
                title="Mapa de Risco"
                description="Visualização de risco por região"
            />

            {/* Filtros */}
            <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
                <div className="flex items-center gap-4">
                    <Filter className="w-5 h-5 text-gray-600" />
                    <select
                        value={selectedRisk}
                        onChange={(e) => setSelectedRisk(e.target.value)}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="all">Todos os Níveis</option>
                        <option value="critico">Crítico</option>
                        <option value="alto">Alto</option>
                        <option value="medio">Médio</option>
                        <option value="baixo">Baixo</option>
                    </select>
                </div>
            </div>

            {/* Mapa Placeholder (Seria integrado com Google Maps ou Leaflet) */}
            <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
                <div className="bg-gray-100 rounded-lg h-96 flex items-center justify-center">
                    <div className="text-center">
                        <MapPin className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">
                            Mapa Interativo
                        </h3>
                        <p className="text-gray-600 mb-4">
                            Integração com Google Maps/Leaflet será adicionada
                        </p>
                        <p className="text-sm text-gray-500">
                            Visualização geográfica dos níveis de risco por comarca
                        </p>
                    </div>
                </div>
            </div>

            {/* Legenda */}
            <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Legenda de Risco</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="flex items-center gap-3">
                        <div className="w-4 h-4 rounded-full bg-green-500"></div>
                        <span className="text-sm text-gray-700">Baixo</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
                        <span className="text-sm text-gray-700">Médio</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="w-4 h-4 rounded-full bg-orange-500"></div>
                        <span className="text-sm text-gray-700">Alto</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="w-4 h-4 rounded-full bg-red-500"></div>
                        <span className="text-sm text-gray-700">Crítico</span>
                    </div>
                </div>
            </div>

            {/* Tabela de Dados */}
            <div className="bg-white rounded-lg border border-gray-200">
                <div className="p-4 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900">Dados por Comarca</h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Comarca
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Nível de Risco
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Processos
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Valor Total
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Taxa Sucesso
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {filteredData.map((item, index) => (
                                <tr key={index} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center gap-2">
                                            <MapPin className="w-4 h-4 text-gray-400" />
                                            <span className="text-sm font-medium text-gray-900">
                                                {item.comarca}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center gap-2">
                                            <div className={`w-3 h-3 rounded-full ${getRiskColor(item.nivel_risco)}`}></div>
                                            <span className="text-sm text-gray-700">
                                                {getRiskLabel(item.nivel_risco)}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        {item.total_processos}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        {new Intl.NumberFormat('pt-BR', {
                                            style: 'currency',
                                            currency: 'BRL',
                                            notation: 'compact'
                                        }).format(item.valor_total)}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center gap-2">
                                            <TrendingUp className={`w-4 h-4 ${item.taxa_sucesso >= 70 ? 'text-green-600' : 'text-orange-600'
                                                }`} />
                                            <span className="text-sm text-gray-900">
                                                {item.taxa_sucesso}%
                                            </span>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Informação Adicional */}
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
                    <div>
                        <h4 className="font-semibold text-blue-900 mb-1">
                            Sobre o Mapa de Risco
                        </h4>
                        <p className="text-sm text-blue-700">
                            O nível de risco é calculado com base no número de processos, valor em causa,
                            taxa de sucesso histórica e tempo médio de tramitação por comarca.
                        </p>
                    </div>
                </div>
            </div>
        </AdminLayout>
    )
}
