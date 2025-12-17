import { useState, useEffect } from 'react';
import { Scale, Plus, Trash2, RefreshCw, AlertCircle } from 'lucide-react';
import api from '../../lib/api';

interface Tese {
    id_tese: number;
    codigo?: string;
    titulo: string;
    probabilidade_sucesso?: number;
    data_associacao?: string;
}

interface TributeResponse {
    id_tributo: number;
    titulo: string;
}

interface Props {
    processoId: number;
    tributoid?: number;
}

export default function TesesAssociadasSection({ processoId, tributoId }: Props) {
    const [teses, setTeses] = useState<Tese[]>([]);
    const [tesesdisponiveis, setTesesdisponiveis] = useState<Tese[]>([]);
    const [loading, setLoading] = useState(true);
    const [loadingTeses, setLoadingTeses] = useState(false);
    const [selectedTeseId, setSelectedTeseId] = useState<number | null>(null);
    const [adicionando, setAdicionando] = useState(false);

    useEffect(() => {
        carregarTesesAssociadas();
        if (tributoId) {
            carregarTesesDisponiveis();
        }
    }, [processoId, tributoId]);

    const carregarTesesAssociadas = async () => {
        setLoading(true);
        try {
            const response = await api.get(`/api/tributario/processos/${processoId}/teses`);
            setTeses(response.data || []);
        } catch (error: any) {
            console.error('Erro ao carregar teses associadas:', error);
            if (error.response?.status !== 404) {
                // Ignora 404 (sem teses)
            }
        } finally {
            setLoading(false);
        }
    };

    const carregarTesesDisponiveis = async () => {
        setLoadingTeses(true);
        try {
            const response = await api.get(`/api/tributario/teses`, {
                params: { tributo_id: tributoId }
            });
            setTesesdisponiveis(response.data || []);
        } catch (error) {
            console.error('Erro ao carregar teses disponíveis:', error);
        } finally {
            setLoadingTeses(false);
        }
    };

    const adicionarTese = async () => {
        if (!selectedTeseId) return;

        setAdicionando(true);
        try {
            await api.post(`/api/tributario/processos/${processoId}/teses`, {
                tese_id: selectedTeseId
            });
            await carregarTesesAssociadas();
            setSelectedTeseId(null);
        } catch (error: any) {
            console.error('Erro ao associar tese:', error);
            alert(error.response?.data?.error || 'Erro ao associar tese');
        } finally {
            setAdicionando(false);
        }
    };

    const removerTese = async (teseId: number) => {
        if (!confirm('Deseja remover esta tese do processo?')) return;

        try {
            await api.delete(`/api/tributario/processos/${processoId}/teses/${teseId}`);
            await carregarTesesAssociadas();
        } catch (error: any) {
            console.error('Erro ao remover tese:', error);
            alert(error.response?.data?.error || 'Erro ao remover tese');
        }
    };

    const formatarData = (data: string) => {
        return new Date(data).toLocaleDateString('pt-BR');
    };

    return (
        <div className="bg-card border border-border rounded-xl p-6">
            <div className="flex items-center gap-2 mb-6">
                <Scale className="w-5 h-5 text-primary" />
                <h3 className="font-semibold text-lg">Teses Associadas</h3>
            </div>

            {/* Adicionar Tese */}
            {tributoId && (
                <div className="mb-6 pb-6 border-b border-border">
                    <label className="block text-sm font-medium mb-2">Adicionar Tese</label>
                    <div className="flex gap-2">
                        <select
                            value={selectedTeseId || ''}
                            onChange={(e) => setSelectedTeseId(parseInt(e.target.value) || null)}
                            disabled={loadingTeses || adicionando}
                            className="flex-1 bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none disabled:opacity-50"
                        >
                            <option value="">
                                {loadingTeses ? 'Carregando teses...' : 'Selecione uma tese...'}
                            </option>
                            {tesesdisponiveis.map(tese => (
                                <option key={tese.id_tese} value={tese.id_tese}>
                                    {tese.codigo ? `${tese.codigo} - ` : ''}{tese.titulo}
                                    {tese.probabilidade_sucesso ? ` (${tese.probabilidade_sucesso}%)` : ''}
                                </option>
                            ))}
                        </select>
                        <button
                            onClick={adicionarTese}
                            disabled={!selectedTeseId || adicionando}
                            className="px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {adicionando ? (
                                <>
                                    <RefreshCw className="w-4 h-4 animate-spin" />
                                    Adicionando...
                                </>
                            ) : (
                                <>
                                    <Plus className="w-4 h-4" />
                                    Adicionar
                                </>
                            )}
                        </button>
                    </div>
                </div>
            )}

            {/* Lista Teses */}
            {loading ? (
                <div className="text-center py-8">
                    <RefreshCw className="w-6 h-6 animate-spin text-muted-foreground mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">Carregando teses...</p>
                </div>
            ) : teses.length === 0 ? (
                <div className="text-center py-8">
                    <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                    <p className="text-sm text-muted-foreground">
                        {tributoId ? 'Nenhuma tese associada ao processo' : 'Configure o tributo do processo para associar teses'}
                    </p>
                </div>
            ) : (
                <div className="space-y-3">
                    {teses.map(tese => (
                        <div
                            key={tese.id_tese}
                            className="flex items-start justify-between p-4 bg-accent/30 border border-border/50 rounded-lg hover:border-primary/30 transition-colors"
                        >
                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                    {tese.codigo && (
                                        <span className="px-2 py-0.5 bg-primary/20 text-primary rounded text-xs font-mono">
                                            {tese.codigo}
                                        </span>
                                    )}
                                    <h4 className="font-medium">{tese.titulo}</h4>
                                </div>
                                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                    {tese.probabilidade_sucesso !== undefined && (
                                        <span className="flex items-center gap-1">
                                            <span className="text-green-500">✓</span>
                                            Probabilidade: {tese.probabilidade_sucesso}%
                                        </span>
                                    )}
                                    {tese.data_associacao && (
                                        <span>Associada em {formatarData(tese.data_associacao)}</span>
                                    )}
                                </div>
                            </div>
                            <button
                                onClick={() => removerTese(tese.id_tese)}
                                className="p-2 hover:bg-red-500/10 text-red-400 rounded-lg transition-colors"
                                title="Remover tese"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
