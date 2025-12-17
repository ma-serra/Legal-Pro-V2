import { useState, useEffect } from 'react';
import { Brain, RefreshCw, TrendingUp, AlertCircle } from 'lucide-react';
import api from '../../lib/api';

interface QuickPredictData {
    valor_contingencia_predito: number;
    confianca: number;
    modelo_versao: string;
    risco_predito?: string;
    data_predicao?: string;
}

interface Props {
    processoId: number;
}

export default function QuickPredictCard({ processoId }: Props) {
    const [predicao, setPredicao] = useState<QuickPredictData | null>(null);
    const [loading, setLoading] = useState(true);
    const [atualizando, setAtualizando] = useState(false);
    const [erro, setErro] = useState<string | null>(null);

    useEffect(() => {
        carregarPredicao();
    }, [processoId]);

    const carregarPredicao = async () => {
        setLoading(true);
        setErro(null);
        try {
            const response = await api.get(`/api/ml/tributario/quick-predict/${processoId}`);
            setPredicao(response.data);
        } catch (error: any) {
            console.error('Erro ao carregar predição:', error);
            if (error.response?.status === 404) {
                setErro('Nenhuma predição disponível');
            } else {
                setErro('Erro ao carregar predição');
            }
        } finally {
            setLoading(false);
        }
    };

    const atualizarPredicao = async () => {
        setAtualizando(true);
        try {
            const response = await api.post('/api/ml/tributario/predict', {
                processo_id: processoId
            });
            setPredicao(response.data);
            setErro(null);
        } catch (error: any) {
            console.error('Erro ao atualizar predição:', error);
            setErro(error.response?.data?.error || 'Erro ao gerar predição');
        } finally {
            setAtualizando(false);
        }
    };

    const formatarMoeda = (valor: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
    };

    const formatarData = (data: string) => {
        const date = new Date(data);
        const hoje = new Date();
        const diffDias = Math.floor((hoje.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

        if (diffDias === 0) return 'Hoje';
        if (diffDias === 1) return 'Ontem';
        if (diffDias < 7) return `${diffDias} dias atrás`;
        return date.toLocaleDateString('pt-BR');
    };

    const getRiscoColor = (risco?: string) => {
        switch (risco?.toLowerCase()) {
            case 'baixo': return 'text-green-500 bg-green-500/10';
            case 'medio': case 'médio': return 'text-yellow-500 bg-yellow-500/10';
            case 'alto': return 'text-red-500 bg-red-500/10';
            default: return 'text-gray-500 bg-gray-500/10';
        }
    };

    if (loading) {
        return (
            <div className="bg-card border border-border rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                    <Brain className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold">Predição ML</h3>
                </div>
                <div className="flex items-center justify-center py-8">
                    <RefreshCw className="w-6 h-6 animate-spin text-muted-foreground" />
                </div>
            </div>
        );
    }

    if (erro && !predicao) {
        return (
            <div className="bg-card border border-border rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                    <Brain className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold">Predição ML</h3>
                </div>
                <div className="text-center py-6">
                    <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                    <p className="text-sm text-muted-foreground mb-4">{erro}</p>
                    <button
                        onClick={atualizarPredicao}
                        disabled={atualizando}
                        className="px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg text-sm transition-colors disabled:opacity-50"
                    >
                        {atualizando ? (
                            <span className="flex items-center gap-2">
                                <RefreshCw className="w-4 h-4 animate-spin" />
                                Gerando...
                            </span>
                        ) : (
                            'Gerar Predição ML'
                        )}
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-gradient-to-br from-primary/5 to-primary/10 border border-primary/20 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Brain className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold">Predição ML</h3>
                </div>
                <button
                    onClick={atualizarPredicao}
                    disabled={atualizando}
                    className="p-2 hover:bg-primary/10 rounded-lg transition-colors disabled:opacity-50"
                    title="Atualizar predição"
                >
                    <RefreshCw className={`w-4 h-4 ${atualizando ? 'animate-spin' : ''}`} />
                </button>
            </div>

            {predicao && (
                <div className="space-y-4">
                    <div>
                        <div className="text-sm text-muted-foreground mb-1">Valor Contingência</div>
                        <div className="text-2xl font-bold text-primary">
                            {formatarMoeda(predicao.valor_contingencia_predito)}
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <div className="text-sm text-muted-foreground mb-1">Confiança</div>
                            <div className="text-lg font-semibold text-green-500">
                                {(predicao.confianca * 100).toFixed(1)}%
                            </div>
                            <div className="w-full bg-accent rounded-full h-2 mt-2">
                                <div
                                    className="bg-green-500 rounded-full h-2 transition-all"
                                    style={{ width: `${predicao.confianca * 100}%` }}
                                />
                            </div>
                        </div>

                        {predicao.risco_predito && (
                            <div>
                                <div className="text-sm text-muted-foreground mb-1">Risco</div>
                                <div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getRiscoColor(predicao.risco_predito)}`}>
                                    {predicao.risco_predito}
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="pt-4 border-t border-border/50 text-xs text-muted-foreground flex items-center justify-between">
                        <span>Modelo {predicao.modelo_versao}</span>
                        {predicao.data_predicao && (
                            <span>{formatarData(predicao.data_predicao)}</span>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
