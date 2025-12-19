/**
 * TesesMultiSelect - Componente para seleção múltipla de teses
 * Para uso no formulário de criação de processo
 */
import { useState, useEffect } from 'react';
import { X, Plus, Scale } from 'lucide-react';
import api from '../../lib/api';

interface Tese {
    id_tese: number;
    codigo?: string;
    titulo: string;
    probabilidade_sucesso?: number;
}

interface Props {
    tributoId?: number;
    selectedTeses: number[];
    onChange: (teses: number[]) => void;
    disabled?: boolean;
}

export default function TesesMultiSelect({ tributoId, selectedTeses, onChange, disabled }: Props) {
    const [tesesDisponiveis, setTesesDisponiveis] = useState<Tese[]>([]);
    const [loading, setLoading] = useState(false);
    const [dropdownOpen, setDropdownOpen] = useState(false);

    useEffect(() => {
        if (tributoId) {
            carregarTeses();
        } else {
            setTesesDisponiveis([]);
        }
    }, [tributoId]);

    const carregarTeses = async () => {
        setLoading(true);
        try {
            const response = await api.get('/api/tributario/teses', {
                params: { tributo_id: tributoId }
            });
            setTesesDisponiveis(response.data || []);
        } catch (error) {
            console.error('Erro ao carregar teses:', error);
        } finally {
            setLoading(false);
        }
    };

    const adicionarTese = (teseId: number) => {
        if (!selectedTeses.includes(teseId)) {
            onChange([...selectedTeses, teseId]);
        }
        setDropdownOpen(false);
    };

    const removerTese = (teseId: number) => {
        onChange(selectedTeses.filter(id => id !== teseId));
    };

    const tesesSelecionadasInfo = tesesDisponiveis.filter(t => selectedTeses.includes(t.id_tese));
    const tesesNaoSelecionadas = tesesDisponiveis.filter(t => !selectedTeses.includes(t.id_tese));

    return (
        <div className="space-y-3">
            <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                <Scale className="w-4 h-4 text-primary" />
                Teses Envolvidas
            </label>

            {/* Teses Selecionadas */}
            <div className="flex flex-wrap gap-2 min-h-[40px] p-2 bg-background border border-border rounded-lg">
                {tesesSelecionadasInfo.length === 0 ? (
                    <span className="text-muted-foreground text-sm">
                        {tributoId ? 'Nenhuma tese selecionada' : 'Selecione um tributo primeiro'}
                    </span>
                ) : (
                    tesesSelecionadasInfo.map(tese => (
                        <span
                            key={tese.id_tese}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary/20 text-primary rounded-full text-sm"
                        >
                            {tese.codigo && <span className="font-mono text-xs">{tese.codigo}</span>}
                            {tese.titulo}
                            {!disabled && (
                                <button
                                    type="button"
                                    onClick={() => removerTese(tese.id_tese)}
                                    className="hover:bg-primary/30 rounded-full p-0.5"
                                >
                                    <X className="w-3 h-3" />
                                </button>
                            )}
                        </span>
                    ))
                )}
            </div>

            {/* Adicionar Tese */}
            {tributoId && !disabled && (
                <div className="relative">
                    <button
                        type="button"
                        onClick={() => setDropdownOpen(!dropdownOpen)}
                        disabled={loading || tesesNaoSelecionadas.length === 0}
                        className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <Plus className="w-4 h-4" />
                        {loading ? 'Carregando...' : 'Adicionar Tese'}
                    </button>

                    {dropdownOpen && tesesNaoSelecionadas.length > 0 && (
                        <>
                            <div
                                className="fixed inset-0 z-10"
                                onClick={() => setDropdownOpen(false)}
                            />
                            <div className="absolute top-full left-0 mt-1 w-96 max-h-60 overflow-y-auto bg-card border border-border rounded-lg shadow-xl z-20">
                                {tesesNaoSelecionadas.map(tese => (
                                    <button
                                        key={tese.id_tese}
                                        type="button"
                                        onClick={() => adicionarTese(tese.id_tese)}
                                        className="w-full text-left px-4 py-3 hover:bg-accent border-b border-border/50 last:border-0 transition-colors"
                                    >
                                        <div className="flex items-center gap-2">
                                            {tese.codigo && (
                                                <span className="px-2 py-0.5 bg-primary/20 text-primary rounded text-xs font-mono">
                                                    {tese.codigo}
                                                </span>
                                            )}
                                            <span className="font-medium">{tese.titulo}</span>
                                        </div>
                                        {tese.probabilidade_sucesso !== undefined && (
                                            <div className="text-xs text-muted-foreground mt-1">
                                                Probabilidade de sucesso: {tese.probabilidade_sucesso}%
                                            </div>
                                        )}
                                    </button>
                                ))}
                            </div>
                        </>
                    )}
                </div>
            )}

            {/* Mensagem se não houver teses cadastradas */}
            {tributoId && !loading && tesesDisponiveis.length === 0 && (
                <p className="text-xs text-yellow-500">
                    ⚠️ Nenhuma tese cadastrada para este tributo.
                    Cadastre teses em Processos → Teses Tributárias.
                </p>
            )}
        </div>
    );
}
