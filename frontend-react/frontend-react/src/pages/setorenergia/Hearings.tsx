import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { Calendar, Clock, MapPin, Users, FileSpreadsheet } from 'lucide-react'
import api from '../../lib/api'

interface Audiencia {
    id: number
    processo_numero: string
    processo_titulo: string
    data_audiencia: string
    hora: string
    tipo: string
    local: string
    comarca: string
    juiz: string
    status: 'agendada' | 'realizada' | 'cancelada' | 'remarcada'
    observacoes: string
}

export default function Hearings() {
    const navigate = useNavigate()
    const [audiencias, setAudiencias] = useState<Audiencia[]>([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState<string>('all')
    const [exporting, setExporting] = useState(false)

    useEffect(() => {
        fetchAudiencias()
    }, [])

    const fetchAudiencias = async () => {
        try {
            const response = await api.get('/setorenergia/api/audiencias')
            setAudiencias(response.data)
        } catch (error) {
            console.error('Error fetching audiências:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleExport = async () => {
        setExporting(true)
        try {
            const response = await api.post('/setorenergia/api/export/audiencias/excel', {}, {
                responseType: 'blob'
            })
            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `audiencias_${new Date().toISOString().split('T')[0]}.xlsx`)
            document.body.appendChild(link)
            link.click()
            link.remove()
        } catch (error) {
            console.error('Error exporting:', error)
            alert('Erro ao exportar audiências')
        } finally {
            setExporting(false)
        }
    }

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'agendada': return 'bg-blue-100 text-blue-800'
            case 'realizada': return 'bg-green-100 text-green-800'
            case 'cancelada': return 'bg-red-100 text-red-800'
            case 'remarcada': return 'bg-yellow-100 text-yellow-800'
            default: return 'bg-gray-100 text-gray-800'
        }
    }

    const filteredAudiencias = filter === 'all'
        ? audiencias
        : audiencias.filter(a => a.status === filter)

    // Agrupar por mês
    const audienciasPorMes = filteredAudiencias.reduce((acc, audiencia) => {
        const mes = new Date(audiencia.data_audiencia).toLocaleDateString('pt-BR', {
            year: 'numeric',
            month: 'long'
        })
        if (!acc[mes]) {
            acc[mes] = []
        }
        acc[mes].push(audiencia)
        return acc
    }, {} as Record<string, Audiencia[]>)

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
                title="Gestão de Audiências"
                description="Calendário e gerenciamento de audiências do setor energia"
                action={
                    <button
                        onClick={handleExport}
                        disabled={exporting}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                    >
                        <FileSpreadsheet className="w-4 h-4" />
                        {exporting ? 'Exportando...' : 'Exportar Excel'}
                    </button>
                }
            />

            {/* Estatísticas */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                <div className="bg-white p-6 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600 mb-1">Total</p>
                            <p className="text-3xl font-bold text-gray-900">{audiencias.length}</p>
                        </div>
                        <Calendar className="w-10 h-10 text-blue-600" />
                    </div>
                </div>
                <div className="bg-white p-6 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600 mb-1">Agendadas</p>
                            <p className="text-3xl font-bold text-blue-600">
                                {audiencias.filter(a => a.status === 'agendada').length}
                            </p>
                        </div>
                        <Clock className="w-10 h-10 text-blue-600" />
                    </div>
                </div>
                <div className="bg-white p-6 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600 mb-1">Realizadas</p>
                            <p className="text-3xl font-bold text-green-600">
                                {audiencias.filter(a => a.status === 'realizada').length}
                            </p>
                        </div>
                        <Users className="w-10 h-10 text-green-600" />
                    </div>
                </div>
                <div className="bg-white p-6 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600 mb-1">Próximos 7 dias</p>
                            <p className="text-3xl font-bold text-orange-600">
                                {audiencias.filter(a => {
                                    const diff = new Date(a.data_audiencia).getTime() - new Date().getTime()
                                    return diff > 0 && diff < 7 * 24 * 60 * 60 * 1000
                                }).length}
                            </p>
                        </div>
                        <Calendar className="w-10 h-10 text-orange-600" />
                    </div>
                </div>
            </div>

            {/* Filtros */}
            <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
                <div className="flex gap-2">
                    <button
                        onClick={() => setFilter('all')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium ${filter === 'all'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        Todas
                    </button>
                    <button
                        onClick={() => setFilter('agendada')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium ${filter === 'agendada'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        Agendadas
                    </button>
                    <button
                        onClick={() => setFilter('realizada')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium ${filter === 'realizada'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        Realizadas
                    </button>
                    <button
                        onClick={() => setFilter('remarcada')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium ${filter === 'remarcada'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        Remarcadas
                    </button>
                </div>
            </div>

            {/* Lista de Audiências por Mês */}
            <div className="space-y-6">
                {Object.entries(audienciasPorMes).map(([mes, audienciasMes]) => (
                    <div key={mes} className="bg-white rounded-lg border border-gray-200">
                        <div className="p-4 border-b border-gray-200 bg-gray-50">
                            <h3 className="font-semibold text-gray-900 capitalize">{mes}</h3>
                            <p className="text-sm text-gray-600">{audienciasMes.length} audiências</p>
                        </div>
                        <div className="divide-y divide-gray-100">
                            {audienciasMes.map((audiencia) => (
                                <div
                                    key={audiencia.id}
                                    className="p-4 hover:bg-gray-50 cursor-pointer"
                                    onClick={() => navigate(`/processos/${audiencia.id}`)}
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-3 mb-2">
                                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                                    <Calendar className="w-4 h-4" />
                                                    <span>{new Date(audiencia.data_audiencia).toLocaleDateString('pt-BR')}</span>
                                                </div>
                                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                                    <Clock className="w-4 h-4" />
                                                    <span>{audiencia.hora}</span>
                                                </div>
                                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(audiencia.status)}`}>
                                                    {audiencia.status}
                                                </span>
                                            </div>
                                            <h4 className="font-medium text-gray-900 mb-1">{audiencia.processo_titulo}</h4>
                                            <p className="text-sm text-gray-600 mb-2">
                                                Processo Nº {audiencia.processo_numero}
                                            </p>
                                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                                                <div>
                                                    <span className="text-gray-600">Tipo:</span>
                                                    <p className="font-medium text-gray-900">{audiencia.tipo}</p>
                                                </div>
                                                <div>
                                                    <span className="text-gray-600">Local:</span>
                                                    <div className="flex items-center gap-1">
                                                        <MapPin className="w-3 h-3 text-gray-400" />
                                                        <p className="font-medium text-gray-900">{audiencia.local}</p>
                                                    </div>
                                                </div>
                                                <div>
                                                    <span className="text-gray-600">Juiz:</span>
                                                    <p className="font-medium text-gray-900">{audiencia.juiz}</p>
                                                </div>
                                            </div>
                                            {audiencia.observacoes && (
                                                <p className="text-sm text-gray-600 mt-2 italic">
                                                    {audiencia.observacoes}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}

                {filteredAudiencias.length === 0 && (
                    <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                        <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">
                            Nenhuma audiência encontrada
                        </h3>
                        <p className="text-gray-600">
                            Não há audiências {filter !== 'all' ? `com status "${filter}"` : 'cadastradas'}
                        </p>
                    </div>
                )}
            </div>
        </AdminLayout>
    )
}
