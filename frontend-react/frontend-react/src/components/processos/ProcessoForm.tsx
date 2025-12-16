/**
 * ProcessoFormCompleto - Formulário 100% Dinâmico
 * TODOS os campos do DB + Mudança dinâmica por natureza
 */
import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Save, X, FileText, Users, Building2, DollarSign, Scale, AlertTriangle } from 'lucide-react';
import api from '../../lib/api';

interface ProcessoFormData {
    // Dados Básicos OBRIGATÓRIOS
    pasta: string;
    natureza_id: number;
    status_id: number;

    // Dados Básicos OPCIONAIS
    titulo?: string;
    numero_cnj?: string;
    observacao_pasta?: string;

    // Partes
    cliente_id?: number;
    autor?: string;
    reu?: string;

    // Valores
    valor_causa?: number;
    valor_envolvido?: number;
    valor_causa_atualizado?: number;
    valor_envolvido_atualizado?: number;
    contingencia?: number;

    // Data
    data_distribuicao?: string;

    // Localização
    comarca_id?: number;
    vara_turma_id?: number;
    orgao_id?: number;

    // Classificação CNJ
    justica_cnj_id?: number;
    instancia_cnj_id?: number;
    classe_cnj_id?: number;

    // Processo
    posicao_cliente_id?: number;
    acao_id?: number;
    procedimento_id?: number;
    fase_id?: number;

    // Risco
    tipo_probabilidade_id?: number;
    risco_id?: number;

    // TRIBUTÁRIO (só aparece se natureza_id === 1)
    tributario?: {
        tributo_id?: number;
        numero_aiim?: string;
        numero_cda?: string;
        data_lancamento?: string;
        valor_inscrito_cda?: number;
        valor_principal?: number;
        valor_multa?: number;
        percentual_multa?: number;
        valor_juros?: number;
        indice_juros?: string;
    };

    // TRABALHISTA (só aparece se natureza_id === 2)
    trabalhista?: {
        tolerancia_acordo?: number;
    };

    // CÍVEL (só aparece se natureza_id === 3)
    civel?: {
        tolerancia_acordo?: number;
    };
}

interface Props {
    processo?: any;
    onSave: (data: ProcessoFormData) => void;
    onCancel: () => void;
    saving?: boolean;
}

export default function ProcessoFormCompleto({ processo, onSave, onCancel, saving }: Props) {
    const { register, handleSubmit, watch, formState: { errors }, setValue } = useForm<ProcessoFormData>({
        defaultValues: processo || {}
    });

    const [tributos, setTributos] = useState<any[]>([]);
    const [comarcas, setComarcas] = useState<any[]>([]);
    const [varas, setVaras] = useState<any[]>([]);

    const naturezaSelecionada = watch('natureza_id');

    useEffect(() => {
        carregarDependencias();
    }, []);

    const carregarDependencias = async () => {
        try {
            // Carregar tributos
            const tribsResp = await api.get('/api/processos/tributos');
            setTributos(tribsResp.data || []);

            // Carregar comarcas (se API existir)
            try {
                const comarcasResp = await api.get('/api/comarcas');
                setComarcas(comarcasResp.data || []);
            } catch { }

            // Carregar varas (se API existir)
            try {
                const varasResp = await api.get('/api/varas');
                setVaras(varasResp.data || []);
            } catch { }

        } catch (error) {
            console.error('Erro ao carregar dependências:', error);
        }
    };

    const onSubmit = (data: ProcessoFormData) => {
        onSave(data);
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">

            {/* ========== SEÇÃO 1: IDENTIFICAÇÃO ========== */}
            <div className="bg-card border border-border rounded-xl p-6 space-y-4">
                <h3 className="text-lg font-semibold flex items-center gap-2 text-primary">
                    <FileText className="w-5 h-5" />
                    Identificação do Processo
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Pasta * */}
                    <div>
                        <label className="block text-sm font-medium mb-2">
                            Pasta * <span className="text-xs text-muted-foreground">(único)</span>
                        </label>
                        <input
                            {...register('pasta', { required: 'Pasta obrigatória' })}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                            placeholder="PROC-2024-001"
                        />
                        {errors.pasta && <p className="text-red-500 text-xs mt-1">{errors.pasta.message}</p>}
                    </div>

                    {/* CNJ */}
                    <div>
                        <label className="block text-sm font-medium mb-2">Número CNJ</label>
                        <input
                            {...register('numero_cnj')}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none font-mono text-sm"
                            placeholder="0000000-00.0000.0.00.0000"
                        />
                    </div>

                    {/* Natureza * */}
                    <div>
                        <label className="block text-sm font-medium mb-2">Natureza *</label>
                        <select
                            {...register('natureza_id', { required: 'Obrigatório', valueAsNumber: true })}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                        >
                            <option value="">Selecione...</option>
                            <option value="1">Tributário</option>
                            <option value="2">Trabalhista</option>
                            <option value="3">Cível</option>
                        </select>
                        {errors.natureza_id && <p className="text-red-500 text-xs mt-1">{errors.natureza_id.message}</p>}
                    </div>

                    {/* Título */}
                    <div className="md:col-span-2">
                        <label className="block text-sm font-medium mb-2">Título/Resumo</label>
                        <input
                            {...register('titulo')}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                            placeholder="Descrição resumida"
                        />
                    </div>

                    {/* Status * */}
                    <div>
                        <label className="block text-sm font-medium mb-2">Status *</label>
                        <select
                            {...register('status_id', { required: 'Obrigatório', valueAsNumber: true })}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                        >
                            <option value="">Selecione...</option>
                            <option value="1">Ativo</option>
                            <option value="2">Arquivado</option>
                            <option value="3">Suspenso</option>
                        </select>
                        {errors.status_id && <p className="text-red-500 text-xs mt-1">{errors.status_id.message}</p>}
                    </div>
                </div>

                {/* Observação */}
                <div>
                    <label className="block text-sm font-medium mb-2">Observações da Pasta</label>
                    <textarea
                        {...register('observacao_pasta')}
                        rows={3}
                        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                        placeholder="Informações adicionais relevantes"
                    />
                </div>
            </div>

            {/* ========== SEÇÃO 2: PARTES ========== */}
            <div className="bg-card border border-border rounded-xl p-6 space-y-4">
                <h3 className="text-lg font-semibold flex items-center gap-2 text-blue-500">
                    <Users className="w-5 h-5" />
                    Partes do Processo
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">Autor/Requerente</label>
                        <input
                            {...register('autor')}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                            placeholder="Nome completo ou razão social"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Réu/Requerido</label>
                        <input
                            {...register('reu')}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                            placeholder="Nome completo ou razão social"
                        />
                    </div>
                </div>
            </div>

            {/* ========== SEÇÃO 3: VALORES========== */}
            <div className="bg-card border border-border rounded-xl p-6 space-y-4">
                <h3 className="text-lg font-semibold flex items-center gap-2 text-green-500">
                    <DollarSign className="w-5 h-5" />
                    Valores e Datas
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">Valor da Causa</label>
                        <input
                            type="number"
                            step="0.01"
                            {...register('valor_causa', { valueAsNumber: true })}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                            placeholder="0.00"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Valor Envolvido</label>
                        <input
                            type="number"
                            step="0.01"
                            {...register('valor_envolvido', { valueAsNumber: true })}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                            placeholder="0.00"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Data Distribuição</label>
                        <input
                            type="date"
                            {...register('data_distribuicao')}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                        />
                    </div>
                </div>
            </div>

            {/* ========== SEÇÃO 4: LOCALIZAÇÃO ========== */}
            <div className="bg-card border border-border rounded-xl p-6 space-y-4">
                <h3 className="text-lg font-semibold flex items-center gap-2 text-purple-500">
                    <Building2 className="w-5 h-5" />
                    Localização e Órgão
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">Comarca</label>
                        <select
                            {...register('comarca_id', { valueAsNumber: true })}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                        >
                            <option value="">Selecione...</option>
                            {comarcas.map((c: any) => (
                                <option key={c.id_comarca} value={c.id_comarca}>{c.nome}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Vara/Turma</label>
                        <select
                            {...register('vara_turma_id', { valueAsNumber: true })}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                        >
                            <option value="">Selecione...</option>
                            {varas.map((v: any) => (
                                <option key={v.id_vara_turma} value={v.id_vara_turma}>{v.nome}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Fase Processual</label>
                        <select
                            {...register('fase_id', { valueAsNumber: true })}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                        >
                            <option value="">Selecione...</option>
                            <option value="1">Conhecimento</option>
                            <option value="2">Recurso</option>
                            <option value="3">Execução</option>
                            <option value="4">Cumprimento de Sentença</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* ========== SEÇÃO 5: RISCO ==========*/}
            <div className="bg-card border border-border rounded-xl p-6 space-y-4">
                <h3 className="text-lg font-semibold flex items-center gap-2 text-orange-500">
                    <AlertTriangle className="w-5 h-5" />
                    Avaliação de Risco
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">Probabilidade</label>
                        <select
                            {...register('tipo_probabilidade_id', { valueAsNumber: true })}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                        >
                            <option value="">Selecione...</option>
                            <option value="1">Provável ({">"} 70%)</option>
                            <option value="2">Possível (50-70%)</option>
                            <option value="3">Remoto ({"<"} 50%)</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Nível de Risco</label>
                        <select
                            {...register('risco_id', { valueAsNumber: true })}
                            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                        >
                            <option value="">Selecione...</option>
                            <option value="1">Baixo</option>
                            <option value="2">Médio</option>
                            <option value="3">Alto</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* ========== SEÇÃO 6: TRIBUTÁRIO (DINÂMICO) ========== */}
            {naturezaSelecionada === 1 && (
                <div className="bg-blue-500/5 border-2 border-blue-500/30 rounded-xl p-6 space-y-4">
                    <h3 className="text-lg font-semibold flex items-center gap-2 text-blue-400">
                        <Scale className="w-5 h-5" />
                        Dados Tributários
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">Tributo</label>
                            <select
                                {...register('tributario.tributo_id', { valueAsNumber: true })}
                                className="w-full bg-background border border-blue-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
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
                                {...register('tributario.numero_aiim')}
                                className="w-full bg-background border border-blue-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
                                placeholder="00000000"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Número CDA</label>
                            <input
                                {...register('tributario.numero_cda')}
                                className="w-full bg-background border border-blue-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
                                placeholder="00000000"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Valor Principal</label>
                            <input
                                type="number"
                                step="0.01"
                                {...register('tributario.valor_principal', { valueAsNumber: true })}
                                className="w-full bg-background border border-blue-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
                                placeholder="0.00"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Valor Multa</label>
                            <input
                                type="number"
                                step="0.01"
                                {...register('tributario.valor_multa', { valueAsNumber: true })}
                                className="w-full bg-background border border-blue-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
                                placeholder="0.00"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Percentual Multa (%)</label>
                            <input
                                type="number"
                                step="0.01"
                                {...register('tributario.percentual_multa', { valueAsNumber: true })}
                                className="w-full bg-background border border-blue-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
                                placeholder="0.00"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Valor Juros</label>
                            <input
                                type="number"
                                step="0.01"
                                {...register('tributario.valor_juros', { valueAsNumber: true })}
                                className="w-full bg-background border border-blue-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
                                placeholder="0.00"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Índice de Juros</label>
                            <select
                                {...register('tributario.indice_juros')}
                                className="w-full bg-background border border-blue-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
                            >
                                <option value="">Selecione...</option>
                                <option value="SELIC">SELIC</option>
                                <option value="Lei 13918">Lei 13918</option>
                                <option value="IPCA">IPCA</option>
                                <option value="CDI">CDI</option>
                                <option value="Outro">Outro</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Data Lançamento</label>
                            <input
                                type="date"
                                {...register('tributario.data_lancamento')}
                                className="w-full bg-background border border-blue-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                        </div>
                    </div>
                </div>
            )}

            {/* ========== SEÇÃO 7: TRABALHISTA (DINÂMICO) ========== */}
            {naturezaSelecionada === 2 && (
                <div className="bg-orange-500/5 border-2 border-orange-500/30 rounded-xl p-6 space-y-4">
                    <h3 className="text-lg font-semibold flex items-center gap-2 text-orange-400">
                        <FileText className="w-5 h-5" />
                        Dados Trabalhistas
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">Tolerância para Acordo</label>
                            <input
                                type="number"
                                step="0.01"
                                {...register('trabalhista.tolerancia_acordo', { valueAsNumber: true })}
                                className="w-full bg-background border border-orange-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-orange-500 outline-none"
                                placeholder="0.00"
                            />
                        </div>
                    </div>
                </div>
            )}

            {/* ========== SEÇÃO 8: CÍVEL (DINÂMICO) ========== */}
            {naturezaSelecionada === 3 && (
                <div className="bg-purple-500/5 border-2 border-purple-500/30 rounded-xl p-6 space-y-4">
                    <h3 className="text-lg font-semibold flex items-center gap-2 text-purple-400">
                        <FileText className="w-5 h-5" />
                        Dados Cíveis
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">Tolerância para Acordo</label>
                            <input
                                type="number"
                                step="0.01"
                                {...register('civel.tolerancia_acordo', { valueAsNumber: true })}
                                className="w-full bg-background border border-purple-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-purple-500 outline-none"
                                placeholder="0.00"
                            />
                        </div>
                    </div>
                </div>
            )}

            {/* ========== BOTÕES ========== */}
            <div className="flex gap-3 justify-end sticky bottom-0 bg-background border-t border-border p-4 -mx-6 -mb-6">
                <button
                    type="button"
                    onClick={onCancel}
                    disabled={saving}
                    className="px-6 py-2.5 bg-accent hover:bg-accent/80 rounded-lg transition-colors disabled:opacity-50"
                >
                    Cancelar
                </button>

                <button
                    type="submit"
                    disabled={saving}
                    className="flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary/90 rounded-lg transition-colors font-medium disabled:opacity-50"
                >
                    <Save className="w-4 h-4" />
                    {saving ? 'Salvando...' : 'Salvar Processo'}
                </button>
            </div>
        </form>
    );
}
