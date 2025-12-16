/**
 * Dashboard Profissional - Índices Econômicos
 * Integração completa com API BACEN
 * Atualização diária automática
 */
import { useState, useEffect } from 'react';
import {
    TrendingUp, TrendingDown, Calendar, RefreshCw,
    DollarSign, Percent, BarChart3, Download, Clock
} from 'lucide-react';
import api from '../../lib/api';
import IndicesChart from '../../components/processos/IndicesChart';

interface Indice {
    id: number;
    nome: string;
    descricao: string;
    fonte_oficial: string;
    total_registros: number;
    ultima_atualizacao: string | null;
    ultimo_valor: number | null;
}

interface HistoricoItem {
    data_referencia: string;
    valor: number;
}

export default function IndicesEconomicosPage() {
    const [indices, setIndices] = useState<Indice[]>([]);
    const [indiceSelecionado, setIndiceSelecionado] = useState<number | null>(null);
    const [historico, setHistorico] = useState<HistoricoItem[]>([]);
    const [carregando, setCarregando] = useState(true);
    const [atualizando, setAtualizando] = useState(false);
    const [filtroTempo, setFiltroTempo] = useState<'30d' | '90d' | '1y' | 'all'>('30d');

    useEffect(() => {
        carregarIndices();
    }, []);

    useEffect(() => {
        if (indiceSelecionado) {
            carregarHistorico(indiceSelecionado);
        }
    }, [indiceSelecionado, filtroTempo]);

    const carregarIndices = async () => {
        setCarregando(true);
        try {
            const response = await api.get('/api/atualizacao-monetaria/indices');
            setIndices(response.data);

            // Selecionar SELIC por padrão
            const selic = response.data.find((i: Indice) => i.nome === 'SELIC');
            if (selic) {
                setIndiceSelecionado(selic.id);
            }
        } catch (error) {
            console.error('Erro ao carregar índices:', error);
        } finally {
            setCarregando(false);
        }
    };

    const carregarHistorico = async (indiceId: number) => {
        try {
            const params: any = { limite: 365 };

            // Filtrar por período
            const hoje = new Date();
            let dataInicio = new Date();

            if (filtroTempo === '30d') {
                dataInicio.setDate(dataInicio.getDate() - 30);
            } else if (filtroTempo === '90d') {
                dataInicio.setDate(dataInicio.getDate() - 90);
            } else if (filtroTempo === '1y') {
                dataInicio.setFullYear(dataInicio.getFullYear() - 1);
            }

            if (filtroTempo !== 'all') {
                params.data_inicio = dataInicio.toISOString().split('T')[0];
            }

            const response = await api.get(
                `/api/atualizacao-monetaria/indices/${indiceId}/historico`,
                { params }
            );
            setHistorico(response.data);
        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
        }
    };

    const atualizarIndices = async () => {
        setAtualizando(true);
        try {
            await api.post('/api/atualizacao-monetaria/atualizar/recentes', { dias: 30 });
            await carregarIndices();
            alert('Índices atualizados com sucesso!');
        } catch (error) {
            console.error('Erro ao atualizar índices:', error);
            alert('Erro ao atualizar índices');
        } finally {
            setAtualizando(false);
        }
    };

    const calcularVariacao = (valores: HistoricoItem[]) => {
        if (valores.length < 2) return null;
        const atual = valores[0].valor;
        const anterior = valores[1].valor;
        const variacao = ((atual - anterior) / anterior) * 100;
        return variacao;
    };

    const formatarData = (data: string) => {
        return new Date(data).toLocaleDateString('pt-BR');
    };

    const formatarValor = (valor: number, indice: string) => {
        if (indice.includes('Taxa') || indice.includes('SELIC') || indice.includes('CDI')) {
            return `${valor.toFixed(2)}% a.a.`;
        }
        return `${valor.toFixed(2)}%`;
    };

    if (carregando) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <RefreshCw className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    const indiceInfo = indices.find(i => i.id === indiceSelecionado);

    return (
        <div className="p-6 max-w-[1600px] mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <BarChart3 className="w-8 h-8 text-primary" />
                        Índices Econômicos
                    </h1>
                    <p className="text-muted-foreground mt-2">
                        Dados oficiais do Banco Central - Atualização diária automática
                    </p>
                </div>

                <button
                    onClick={atualizarIndices}
                    disabled={atualizando}
                    className="px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50"
                >
                    <RefreshCw className={`w-4 h-4 ${atualizando ? 'animate-spin' : ''}`} />
                    {atualizando ? 'Atualizando...' : 'Atualizar Índices'}
                </button>
            </div>

            {/* Cards de Índices */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
                {indices.map((indice) => {
                    const variacao = calcularVariacao(historico.filter(h => true));
                    const estaEmAlta = variacao && variacao > 0;

                    return (
                        <button
                            key={indice.id}
                            onClick={() => setIndiceSelecionado(indice.id)}
                            className={`bg-card border-2 rounded-xl p-4 text-left transition-all hover: shadow-lg ${indiceSelecionado === indice.id
                                    ? 'border-primary shadow-lg scale-105'
                                    : 'border-border hover:border-primary/50'
                                }`}
                        >
                            <div className="flex items-start justify-between mb-3">
                                <div>
                                    <h3 className="font-bold text-lg">{indice.nome}</h3>
                                    <p className="text-xs text-muted-foreground">{indice.descricao}</p>
                                </div>
                                {indice.ultimo_valor && estaEmAlta !== null && (
                                    estaEmAlta ? (
                                        <TrendingUp className="w-5 h-5 text-green-500" />
                                    ) : (
                                        <TrendingDown className="w-5 h-5 text-red-500" />
                                    )
                                )}
                            </div>

                            {indice.ultimo_valor ? (
                                <>
                                    <div className="text-2xl font-bold text-primary mb-1">
                                        {formatarValor(indice.ultimo_valor, indice.nome)}
                                    </div>
                                    {variacao !== null && (
                                        <div className={`text-sm font-medium ${estaEmAlta ? 'text-green-500' : 'text-red-500'}`}>
                                            {estaEmAlta ? '+' : ''}{variacao.toFixed(2)}% mês
                                        </div>
                                    )}
                                    <div className="flex items-center gap-1 text-xs text-muted-foreground mt-2">
                                        <Clock className="w-3 h-3" />
                                        {indice.ultima_atualizacao && formatarData(indice.ultima_atualizacao)}
                                    </div>
                                </>
                            ) : (
                                <div className="text-sm text-muted-foreground">Sem dados</div>
                            )}

                            <div className="text-xs text-muted-foreground mt-2 pt-2 border-t border-border">
                                {indice.total_registros} registros
                            </div>
                        </button>
                    );
                })}
            </div>

            {/* Gráfico detalhado */}
            {indiceInfo && (
                <div className="bg-card border border-border rounded-xl p-6">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h2 className="text-2xl font-bold flex items-center gap-2">
                                {indiceInfo.nome}
                                <span className="text-sm font-normal text-muted-foreground">
                                    {indiceInfo.descricao}
                                </span>
                            </h2>
                            <p className="text-sm text-muted-foreground mt-1">
                                Fonte: {indiceInfo.fonte_oficial}
                            </p>
                        </div>

                        <div className="flex items-center gap-2">
                            {/* Filtro de tempo */}
                            {['30d', '90d', '1y', 'all'].map((periodo) => (
                                <button
                                    key={periodo}
                                    onClick={() => setFiltroTempo(periodo as any)}
                                    className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${filtroTempo === periodo
                                            ? 'bg-primary text-white'
                                            : 'bg-accent hover:bg-accent/80'
                                        }`}
                                >
                                    {periodo === '30d' && '30 dias'}
                                    {periodo === '90d' && '90 dias'}
                                    {periodo === '1y' && '1 ano'}
                                    {periodo === 'all' && 'Tudo'}
                                </button>
                            ))}

                            <button className="p-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors">
                                <Download className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    {/* Gráfico */}
                    {historico.length > 0 ? (
                        <div className="h-[400px]">
                            <IndicesChart
                                indiceId={indiceInfo.id}
                                indiceName={indiceInfo.nome}
                            />
                        </div>
                    ) : (
                        <div className="h-[400px] flex items-center justify-center text-muted-foreground">
                            Sem dados disponíveis para o período selecionado
                        </div>
                    )}

                    {/* Tabela de últimos valores */}
                    <div className="mt-6 pt-6 border-t border-border">
                        <h3 className="font-bold mb-4">Últimos 10 Registros</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-border">
                                        <th className="text-left py-2 px-4 text-sm font-medium text-muted-foreground">Data</th>
                                        <th className="text-right py-2 px-4 text-sm font-medium text-muted-foreground">Valor</th>
                                        <th className="text-right py-2 px-4 text-sm font-medium text-muted-foreground">Variação</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {historico.slice(0, 10).map((item, index) => {
                                        const variacaoItem = index < historico.length - 1
                                            ? ((item.valor - historico[index + 1].valor) / historico[index + 1].valor) * 100
                                            : null;
                                        const estaEmAlta = variacaoItem && variacaoItem > 0;

                                        return (
                                            <tr key={item.data_referencia} className="border-b border-border/50 hover:bg-accent/50">
                                                <td className="py-3 px-4 text-sm">{formatarData(item.data_referencia)}</td>
                                                <td className="py-3 px-4 text-sm text-right font-medium">
                                                    {formatarValor(item.valor, indiceInfo.nome)}
                                                </td>
                                                <td className="py-3 px-4 text-sm text-right">
                                                    {variacaoItem !== null ? (
                                                        <span className={estaEmAlta ? 'text-green-500' : 'text-red-500'}>
                                                            {estaEmAlta ? '+' : ''}{variacaoItem.toFixed(2)}%
                                                        </span>
                                                    ) : (
                                                        <span className="text-muted-foreground">-</span>
                                                    )}
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}

            {/* Info Footer */}
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
                <div className="flex items-start gap-3">
                    <Calendar className="w-5 h-5 text-blue-400 mt-0.5" />
                    <div className="text-sm">
                        <p className="font-medium text-blue-300 mb-1">Atualização Automática Diária</p>
                        <p className="text-blue-200/80">
                            Os índices são atualizados automaticamente todos os dias às 8h da manhã,
                            buscando os dados mais recentes diretamente do Sistema Gerenciador de Séries
                            Temporais (SGS) do Banco Central do Brasil.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
