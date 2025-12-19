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

    // Função para converter valor baseado no tipo de índice
    const converterValor = (valor: number): number => {
        // SELIC e CDI vêm como taxa diária - converter para anual
        if (indiceName === 'SELIC' || indiceName === 'CDI' || indiceName === 'SELIC-EFETIVA') {
            return valor * 252; // Taxa diária * 252 dias úteis
        }
        return valor;
    };

    const formatarLabel = (): string => {
        if (indiceName === 'SELIC' || indiceName === 'CDI' || indiceName === 'SELIC-EFETIVA' || indiceName === 'TJLP') {
            return '% a.a.';
        }
        if (indiceName.includes('DOLAR') || indiceName.includes('EURO')) {
            return 'R$';
        }
        return '% mês';
    };

    const chartData = historico.map(h => ({
        data: new Date(h.data_referencia).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
        valor: converterValor(parseFloat(h.valor.toString()))
    }));

    const media = chartData.length > 0 ? chartData.reduce((acc, d) => acc + d.valor, 0) / chartData.length : 0;
    const minimo = chartData.length > 0 ? Math.min(...chartData.map(d => d.valor)) : 0;
    const maximo = chartData.length > 0 ? Math.max(...chartData.map(d => d.valor)) : 0;

    return (
        <div className="space-y-4">
            {/* Header com Seletor de Período */}
            <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary/20 rounded-lg">
                        <TrendingUp className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                        <h3 className="font-semibold">Histórico {indiceName}</h3>
                        <p className="text-sm text-muted-foreground">Últimos {periodo} dias</p>
                    </div>
                </div>

                <div className="flex gap-2">
                    {[30, 90, 180, 365].map(dias => (
                        <button
                            key={dias}
                            onClick={() => setPeriodo(dias)}
                            className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${periodo === dias
                                    ? 'bg-primary text-white'
                                    : 'bg-accent hover:bg-accent/80'
                                }`}
                        >
                            {dias}d
                        </button>
                    ))}
                </div>
            </div>

            {/* Chart Container */}
            {loading ? (
                <div className="animate-pulse bg-accent rounded-xl h-80"></div>
            ) : chartData.length === 0 ? (
                <div className="bg-accent rounded-xl p-12 text-center">
                    <Calendar className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">Sem dados para o período selecionado</p>
                </div>
            ) : (
                <div className="bg-card border border-border rounded-xl p-4">
                    <div style={{ width: '100%', height: 300 }}>
                        <ResponsiveContainer>
                            <LineChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                <XAxis
                                    dataKey="data"
                                    stroke="#888"
                                    style={{ fontSize: '11px' }}
                                    tickMargin={10}
                                />
                                <YAxis
                                    stroke="#888"
                                    style={{ fontSize: '11px' }}
                                    tickFormatter={(value) => `${value.toFixed(2)}`}
                                    domain={['auto', 'auto']}
                                    width={60}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1f1f1f',
                                        border: '1px solid #333',
                                        borderRadius: '8px'
                                    }}
                                    formatter={(value: any) => [`${parseFloat(value).toFixed(2)} ${formatarLabel()}`, indiceName]}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="valor"
                                    name={indiceName}
                                    stroke="#3b82f6"
                                    strokeWidth={2}
                                    dot={{ fill: '#3b82f6', r: 2 }}
                                    activeDot={{ r: 5 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Stats - Separados claramente do gráfico */}
                    <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-border">
                        <div className="text-center">
                            <p className="text-xs text-muted-foreground mb-1">Média</p>
                            <p className="text-lg font-bold text-primary">
                                {media.toFixed(2)} {formatarLabel()}
                            </p>
                        </div>
                        <div className="text-center">
                            <p className="text-xs text-muted-foreground mb-1">Mínima</p>
                            <p className="text-lg font-bold text-green-400">
                                {minimo.toFixed(2)} {formatarLabel()}
                            </p>
                        </div>
                        <div className="text-center">
                            <p className="text-xs text-muted-foreground mb-1">Máxima</p>
                            <p className="text-lg font-bold text-red-400">
                                {maximo.toFixed(2)} {formatarLabel()}
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
