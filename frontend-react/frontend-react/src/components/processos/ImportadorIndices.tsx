/**
 * ImportadorIndices - Interface para Importação de Índices BACEN
 * Integra com API de Atualização Monetária
 */
import { useState, useEffect } from 'react';
import { IndiceMonetario } from '../../../types/processos';
import api from '../../../lib/api';
import { Download, TrendingUp, Calendar, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react';

export default function ImportadorIndices() {
    const [indices, setIndices] = useState<IndiceMonetario[]>([]);
    const [loading, setLoading] = useState(false);
    const [importing, setImporting] = useState<string | null>(null);
    const [resultado, setResultado] = useState<any>(null);

    useEffect(() => {
        fetchIndices();
    }, []);

    const fetchIndices = async () => {
        try {
            const response = await api.get('/api/atualizacao-monetaria/indices');
            setIndices(response.data || []);
        } catch (error) {
            console.error('Erro ao carregar índices:', error);
        }
    };

    const importarIndice = async (indice: string) => {
        setImporting(indice);
        setResultado(null);

        try {
            const response = await api.post(`/api/atualizacao-monetaria/importar/${indice}`);
            setResultado({
                sucesso: true,
                indice,
                registros: response.data.registros_importados
            });
            fetchIndices();
        } catch (error: any) {
            setResultado({
                sucesso: false,
                indice,
                erro: error.response?.data?.error || 'Erro ao importar'
            });
        } finally {
            setImporting(null);
        }
    };

    const importarTodos = async () => {
        setLoading(true);
        setResultado(null);

        try {
            const response = await api.post('/api/atualizacao-monetaria/importar/todos');
            setResultado({
                sucesso: true,
                todos: true,
                resultados: response.data.resultados,
                total: response.data.total_registros
            });
            fetchIndices();
        } catch (error: any) {
            setResultado({
                sucesso: false,
                todos: true,
                erro: error.response?.data?.error || 'Erro ao importar'
            });
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString?: string) => {
        if (!dateString) return 'Nunca';
        return new Date(dateString).toLocaleDateString('pt-BR');
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold flex items-center gap-3">
                        <Download className="w-7 h-7 text-primary" />
                        Importador de Índices
                    </h2>
                    <p className="text-muted-foreground mt-1">
                        Dados oficiais do Banco Central do Brasil
                    </p>
                </div>

                <button
                    onClick={importarTodos}
                    disabled={loading}
                    className="flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary/90 rounded-lg transition-colors font-medium disabled:opacity-50"
                >
                    <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                    Importar Todos
                </button>
            </div>

            {/* Resultado */}
            {resultado && (
                <div className={`${resultado.sucesso ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20'} border rounded-xl p-4`}>
                    <div className="flex items-start gap-3">
                        {resultado.sucesso ? (
                            <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                        ) : (
                            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
                        )}

                        <div className="flex-1">
                            <h4 className={`font-semibold ${resultado.sucesso ? 'text-green-400' : 'text-red-400'}`}>
                                {resultado.sucesso ? 'Importação Concluída!' : 'Erro na Importação'}
                            </h4>

                            {resultado.todos ? (
                                <p className="text-sm text-muted-foreground mt-1">
                                    {resultado.sucesso
                                        ? `${resultado.total} registros importados`
                                        : resultado.erro
                                    }
                                </p>
                            ) : (
                                <p className="text-sm text-muted-foreground mt-1">
                                    {resultado.sucesso
                                        ? `${resultado.indice}: ${resultado.registros} novos registros`
                                        : `${resultado.indice}: ${resultado.erro}`
                                    }
                                </p>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Lista de Índices */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {indices.map(indice => (
                    <div
                        key={indice.id_indice}
                        className="bg-card border border-border rounded-xl p-6 hover:shadow-lg transition-all"
                    >
                        <div className="flex items-start justify-between mb-4">
                            <div className="p-3 bg-primary/20 rounded-lg">
                                <TrendingUp className="w-6 h-6 text-primary" />
                            </div>
                            <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-medium">
                                Ativo
                            </span>
                        </div>

                        <h3 className="font-bold text-lg mb-2">{indice.nome}</h3>
                        <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                            {indice.descricao}
                        </p>

                        <div className="space-y-2 mb-4 text-sm">
                            <div className="flex items-center gap-2">
                                <Calendar className="w-4 h-4 text-muted-foreground" />
                                <span className="text-muted-foreground">
                                    Última: {formatDate(indice.ultima_atualizacao)}
                                </span>
                            </div>

                            <div className="flex items-center gap-2">
                                <Download className="w-4 h-4 text-muted-foreground" />
                                <span className="text-muted-foreground">
                                    {indice.total_registros || 0} registros
                                </span>
                            </div>

                            {indice.ultimo_valor && (
                                <div className="flex items-center gap-2">
                                    <TrendingUp className="w-4 h-4 text-primary" />
                                    <span className="font-medium text-primary">
                                        {indice.ultimo_valor}%
                                    </span>
                                </div>
                            )}
                        </div>

                        <button
                            onClick={() => importarIndice(indice.nome)}
                            disabled={importing === indice.nome}
                            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary/20 hover:bg-primary/30 rounded-lg transition-colors text-primary disabled:opacity-50"
                        >
                            <Download className={`w-4 h-4 ${importing === indice.nome ? 'animate-bounce' : ''}`} />
                            {importing === indice.nome ? 'Importando...' : 'Importar'}
                        </button>
                    </div>
                ))}
            </div>

            {/* Info */}
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-6">
                <div className="flex gap-3">
                    <AlertCircle className="w-5 h-5 text-blue-400 mt-0.5" />
                    <div>
                        <h4 className="font-semibold text-blue-400 mb-1">Fonte Oficial</h4>
                        <p className="text-sm text-muted-foreground">
                            Dados importados diretamente da API do Banco Central do Brasil (BACEN)
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
