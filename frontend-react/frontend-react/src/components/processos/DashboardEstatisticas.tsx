import { useState, useEffect } from 'react';
import {
    PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line
} from 'recharts';
import {
    TrendingUp, DollarSign, Scale, Gavel, AlertTriangle, Users, Calendar, Activity
} from 'lucide-react';
import api from '../../lib/api';

// Cores do Sistema
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ef4444'];
const NATUREZA_COLORS: Record<string, string> = {
    '1': '#3b82f6', // Tributário - Azul
    '2': '#f97316', // Trabalhista - Laranja
    '3': '#a855f7', // Cível - Roxo
    '4': '#14b8a6', // Previdenciário - Teal
    '10': '#ef4444', // Penal - Vermelho
    '14': '#eab308', // Administrativo - Amarelo
    '15': '#6366f1', // Constitucional - Indigo
};

const NATUREZA_NAMES: Record<string, string> = {
    '1': 'Tributário',
    '2': 'Trabalhista',
    '3': 'Cível',
    '4': 'Previdenciário',
    '10': 'Penal',
    '14': 'Administrativo',
    '15': 'Constitucional',
};

interface Estatisticas {
    total_processos: number;
    por_natureza: Record<string, number>;
    por_status: Record<string, number>;
    por_risco: Record<string, number>;
    valores_financeiros: {
        total_valor_causa: number;
        total_valor_envolvido: number;
        total_contingencia: number;
        media_valor_causa: number;
    };
    por_ano: Record<string, number>;
}

export default function DashboardEstatisticas() {
    const [stats, setStats] = useState<Estatisticas | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        carregarEstatisticas();
    }, []);

    const carregarEstatisticas = async () => {
        try {
            const response = await api.get('/api/processos/estatisticas');
            setStats(response.data);
        } catch (err) {
            console.error('Erro ao carregar estatísticas:', err);
            console.error('Erro ao carregar estatísticas:', err);
            setError('Erro ao carregar estatísticas. Verifique a conexão com o servidor.');
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(value);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent"></div>
            </div>
        );
    }

    if (!stats) return null;

    // Transformação de dados para Recharts
    const dataNatureza = Object.entries(stats.por_natureza).map(([key, value]) => ({
        name: NATUREZA_NAMES[key] || `Natureza ${key}`,
        value: value,
        key: key
    }));

    const dataAno = Object.entries(stats.por_ano)
        .sort((a, b) => parseInt(a[0]) - parseInt(b[0]))
        .map(([ano, qtd]) => ({
            ano,
            processos: qtd
        }));

    const dataRisco = Object.entries(stats.por_risco).map(([key, value]) => ({
        name: key === '1' ? 'Provável' : key === '2' ? 'Possível' : 'Remoto',
        value: value
    }));

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {error && (
                <div className="bg-yellow-500/10 border border-yellow-500/30 text-yellow-500 p-3 rounded-lg flex items-center gap-2 text-sm">
                    <AlertTriangle className="w-4 h-4" />
                    {error}
                </div>
            )}

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-card border border-border p-6 rounded-xl hover:shadow-lg transition-all">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">Total Processos</p>
                            <h3 className="text-3xl font-bold mt-2">{stats.total_processos}</h3>
                        </div>
                        <div className="p-3 bg-blue-500/10 rounded-lg">
                            <Scale className="w-6 h-6 text-blue-500" />
                        </div>
                    </div>
                    <div className="mt-4 flex items-center gap-2 text-xs text-green-500">
                        <TrendingUp className="w-3 h-3" />
                        <span>+12% este mês</span>
                    </div>
                </div>

                <div className="bg-card border border-border p-6 rounded-xl hover:shadow-lg transition-all">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">Valor Total Causa</p>
                            <h3 className="text-2xl font-bold mt-2 text-green-600">
                                {formatCurrency(stats.valores_financeiros.total_valor_causa)}
                            </h3>
                        </div>
                        <div className="p-3 bg-green-500/10 rounded-lg">
                            <DollarSign className="w-6 h-6 text-green-600" />
                        </div>
                    </div>
                    <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
                        <span>Ticket Médio: {formatCurrency(stats.valores_financeiros.media_valor_causa)}</span>
                    </div>
                </div>

                <div className="bg-card border border-border p-6 rounded-xl hover:shadow-lg transition-all">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">Contingência</p>
                            <h3 className="text-2xl font-bold mt-2 text-orange-600">
                                {formatCurrency(stats.valores_financeiros.total_contingencia)}
                            </h3>
                        </div>
                        <div className="p-3 bg-orange-500/10 rounded-lg">
                            <Activity className="w-6 h-6 text-orange-600" />
                        </div>
                    </div>
                    <div className="mt-4 text-xs text-muted-foreground">
                        <span>Recomendado provisionar</span>
                    </div>
                </div>

                <div className="bg-card border border-border p-6 rounded-xl hover:shadow-lg transition-all">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">Ativos</p>
                            <h3 className="text-3xl font-bold mt-2">{stats.por_status['1'] || 0}</h3>
                        </div>
                        <div className="p-3 bg-purple-500/10 rounded-lg">
                            <Gavel className="w-6 h-6 text-purple-600" />
                        </div>
                    </div>
                    <p className="mt-4 text-xs text-muted-foreground">
                        {stats.por_status['2'] || 0} Arquivados | {stats.por_status['3'] || 0} Suspensos
                    </p>
                </div>
            </div>

            {/* Charts Row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Distribuição por Natureza */}
                <div className="bg-card border border-border p-6 rounded-xl">
                    <h3 className="font-semibold text-lg mb-6 flex items-center gap-2">
                        <Scale className="w-5 h-5 text-primary" />
                        Distribuição por Natureza
                    </h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={dataNatureza}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={(props: any) => `${props.name} ${(props.percent * 100).toFixed(0)}%`}
                                    outerRadius={100}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {dataNatureza.map((entry, index) => (
                                        <Cell
                                            key={`cell-${index}`}
                                            fill={NATUREZA_COLORS[entry.key as keyof typeof NATUREZA_COLORS] || COLORS[index % COLORS.length]}
                                        />
                                    ))}
                                </Pie>
                                <Tooltip formatter={(value) => [value, 'Processos']} />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Evolução Temporal */}
                <div className="bg-card border border-border p-6 rounded-xl">
                    <h3 className="font-semibold text-lg mb-6 flex items-center gap-2">
                        <Calendar className="w-5 h-5 text-primary" />
                        Evolução de Processos (Ano)
                    </h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={dataAno}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="ano" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar
                                    dataKey="processos"
                                    name="Novos Processos"
                                    fill="#3b82f6"
                                    radius={[4, 4, 0, 0]}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Charts Row 2 - Risco e Valores */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Risco */}
                <div className="bg-card border border-border p-6 rounded-xl">
                    <h3 className="font-semibold text-lg mb-6 flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-primary" />
                        Classificação de Risco
                    </h3>
                    <div className="h-[250px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={dataRisco} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                                <XAxis type="number" />
                                <YAxis dataKey="name" type="category" width={100} />
                                <Tooltip />
                                <Legend />
                                <Bar
                                    dataKey="value"
                                    name="Processos"
                                    fill="#f59e0b"
                                    radius={[0, 4, 4, 0]}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Info Card */}
                <div className="bg-gradient-to-br from-indigo-900 to-purple-900 p-6 rounded-xl text-white flex flex-col justify-center">
                    <h3 className="text-2xl font-bold mb-4">Insights Financeiros</h3>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center border-b border-white/10 pb-2">
                            <span className="text-indigo-200">Valor Envolvido Total</span>
                            <span className="font-semibold text-xl">
                                {formatCurrency(stats.valores_financeiros.total_valor_envolvido)}
                            </span>
                        </div>
                        <div className="flex justify-between items-center border-b border-white/10 pb-2">
                            <span className="text-indigo-200">Risco Financeiro (Contingência)</span>
                            <span className="font-semibold text-xl text-orange-300">
                                {formatCurrency(stats.valores_financeiros.total_contingencia)}
                            </span>
                        </div>
                        <div className="flex justify-between items-center pt-2">
                            <span className="text-indigo-200">Eficiência Jurídica</span>
                            <span className="px-3 py-1 bg-green-500/20 text-green-300 rounded-full text-sm font-medium">
                                Alta Performance
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
