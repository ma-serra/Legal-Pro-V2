import { useState } from 'react';
import { Brain, X, Download, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';
import api from '../../lib/api';

interface PredicaoResultado {
    processo_id: number;
    pasta?: string;
    valor_contingencia_predito: number;
    confianca: number;
    risco_predito?: string;
}

interface BatchResponse {
    predicoes: PredicaoResultado[];
    total_processados: number;
    tempo_processamento: string;
}

interface Props {
    processoIds: number[];
    onClose: () => void;
    onSuccess: () => void;
}

export default function BatchPredictModal({ processoIds, onClose, onSuccess }: Props) {
    const [resultado, setResultado] = useState<BatchResponse | null>(null);
    const [analisando, setAnalisando] = useState(false);
    const [erro, setErro] = useState<string | null>(null);

    const executarAnalise = async () => {
        setAnalisando(true);
        setErro(null);

        try {
            const response = await api.post('/api/ml/tributario/batch-predict', {
                processo_ids: processoIds
            });
            setResultado(response.data);
        } catch (error: any) {
            console.error('Erro batch predict:', error);
            setErro(error.response?.data?.error || 'Erro ao realizar análise em lote');
        } finally {
            setAnalisando(false);
        }
    };

    const exportarCSV = () => {
        if (!resultado) return;

        const headers = ['Processo ID', 'Pasta', 'Valor Predito', 'Confiança (%)', 'Risco'];
        const rows = resultado.predicoes.map(p => [
            p.processo_id,
            p.pasta || '-',
            p.valor_contingencia_predito.toFixed(2),
            (p.confianca * 100).toFixed(1),
            p.risco_predito || '-'
        ]);

        const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `batch_predict_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const formatarMoeda = (valor: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
    };

    const getRiscoColor = (risco?: string) => {
        switch (risco?.toLowerCase()) {
            case 'baixo': return 'text-green-500 bg-green-500/10';
            case 'medio': case 'médio': return 'text-yellow-500 bg-yellow-500/10';
            case 'alto': return 'text-red-500 bg-red-500/10';
            default: return 'text-gray-500 bg-gray-500/10';
        }
    };

    const calcularMediaConfianca = () => {
        if (!resultado || resultado.predicoes.length === 0) return 0;
        const soma = resultado.predicoes.reduce((acc, p) => acc + p.confianca, 0);
        return (soma / resultado.predicoes.length) * 100;
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-card border border-border rounded-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="bg-gradient-to-r from-primary/20 to-primary/5 border-b border-border p-6">
                    <div className="flex items-start justify-between">
                        <div>
                            <div className="flex items-center gap-3 mb-2">
                                <Brain className="w-6 h-6 text-primary" />
                                <h2 className="text-2xl font-bold">Análise ML em Lote</h2>
                            </div>
                            <p className="text-muted-foreground">
                                {processoIds.length} processo(s) selecionado(s)
                            </p>
                        </div>
                        <button onClick={onClose} className="p-2 hover:bg-accent rounded-lg transition-colors">
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    {!resultado && !analisando && !erro && (
                        <div className="text-center py-12">
                            <Brain className="w-16 h-16 text-primary mx-auto mb-4" />
                            <h3 className="text-lg font-semibold mb-2">Pronto para Analisar</h3>
                            <p className="text-muted-foreground mb-6">
                                Clique no botão abaixo para iniciar a análise ML de {processoIds.length} processo(s).
                            </p>
                            <button
                                onClick={executarAnalise}
                                className="px-6 py-3 bg-primary hover:bg-primary/90 text-white rounded-lg font-semibold transition-colors"
                            >
                                Iniciar Análise
                            </button>
                        </div>
                    )}

                    {analisando && (
                        <div className="text-center py-12">
                            <RefreshCw className="w-16 h-16 text-primary animate-spin mx-auto mb-4" />
                            <h3 className="text-lg font-semibold mb-2">Processando...</h3>
                            <p className="text-muted-foreground">
                                Analisando {processoIds.length} processo(s). Isso pode levar alguns segundos.
                            </p>
                        </div>
                    )}

                    {erro && (
                        <div className="text-center py-12">
                            <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                            <h3 className="text-lg font-semibold mb-2 text-red-400">Erro na Análise</h3>
                            <p className="text-muted-foreground mb-6">{erro}</p>
                            <button
                                onClick={executarAnalise}
                                className="px-6 py-3 bg-primary hover:bg-primary/90 text-white rounded-lg font-semibold transition-colors"
                            >
                                Tentar Novamente
                            </button>
                        </div>
                    )}

                    {resultado && (
                        <div className="space-y-6">
                            {/* Métricas Resumo */}
                            <div className="grid grid-cols-3 gap-4">
                                <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4 text-center">
                                    <CheckCircle2 className="w-8 h-8 text-green-500 mx-auto mb-2" />
                                    <div className="text-2xl font-bold text-green-500">
                                        {resultado.total_processados}
                                    </div>
                                    <div className="text-sm text-muted-foreground">Processados</div>
                                </div>

                                <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4 text-center">
                                    <Brain className="w-8 h-8 text-blue-500 mx-auto mb-2" />
                                    <div className="text-2xl font-bold text-blue-500">
                                        {calcularMediaConfianca().toFixed(1)}%
                                    </div>
                                    <div className="text-sm text-muted-foreground">Confiança Média</div>
                                </div>

                                <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-4 text-center">
                                    <RefreshCw className="w-8 h-8 text-purple-500 mx-auto mb-2" />
                                    <div className="text-2xl font-bold text-purple-500">
                                        {resultado.tempo_processamento}
                                    </div>
                                    <div className="text-sm text-muted-foreground">Tempo</div>
                                </div>
                            </div>

                            {/* Tabela Resultados */}
                            <div className="bg-accent/30 border border-border rounded-xl overflow-hidden">
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead className="bg-accent border-b border-border">
                                            <tr>
                                                <th className="text-left py-3 px-4 text-sm font-medium">Processo</th>
                                                <th className="text-right py-3 px-4 text-sm font-medium">Valor Predito</th>
                                                <th className="text-center py-3 px-4 text-sm font-medium">Confiança</th>
                                                <th className="text-center py-3 px-4 text-sm font-medium">Risco</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {resultado.predicoes.map((pred, index) => (
                                                <tr key={index} className="border-b border-border/50 hover:bg-accent/50">
                                                    <td className="py-3 px-4">
                                                        <div className="font-medium">#{pred.processo_id}</div>
                                                        {pred.pasta && (
                                                            <div className="text-xs text-muted-foreground">
                                                                {pred.pasta}
                                                            </div>
                                                        )}
                                                    </td>
                                                    <td className="py-3 px-4 text-right font-semibold text-primary">
                                                        {formatarMoeda(pred.valor_contingencia_predito)}
                                                    </td>
                                                    <td className="py-3 px-4 text-center">
                                                        <div className="inline-block px-3 py-1 bg-green-500/10 text-green-500 rounded-full text-sm font-semibold">
                                                            {(pred.confianca * 100).toFixed(1)}%
                                                        </div>
                                                    </td>
                                                    <td className="py-3 px-4 text-center">
                                                        {pred.risco_predito && (
                                                            <div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getRiscoColor(pred.risco_predito)}`}>
                                                                {pred.risco_predito}
                                                            </div>
                                                        )}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                {resultado && (
                    <div className="border-t border-border p-6 flex items-center justify-between bg-accent/20">
                        <button
                            onClick={exportarCSV}
                            className="px-4 py-2 border border-border hover:bg-accent rounded-lg flex items-center gap-2 transition-colors"
                        >
                            <Download className="w-4 h-4" />
                            Exportar CSV
                        </button>
                        <div className="flex gap-3">
                            <button
                                onClick={onClose}
                                className="px-6 py-2 border border-border hover:bg-accent rounded-lg transition-colors"
                            >
                                Fechar
                            </button>
                            <button
                                onClick={() => {
                                    onSuccess();
                                    onClose();
                                }}
                                className="px-6 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg font-semibold transition-colors"
                            >
                                Concluir
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
