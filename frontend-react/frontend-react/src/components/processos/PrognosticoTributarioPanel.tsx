/**
 * PrognosticoTributarioPanel - Painel de Prognóstico
 * 3 Cenários: Provável, Possível, Remoto
 */
import { useState, useEffect } from 'react';
import { PrognosticoTributario } from '../../../types/processos';
import api from '../../../lib/api';
import { TrendingUp, DollarSign, Percent, Save } from 'lucide-react';

interface PrognosticoTributarioPanelProps {
    processoId: number;
}

export default function PrognosticoTributarioPanel({ processoId }: PrognosticoTributarioPanelProps) {
    const [prognostico, setPrognostico] = useState<PrognosticoTributario | null>(null);
    const [editing, setEditing] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchPrognostico();
    }, [processoId]);

    const fetchPrognostico = async () => {
        try {
            const response = await api.get(`/api/tributario/processos/${processoId}/prognostico`);
            setPrognostico(response.data);
        } catch (error) {
            console.error('Erro ao carregar prognóstico:', error);
        } finally {
            setLoading(false);
        }
    };

    const savePrognostico = async (data: any) => {
        try {
            await api.post(`/api/tributario/processos/${processoId}/prognostico`, data);
            fetchPrognostico();
            setEditing(false);
        } catch (error) {
            console.error('Erro ao salvar prognóstico:', error);
        }
    };

    const formatCurrency = (value?: number) => {
        if (!value) return 'R$ 0,00';
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };

    if (loading) {
        return <div className="animate-pulse bg-accent rounded-xl h-64"></div>;
    }

    const cenarios = [
        {
            tipo: 'provavel',
            label: 'Provável',
            color: 'green',
            data: prognostico?.provavel
        },
        {
            tipo: 'possivel',
            label: 'Possível',
            color: 'yellow',
            data: prognostico?.possivel
        },
        {
            tipo: 'remoto',
            label: 'Remoto',
            color: 'red',
            data: prognostico?.remoto
        }
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-primary/20 rounded-lg">
                        <TrendingUp className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold">Prognóstico Tributário</h3>
                        <p className="text-sm text-muted-foreground">Análise de cenários</p>
                    </div>
                </div>

                {!editing && (
                    <button
                        onClick={() => setEditing(true)}
                        className="px-4 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors"
                    >
                        {prognostico ? 'Editar' : 'Criar Prognóstico'}
                    </button>
                )}
            </div>

            {/* Cenários */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {cenarios.map(cenario => (
                    <div
                        key={cenario.tipo}
                        className={`bg-${cenario.color}-500/10 border border-${cenario.color}-500/20 rounded-xl p-6 hover:shadow-lg transition-all`}
                    >
                        <div className="flex items-center gap-2 mb-4">
                            <div className={`p-2 bg-${cenario.color}-500/20 rounded-lg`}>
                                <TrendingUp className={`w-5 h-5 text-${cenario.color}-400`} />
                            </div>
                            <h4 className={`font-semibold text-${cenario.color}-400`}>{cenario.label}</h4>
                        </div>

                        {cenario.data ? (
                            <div className="space-y-3">
                                <div>
                                    <label className="text-xs text-muted-foreground">Valor</label>
                                    <p className="text-2xl font-bold">{formatCurrency(cenario.data.valor)}</p>
                                </div>

                                <div>
                                    <label className="text-xs text-muted-foreground">Percentual</label>
                                    <div className="flex items-center gap-2">
                                        <div className="flex-1 bg-accent rounded-full h-2">
                                            <div
                                                className={`bg-${cenario.color}-500 rounded-full h-2 transition-all`}
                                                style={{ width: `${cenario.data.percentual}%` }}
                                            />
                                        </div>
                                        <span className="text-sm font-medium">{cenario.data.percentual}%</span>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <p className="text-sm text-muted-foreground">Não configurado</p>
                        )}
                    </div>
                ))}
            </div>

            {/* Valor Esperado */}
            {prognostico && (
                <div className="bg-gradient-to-r from-primary/20 to-primary/5 border border-primary/20 rounded-xl p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h4 className="text-sm text-muted-foreground mb-1">Valor Esperado (Ponderado)</h4>
                            <p className="text-3xl font-bold text-primary">Calcular via API</p>
                        </div>
                        <DollarSign className="w-12 h-12 text-primary/50" />
                    </div>
                </div>
            )}
        </div>
    );
}
