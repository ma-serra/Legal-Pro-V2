/**
 * ProcessoStats - Dashboard de Estatísticas
 * Métricas e KPIs de processos
 */
import { useState, useEffect } from 'react';
import api from '../../lib/api';
import { Gavel, TrendingUp, DollarSign, AlertCircle, BarChart3, PieChart } from 'lucide-react';

export default function ProcessoStats() {
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const response = await api.get('/api/processos/estatisticas');
            setStats(response.data || {});
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map(i => (
                    <div key={i} className="animate-pulse bg-accent rounded-xl h-32"></div>
                ))}
            </div>
        );
    }

    const cards = [
        {
            title: 'Total de Processos',
            value: stats?.total || 0,
            icon: Gavel,
            color: 'blue',
            trend: '+12%'
        },
        {
            title: 'Valor Total',
            value: new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL',
                notation: 'compact'
            }).format(stats?.valor_total || 0),
            icon: DollarSign,
            color: 'green',
            trend: '+8%'
        },
        {
            title: 'Processos Ativos',
            value: stats?.ativos || 0,
            icon: TrendingUp,
            color: 'orange',
            trend: '+5%'
        },
        {
            title: 'Alto Risco',
            value: stats?.alto_risco || 0,
            icon: AlertCircle,
            color: 'red',
            trend: '-3%'
        }
    ];

    return (
        <div className="space-y-6">
            {/* Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {cards.map((card, index) => (
                    <div
                        key={index}
                        className={`bg-gradient-to-br from-${card.color}-500/10 to-${card.color}-600/5 border border-${card.color}-500/20 rounded-xl p-6 hover:shadow-xl hover:scale-105 transition-all duration-300`}
                    >
                        <div className="flex items-start justify-between mb-4">
                            <div className={`p-3 bg-${card.color}-500/20 rounded-lg`}>
                                <card.icon className={`w-6 h-6 text-${card.color}-400`} />
                            </div>
                            <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs font-medium">
                                {card.trend}
                            </span>
                        </div>

                        <div>
                            <p className="text-sm text-muted-foreground mb-1">{card.title}</p>
                            <p className="text-3xl font-bold">{card.value}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Distribuição por Natureza */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div className="bg-card border border-border rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <PieChart className="w-5 h-5 text-primary" />
                        <h3 className="font-semibold">Distribuição por Natureza</h3>
                    </div>

                    <div className="space-y-4">
                        {[
                            { natureza: 'Tributário', count: stats?.tributario || 0, color: 'blue' },
                            { natureza: 'Trabalhista', count: stats?.trabalhista || 0, color: 'orange' },
                            { natureza: 'Cível', count: stats?.civel || 0, color: 'purple' }
                        ].map(item => {
                            const total = (stats?.tributario || 0) + (stats?.trabalhista || 0) + (stats?.civel || 0);
                            const percentage = total > 0 ? (item.count / total * 100).toFixed(1) : '0';

                            return (
                                <div key={item.natureza}>
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm font-medium">{item.natureza}</span>
                                        <span className="text-sm text-muted-foreground">
                                            {item.count} ({percentage}%)
                                        </span>
                                    </div>
                                    <div className="w-full bg-accent rounded-full h-2">
                                        <div
                                            className={`bg-${item.color}-500 rounded-full h-2 transition-all duration-500`}
                                            style={{ width: `${percentage}%` }}
                                        />
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                <div className="bg-card border border-border rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <BarChart3 className="w-5 h-5 text-primary" />
                        <h3 className="font-semibold">Status dos Processos</h3>
                    </div>

                    <div className="space-y-4">
                        {[
                            { status: 'Ativos', count: stats?.ativos || 0, color: 'green' },
                            { status: 'Arquivados', count: stats?.arquivados || 0, color: 'gray' },
                            { status: 'Suspensos', count: stats?.suspensos || 0, color: 'yellow' }
                        ].map(item => {
                            const total = (stats?.ativos || 0) + (stats?.arquivados || 0) + (stats?.suspensos || 0);
                            const percentage = total > 0 ? (item.count / total * 100).toFixed(1) : '0';

                            return (
                                <div key={item.status}>
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm font-medium">{item.status}</span>
                                        <span className="text-sm text-muted-foreground">
                                            {item.count} ({percentage}%)
                                        </span>
                                    </div>
                                    <div className="w-full bg-accent rounded-full h-2">
                                        <div
                                            className={`bg-${item.color}-500 rounded-full h-2 transition-all duration-500`}
                                            style={{ width: `${percentage}%` }}
                                        />
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}
