/**
 * ProcessoFormComAbas - Formulário COM SISTEMA DE ABAS
 * Conforme solicitação do cliente
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

    // TRIBUTÁRIO
    tributario?: {
        tributo_id?: number;
        numero_aiim?: string;
        numero_cda?: string;
        data_lancamento?: string;
        valor_inscrito_cda?: number;
        valor_principal?: number;
        valor_multa?: number;
        percentual_multa?: number;
        base_calculo_multa?: string;
        valor_juros?: number;
        indice_juros?: string;
        vara_primeira_instancia_id?: number;
        turma_segunda_instancia_id?: number;
    };

    // TRABALHISTA
    trabalhista?: {
        tolerancia_acordo?: number;
        acordo_realizado?: number;
        data_acordo?: string;
        tese_provavel?: string;
        valor_provavel?: number;
        tese_possivel?: string;
        valor_possivel?: number;
        tese_remota?: string;
        valor_remoto?: number;
    };

    // CÍVEL
    civel?: {
        tolerancia_acordo?: number;
        acordo_realizado?: number;
        data_acordo?: string;
        tese_provavel?: string;
        valor_provavel?: number;
        tese_possivel?: string;
        valor_possivel?: number;
        tese_remota?: string;
        valor_remoto?: number;
    };
}

interface Props {
    processo?: any;
    onSave: (data: ProcessoFormData) => void;
    onCancel: () => void;
    saving?: boolean;
}

export default function ProcessoFormComAbas({ processo, onSave, onCancel, saving }: Props) {
    const { register, handleSubmit, watch, formState: { errors }, setValue } = useForm<ProcessoFormData>({
        defaultValues: processo || {}
    });

    const [activeTab, setActiveTab] = useState(0);
    const [tributos, setTributos] = useState<any[]>([]);
    const [clientes, setClientes] = useState<any[]>([]);
    const [comarcas, setComarcas] = useState<any[]>([]);
    const [varas, setVaras] = useState<any[]>([]);

    const naturezaSelecionada = watch('natureza_id');

    // Definir abas baseado na natureza
    const tabs = [
        { id: 0, label: 'Dados Básicos', icon: FileText, visible: true },
        { id: 1, label: 'Tributário', icon: Scale, visible: naturezaSelecionada === 1 },
        { id: 2, label: 'Trabalhista', icon: Users, visible: naturezaSelecionada === 2 },
        { id: 3, label: 'Cível', icon: Building2, visible: naturezaSelecionada === 3 }
    ].filter(tab => tab.visible);

    useEffect(() => {
        carregarDependencias();
    }, []);

    // Ajustar tab ativa quando natureza muda
    useEffect(() => {
        if (activeTab > 0 && !tabs.find(t => t.id === activeTab)) {
            setActiveTab(0);
        }
    }, [naturezaSelecionada]);

    const carregarDependencias = async () => {
        try {
            // Tributos
            const tribsResp = await api.get('/api/processos/tributos');
            setTributos(tribsResp.data || []);

            // Clientes
            try {
                const clientesResp = await api.get('/api/clientes');
                setClientes(clientesResp.data || []);
            } catch { }

            // Comarcas
            try {
                const comarcasResp = await api.get('/api/comarcas');
                setComarcas(comarcasResp.data || []);
            } catch { }

            // Varas
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
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col h-full">

            {/* TABS HEADER */}
            <div className="border-b border-border bg-card">
                <div className="flex gap-1 px-6 pt-4">
                    {tabs.map((tab) => {
                        const Icon = tab.icon;
                        return (
                            <button
                                key={tab.id}
                                type="button"
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center gap-2 px-6 py-3 rounded-t-lg transition-all ${activeTab === tab.id
                                    ? 'bg-background border-t border-x border-border text-primary font-semibold'
                                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                                    }`}
                            >
                                <Icon className="w-4 h-4" />
                                {tab.label}
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* TAB CONTENT */}
            <div className="flex-1 overflow-y-auto p-6 bg-background">

                {/* ========== TAB 0: DADOS BÁSICOS ========== */}
                {activeTab === 0 && (
                    <div className="space-y-6 max-w-5xl">

                        {/* Identificação */}
                        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
                            <h3 className="text-lg font-semibold flex items-center gap-2 text-primary">
                                <FileText className="w-5 h-5" />
                                Identificação do Processo
                            </h3>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2">Pasta *</label>
                                    <input
                                        {...register('pasta', { required: 'Pasta obrigatória' })}
                                        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                                        placeholder="PROC-2024-001"
                                    />
                                    {errors.pasta && <p className="text-red-500 text-xs mt-1">{errors.pasta.message}</p>}
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">Número CNJ</label>
                                    <input
                                        {...register('numero_cnj')}
                                        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none font-mono text-sm"
                                        placeholder="0000000-00.0000.0.00.0000"
                                    />
                                </div>

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

                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium mb-2">Título/Resumo</label>
                                    <input
                                        {...register('titulo')}
                                        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                                        placeholder="Descrição resumida (gerado automaticamente se vazio)"
                                    />
                                </div>

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

                        {/* Partes e Cliente */}
                        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
                            <h3 className="text-lg font-semibold flex items-center gap-2 text-blue-500">
                                <Users className="w-5 h-5" />
                                Cliente e Partes
                            </h3>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2">Cliente</label>
                                    <select
                                        {...register('cliente_id', { valueAsNumber: true })}
                                        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                                    >
                                        <option value="">Selecione...</option>
                                        {clientes.map((c: any) => (
                                            <option key={c.id} value={c.id}>{c.nome}</option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">Autor/Requerente</label>
                                    <input
                                        {...register('autor')}
                                        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                                        placeholder="Nome completo"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">Réu/Requerido</label>
                                    <input
                                        {...register('reu')}
                                        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                                        placeholder="Nome completo"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Valores */}
                        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
                            <h3 className="text-lg font-semibold flex items-center gap-2 text-green-500">
                                <DollarSign className="w-5 h-5" />
                                Valores e Data
                            </h3>

                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
                                    <label className="block text-sm font-medium mb-2">Contingência</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        {...register('contingencia', { valueAsNumber: true })}
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

                        {/* Localização */}
                        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
                            <h3 className="text-lg font-semibold flex items-center gap-2 text-purple-500">
                                <Building2 className="w-5 h-5" />
                                Localização
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

                        {/* Risco */}
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
                                        <option value="1">Provável ({">"}70%)</option>
                                        <option value="2">Possível (50-70%)</option>
                                        <option value="3">Remoto ({"<"}50%)</option>
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

                    </div>
                )}

                {/* ========== TAB 1: TRIBUTÁRIO ========== */}
                {activeTab === 1 && naturezaSelecionada === 1 && (
                    <div className="space-y-6 max-w-5xl">
                        <div className="bg-blue-500/5 border-2 border-blue-500/30 rounded-xl p-6 space-y-4">
                            <h3 className="text-2xl font-semibold flex items-center gap-2 text-blue-400">
                                <Scale className="w-6 h-6" />
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
                                            <option key={t.id_tributo} value={t.id_tributo}>{t.nome} ({t.codigo})</option>
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
                                    <label className="block text-sm font-medium mb-2">Valor Inscrito CDA</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        {...register('tributario.valor_inscrito_cda', { valueAsNumber: true })}
                                        className="w-full bg-background border border-blue-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
                                        placeholder="0.00"
                                    />
                                    <p className="text-xs text-muted-foreground mt-1">*Valor constante na CDA</p>
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
                                    <p className="text-xs text-muted-foreground mt-1">*Valor do imposto</p>
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
                                    <p className="text-xs text-muted-foreground mt-1">*Valor da multa</p>
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

                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium mb-2">Base de Cálculo da Multa</label>
                                    <input
                                        {...register('tributario.base_calculo_multa')}
                                        className="w-full bg-background border border-blue-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
                                        placeholder="Ex: valor do tributo, valor da operação"
                                    />
                                    <p className="text-xs text-muted-foreground mt-1">*Sobre qual valor incide o percentual da multa</p>
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

                            {/* Varas para Jurimetria */}
                            <div className="mt-6 pt-6 border-t border-blue-500/20">
                                <h4 className="text-lg font-semibold text-blue-300 mb-4">Varas para Jurimetria</h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium mb-2">Vara 1ª Instância</label>
                                        <select
                                            {...register('tributario.vara_primeira_instancia_id', { valueAsNumber: true })}
                                            className="w-full bg-background border border-blue-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
                                        >
                                            <option value="">Selecione...</option>
                                            {varas.map((v: any) => (
                                                <option key={v.id_vara_turma} value={v.id_vara_turma}>{v.nome}</option>
                                            ))}
                                        </select>
                                        <p className="text-xs text-muted-foreground mt-1">*Vara que julgou/julgará em 1ª instância</p>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium mb-2">Turma/Câmara 2ª Instância</label>
                                        <select
                                            {...register('tributario.turma_segunda_instancia_id', { valueAsNumber: true })}
                                            className="w-full bg-background border border-blue-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
                                        >
                                            <option value="">Selecione...</option>
                                            {varas.map((v: any) => (
                                                <option key={v.id_vara_turma} value={v.id_vara_turma}>{v.nome}</option>
                                            ))}
                                        </select>
                                        <p className="text-xs text-muted-foreground mt-1">*Turma que julgou/julgará em 2ª instância</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* ========== TAB 2: TRABALHISTA ========== */}
                {activeTab === 2 && naturezaSelecionada === 2 && (
                    <div className="space-y-6 max-w-5xl">
                        <div className="bg-orange-500/5 border-2 border-orange-500/30 rounded-xl p-6 space-y-6">
                            <h3 className="text-2xl font-semibold flex items-center gap-2 text-orange-400">
                                <Users className="w-6 h-6" />
                                Dados Trabalhistas
                            </h3>

                            {/* Acordo Trabalhista */}
                            <div>
                                <h4 className="text-lg font-semibold text-orange-300 mb-4">Acordo</h4>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium mb-2">Tolerância para Acordo</label>
                                        <input
                                            type="number"
                                            step="0.01"
                                            {...register('trabalhista.tolerancia_acordo', { valueAsNumber: true })}
                                            className="w-full bg-background border border-orange-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-orange-500 outline-none"
                                            placeholder="0.00"
                                        />
                                        <p className="text-xs text-muted-foreground mt-1">*Valor que o cliente está disposto a aceitar</p>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium mb-2">Acordo Realizado</label>
                                        <input
                                            type="number"
                                            step="0.01"
                                            {...register('trabalhista.acordo_realizado', { valueAsNumber: true })}
                                            className="w-full bg-background border border-orange-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-orange-500 outline-none"
                                            placeholder="0.00"
                                        />
                                        <p className="text-xs text-muted-foreground mt-1">*Valor do acordo efetivado</p>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium mb-2">Data do Acordo</label>
                                        <input
                                            type="date"
                                            {...register('trabalhista.data_acordo')}
                                            className="w-full bg-background border border-orange-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-orange-500 outline-none"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Prognóstico de Êxito Trabalhista */}
                            <div className="mt-6 pt-6 border-t border-orange-500/20">
                                <h4 className="text-lg font-semibold text-orange-300 mb-4">Prognóstico de Êxito</h4>
                                <p className="text-sm text-muted-foreground mb-4">
                                    Indique a expectativa real de ganho considerando a probabilidade de êxito de cada tese.
                                </p>

                                <div className="space-y-4">
                                    {/* Êxito Provável */}
                                    <div className="bg-background border border-green-500/30 rounded-lg p-4">
                                        <h5 className="text-md font-semibold text-green-400 mb-3">Êxito Provável ({">"}70%)</h5>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium mb-2">Tese</label>
                                                <textarea
                                                    {...register('trabalhista.tese_provavel')}
                                                    rows={2}
                                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-green-500 outline-none"
                                                    placeholder="Descreva a tese com alta probabilidade"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium mb-2">Valor</label>
                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    {...register('trabalhista.valor_provavel', { valueAsNumber: true })}
                                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-green-500 outline-none"
                                                    placeholder="0.00"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Êxito Possível */}
                                    <div className="bg-background border border-yellow-500/30 rounded-lg p-4">
                                        <h5 className="text-md font-semibold text-yellow-400 mb-3">Êxito Possível (50-70%)</h5>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium mb-2">Tese</label>
                                                <textarea
                                                    {...register('trabalhista.tese_possivel')}
                                                    rows={2}
                                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-yellow-500 outline-none"
                                                    placeholder="Descreva a tese com probabilidade moderada"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium mb-2">Valor</label>
                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    {...register('trabalhista.valor_possivel', { valueAsNumber: true })}
                                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-yellow-500 outline-none"
                                                    placeholder="0.00"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Êxito Remoto */}
                                    <div className="bg-background border border-red-500/30 rounded-lg p-4">
                                        <h5 className="text-md font-semibold text-red-400 mb-3">Êxito Remoto ({"<"}50%)</h5>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium mb-2">Tese</label>
                                                <textarea
                                                    {...register('trabalhista.tese_remota')}
                                                    rows={2}
                                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-red-500 outline-none"
                                                    placeholder="Descreva a tese com baixa probabilidade"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium mb-2">Valor</label>
                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    {...register('trabalhista.valor_remoto', { valueAsNumber: true })}
                                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-red-500 outline-none"
                                                    placeholder="0.00"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* ========== TAB 3: CÍVEL ========== */}
                {activeTab === 3 && naturezaSelecionada === 3 && (
                    <div className="space-y-6 max-w-5xl">
                        <div className="bg-purple-500/5 border-2 border-purple-500/30 rounded-xl p-6 space-y-6">
                            <h3 className="text-2xl font-semibold flex items-center gap-2 text-purple-400">
                                <Building2 className="w-6 h-6" />
                                Dados Cíveis
                            </h3>

                            {/* Acordo Cível */}
                            <div>
                                <h4 className="text-lg font-semibold text-purple-300 mb-4">Acordo</h4>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium mb-2">Tolerância para Acordo</label>
                                        <input
                                            type="number"
                                            step="0.01"
                                            {...register('civel.tolerancia_acordo', { valueAsNumber: true })}
                                            className="w-full bg-background border border-purple-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-purple-500 outline-none"
                                            placeholder="0.00"
                                        />
                                        <p className="text-xs text-muted-foreground mt-1">*Valor que o cliente está disposto a aceitar</p>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium mb-2">Acordo Realizado</label>
                                        <input
                                            type="number"
                                            step="0.01"
                                            {...register('civel.acordo_realizado', { valueAsNumber: true })}
                                            className="w-full bg-background border border-purple-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-purple-500 outline-none"
                                            placeholder="0.00"
                                        />
                                        <p className="text-xs text-muted-foreground mt-1">*Valor do acordo efetivado</p>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium mb-2">Data do Acordo</label>
                                        <input
                                            type="date"
                                            {...register('civel.data_acordo')}
                                            className="w-full bg-background border border-purple-500/30 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-purple-500 outline-none"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Prognóstico de Êxito Cível */}
                            <div className="mt-6 pt-6 border-t border-purple-500/20">
                                <h4 className="text-lg font-semibold text-purple-300 mb-4">Prognóstico de Êxito</h4>
                                <p className="text-sm text-muted-foreground mb-4">
                                    Indique a expectativa real de ganho considerando a probabilidade de êxito de cada tese.
                                </p>

                                <div className="space-y-4">
                                    {/* Êxito Provável */}
                                    <div className="bg-background border border-green-500/30 rounded-lg p-4">
                                        <h5 className="text-md font-semibold text-green-400 mb-3">Êxito Provável ({">"}70%)</h5>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium mb-2">Tese</label>
                                                <textarea
                                                    {...register('civel.tese_provavel')}
                                                    rows={2}
                                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-green-500 outline-none"
                                                    placeholder="Descreva a tese com alta probabilidade"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium mb-2">Valor</label>
                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    {...register('civel.valor_provavel', { valueAsNumber: true })}
                                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-green-500 outline-none"
                                                    placeholder="0.00"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Êxito Possível */}
                                    <div className="bg-background border border-yellow-500/30 rounded-lg p-4">
                                        <h5 className="text-md font-semibold text-yellow-400 mb-3">Êxito Possível (50-70%)</h5>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium mb-2">Tese</label>
                                                <textarea
                                                    {...register('civel.tese_possivel')}
                                                    rows={2}
                                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-yellow-500 outline-none"
                                                    placeholder="Descreva a tese com probabilidade moderada"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium mb-2">Valor</label>
                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    {...register('civel.valor_possivel', { valueAsNumber: true })}
                                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-yellow-500 outline-none"
                                                    placeholder="0.00"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Êxito Remoto */}
                                    <div className="bg-background border border-red-500/30 rounded-lg p-4">
                                        <h5 className="text-md font-semibold text-red-400 mb-3">Êxito Remoto ({"<"}50%)</h5>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium mb-2">Tese</label>
                                                <textarea
                                                    {...register('civel.tese_remota')}
                                                    rows={2}
                                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-red-500 outline-none"
                                                    placeholder="Descreva a tese com baixa probabilidade"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium mb-2">Valor</label>
                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    {...register('civel.valor_remoto', { valueAsNumber: true })}
                                                    className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-red-500 outline-none"
                                                    placeholder="0.00"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

            </div>

            {/* BOTÕES FOOTER */}
            <div className="border-t border-border bg-card p-4 flex items-center justify-between">
                <div className="flex gap-2">
                    {tabs.map((tab, index) => (
                        tab.id !== 0 && (
                            <button
                                key={tab.id}
                                type="button"
                                onClick={() => setActiveTab(index > 0 ? tabs[index - 1].id : 0)}
                                disabled={index === 0}
                                className="px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors disabled:opacity-50"
                            >
                                ← Anterior
                            </button>
                        )
                    ))}

                    {activeTab < tabs.length - 1 && (
                        <button
                            type="button"
                            onClick={() => {
                                const currentIndex = tabs.findIndex(t => t.id === activeTab);
                                if (currentIndex < tabs.length - 1) {
                                    setActiveTab(tabs[currentIndex + 1].id);
                                }
                            }}
                            className="px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors"
                        >
                            Próxima →
                        </button>
                    )}
                </div>

                <div className="flex gap-3">
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
            </div>

        </form>
    );
}
