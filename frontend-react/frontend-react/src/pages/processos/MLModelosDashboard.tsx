import { useState, useEffect } from 'react';
import { Brain, RefreshCw, TrendingUp, Database, Zap, AlertCircle, CheckCircle2, BarChart3, LineChart as LineChartIcon } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';
import api from '../../lib/api';

interface ModeloInfo {
    modelo_atual: string;
    algoritmo: string;
    features_importantes: Array<{
        nome: string;
        importancia: number;
    }>;
    metricas: {
        mae: number;
        r2: number;
        rmse: number;
    };
    hiperparametros?: any;
    amostras_treino?: number;
}

interface Modelo {
    versao: string;
    algoritmo: string;
    mae: number;
    r2: number;
    rmse?: number;
    data_criacao?: string; // ou data_treinamento
    data_treinamento?: string;
    ativo?: boolean;
}

interface DataStatus {
    total_processos: number;
    com_contingencia: number;
    com_features_completas: number;
    status: string;
}

export default function MLModelosDashboard() {
    const [modeloInfo, setModeloInfo] = useState<ModeloInfo | null>(null);
    const [modelos, setModelos] = useState<Modelo[]>([]);
    const [dataStatus, setDataStatus] = useState<DataStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [retraining, setRetraining] = useState(false);
    const [erro, setErro] = useState<string | null>(null);

    useEffect(() => {
        carregarDados();
    }, []);

    const carregarDados = async () => {
        setLoading(true);
        setErro(null);

        try {
            const [infoRes, modelsRes, statusRes] = await Promise.all([
                api.get('/api/ml/tributario/model-info'),
                api.get('/api/ml/tributario/models'),
                api.get('/api/ml/tributario/data-status')
            ]);

            setModeloInfo(infoRes.data);
            setModelos(modelsRes.data.models || []);
            setDataStatus(statusRes.data);
        } catch (error: any) {
            console.error('Erro ao carregar dados:', error);
            setErro(error.response?.data?.error || 'Erro ao carregar informações');
        } finally {
            setLoading(false);
        }
    };

    const handleRetreinar = async () => {
        if (!confirm('Deseja retreinar o modelo ML? Isso pode levar alguns minutos.')) {
            return;
        }

        setRetraining(true);
        try {
            const response = await api.post('/api/ml/tributario/retrain');
            alert(`Modelo retreinado com sucesso!\nNova versão: ${response.data.version}\nMAE: ${response.data.metrics.mae}\nR²: ${response.data.metrics.r2_score}`);
            await carregarDados();
        } catch (error: any) {
            console.error('Erro ao retreinar:', error);
            alert(error.response?.data?.error || 'Erro ao retreinar modelo');
        } finally {
            setRetraining(false);
        }
    };

    // Dados para gráficos
    const featureData = modeloInfo?.features_importantes.slice(0, 7).map(f => ({
        name: f.nome.replace(/_/g, ' '),
        importance: (f.importancia * 100).toFixed(1)
    })) || [];

    // Dados para histórico (invertendo para ordem cronológica)
    const historyData = [...modelos].reverse().map(m => ({
        versao: m.versao,
        r2: (m.r2 || 0) * 100,
        mae: m.mae || 0
    }));

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="text-center space-y-4">
                    <RefreshCw className="w-12 h-12 animate-spin text-primary mx-auto" />
                    <p className="text-muted-foreground">Carregando informações ML...</p>
                </div>
            </div>
        );
    }

    if (erro) {
        return (
            <div className="p-6">
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-center">
                    <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                    <p className="text-red-400 font-semibold">{erro}</p>
                    <button
                        onClick={carregarDados}
                        className="mt-4 px-6 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors"
                    >
                        Tentar Novamente
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 p-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <Brain className="w-8 h-8 text-primary" />
                        Dashboard Modelos ML
                    </h1>
                    <p className="text-muted-foreground mt-1">
                        Gerenciamento e monitoramento de modelos de Machine Learning
                    </p>
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={carregarDados}
                        className="px-4 py-3 bg-accent hover:bg-accent/80 rounded-lg transition-colors"
                        title="Atualizar Dados"
                    >
                        <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                    <button
                        onClick={handleRetreinar}
                        disabled={retraining}
                        className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white rounded-lg font-semibold shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {retraining ? (
                            <>
                                <RefreshCw className="w-5 h-5 animate-spin" />
                                Retreinando...
                            </>
                        ) : (
                            <>
                                <Zap className="w-5 h-5" />
                                Re-treinar Modelo
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* KPI Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {/* Modelo Atual Info */}
                <div className="bg-card border border-border rounded-xl p-6 col-span-1 md:col-span-2">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                            <Brain className="w-5 h-5 text-primary" />
                            <h3 className="font-semibold text-lg">Modelo Ativo</h3>
                        </div>
                        <span className="bg-green-500/20 text-green-600 text-xs px-2 py-1 rounded-full font-bold">
                            {modeloInfo?.modelo_atual}
                        </span>
                    </div>

                    <div className="grid grid-cols-3 gap-4 text-center">
                        <div className="p-3 bg-accent rounded-lg">
                            <div className="text-sm text-muted-foreground">R² Score</div>
                            <div className="text-2xl font-bold text-blue-500">
                                {modeloInfo?.metricas.r2.toFixed(3)}
                            </div>
                        </div>
                        <div className="p-3 bg-accent rounded-lg">
                            <div className="text-sm text-muted-foreground">Erro Médio (MAE)</div>
                            <div className="text-2xl font-bold text-red-500">
                                R$ {modeloInfo?.metricas.mae.toFixed(0)}
                            </div>
                        </div>
                        <div className="p-3 bg-accent rounded-lg">
                            <div className="text-sm text-muted-foreground">Treinado Em</div>
                            <div className="text-sm font-semibold mt-1">
                                {modelos.find(m => m.versao === modeloInfo?.modelo_atual)?.data_treinamento
                                    ? new Date(modelos.find(m => m.versao === modeloInfo?.modelo_atual)!.data_treinamento!).toLocaleDateString()
                                    : '-'}
                            </div>
                        </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-border flex justify-between text-sm text-muted-foreground">
                        <span>Algoritmo: <strong>{modeloInfo?.algoritmo}</strong></span>
                        <span>Amostras Treino: <strong>{modeloInfo?.amostras_treino || '-'}</strong></span>
                    </div>
                </div>

                {/* Status Dados */}
                {dataStatus && (
                    <div className="bg-card border border-border rounded-xl p-6 col-span-1 md:col-span-2">
                        <div className="flex items-center gap-2 mb-4">
                            <Database className="w-5 h-5 text-blue-500" />
                            <h3 className="font-semibold text-lg">Saúde dos Dados</h3>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between text-sm mb-1">
                                    <span>Cobertura de Contingência</span>
                                    <span className="font-bold">{((dataStatus.com_contingencia / dataStatus.total_processos) * 100).toFixed(0)}%</span>
                                </div>
                                <div className="w-full bg-accent rounded-full h-2">
                                    <div
                                        className="bg-blue-500 rounded-full h-2"
                                        style={{ width: `${(dataStatus.com_contingencia / dataStatus.total_processos) * 100}%` }}
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <span className="text-sm text-muted-foreground">Total Processos</span>
                                    <div className="text-xl font-bold">{dataStatus.total_processos}</div>
                                </div>
                                <div>
                                    <span className="text-sm text-muted-foreground">Dataset Treino</span>
                                    <div className="text-xl font-bold">{dataStatus.com_contingencia}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Gráficos */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Evolution Chart */}
                <div className="bg-card border border-border rounded-xl p-6 min-h-[400px]">
                    <h3 className="font-bold text-lg mb-6 flex items-center gap-2">
                        <LineChartIcon className="w-5 h-5 text-primary" />
                        Evolução da Performance (R²)
                    </h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={historyData}>
                                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                                <XAxis dataKey="versao" tick={{ fontSize: 12 }} />
                                <YAxis domain={[0, 100]} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="r2"
                                    stroke="#3b82f6"
                                    strokeWidth={3}
                                    name="R² Score (%)"
                                    activeDot={{ r: 8 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Feature Importance */}
                <div className="bg-card border border-border rounded-xl p-6 min-h-[400px]">
                    <h3 className="font-bold text-lg mb-6 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-orange-500" />
                        Top Features de Impacto
                    </h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart layout="vertical" data={featureData} margin={{ left: 20 }}>
                                <CartesianGrid strokeDasharray="3 3" opacity={0.3} horizontal={false} />
                                <XAxis type="number" hide />
                                <YAxis
                                    dataKey="name"
                                    type="category"
                                    width={150}
                                    tick={{ fontSize: 11 }}
                                />
                                <Tooltip
                                    formatter={(value: any) => [`${value}%`, 'Importância']}
                                    contentStyle={{ borderRadius: '8px' }}
                                />
                                <Bar
                                    dataKey="importance"
                                    fill="#f97316"
                                    radius={[0, 4, 4, 0]}
                                    barSize={20}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Histórico Modelos */}
            <div className="bg-card border border-border rounded-xl p-6">
                <div className="flex items-center gap-3 mb-6">
                    <BarChart3 className="w-6 h-6 text-primary" />
                    <h3 className="font-semibold text-lg">Histórico de Treinamentos</h3>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-accent border-b border-border">
                            <tr>
                                <th className="text-left py-3 px-4 text-sm font-medium">Versão</th>
                                <th className="text-left py-3 px-4 text-sm font-medium">Algoritmo</th>
                                <th className="text-center py-3 px-4 text-sm font-medium">Data</th>
                                <th className="text-center py-3 px-4 text-sm font-medium">MAE</th>
                                <th className="text-center py-3 px-4 text-sm font-medium">R²</th>
                                <th className="text-center py-3 px-4 text-sm font-medium">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {modelos.map((modelo, index) => (
                                <tr key={index} className="border-b border-border/50 hover:bg-accent/50">
                                    <td className="py-3 px-4 font-mono text-sm font-semibold">
                                        {modelo.versao}
                                    </td>
                                    <td className="py-3 px-4 text-sm">{modelo.algoritmo}</td>
                                    <td className="py-3 px-4 text-center text-sm text-muted-foreground">
                                        {modelo.data_treinamento
                                            ? new Date(modelo.data_treinamento).toLocaleDateString()
                                            : (modelo.data_criacao ? new Date(modelo.data_criacao).toLocaleDateString() : '-')}
                                    </td>
                                    <td className="py-3 px-4 text-center text-sm font-semibold text-red-400">
                                        R$ {modelo.mae.toFixed(0)}
                                    </td>
                                    <td className="py-3 px-4 text-center text-sm font-semibold text-blue-400">
                                        {modelo.r2.toFixed(3)}
                                    </td>
                                    <td className="py-3 px-4 text-center">
                                        {modelo.versao === modeloInfo?.modelo_atual ? (
                                            <span className="inline-block px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-semibold">
                                                <CheckCircle2 className="w-3 h-3 inline mr-1" />
                                                ATIVO
                                            </span>
                                        ) : (
                                            <span className="text-xs text-muted-foreground opacity-50">Arquivado</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
