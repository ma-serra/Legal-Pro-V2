/**
 * VinculoTesesPanel - Vinculação Tese-Processo
 * Gerencia teses vinculadas a um processo
 */
import { useState, useEffect } from 'react';
import { TeseTributaria } from '../../types/processos';
import api from '../../lib/api';
import { Plus, X, Check, ArrowUp, ArrowDown, Link as LinkIcon } from 'lucide-react';

interface VinculoTesesPanelProps {
    processoId: number;
}

export default function VinculoTesesPanel({ processoId }: VinculoTesesPanelProps) {
    const [tesVinculadas, setTesesVinculadas] = useState<any[]>([]);
    const [tesasDisponiveis, setTesesDisponiveis] = useState<TeseTributaria[]>([]);
    const [showModal, setShowModal] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchTeses();
    }, [processoId]);

    const fetchTeses = async () => {
        setLoading(true);
        try {
            const [vinculadasRes, disponiveisRes] = await Promise.all([
                api.get(`/api/tributario/processos/${processoId}/teses`),
                api.get('/api/tributario/teses')
            ]);

            setTesesVinculadas(vinculadasRes.data || []);
            setTesesDisponiveis(disponiveisRes.data.teses || []);
        } catch (error) {
            console.error('Erro ao carregar teses:', error);
        } finally {
            setLoading(false);
        }
    };

    const vincularTese = async (teseId: number) => {
        try {
            await api.post(`/api/tributario/processos/${processoId}/teses`, {
                tese_id: teseId,
                ordem: tesVinculadas.length + 1
            });

            fetchTeses();
            setShowModal(false);
        } catch (error) {
            console.error('Erro ao vincular tese:', error);
            alert('Erro ao vincular tese');
        }
    };

    const desvincularTese = async (teseId: number) => {
        if (!confirm('Deseja desvincular esta tese?')) return;

        try {
            await api.delete(`/api/tributario/processos/${processoId}/teses/${teseId}`);
            fetchTeses();
        } catch (error) {
            console.error('Erro ao desvincular:', error);
        }
    };

    const atualizarStatus = async (teseId: number, novoStatus: string) => {
        try {
            await api.put(`/api/tributario/processos/${processoId}/teses/${teseId}/status`, {
                status: novoStatus
            });
            fetchTeses();
        } catch (error) {
            console.error('Erro ao atualizar status:', error);
        }
    };

    if (loading) {
        return <div className="animate-pulse bg-accent rounded-xl h-64"></div>;
    }

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <LinkIcon className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold">Teses Vinculadas</h3>
                    <span className="px-2 py-1 bg-primary/20 text-primary rounded-full text-xs">
                        {tesVinculadas.length}
                    </span>
                </div>

                <button
                    onClick={() => setShowModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors text-sm"
                >
                    <Plus className="w-4 h-4" />
                    Vincular Tese
                </button>
            </div>

            {/* Lista de Teses Vinculadas */}
            {tesVinculadas.length === 0 ? (
                <div className="bg-accent rounded-xl p-8 text-center">
                    <p className="text-muted-foreground">Nenhuma tese vinculada</p>
                </div>
            ) : (
                <div className="space-y-3">
                    {tesVinculadas.map((vinculo, index) => (
                        <div
                            key={vinculo.tese.id_tese}
                            className="bg-card border border-border rounded-xl p-4 hover:shadow-lg transition-all"
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs font-medium">
                                            #{vinculo.ordem}
                                        </span>
                                        <span className="px-2 py-1 bg-primary/20 text-primary rounded text-xs">
                                            {vinculo.tese.codigo}
                                        </span>
                                        <select
                                            value={vinculo.status}
                                            onChange={(e) => atualizarStatus(vinculo.tese.id_tese, e.target.value)}
                                            className="px-2 py-1 bg-background border border-border rounded text-xs focus:outline-none focus:ring-2 focus:ring-primary"
                                        >
                                            <option value="Aguardando">Aguardando</option>
                                            <option value="Em análise">Em análise</option>
                                            <option value="Aceita">Aceita</option>
                                            <option value="Rejeitada">Rejeitada</option>
                                        </select>
                                    </div>

                                    <p className="font-medium mb-1">{vinculo.tese.titulo}</p>
                                    {vinculo.tese.probabilidade_sucesso && (
                                        <p className="text-sm text-muted-foreground">
                                            Probabilidade: {vinculo.tese.probabilidade_sucesso}%
                                        </p>
                                    )}
                                </div>

                                <button
                                    onClick={() => desvincularTese(vinculo.tese.id_tese)}
                                    className="p-2 hover:bg-red-500/20 rounded-lg transition-colors text-red-400"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Modal de Seleção */}
            {showModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-card border border-border rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col">
                        <div className="p-6 border-b border-border flex items-center justify-between">
                            <h3 className="text-xl font-bold">Selecionar Tese</h3>
                            <button onClick={() => setShowModal(false)} className="p-2 hover:bg-accent rounded-lg">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto p-6 space-y-3">
                            {tesesDisponiveis.filter((t: TeseTributaria) =>
                                !tesVinculadas.some(v => v.tese.id_tese === t.id_tese)
                            ).map((tese: TeseTributaria) => (
                                <div
                                    key={tese.id_tese}
                                    className="bg-background border border-border rounded-lg p-4 hover:border-primary transition-colors cursor-pointer"
                                    onClick={() => vincularTese(tese.id_tese)}
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-2">
                                                <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">
                                                    {tese.codigo}
                                                </span>
                                                {tese.probabilidade_sucesso && (
                                                    <span className="text-xs text-muted-foreground">
                                                        {tese.probabilidade_sucesso}% sucesso
                                                    </span>
                                                )}
                                            </div>
                                            <p className="font-medium">{tese.titulo}</p>
                                        </div>

                                        <Check className="w-5 h-5 text-primary" />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
