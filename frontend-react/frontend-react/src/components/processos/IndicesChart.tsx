/**
 * IndicesChart - Gráfico de Histórico de Índices
 * Visualização temporal com Recharts
 */
import { useState, useEffect } from 'react';
import { HistoricoIndice } from '../../types/processos';
import api from '../../lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Calendar } from 'lucide-react';

interface IndicesChartProps {
    indiceId: number;
    indiceName: string;
}

export default function IndicesChart({ indiceId, indiceName }: IndicesChartProps) {
    const [historico, setHistorico] = useState<HistoricoIndice[]>([]);
    const [loading, setLoading] = useState(true);
    const [periodo, setPeriodo] = useState(90); // dias

    useEffect(() => {
        fetchHistorico();
    }, [indiceId, periodo]);

    const fetchHistorico = async () => {
        setLoading(true);
        try {
            const dataInicio = new Date();
            dataInicio.setDate(dataInicio.getDate() - periodo);

            const response = await api.get(
                `/api/atualizacao-monetaria/indices/${indiceId}/historico`,
                {
                    params: {
                        data_inicio: dataInicio.toISOString().split('T')[0],
                        limite: 100
                    }
                }
            );

            setHistorico((response.data || []).reverse());
        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
        } finally {
            setLoading(false);
        }
    };

    const chartData = historico.map(h => ({
        data: new Date(h.data_referencia).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
        valor: parseFloat(h.valor.toString())
    }));

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary/20 rounded-lg">
                        <TrendingUp className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                        <h3 className="font-semibold">Histórico {indiceName}</h3>
                        <p className="text-sm text-muted-foreground">Últimos {periodo} dias</p>
                    </div>
                </div>

                {/* Seletor de Período */}
                <div className="flex gap-2">
                    {[30, 90, 180, 365].map(dias => (
                        <button
                            key={dias}
                            onClick={() => setPeriodo(dias)}
                            className={`px-4 py-2 rounded-lg transition-colors ${periodo === dias
                                    ? 'bg-primary text-white'
                                    : 'bg-accent hover:bg-accent/80'
                                }`}
                        >
                            {dias}d
                        </button>
                    ))}
                </div>
            </div>

            {/* Chart */}
            {loading ? (
                <div className="animate-pulse bg-accent rounded-xl h-80"></div>
            ) : chartData.length === 0 ? (
                <div className="bg-accent rounded-xl p-12 text-center">
                    <Calendar className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">Sem dados para o período selecionado</p>
                </div>
            ) : (
                <div className="bg-card border border-border rounded-xl p-6">
                    <ResponsiveContainer width="100%" height={350}>
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                            <XAxis
                                dataKey="data"
                                stroke="#888"
                                style={{ fontSize: '12px' }}
                            />
                            <YAxis
                                stroke="#888"
                                style={{ fontSize: '12px' }}
                                tickFormatter={(value) => `${value}%`}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1f1f1f',
                                    border: '1px solid #333',
                                    borderRadius: '8px'
                                }}
                                formatter={(value: any) => [`${value}%`, indiceName]}
                            />
                            <Legend />
                            <Line
                                type="monotone"
                                dataKey="valor"
                                name={indiceName}
                                stroke="#3b82f6"
                                strokeWidth={2}
                                dot={{ fill: '#3b82f6', r: 3 }}
                                activeDot={{ r: 5 }}
                            />
                        </LineChart>
                    </ResponsiveContainer>

                    {/* Stats */}
                    <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-border">
                        <div className="text-center">
                            <p className="text-sm text-muted-foreground mb-1">Média</p>
                            <p className="text-xl font-bold text-primary">
                                {(chartData.reduce((acc, d) => acc + d.valor, 0) / chartData.length).toFixed(2)}%
                            </p>
                        </div>
                        <div className="text-center">
                            <p className="text-sm text-muted-foreground mb-1">Mínima</p>
                            <p className="text-xl font-bold text-green-400">
                                {Math.min(...chartData.map(d => d.valor)).toFixed(2)}%
                            </p>
                        </div>
                        <div className="text-center">
                            <p className="text-sm text-muted-foreground mb-1">Máxima</p>
                            <p className="text-xl font-bold text-red-400">
                                {Math.max(...chartData.map(d => d.valor)).toFixed(2)}%
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
