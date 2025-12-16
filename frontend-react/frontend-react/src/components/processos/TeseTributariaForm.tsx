/**
 * TeseTributariaForm - CRUD de Teses
 * Modal para criar/editar teses tributárias
 */
import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { TeseTributaria, Tributo } from '../../types/processos';
import api from '../../lib/api';
import { X, Save, FileText, Percent } from 'lucide-react';

interface TeseTributariaFormProps {
    tese?: TeseTributaria;
    onClose: () => void;
    onSave: () => void;
}

export default function TeseTributariaForm({ tese, onClose, onSave }: TeseTributariaFormProps) {
    const { register, handleSubmit, formState: { errors } } = useForm({
        defaultValues: tese || {}
    });

    const [tributos, setTributos] = useState<Tributo[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchTributos();
    }, []);

    const fetchTributos = async () => {
        try {
            const response = await api.get('/api/processos/tributos');
            setTributos(response.data || []);
        } catch (error) {
            console.error('Erro ao carregar tributos:', error);
        }
    };

    const onSubmit = async (data: any) => {
        setLoading(true);
        try {
            if (tese?.id_tese) {
                await api.put(`/api/tributario/teses/${tese.id_tese}`, data);
            } else {
                await api.post('/api/tributario/teses', data);
            }
            onSave();
            onClose();
        } catch (error) {
            console.error('Erro ao salvar tese:', error);
            alert('Erro ao salvar tese');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-card border border-border rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="sticky top-0 bg-card border-b border-border p-6 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-blue-500/20 rounded-lg">
                            <FileText className="w-6 h-6 text-blue-400" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold">
                                {tese ? 'Editar Tese' : 'Nova Tese Tributária'}
                            </h2>
                            <p className="text-sm text-muted-foreground">Cadastro de tese jurídica</p>
                        </div>
                    </div>

                    <button onClick={onClose} className="p-2 hover:bg-accent rounded-lg transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Código */}
                        <div>
                            <label className="block text-sm font-medium mb-2">
                                Código * <span className="text-muted-foreground text-xs">(ex: TESE-001)</span>
                            </label>
                            <input
                                {...register('codigo', { required: 'Código é obrigatório' })}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                placeholder="TESE-001"
                            />
                            {errors.codigo && <p className="text-red-500 text-xs mt-1">{errors.codigo.message as string}</p>}
                        </div>

                        {/* Tributo */}
                        <div>
                            <label className="block text-sm font-medium mb-2">Tributo</label>
                            <select
                                {...register('tributo_id', { valueAsNumber: true })}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                            >
                                <option value="">Selecione...</option>
                                {tributos.map(t => (
                                    <option key={t.id_tributo} value={t.id_tributo}>{t.nome}</option>
                                ))}
                            </select>
                        </div>

                        {/* Título */}
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium mb-2">Título *</label>
                            <input
                                {...register('titulo', { required: 'Título é obrigatório' })}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                placeholder="Descrição da tese"
                            />
                            {errors.titulo && <p className="text-red-500 text-xs mt-1">{errors.titulo.message as string}</p>}
                        </div>

                        {/* Descrição */}
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium mb-2">Descrição</label>
                            <textarea
                                {...register('descricao')}
                                rows={3}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                placeholder="Detalhes da tese..."
                            />
                        </div>

                        {/* Tema Repercussão Geral */}
                        <div>
                            <label className="block text-sm font-medium mb-2">Tema Repercussão Geral</label>
                            <input
                                {...register('tema_repercussao_geral')}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                placeholder="Tema nº"
                            />
                        </div>

                        {/* Tema Repetitivo */}
                        <div>
                            <label className="block text-sm font-medium mb-2">Tema Repetitivo</label>
                            <input
                                {...register('tema_repetitivo')}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                placeholder="Tema nº"
                            />
                        </div>

                        {/* Tribunal */}
                        <div>
                            <label className="block text-sm font-medium mb-2">Tribunal Origem</label>
                            <select
                                {...register('tribunal_origem')}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                            >
                                <option value="">Selecione...</option>
                                <option value="STF">STF</option>
                                <option value="STJ">STJ</option>
                                <option value="TST">TST</option>
                                <option value="TRF">TRF</option>
                                <option value="TJ">TJ</option>
                            </select>
                        </div>

                        {/* Probabilidade */}
                        <div>
                            <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                                <Percent className="w-4 h-4" />
                                Probabilidade de Sucesso
                            </label>
                            <input
                                type="number"
                                min="0"
                                max="100"
                                {...register('probabilidade_sucesso', { valueAsNumber: true })}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                placeholder="0-100"
                            />
                        </div>

                        {/* Situação */}
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium mb-2">Situação</label>
                            <select
                                {...register('situacao')}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                            >
                                <option value="Pendente">Pendente</option>
                                <option value="Favorável">Favorável</option>
                                <option value="Desfavorável">Desfavorável</option>
                                <option value="Parcial">Parcial</option>
                            </select>
                        </div>

                        {/* Fundamentação */}
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium mb-2">Fundamentação</label>
                            <textarea
                                {...register('fundamentacao')}
                                rows={4}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                placeholder="Base legal e jurisprudencial..."
                            />
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3 justify-end pt-6 border-t border-border">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-6 py-2.5 bg-accent hover:bg-accent/80 rounded-lg transition-colors"
                        >
                            Cancelar
                        </button>

                        <button
                            type="submit"
                            disabled={loading}
                            className="flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary/90 rounded-lg transition-colors font-medium disabled:opacity-50"
                        >
                            <Save className="w-4 h-4" />
                            {loading ? 'Salvando...' : 'Salvar Tese'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
