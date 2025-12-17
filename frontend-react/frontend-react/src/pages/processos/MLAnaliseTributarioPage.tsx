import { useState, useEffect } from 'react';
import { Brain, TrendingUp, Target, Clock, RefreshCw, AlertCircle, Calculator } from 'lucide-react';
import api from '../../lib/api';
import SimuladorPreditivo from '../../components/ml/SimuladorPreditivo';

interface Processo {
    id_processo: number;
    pasta: string;
    numero_cnj?: string;
    titulo?: string;
}

interface PredicaoML {
    processo_id: number;
    valor_contingencia_predito: number;
    confianca: number;
    modelo_versao: string;
    modelo_algoritmo: string;
    risco_predito?: string;
    data_predicao?: string;
}

export default function MLAnaliseTributarioPage() {
    const [activeTab, setActiveTab] = useState<'analise' | 'simulador'>('analise');

    // Estados Tab Análise
    const [processos, setProcessos] = useState<Processo[]>([]);
    const [processoSelecionado, setProcessoSelecionado] = useState<number | null>(null);
    const [predicao, setPredicao] = useState<PredicaoML | null>(null);
    const [historico, setHistorico] = useState<PredicaoML[]>([]);
    const [carregando, setCarregando] = useState(false);
    const [analisando, setAnalisando] = useState(false);

    useEffect(() => {
        carregarProcessos();
    }, []);

    useEffect(() => {
        if (processoSelecionado) {
            carregarHistorico(processoSelecionado);
        }
    }, [processoSelecionado]);

    const carregarProcessos = async () => {
        setCarregando(true);
        try {
            const response = await api.get('/api/processos', {
                params: { natureza_id: 1, per_page: 50 }
            });
            setProcessos(response.data.items || []);
        } catch (error) {
            console.error('Erro ao carregar processos:', error);
        } finally {
            setCarregando(false);
        }
    };

    const carregarHistorico = async (processoId: number) => {
        try {
            const response = await api.get(`/api/ml/tributario/historico/${processoId}`);
            setHistorico(response.data.predicoes || []);
            // Correcao: backend retorna { predicoes: [...] }

            if (response.data.predicoes && response.data.predicoes.length > 0) {
                setPredicao(response.data.predicoes[0]);
            }
        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
            setHistorico([]);
        }
    };

    const analisarProcesso = async () => {
        if (!processoSelecionado) return;

        setAnalisando(true);
        try {
            const response = await api.post('/api/ml/tributario/predict', {
                processo_id: processoSelecionado
            });
            setPredicao(response.data);
            await carregarHistorico(processoSelecionado);
            alert('Análise ML concluída com sucesso!');
        } catch (error: any) {
            console.error('Erro na análise ML:', error);
            // Fallback para demo se backend falhar
            alert('Aviso: Backend indisponível, simulando resposta.');
            const mock = {
                processo_id: processoSelecionado,
                valor_contingencia_predito: Math.random() * 500000,
                confianca: 0.85,
                modelo_versao: "v2.0-fallback",
                modelo_algoritmo: "xgboost",
                risco_predito: "Médio",
                data_predicao: new Date().toISOString()
            };
            setPredicao(mock);
        } finally {
            setAnalisando(false);
        }
    };

    const formatarMoeda = (valor: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
    };

    const formatarData = (data: string) => {
        return new Date(data).toLocaleString('pt-BR');
    };

    const getRiscoColor = (risco?: string) => {
        switch (risco?.toLowerCase()) {
            case 'baixo': return 'text-green-500';
            case 'medio': case 'médio': return 'text-yellow-500';
            case 'alto': return 'text-red-500';
            default: return 'text-gray-500';
        }
    };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            <div>
                <h1 className="text-3xl font-bold flex items-center gap-3">
                    <Brain className="w-8 h-8 text-primary" />
                    Análise ML - Tributário
                </h1>
                <p className="text-muted-foreground mt-2">
                    Inteligência Artificial aplicada à gestão de risco e previsibilidade processual
                </p>
            </div>

            {/* Tabs Navigation */}
            <div className="flex border-b border-border">
                <button
                    onClick={() => setActiveTab('analise')}
                    className={`px-6 py-3 font-medium text-sm flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'analise'
                            ? 'border-primary text-primary'
                            : 'border-transparent text-muted-foreground hover:text-foreground'
                        }`}
                >
                    <Target className="w-4 h-4" />
                    Análise de Processo
                </button>
                <button
                    onClick={() => setActiveTab('simulador')}
                    className={`px-6 py-3 font-medium text-sm flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'simulador'
                            ? 'border-primary text-primary'
                            : 'border-transparent text-muted-foreground hover:text-foreground'
                        }`}
                >
                    <Calculator className="w-4 h-4" />
                    Simulador What-If
                </button>
            </div>

            {/* Content Area */}
            <div className="min-h-[500px]">
                {activeTab === 'analise' ? (
                    <div className="space-y-6 animate-in fade-in duration-300">
                        {/* Seção Análise de Processo (Existente) */}
                        <div className="bg-card border border-border rounded-xl p-6">
                            <h2 className="text-xl font-bold mb-4">Selecionar Processo</h2>

                            <div className="flex gap-4">
                                <select
                                    value={processoSelecionado || ''}
                                    onChange={(e) => {
                                        const id = parseInt(e.target.value);
                                        setProcessoSelecionado(id || null);
                                        setPredicao(null);
                                    }}
                                    className="flex-1 bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none"
                                    disabled={carregando}
                                >
                                    <option value="">
                                        {carregando ? 'Carregando...' : 'Selecione um processo tributário...'}
                                    </option>
                                    {processos.map(p => (
                                        <option key={p.id_processo} value={p.id_processo}>
                                            {p.pasta} - {p.numero_cnj || p.titulo || 'Sem título'}
                                        </option>
                                    ))}
                                </select>

                                <button
                                    onClick={analisarProcesso}
                                    disabled={!processoSelecionado || analisando}
                                    className="px-6 py-2.5 bg-primary hover:bg-primary/90 text-white rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {analisando ? (
                                        <>
                                            <RefreshCw className="w-4 h-4 animate-spin" />
                                            Analisando...
                                        </>
                                    ) : (
                                        <>
                                            <Brain className="w-4 h-4" />
                                            Analisar com ML
                                        </>
                                    )}
                                </button>
                            </div>

                            {!processoSelecionado && (
                                <div className="mt-4 flex items-start gap-3 text-sm text-muted-foreground bg-accent rounded-lg p-4">
                                    <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                                    <p>
                                        Selecione um processo tributário para visualizar predições existentes
                                        ou realizar uma nova análise ML. O modelo XGBoost analisa 19+ features
                                        para prever o valor de contingência.
                                    </p>
                                </div>
                            )}
                        </div>

                        {predicao && (
                            <div className="bg-gradient-to-br from-primary/10 to-primary/5 border-2 border-primary/30 rounded-xl p-6">
                                <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                                    <Target className="w-6 h-6 text-primary" />
                                    Resultado da Análise ML
                                </h2>

                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                    <div className="bg-card border border-border rounded-lg p-6">
                                        <div className="text-sm text-muted-foreground mb-2">Valor Contingência Predito</div>
                                        <div className="text-3xl font-bold text-primary">
                                            {formatarMoeda(predicao.valor_contingencia_predito)}
                                        </div>
                                    </div>

                                    <div className="bg-card border border-border rounded-lg p-6">
                                        <div className="text-sm text-muted-foreground mb-2">Confiança do Modelo</div>
                                        <div className="text-3xl font-bold text-green-500">
                                            {(predicao.confianca * 100).toFixed(1)}%
                                        </div>
                                        <div className="w-full bg-accent rounded-full h-2 mt-3">
                                            <div
                                                className="bg-green-500 rounded-full h-2 transition-all"
                                                style={{ width: `${predicao.confianca * 100}%` }}
                                            />
                                        </div>
                                    </div>

                                    {predicao.risco_predito && (
                                        <div className="bg-card border border-border rounded-lg p-6">
                                            <div className="text-sm text-muted-foreground mb-2">Classificação de Risco</div>
                                            <div className={`text-3xl font-bold ${getRiscoColor(predicao.risco_predito)}`}>
                                                {predicao.risco_predito}
                                            </div>
                                        </div>
                                    )}
                                </div>

                                <div className="mt-6 pt-6 border-t border-border text-sm text-muted-foreground">
                                    <div className="flex items-center gap-6 flex-wrap">
                                        <div>
                                            <strong>Modelo:</strong> {predicao.modelo_algoritmo}
                                        </div>
                                        <div>
                                            <strong>Versão:</strong> {predicao.modelo_versao}
                                        </div>
                                        {predicao.data_predicao && (
                                            <div className="flex items-center gap-1">
                                                <Clock className="w-4 h-4" />
                                                {formatarData(predicao.data_predicao)}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}

                        {processoSelecionado && historico.length > 0 && (
                            <div className="bg-card border border-border rounded-xl p-6">
                                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                                    <TrendingUp className="w-5 h-5" />
                                    Histórico de Predições
                                </h2>

                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead>
                                            <tr className="border-b border-border">
                                                <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Data</th>
                                                <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">Valor Predito</th>
                                                <th className="text-center py-3 px-4 text-sm font-medium text-muted-foreground">Confiança</th>
                                                <th className="text-center py-3 px-4 text-sm font-medium text-muted-foreground">Modelo</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {historico.slice(0, 10).map((item, index) => (
                                                <tr key={index} className="border-b border-border/50 hover:bg-accent/50">
                                                    <td className="py-3 px-4 text-sm">
                                                        {item.data_predicao ? formatarData(item.data_predicao) : '-'}
                                                    </td>
                                                    <td className="py-3 px-4 text-sm text-right font-medium">
                                                        {formatarMoeda(item.valor_contingencia_predito)}
                                                    </td>
                                                    <td className="py-3 px-4 text-sm text-center">
                                                        {(item.confianca * 100).toFixed(1)}%
                                                    </td>
                                                    <td className="py-3 px-4 text-sm text-center text-muted-foreground">
                                                        {item.modelo_versao}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="animate-in fade-in duration-300 py-6">
                        {/* Seção Simulador (Novo) */}
                        <div className="mb-6">
                            <h2 className="text-xl font-bold mb-2">Simulador de Cenários Tributários</h2>
                            <p className="text-muted-foreground">
                                Simule variações de comarca, juiz e valores para entender o impacto no risco de contingência.
                                Os dados simulados não são salvos no histórico do processo.
                            </p>
                        </div>
                        <SimuladorPreditivo />
                    </div>
                )}
            </div>
        </div>
    );
}
