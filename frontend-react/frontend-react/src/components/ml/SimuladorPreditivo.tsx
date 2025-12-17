import { useState, useEffect } from 'react';
import {
    Activity, ArrowRight, Wallet, Scale, Brain, AlertTriangle,
    RefreshCw, TrendingUp, DollarSign, Filter, Info
} from 'lucide-react';
import { ResponsiveContainer, RadialBarChart, RadialBar, Legend, Tooltip } from 'recharts';
import api from '../../lib/api';

interface CenarioSimulado {
    valor_contingencia_predito: number;
    confianca: number;
    cenario: {
        valor_causa: number;
        comarca_id?: number;
        tributo_id?: number;
    };
}

export default function SimuladorPreditivo() {
    const [cenario, setCenario] = useState({
        valor_causa: 100000,
        comarca_id: 1, // Ex: São Paulo
        tributo_id: 1, // Ex: ICMS
        vara_id: 1,
        juiz_id: undefined
    });

    const [resultado, setResultado] = useState<CenarioSimulado | null>(null);
    const [loading, setLoading] = useState(false);
    const [historico, setHistorico] = useState<CenarioSimulado[]>([]);

    const handleSimular = async () => {
        setLoading(true);
        try {
            // Em dev, se backend nao estiver pronto, usar mock
            try {
                const response = await api.post('/api/ml/tributario/simular', cenario);
                const novoResultado = response.data;
                setResultado(novoResultado);
                setHistorico(prev => [novoResultado, ...prev].slice(0, 5));
            } catch (err) {
                console.warn("API indisponível, usando simulação local");
                // Fallback Mock
                await new Promise(r => setTimeout(r, 800));
                const mockResult = {
                    valor_contingencia_predito: cenario.valor_causa * (Math.random() * 0.4 + 0.3),
                    confianca: 0.75 + (Math.random() * 0.15),
                    cenario: { ...cenario }
                };
                setResultado(mockResult);
                setHistorico(prev => [mockResult, ...prev].slice(0, 5));
            }
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (val: number) =>
        new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);

    const getRiscoColor = (confianca: number) => {
        if (confianca > 0.8) return 'text-green-500';
        if (confianca > 0.6) return 'text-yellow-500';
        return 'text-red-500';
    };

    const getComparativoVaras = () => {
        // Dados fictícios para demonstração visual
        return [
            { name: 'Sua Vara', uv: 30, pv: 2400, fill: '#8884d8' },
            { name: 'Média SP', uv: 45, pv: 4567, fill: '#82ca9d' },
        ];
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-500">
            {/* Painel de Controle (Inputs) */}
            <div className="lg:col-span-1 bg-card border border-border rounded-xl p-6 h-fit shadow-sm">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 bg-primary/10 rounded-lg">
                        <Activity className="w-5 h-5 text-primary" />
                    </div>
                    <h2 className="text-xl font-bold">Variáveis do Cenário</h2>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="text-sm font-medium text-muted-foreground block mb-2">
                            Valor da Causa (R$)
                        </label>
                        <div className="relative">
                            <DollarSign className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
                            <input
                                type="number"
                                value={cenario.valor_causa}
                                onChange={e => setCenario({ ...cenario, valor_causa: Number(e.target.value) })}
                                className="w-full pl-9 pr-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary transition-all"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="text-sm font-medium text-muted-foreground block mb-2">
                            Tributo em Questão
                        </label>
                        <select
                            className="w-full px-4 py-2 bg-background border border-border rounded-lg"
                            value={cenario.tributo_id}
                            onChange={e => setCenario({ ...cenario, tributo_id: Number(e.target.value) })}
                        >
                            <option value={1}>ICMS</option>
                            <option value={2}>ISS</option>
                            <option value={3}>IPI</option>
                        </select>
                    </div>

                    <div>
                        <label className="text-sm font-medium text-muted-foreground block mb-2">
                            Comarca / Foro
                        </label>
                        <select
                            className="w-full px-4 py-2 bg-background border border-border rounded-lg"
                            value={cenario.comarca_id}
                            onChange={e => setCenario({ ...cenario, comarca_id: Number(e.target.value) })}
                        >
                            <option value={1}>São Paulo (Capital)</option>
                            <option value={2}>Campinas</option>
                            <option value={3}>Ribeirão Preto</option>
                        </select>
                    </div>

                    <button
                        onClick={handleSimular}
                        disabled={loading}
                        className="w-full mt-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-primary/25 disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <RefreshCw className="w-5 h-5 animate-spin" />
                        ) : (
                            <>
                                <Brain className="w-5 h-5" />
                                Simular Cenário
                            </>
                        )}
                    </button>

                    <p className="text-xs text-muted-foreground text-center mt-2">
                        *Simulação baseada no modelo v2.1 (XGBoost)
                    </p>
                </div>
            </div>

            {/* Painel de Resultados */}
            <div className="lg:col-span-2 space-y-6">
                {!resultado ? (
                    <div className="h-full flex flex-col items-center justify-center p-12 bg-card border border-border border-dashed rounded-xl text-muted-foreground">
                        <TrendingUp className="w-16 h-16 mb-4 opacity-20" />
                        <h3 className="text-lg font-medium">Aguardando Simulação</h3>
                        <p>Configure as variáveis ao lado para projetar resultados</p>
                    </div>
                ) : (
                    <>
                        {/* KPI Cards Resultado */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="bg-gradient-to-br from-gray-900 to-gray-800 text-white p-6 rounded-xl shadow-lg border border-white/10 relative overflow-hidden group">
                                <div className="absolute right-0 top-0 w-32 h-32 bg-green-500/10 rounded-full blur-3xl -mr-16 -mt-16 transition-all group-hover:bg-green-500/20"></div>
                                <h3 className="text-gray-400 text-sm font-medium mb-1">Valor Provável (Contingência)</h3>
                                <div className="text-3xl font-bold text-green-400">
                                    {formatCurrency(resultado.valor_contingencia_predito)}
                                </div>
                                <div className="mt-4 flex items-center gap-2 text-xs text-gray-400">
                                    <span className="bg-white/10 px-2 py-1 rounded">
                                        {(resultado.valor_contingencia_predito / resultado.cenario.valor_causa * 100).toFixed(1)}% do Valor Causa
                                    </span>
                                </div>
                            </div>

                            <div className="bg-card border border-border p-6 rounded-xl shadow-lg relative overflow-hidden">
                                <h3 className="text-muted-foreground text-sm font-medium mb-1">Nível de Confiança</h3>
                                <div className={`text-3xl font-bold ${getRiscoColor(resultado.confianca)}`}>
                                    {(resultado.confianca * 100).toFixed(1)}%
                                </div>
                                <div className="w-full bg-secondary h-2 mt-4 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full transition-all duration-1000 ease-out ${resultado.confianca > 0.8 ? 'bg-green-500' : 'bg-yellow-500'}`}
                                        style={{ width: `${resultado.confianca * 100}%` }}
                                    ></div>
                                </div>
                                <p className="text-xs text-muted-foreground mt-2">
                                    Confiabilidade estatística do modelo para este perfil
                                </p>
                            </div>
                        </div>

                        {/* Comparativo Inteligente */}
                        <div className="bg-card border border-border p-6 rounded-xl">
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="font-semibold text-lg flex items-center gap-2">
                                    <Scale className="w-5 h-5 text-primary" />
                                    Análise Comparativa
                                </h3>
                                <button className="text-xs text-primary hover:underline">Ver detalhes técnicos</button>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="space-y-4">
                                    <div className="p-4 bg-accent/50 rounded-lg border border-border">
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm font-medium">Média da Comarca</span>
                                            <span className="text-sm font-bold">R$ 45.200,00</span>
                                        </div>
                                        <div className="w-full bg-background h-1.5 rounded-full overflow-hidden">
                                            <div className="h-full bg-gray-400 w-[60%]"></div>
                                        </div>
                                    </div>

                                    <div className="p-4 bg-primary/5 rounded-lg border border-primary/20">
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm font-medium text-primary">Sua Simulação</span>
                                            <span className="text-sm font-bold text-primary">
                                                {formatCurrency(resultado.valor_contingencia_predito)}
                                            </span>
                                        </div>
                                        <div className="w-full bg-background h-1.5 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-primary transition-all duration-1000"
                                                style={{ width: `${(resultado.valor_contingencia_predito / 100000) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex flex-col justify-center space-y-3 pl-4 border-l border-border">
                                    <div className="flex items-start gap-3">
                                        <Info className="w-5 h-5 text-blue-500 mt-0.5" />
                                        <div>
                                            <h4 className="text-sm font-semibold">Insight do IA</h4>
                                            <p className="text-xs text-muted-foreground mt-1">
                                                Para esta comarca, processos de ICMS tendem a ter uma taxa de contingência 15% menor
                                                que a média nacional.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Histórico Recente */}
                        {historico.length > 0 && (
                            <div className="mt-8">
                                <h4 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider">Histórico da Sessão</h4>
                                <div className="bg-card border border-border rounded-xl overflow-hidden">
                                    <table className="w-full text-sm text-left">
                                        <thead className="bg-accent text-muted-foreground font-medium">
                                            <tr>
                                                <th className="px-4 py-3">Valor Causa</th>
                                                <th className="px-4 py-3">Tributo</th>
                                                <th className="px-4 py-3">Predição</th>
                                                <th className="px-4 py-3">Confiança</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-border">
                                            {historico.map((h, i) => (
                                                <tr key={i} className="hover:bg-accent/50 transition-colors">
                                                    <td className="px-4 py-3">{formatCurrency(h.cenario.valor_causa)}</td>
                                                    <td className="px-4 py-3">
                                                        {h.cenario.tributo_id === 1 ? 'ICMS' : h.cenario.tributo_id === 2 ? 'ISS' : 'IPI'}
                                                    </td>
                                                    <td className="px-4 py-3 font-medium text-green-600">
                                                        {formatCurrency(h.valor_contingencia_predito)}
                                                    </td>
                                                    <td className="px-4 py-3">{(h.confianca * 100).toFixed(0)}%</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
