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
    const [showModal, setShowModal] = useState(false);
    const [editingTese, setEditingTese] = useState<TeseTributaria | null>(null);

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

                <button
                    onClick={() => {
                        setEditingTese(null);
                        setShowModal(true);
                    }}
                    className="flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary/90 rounded-lg transition-colors font-medium"
                >
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
                                <button
                                    onClick={() => {
                                        setEditingTese(tese);
                                        setShowModal(true);
                                    }}
                                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary/20 hover:bg-primary/30 rounded-lg transition-colors text-primary"
                                >
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

            {/* Modal Nova/Editar Tese */}
            {showModal && (
                <TeseModal
                    tese={editingTese}
                    tributos={tributos}
                    onClose={() => {
                        setShowModal(false);
                        setEditingTese(null);
                    }}
                    onSave={() => {
                        setShowModal(false);
                        setEditingTese(null);
                        fetchData();
                    }}
                />
            )}
        </div>
    );
}

// Modal Component
function TeseModal({ tese, tributos, onClose, onSave }: {
    tese: TeseTributaria | null;
    tributos: Tributo[];
    onClose: () => void;
    onSave: () => void;
}) {
    const [formData, setFormData] = useState({
        codigo: tese?.codigo || '',
        titulo: tese?.titulo || '',
        descricao: tese?.descricao || '',
        tributo_id: tese?.tributo_id || '',
        probabilidade_sucesso: tese?.probabilidade_sucesso || '',
        fundamentacao_legal: tese?.fundamentacao_legal || '',
        jurisprudencia: tese?.jurisprudencia || '',
        ativo: tese?.ativo ?? true
    });
    const [saving, setSaving] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);

        try {
            if (tese) {
                await api.put(`/api/tributario/teses/${tese.id_tese}`, formData);
            } else {
                await api.post('/api/tributario/teses', formData);
            }
            onSave();
        } catch (error) {
            console.error('Erro ao salvar tese:', error);
            alert('Erro ao salvar tese');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-card border border-border rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                <div className="p-6 border-b border-border">
                    <h3 className="text-xl font-bold">{tese ? 'Editar Tese' : 'Nova Tese'}</h3>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">Código</label>
                            <input
                                type="text"
                                required
                                value={formData.codigo}
                                onChange={(e) => setFormData({ ...formData, codigo: e.target.value })}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Tributo</label>
                            <select
                                required
                                value={formData.tributo_id}
                                onChange={(e) => setFormData({ ...formData, tributo_id: e.target.value })}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2"
                            >
                                <option value="">Selecione...</option>
                                {tributos.map(t => (
                                    <option key={t.id_tributo} value={t.id_tributo}>{t.nome}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Título</label>
                        <input
                            type="text"
                            required
                            value={formData.titulo}
                            onChange={(e) => setFormData({ ...formData, titulo: e.target.value })}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Descrição</label>
                        <textarea
                            rows={3}
                            value={formData.descricao}
                            onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Probabilidade Sucesso (%)</label>
                        <input
                            type="number"
                            min="0"
                            max="100"
                            value={formData.probabilidade_sucesso}
                            onChange={(e) => setFormData({ ...formData, probabilidade_sucesso: e.target.value })}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Fundamentação Legal</label>
                        <textarea
                            rows={2}
                            value={formData.fundamentacao_legal}
                            onChange={(e) => setFormData({ ...formData, fundamentacao_legal: e.target.value })}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Jurisprudência</label>
                        <textarea
                            rows={2}
                            value={formData.jurisprudencia}
                            onChange={(e) => setFormData({ ...formData, jurisprudencia: e.target.value })}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2"
                        />
                    </div>

                    <div className="flex items-center gap-2">
                        <input
                            type="checkbox"
                            id="ativo"
                            checked={formData.ativo}
                            onChange={(e) => setFormData({ ...formData, ativo: e.target.checked })}
                            className="w-4 h-4 rounded border-border text-primary focus:ring-primary"
                        />
                        <label htmlFor="ativo" className="text-sm font-medium">Tese Ativa</label>
                    </div>

                    <div className="flex gap-3 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            disabled={saving}
                            className="flex-1 px-4 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors disabled:opacity-50"
                        >
                            {saving ? 'Salvando...' : 'Salvar'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
