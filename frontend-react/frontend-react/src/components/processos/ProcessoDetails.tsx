/**
 * ProcessoDetails - Visualização Completa do Processo
 * Tabs: Geral, Específico, Prognóstico, Histórico
 */
import { useState, useEffect } from 'react';
import { Processo } from '../../types/processos';
import api from '../../lib/api';
import { FileText, DollarSign, Calendar, Building2, TrendingUp, History, X } from 'lucide-react';
import QuickPredictCard from './QuickPredictCard';
import TesesAssociadasSection from './TesesAssociadasSection';
import PrognosticoTab from './PrognosticoTab';


interface ProcessoDetailsProps {
    processoId: number;
    onClose: () => void;
}

export default function ProcessoDetails({ processoId, onClose }: ProcessoDetailsProps) {
    const [processo, setProcesso] = useState<Processo | null>(null);
    const [activeTab, setActiveTab] = useState('geral');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchProcesso();
    }, [processoId]);

    const fetchProcesso = async () => {
        try {
            const response = await api.get(`/api/processos/${processoId}`);
            setProcesso(response.data);
        } catch (error) {
            console.error('Erro ao carregar processo:', error);
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (value?: number) => {
        if (!value) return 'R$ 0,00';
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };

    const formatDate = (dateString?: string) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString('pt-BR');
    };

    if (loading) {
        return (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div className="bg-card rounded-xl p-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto"></div>
                </div>
            </div>
        );
    }

    if (!processo) return null;

    const tabs = [
        { id: 'geral', label: 'Geral', icon: FileText },
        { id: 'valores', label: 'Valores', icon: DollarSign },
        { id: 'especifico', label: 'Específico', icon: Building2 },
        { id: 'prognostico', label: 'Prognóstico', icon: TrendingUp }
    ];

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-card border border-border rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="bg-gradient-to-r from-primary/20 to-primary/5 border-b border-border p-6">
                    <div className="flex items-start justify-between">
                        <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="p-2 bg-primary/20 rounded-lg">
                                    <FileText className="w-5 h-5 text-primary" />
                                </div>
                                <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs font-medium">
                                    {processo.natureza_id === 1 ? 'Tributário' : processo.natureza_id === 2 ? 'Trabalhista' : 'Cível'}
                                </span>
                            </div>
                            <h2 className="text-2xl font-bold mb-1">{processo.titulo || processo.pasta}</h2>
                            <p className="text-muted-foreground text-sm">Pasta: {processo.pasta}</p>
                            {processo.numero_cnj && (
                                <p className="text-muted-foreground text-sm font-mono">CNJ: {processo.numero_cnj}</p>
                            )}
                        </div>

                        <button onClick={onClose} className="p-2 hover:bg-accent rounded-lg transition-colors">
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Tabs */}
                <div className="border-b border-border px-6">
                    <div className="flex gap-1">
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${activeTab === tab.id
                                    ? 'border-primary text-primary font-medium'
                                    : 'border-transparent text-muted-foreground hover:text-foreground'
                                    }`}
                            >
                                <tab.icon className="w-4 h-4" />
                                {tab.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    {activeTab === 'geral' && (
                        <div className="space-y-6">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm text-muted-foreground">Status</label>
                                    <p className="font-medium">Ativo</p>
                                </div>
                                <div>
                                    <label className="text-sm text-muted-foreground">Data Criação</label>
                                    <p className="font-medium">{formatDate(processo.data_criacao)}</p>
                                </div>
                                {processo.data_distribuicao && (
                                    <div>
                                        <label className="text-sm text-muted-foreground">Data Distribuição</label>
                                        <p className="font-medium">{formatDate(processo.data_distribuicao)}</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {activeTab === 'valores' && (
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            <div className="lg:col-span-2 space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4">
                                        <label className="text-sm text-muted-foreground">Valor da Causa</label>
                                        <p className="text-2xl font-bold text-green-400">{formatCurrency(processo.valor_causa)}</p>
                                    </div>
                                    <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
                                        <label className="text-sm text-muted-foreground">Contingência</label>
                                        <p className="text-2xl font-bold text-blue-400">{formatCurrency(processo.contingencia)}</p>
                                    </div>
                                </div>
                            </div>

                            {/* QuickPredict ML - Sidebar */}
                            {processo.natureza_id === 1 && (
                                <div className="lg:col-span-1">
                                    <QuickPredictCard processoId={processoId} />
                                </div>
                            )}
                        </div>
                    )}


                    {activeTab === 'especifico' && (
                        <div>
                            {processo.natureza_id === 1 && (
                                <TesesAssociadasSection
                                    processoId={processoId}
                                    tributoId={processo.tributario?.tributo_id}
                                />
                            )}
                            {processo.natureza_id === 2 && (
                                <div className="text-center py-8 text-muted-foreground">
                                    Dados específicos trabalhistas aparecerão aqui
                                </div>
                            )}
                            {processo.natureza_id === 3 && (
                                <div className="text-center py-8 text-muted-foreground">
                                    Dados específicos cíveis aparecerão aqui
                                </div>
                            )}
                        </div>
                    )}


                    {activeTab === 'prognostico' && (
                        <div>
                            {processo.natureza_id === 1 && (
                                <PrognosticoTab processoId={processoId} />
                            )}
                            {processo.natureza_id !== 1 && (
                                <div className="text-center py-8 text-muted-foreground">
                                    Prognóstico disponível apenas para processos tributários
                                </div>
                            )}
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
}
