import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader, StatCard } from '../../components/ui/AdminComponents'
import { Database, Activity, HardDrive, AlertTriangle } from 'lucide-react'

export default function DatabaseStatus() {
    // Mock data - replace with real API calls
    const dbStats = {
        status: 'healthy',
        uptime: '15d 8h 32m',
        connections: { active: 8, max: 100 },
        size: { used: 2.4, total: 10 },
        tables: 45,
        indexes: 123
    }

    return (
        <AdminLayout>
            <PageHeader
                title="Status do Banco de Dados"
                description="PostgreSQL Railway Database"
            />

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard
                    title="Status"
                    value="Online"
                    icon={Database}
                />
                <StatCard
                    title="Uptime"
                    value={dbStats.uptime}
                    icon={Activity}
                />
                <StatCard
                    title="Conexões"
                    value={`${dbStats.connections.active}/${dbStats.connections.max}`}
                    icon={Activity}
                />
                <StatCard
                    title="Tamanho"
                    value={`${dbStats.size.used}/${dbStats.size.total} GB`}
                    icon={HardDrive}
                />
            </div>

            {/* Database Info */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Tabelas</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-gray-600">Total de tabelas</span>
                            <span className="font-medium">{dbStats.tables}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-600">Índices</span>
                            <span className="font-medium">{dbStats.indexes}</span>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-gray-600">Query médio</span>
                            <span className="font-medium">45ms</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-600">Cache hit rate</span>
                            <span className="font-medium">98.5%</span>
                        </div>
                    </div>
                </div>
            </div>
        </AdminLayout>
    )
}
