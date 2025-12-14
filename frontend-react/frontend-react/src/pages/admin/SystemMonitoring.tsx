import { useEffect, useState } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { StatCard, PageHeader } from '../../components/ui/AdminComponents'
import {
    Activity,
    Cpu,
    HardDrive,
    Network,
    Clock,
    AlertTriangle
} from 'lucide-react'
import api from '../../lib/api'

interface SystemMetrics {
    cpu: number
    memory: number
    disk: number
    network: number
    uptime: string
    requests24h: number
}

export default function SystemMonitoring() {
    const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchMetrics()
        const interval = setInterval(fetchMetrics, 5000) // Update every 5s
        return () => clearInterval(interval)
    }, [])

    const fetchMetrics = async () => {
        try {
            const response = await api.get('/api/admin/api/admin/vectorial/metrics')
            setMetrics({
                cpu: Math.random() * 100,
                memory: Math.random() * 100,
                disk: Math.random() * 100,
                network: Math.random() * 100,
                uptime: '5d 12h 34m',
                requests24h: Math.floor(Math.random() * 10000),
            })
        } catch (error) {
            console.error('Error fetching metrics:', error)
        } finally {
            setLoading(false)
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
                title="Monitoramento do Sistema"
                description="Métricas em tempo real do servidor e serviços"
            />

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard
                    title="CPU"
                    value={`${metrics?.cpu.toFixed(1)}%`}
                    icon={Cpu}
                />
                <StatCard
                    title="Memória"
                    value={`${metrics?.memory.toFixed(1)}%`}
                    icon={HardDrive}
                />
                <StatCard
                    title="Disco"
                    value={`${metrics?.disk.toFixed(1)}%`}
                    icon={HardDrive}
                />
                <StatCard
                    title="Rede"
                    value={`${metrics?.network.toFixed(1)} MB/s`}
                    icon={Network}
                />
            </div>

            {/* System Info */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Uptime */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <Clock className="w-6 h-6 text-green-600" />
                        <h2 className="text-lg font-semibold text-gray-900">Uptime</h2>
                    </div>
                    <p className="text-3xl font-bold text-gray-900">{metrics?.uptime}</p>
                    <p className="text-sm text-gray-600 mt-2">Sistema estável e operacional</p>
                </div>

                {/* Requests */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <Activity className="w-6 h-6 text-blue-600" />
                        <h2 className="text-lg font-semibold text-gray-900">Requisições (24h)</h2>
                    </div>
                    <p className="text-3xl font-bold text-gray-900">{metrics?.requests24h.toLocaleString()}</p>
                    <p className="text-sm text-gray-600 mt-2">Média de 416 req/hora</p>
                </div>
            </div>

            {/* Alert */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                <div>
                    <h3 className="font-medium text-yellow-900">Aviso</h3>
                    <p className="text-sm text-yellow-800 mt-1">
                        Métricas são simuladas para demonstração. Configure monitoramento real para produção.
                    </p>
                </div>
            </div>
        </AdminLayout>
    )
}
