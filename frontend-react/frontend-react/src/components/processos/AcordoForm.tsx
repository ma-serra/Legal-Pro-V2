/**
 * AcordoForm - Registro de Acordos (Trabalhista/Cível)
 * Componente genérico para ambas naturezas
 */
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import api from '../../lib/api';
import { X, Save, DollarSign, Calendar, AlertCircle } from 'lucide-react';

interface AcordoFormProps {
    processoId: number;
    natureza: 'trabalhista' | 'civel';
    tolerancia?: number;
    onClose: () => void;
    onSave: () => void;
}

export default function AcordoForm({ processoId, natureza, tolerancia, onClose, onSave }: AcordoFormProps) {
    const { register, handleSubmit, watch, formState: { errors } } = useForm();
    const [loading, setLoading] = useState(false);
    const [viabilidade, setViabilidade] = useState<any>(null);

    const valorProposta = watch('valor_acordo');

    const verificarViabilidade = async () => {
        if (!valorProposta) return;

        try {
            const response = await api.post(
                `/api/${natureza}/processos/${processoId}/acordo/viabilidade`,
                { valor_proposta: parseFloat(valorProposta) }
            );
            setViabilidade(response.data);
        } catch (error) {
            console.error('Erro ao verificar viabilidade:', error);
        }
    };

    const onSubmit = async (data: any) => {
        setLoading(true);
        try {
            await api.post(`/api/${natureza}/processos/${processoId}/acordo`, {
                valor_acordo: parseFloat(data.valor_acordo),
                data_acordo: data.data_acordo,
                observacoes: data.observacoes
            });

            onSave();
            onClose();
        } catch (error) {
            console.error('Erro ao registrar acordo:', error);
            alert('Erro ao registrar acordo');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-card border border-border rounded-2xl max-w-2xl w-full">
                {/* Header */}
                <div className="p-6 border-b border-border flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-green-500/20 rounded-lg">
                            <DollarSign className="w-6 h-6 text-green-400" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold">Registrar Acordo</h2>
                            <p className="text-sm text-muted-foreground capitalize">{natureza}</p>
                        </div>
                    </div>

                    <button onClick={onClose} className="p-2 hover:bg-accent rounded-lg transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">

                    {/* Tolerância Info */}
                    {tolerancia && (
                        <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
                            <div className="flex items-start gap-3">
                                <AlertCircle className="w-5 h-5 text-blue-400 mt-0.5" />
                                <div>
                                    <h4 className="font-semibold text-blue-400 mb-1">Tolerância Configurada</h4>
                                    <p className="text-sm text-muted-foreground">
                                        Valor máximo aceitável: {new Intl.NumberFormat('pt-BR', {
                                            style: 'currency',
                                            currency: 'BRL'
                                        }).format(tolerancia)}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="space-y-4">
                        {/* Valor do Acordo */}
                        <div>
                            <label className="block text-sm font-medium mb-2">
                                Valor do Acordo * <span className="text-muted-foreground text-xs">(R$)</span>
                            </label>
                            <div className="relative">
                                <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                                <input
                                    type="number"
                                    step="0.01"
                                    {...register('valor_acordo', { required: 'Valor é obrigatório' })}
                                    onBlur={verificarViabilidade}
                                    className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                    placeholder="0.00"
                                />
                            </div>
                            {errors.valor_acordo && (
                                <p className="text-red-500 text-xs mt-1">{errors.valor_acordo.message as string}</p>
                            )}
                        </div>

                        {/* Viabilidade */}
                        {viabilidade && (
                            <div className={`${viabilidade.viavel
                                    ? 'bg-green-500/10 border-green-500/20'
                                    : 'bg-red-500/10 border-red-500/20'
                                } border rounded-xl p-4`}>
                                <p className={`font-semibold ${viabilidade.viavel ? 'text-green-400' : 'text-red-400'}`}>
                                    {viabilidade.mensagem}
                                </p>
                                {viabilidade.percentual_tolerancia && (
                                    <p className="text-sm text-muted-foreground mt-1">
                                        {viabilidade.percentual_tolerancia.toFixed(1)}% da tolerância
                                    </p>
                                )}
                            </div>
                        )}

                        {/* Data do Acordo */}
                        <div>
                            <label className="block text-sm font-medium mb-2">Data do Acordo *</label>
                            <div className="relative">
                                <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                                <input
                                    type="date"
                                    {...register('data_acordo', { required: 'Data é obrigatória' })}
                                    className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                />
                            </div>
                            {errors.data_acordo && (
                                <p className="text-red-500 text-xs mt-1">{errors.data_acordo.message as string}</p>
                            )}
                        </div>

                        {/* Observações */}
                        <div>
                            <label className="block text-sm font-medium mb-2">Observações</label>
                            <textarea
                                {...register('observacoes')}
                                rows={3}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                                placeholder="Detalhes do acordo..."
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
                            disabled={loading || (viabilidade && !viabilidade.viavel)}
                            className="flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary/90 rounded-lg transition-colors font-medium disabled:opacity-50"
                        >
                            <Save className="w-4 h-4" />
                            {loading ? 'Salvando...' : 'Registrar Acordo'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
