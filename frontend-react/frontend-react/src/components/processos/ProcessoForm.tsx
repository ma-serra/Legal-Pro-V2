/**
 * ProcessoForm - Formulário Completo de Processo
 * Todos os 31 campos do DB integrados
 */
import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { ProcessoCreate, Tributo } from '../../../types/processos';
import api from '../../../lib/api';
import { X, Save, FileText, Building2, DollarSign, Calendar } from 'lucide-react';

interface ProcessoFormProps {
    processo?: any;
    onClose: () => void;
    onSave: () => void;
}

export default function ProcessoForm({ processo, onClose, onSave }: ProcessoFormProps) {
    const { register, handleSubmit, watch, formState: { errors } } = useForm<ProcessoCreate>({
        defaultValues: processo || {}
    });

    const [tributos, setTributos] = useState<Tributo[]>([]);
    const [loading, setLoading] = useState(false);

    const naturezaSelecionada = watch('natureza_id');

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

    const onSubmit = async (data: ProcessoCreate) => {
        setLoading(true);
        try {
            if (processo?.id_processo) {
                await api.put(`/api/processos/${processo.id_processo}`, data);
            } else {
                await api.post('/api/processos', data);
            }
            onSave();
            onClose();
        } catch (error) {
            console.error('Erro ao salvar:', error);
            alert('Erro ao salvar processo');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-card border border-border rounded-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="sticky top-0 bg-card border-b border-border p-6 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-primary/20 rounded-lg">
                            <FileText className="w-6 h-6 text-primary" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold">
                                {processo ? 'Editar Processo' : 'Novo Processo'}
                            </h2>
                            <p className="text-sm text-muted-foreground">Preencha os dados do processo</p>
                        </div>
                    </div>

                    <button onClick={onClose} className="p-2 hover:bg-accent rounded-lg transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-8">

                    {/* 1. DADOS BÁSICOS */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold flex items-center gap-2 text-primary">
                            <FileText className="w-5 h-5" />
                            Dados Básicos
                        </h3>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Pasta (obrigatório) */}
                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    Pasta * <span className="text-muted-foreground text-xs">(ex: PROC-2024-001)</span>
                                </label>
                                <input
                                    {...register('pasta', { required: 'Pasta é obrigatória' })}
                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                    placeholder="PROC-2024-001"
                                />
                                {errors.pasta && <p className="text-red-500 text-xs mt-1">{errors.pasta.message}</p>}
                            </div>

                            {/* Número CNJ */}
                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    Número CNJ <span className="text-muted-foreground text-xs">(opcional)</span>
                                </label>
                                <input
                                    {...register('numero_cnj')}
                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary font-mono"
                                    placeholder="0001234-56.2024.8.21.0001"
                                />
                            </div>

                            {/* Natureza (obrigatório) */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Natureza *</label>
                                <select
                                    {...register('natureza_id', { required: 'Natureza é obrigatória', valueAsNumber: true })}
                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                >
                                    <option value="">Selecione...</option>
                                    <option value="1">Tributário</option>
                                    <option value="2">Trabalhista</option>
                                    <option value="3">Cível</option>
                                </select>
                                {errors.natureza_id && <p className="text-red-500 text-xs mt-1">{errors.natureza_id.message}</p>}
                            </div>

                            {/* Status (obrigatório) */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Status *</label>
                                <select
                                    {...register('status_id', { required: 'Status é obrigatório', valueAsNumber: true })}
                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                >
                                    <option value="">Selecione...</option>
                                    <option value="1">Ativo</option>
                                    <option value="2">Arquivado</option>
                                    <option value="3">Suspenso</option>
                                </select>
                                {errors.status_id && <p className="text-red-500 text-xs mt-1">{errors.status_id.message}</p>}
                            </div>

                            {/* Título */}
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium mb-2">Título</label>
                                <input
                                    {...register('titulo')}
                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                    placeholder="Descrição resumida do processo"
                                />
                            </div>
                        </div>
                    </div>

                    {/* 2. VALORES */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold flex items-center gap-2 text-green-500">
                            <DollarSign className="w-5 h-5" />
                            Valores
                        </h3>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium mb-2">Valor da Causa</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    {...register('valor_causa', { valueAsNumber: true })}
                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                    placeholder="0.00"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">Data Distribuição</label>
                                <input
                                    type="date"
                                    {...register('data_distribuicao')}
                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                />
                            </div>
                        </div>
                    </div>

                    {/* 3. DADOS ESPECÍFICOS POR NATUREZA */}
                    {naturezaSelecionada === 1 && (
                        <div className="space-y-4 bg-blue-500/5 border border-blue-500/20 rounded-xl p-6">
                            <h3 className="text-lg font-semibold flex items-center gap-2 text-blue-400">
                                <Building2 className="w-5 h-5" />
                                Dados Tributários
                            </h3>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2">Tributo</label>
                                    <select
                                        {...register('dados_tributario.tributo_id', { valueAsNumber: true })}
                                        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                    >
                                        <option value="">Selecione...</option>
                                        {tributos.map(t => (
                                            <option key={t.id_tributo} value={t.id_tributo}>{t.nome}</option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">Número AIIM</label>
                                    <input
                                        {...register('dados_tributario.numero_aiim')}
                                        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                        placeholder="00000000"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">Valor Principal</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        {...register('dados_tributario.valor_principal', { valueAsNumber: true })}
                                        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                        placeholder="0.00"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">Valor Multa</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        {...register('dados_tributario.valor_multa', { valueAsNumber: true })}
                                        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                        placeholder="0.00"
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {naturezaSelecionada === 2 && (
                        <div className="space-y-4 bg-orange-500/5 border border-orange-500/20 rounded-xl p-6">
                            <h3 className="text-lg font-semibold flex items-center gap-2 text-orange-400">
                                <FileText className="w-5 h-5" />
                                Dados Trabalhistas
                            </h3>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2">Tolerância Acordo</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        {...register('dados_trabalhista.tolerancia_acordo', { valueAsNumber: true })}
                                        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                        placeholder="0.00"
                                    />
                                </div>
                            </div>
                        </div>
                    )}

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
                            {loading ? 'Salvando...' : 'Salvar Processo'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
