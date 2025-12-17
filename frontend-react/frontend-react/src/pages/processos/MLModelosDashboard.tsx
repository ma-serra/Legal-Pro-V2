import { useState, useEffect } from 'react';
import { Brain, RefreshCw, TrendingUp, Database, Zap, AlertCircle, CheckCircle2, BarChart3 } from 'lucide-react';
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
}

interface Modelo {
    versao: string;
    algoritmo: string;
    mae: number;
    r2: number;
    rmse?: number;
    data_criacao?: string;
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
            setModelos(modelsRes.data || []);
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
            alert(`Modelo retreinado com sucesso!\nNova versão: ${response.data.nova_versao}\nMAE: ${response.data.metricas.mae}\nR²: ${response.data.metricas.r2}`);
            await carregarDados();
        } catch (error: any) {
            console.error('Erro ao retreinar:', error);
            alert(error.response?.data?.error || 'Erro ao retreinar modelo');
        } finally {
            setRetraining(false);
        }
    };

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
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <Brain className="w-8 h-8 text-primary" />
                        Dashboard Modelos ML
                    </h1>
                    <p className="text-muted-foreground mt-1">
                        Gerenciamento e monitoramento de modelos de Machine Learning
                    </p>
                </div>

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

            {/* Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Status Dados */}
                {dataStatus && (
                    <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/5 border border-blue-500/20 rounded-xl p-6">
                        <div className="flex items-center gap-3 mb-4">
                            <Database className="w-6 h-6 text-blue-400" />
                            <h3 className="font-semibold text-lg">Status dos Dados</h3>
                        </div>

                        <div className="space-y-3">
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-muted-foreground">Total Processos</span>
                                <span className="text-2xl font-bold text-blue-400">{dataStatus.total_processos}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-muted-foreground">Com Contingência</span>
                                <span className="text-xl font-semibold">{dataStatus.com_contingencia}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-muted-foreground">Features Completas</span>
                                <span className="text-xl font-semibold">{dataStatus.com_features_completas}</span>
                            </div>

                            <div className="pt-3 border-t border-border">
                                <div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${dataStatus.status === 'OK'
                                        ? 'bg-green-500/20 text-green-400'
                                        : 'bg-yellow-500/20 text-yellow-400'
                                    }`}>
                                    {dataStatus.status}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Modelo Atual */}
                {modeloInfo && (
                    <div className="bg-gradient-to-br from-purple-500/10 to-purple-600/5 border border-purple-500/20 rounded-xl p-6">
                        <div className="flex items-center gap-3 mb-4">
                            <Brain className="w-6 h-6 text-purple-400" />
                            <h3 className="font-semibold text-lg">Modelo Atual</h3>
                        </div>

                        <div className="space-y-3">
                            <div>
                                <span className="text-sm text-muted-foreground">Versão</span>
                                <div className="text-2xl font-bold text-purple-400">{modeloInfo.modelo_atual}</div>
                            </div>
                            <div>
                                <span className="text-sm text-muted-foreground">Algoritmo</span>
                                <div className="text-lg font-semibold">{modeloInfo.algoritmo}</div>
                            </div>

                            <div className="pt-3 border-t border-border grid grid-cols-3 gap-2 text-center">
                                <div>
                                    <div className="text-xs text-muted-foreground">MAE</div>
                                    <div className="text-sm font-bold text-green-400">
                                        {modeloInfo.metricas.mae.toFixed(0)}
                                    </div>
                                </div>
                                <div>
                                    <div className="text-xs text-muted-foreground">R²</div>
                                    <div className="text-sm font-bold text-blue-400">
                                        {modeloInfo.metricas.r2.toFixed(3)}
                                    </div>
                                </div>
                                <div>
                                    <div className="text-xs text-muted-foreground">RMSE</div>
                                    <div className="text-sm font-bold text-purple-400">
                                        {modeloInfo.metricas.rmse.toFixed(0)}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Features Importantes */}
                {modeloInfo && modeloInfo.features_importantes.length > 0 && (
                    <div className="bg-gradient-to-br from-orange-500/10 to-orange-600/5 border border-orange-500/20 rounded-xl p-6">
                        <div className="flex items-center gap-3 mb-4">
                            <TrendingUp className="w-6 h-6 text-orange-400" />
                            <h3 className="font-semibold text-lg">Features Importantes</h3>
                        </div>

                        <div className="space-y-3">
                            {modeloInfo.features_importantes.slice(0, 5).map((feature, index) => (
                                <div key={index}>
                                    <div className="flex justify-between items-center mb-1">
                                        <span className="text-sm text-muted-foreground truncate">
                                            {feature.nome.replace(/_/g, ' ')}
                                        </span>
                                        <span className="text-xs font-semibold text-orange-400">
                                            {(feature.importancia * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                    <div className="w-full bg-accent rounded-full h-2">
                                        <div
                                            className="bg-gradient-to-r from-orange-500 to-yellow-500 rounded-full h-2 transition-all"
                                            style={{ width: `${feature.importancia * 100}%` }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Histórico Modelos */}
            {modelos.length > 0 && (
                <div className="bg-card border border-border rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <BarChart3 className="w-6 h-6 text-primary" />
                        <h3 className="font-semibold text-lg">Histórico de Modelos</h3>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-accent border-b border-border">
                                <tr>
                                    <th className="text-left py-3 px-4 text-sm font-medium">Versão</th>
                                    <th className="text-left py-3 px-4 text-sm font-medium">Algoritmo</th>
                                    <th className="text-center py-3 px-4 text-sm font-medium">MAE</th>
                                    <th className="text-center py-3 px-4 text-sm font-medium">R²</th>
                                    <th className="text-center py-3 px-4 text-sm font-medium">RMSE</th>
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
                                        <td className="py-3 px-4 text-center text-sm font-semibold text-green-400">
                                            {modelo.mae.toFixed(0)}
                                        </td>
                                        <td className="py-3 px-4 text-center text-sm font-semibold text-blue-400">
                                            {modelo.r2.toFixed(3)}
                                        </td>
                                        <td className="py-3 px-4 text-center text-sm font-semibold text-purple-400">
                                            {modelo.rmse ? modelo.rmse.toFixed(0) : '-'}
                                        </td>
                                        <td className="py-3 px-4 text-center">
                                            {modelo.versao === modeloInfo?.modelo_atual ? (
                                                <span className="inline-block px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-semibold">
                                                    <CheckCircle2 className="w-3 h-3 inline mr-1" />
                                                    ATIVO
                                                </span>
                                            ) : (
                                                <span className="text-xs text-muted-foreground">-</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
