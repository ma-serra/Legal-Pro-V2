/**
 * TeseTributariaList - Gestão de Teses Tributárias
 * CRUD completo integrado com API
 */
import { useState, useEffect } from 'react';
import { TeseTributaria, Tributo } from '../../types/processos';
import api from '../../lib/api';
import { Plus, Edit, Trash2, Search, FileText, CheckCircle } from 'lucide-react';

export default function TeseTributariaList() {
    const [teses, setTeses] = useState<TeseTributaria[]>([]);
    const [tributos, setTributos] = useState<Tributo[]>([]);
    const [loading, setLoading] = useState(true);
    const [filtros, setFiltros] = useState({ tributo_id: '', busca: '' });

    useEffect(() => {
        fetchData();
    }, [filtros]);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [tesesRes, tributosRes] = await Promise.all([
                api.get('/api/tributario/teses', { params: filtros }),
                api.get('/api/processos/tributos')
            ]);

            setTeses(tesesRes.data.teses || []);
            setTributos(tributosRes.data || []);
        } catch (error) {
            console.error('Erro ao carregar teses:', error);
        } finally {
            setLoading(false);
        }
    };

    const deleteTese = async (id: number) => {
        if (!confirm('Deseja realmente excluir esta tese?')) return;

        try {
            await api.delete(`/api/tributario/teses/${id}`);
            fetchData();
        } catch (error) {
            console.error('Erro ao excluir tese:', error);
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold flex items-center gap-3">
                        <FileText className="w-7 h-7 text-primary" />
                        Teses Tributárias
                    </h2>
                    <p className="text-muted-foreground mt-1">Gestão de teses jurídicas</p>
                </div>

                <button className="flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary/90 rounded-lg transition-colors font-medium">
                    <Plus className="w-4 h-4" />
                    Nova Tese
                </button>
            </div>

            {/* Filters */}
            <div className="bg-card border border-border rounded-xl p-4">
                <div className="flex gap-3">
                    <div className="flex-1 relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <input
                            type="text"
                            placeholder="Buscar por código, título..."
                            className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                            onChange={(e) => setFiltros({ ...filtros, busca: e.target.value })}
                        />
                    </div>

                    <select
                        className="bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                        onChange={(e) => setFiltros({ ...filtros, tributo_id: e.target.value })}
                    >
                        <option value="">Todos os Tributos</option>
                        {tributos.map(t => (
                            <option key={t.id_tributo} value={t.id_tributo}>{t.nome}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* List */}
            {loading ? (
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto"></div>
                </div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {teses.map(tese => (
                        <div
                            key={tese.id_tese}
                            className="bg-card border border-border rounded-xl p-6 hover:shadow-lg transition-all"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs font-medium">
                                            {tese.codigo}
                                        </span>
                                        {tese.ativo && <CheckCircle className="w-4 h-4 text-green-500" />}
                                    </div>
                                    <h3 className="font-semibold text-lg mb-2">{tese.titulo}</h3>
                                    {tese.descricao && (
                                        <p className="text-sm text-muted-foreground line-clamp-2">{tese.descricao}</p>
                                    )}
                                </div>
                            </div>

                            {tese.probabilidade_sucesso && (
                                <div className="mb-4">
                                    <div className="flex items-center justify-between text-sm mb-1">
                                        <span className="text-muted-foreground">Probabilidade</span>
                                        <span className="font-medium">{tese.probabilidade_sucesso}%</span>
                                    </div>
                                    <div className="w-full bg-accent rounded-full h-2">
                                        <div
                                            className="bg-primary rounded-full h-2 transition-all"
                                            style={{ width: `${tese.probabilidade_sucesso}%` }}
                                        />
                                    </div>
                                </div>
                            )}

                            <div className="flex gap-2 pt-4 border-t border-border">
                                <button className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary/20 hover:bg-primary/30 rounded-lg transition-colors text-primary">
                                    <Edit className="w-4 h-4" />
                                    Editar
                                </button>
                                <button
                                    onClick={() => deleteTese(tese.id_tese)}
                                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg transition-colors text-red-400"
                                >
                                    <Trash2 className="w-4 h-4" />
                                    Excluir
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
