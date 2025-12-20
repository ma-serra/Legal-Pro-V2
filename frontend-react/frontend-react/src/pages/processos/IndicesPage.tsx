/**
 * Dashboard Completo - Índices Econômicos e Dados BCB
 * Integração com APIs do Banco Central:
 * - SGS: Séries Temporais (SELIC, IPCA, INPC, etc.)
 * - Olinda PTAX: Cotações de Câmbio
 * - Expectativas de Mercado (Focus)
 */
import { useState, useEffect } from 'react';
import {
    TrendingUp, TrendingDown, Calendar, RefreshCw,
    DollarSign, Percent, BarChart3, Download, Clock,
    Globe, Target, ArrowRight, LineChart as LineIcon
} from 'lucide-react';
import api from '../../lib/api';
import IndicesChart from '../../components/processos/IndicesChart';
import ExpectativasChart from '../../components/processos/ExpectativasChart';

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

interface CotacaoPTAX {
    moeda: string;
    data: string;
    cotacao_compra: number;
    cotacao_venda: number;
}

interface Expectativa {
    indicador: string;
    data: string;
    data_referencia: string;
    media: number;
    mediana: number;
    minimo: number;
    maximo: number;
}

export default function IndicesEconomicosPage() {
    const [indices, setIndices] = useState<Indice[]>([]);
    const [indiceSelecionado, setIndiceSelecionado] = useState<number | null>(null);
    const [historico, setHistorico] = useState<HistoricoItem[]>([]);
    const [carregando, setCarregando] = useState(true);
    const [atualizando, setAtualizando] = useState(false);
    const [filtroTempo, setFiltroTempo] = useState<'30d' | '90d' | '1y' | 'all'>('30d');

    // Novos estados para PTAX e Expectativas
    const [ptaxUSD, setPtaxUSD] = useState<CotacaoPTAX | null>(null);
    const [ptaxEUR, setPtaxEUR] = useState<CotacaoPTAX | null>(null);
    const [expectativas, setExpectativas] = useState<{
        selic: Expectativa[];
        ipca: Expectativa[];
        pib: Expectativa[];
        cambio: Expectativa[];
    }>({ selic: [], ipca: [], pib: [], cambio: [] });

    // Estado para detalhe de expectativa (histórico Top 5)
    const [expectativaDetalhe, setExpectativaDetalhe] = useState<{ key: string, label: string } | null>(null);

    useEffect(() => {
        carregarTodosDados();
    }, []);

    useEffect(() => {
        if (indiceSelecionado) {
            carregarHistorico(indiceSelecionado);
        }
    }, [indiceSelecionado, filtroTempo]);

    const carregarTodosDados = async () => {
        setCarregando(true);
        try {
            // Carregar em paralelo
            const [indicesRes, ptaxUSDRes, ptaxEURRes, expectativasRes] = await Promise.allSettled([
                api.get('/api/atualizacao-monetaria/indices'),
                api.get('/api/bcb/ptax/hoje?moeda=USD'),
                api.get('/api/bcb/ptax/hoje?moeda=EUR'),
                api.get('/api/bcb/expectativas/resumo')
            ]);

            if (indicesRes.status === 'fulfilled') {
                setIndices(indicesRes.value.data);
                const selic = indicesRes.value.data.find((i: Indice) => i.nome === 'SELIC');
                if (selic) setIndiceSelecionado(selic.id);
            }
            if (ptaxUSDRes.status === 'fulfilled' && !ptaxUSDRes.value.data.erro) {
                setPtaxUSD(ptaxUSDRes.value.data);
            }
            if (ptaxEURRes.status === 'fulfilled' && !ptaxEURRes.value.data.erro) {
                setPtaxEUR(ptaxEURRes.value.data);
            }
            if (expectativasRes.status === 'fulfilled') {
                setExpectativas(expectativasRes.value.data);
            }
        } catch (error) {
            console.error('Erro ao carregar dados:', error);
        } finally {
            setCarregando(false);
        }
    };

    const carregarHistorico = async (indiceId: number) => {
        try {
            const params: any = { limite: 365 };
            const hoje = new Date();
            let dataInicio = new Date();

            if (filtroTempo === '30d') dataInicio.setDate(dataInicio.getDate() - 30);
            else if (filtroTempo === '90d') dataInicio.setDate(dataInicio.getDate() - 90);
            else if (filtroTempo === '1y') dataInicio.setFullYear(dataInicio.getFullYear() - 1);

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
            await carregarTodosDados();
            alert('Índices atualizados com sucesso!');
        } catch (error) {
            console.error('Erro ao atualizar índices:', error);
            alert('Erro ao atualizar índices');
        } finally {
            setAtualizando(false);
        }
    };

    // Formatadores padrão BCB
    const formatarMoeda = (valor: number, casas: number = 4) => {
        return valor.toLocaleString('pt-BR', {
            minimumFractionDigits: casas,
            maximumFractionDigits: casas
        });
    };

    const formatarData = (data: string) => {
        if (!data) return '-';
        return new Date(data).toLocaleDateString('pt-BR');
    };

    const formatarValor = (valor: number, indice: string) => {
        if (indice === 'SELIC' || indice === 'CDI' || indice === 'SELIC-EFETIVA') {
            const taxaAnual = valor * 252;
            return `${taxaAnual.toFixed(2)}% a.a.`;
        }
        if (indice === 'TJLP') return `${valor.toFixed(2)}% a.a.`;
        if (indice.includes('DOLAR') || indice.includes('EURO')) return `R$ ${formatarMoeda(valor)}`;
        return `${valor.toFixed(2)}% mês`;
    };

    if (carregando) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <RefreshCw className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
                    <p className="text-muted-foreground">Carregando dados do Banco Central...</p>
                </div>
            </div>
        );
    }

    const indiceInfo = indices.find(i => i.id === indiceSelecionado);

    return (
        <div className="p-6 max-w-[1600px] mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <BarChart3 className="w-8 h-8 text-primary" />
                        Dados Monetários BCB
                    </h1>
                    <p className="text-muted-foreground mt-1">
                        Dados oficiais do Banco Central do Brasil - Atualização em tempo real
                    </p>
                </div>

                <button
                    onClick={atualizarIndices}
                    disabled={atualizando}
                    className="px-5 py-2.5 bg-primary hover:bg-primary/90 text-white rounded-lg flex items-center gap-2 disabled:opacity-50"
                >
                    <RefreshCw className={`w-4 h-4 ${atualizando ? 'animate-spin' : ''}`} />
                    {atualizando ? 'Atualizando...' : 'Atualizar Dados'}
                </button>
            </div>

            {/* Cotações PTAX - Destaque no topo */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Dólar */}
                <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/10 border border-green-500/30 rounded-xl p-5">
                    <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                            <DollarSign className="w-6 h-6 text-green-400" />
                            <h2 className="font-bold">Dólar PTAX</h2>
                        </div>
                        <span className="text-xs text-muted-foreground">
                            {ptaxUSD ? formatarData(ptaxUSD.data) : '-'}
                        </span>
                    </div>
                    {ptaxUSD ? (
                        <div className="grid grid-cols-2 gap-3">
                            <div>
                                <p className="text-xs text-muted-foreground">Compra</p>
                                <p className="text-2xl font-bold text-green-400">R$ {formatarMoeda(ptaxUSD.cotacao_compra)}</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground">Venda</p>
                                <p className="text-2xl font-bold">R$ {formatarMoeda(ptaxUSD.cotacao_venda)}</p>
                            </div>
                        </div>
                    ) : (
                        <p className="text-muted-foreground">Cotação não disponível</p>
                    )}
                </div>

                {/* Euro */}
                <div className="bg-gradient-to-br from-blue-500/20 to-indigo-500/10 border border-blue-500/30 rounded-xl p-5">
                    <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                            <Globe className="w-6 h-6 text-blue-400" />
                            <h2 className="font-bold">Euro PTAX</h2>
                        </div>
                        <span className="text-xs text-muted-foreground">
                            {ptaxEUR ? formatarData(ptaxEUR.data) : '-'}
                        </span>
                    </div>
                    {ptaxEUR ? (
                        <div className="grid grid-cols-2 gap-3">
                            <div>
                                <p className="text-xs text-muted-foreground">Compra</p>
                                <p className="text-2xl font-bold text-blue-400">R$ {formatarMoeda(ptaxEUR.cotacao_compra)}</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground">Venda</p>
                                <p className="text-2xl font-bold">R$ {formatarMoeda(ptaxEUR.cotacao_venda)}</p>
                            </div>
                        </div>
                    ) : (
                        <p className="text-muted-foreground">Cotação não disponível</p>
                    )}
                </div>
            </div>

            {/* Expectativas de Mercado - Focus */}
            <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <Target className="w-5 h-5 text-primary" />
                        <h2 className="font-bold">Expectativas de Mercado (Focus)</h2>
                    </div>
                    <span className="text-xs text-muted-foreground">Clique para ver histórico</span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {[
                        { key: 'selic', label: 'SELIC', cor: 'orange', sufixo: '% a.a.', api_indicador: 'Selic' },
                        { key: 'ipca', label: 'IPCA', cor: 'red', sufixo: '%', api_indicador: 'IPCA' },
                        { key: 'pib', label: 'PIB', cor: 'green', sufixo: '%', api_indicador: 'PIB Total' },
                        { key: 'cambio', label: 'Câmbio', cor: 'blue', prefixo: 'R$ ', api_indicador: 'Câmbio' }
                    ].map(({ key, label, cor, sufixo, prefixo, api_indicador }) => {
                        const dados = expectativas[key as keyof typeof expectativas]?.[0];
                        const isSelected = expectativaDetalhe?.key === key;

                        return (
                            <button
                                key={key}
                                onClick={() => setExpectativaDetalhe(isSelected ? null : { key, label: api_indicador })}
                                className={`bg-background border rounded-lg p-3 text-left transition-all hover:shadow-md ${isSelected ? 'border-primary ring-1 ring-primary' : 'border-border hover:border-primary/50'
                                    }`}
                            >
                                <h3 className={`font-semibold text-${cor}-400 text-sm mb-2 flex items-center justify-between`}>
                                    {label}
                                    {isSelected && <LineIcon className="w-3 h-3 text-primary" />}
                                </h3>
                                {dados ? (
                                    <>
                                        <p className="text-xl font-bold">
                                            {prefixo || ''}{formatarMoeda(dados.mediana, 2)}{sufixo || ''}
                                        </p>
                                        <p className="text-xs text-muted-foreground">{dados.data_referencia}</p>
                                    </>
                                ) : <p className="text-muted-foreground text-sm">Sem dados</p>}
                            </button>
                        );
                    })}
                </div>

                {/* Gráfico Histórico Focus (Condicional) */}
                {expectativaDetalhe && (
                    <ExpectativasChart
                        indicador={expectativaDetalhe.label}
                        titulo={expectativaDetalhe.label}
                    />
                )}
            </div>

            {/* Cards de Índices */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6 gap-3">
                {indices.map((indice) => (
                    <button
                        key={indice.id}
                        onClick={() => setIndiceSelecionado(indice.id)}
                        className={`bg-card border-2 rounded-xl p-4 text-left transition-all hover:shadow-lg ${indiceSelecionado === indice.id
                                ? 'border-primary shadow-lg'
                                : 'border-border hover:border-primary/50'
                            }`}
                    >
                        <h3 className="font-bold text-sm truncate">{indice.nome}</h3>
                        <p className="text-xs text-muted-foreground truncate mb-2">{indice.descricao}</p>
                        {indice.ultimo_valor ? (
                            <>
                                <p className="text-lg font-bold text-primary">
                                    {formatarValor(indice.ultimo_valor, indice.nome)}
                                </p>
                                <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                                    <Clock className="w-3 h-3" />
                                    {formatarData(indice.ultima_atualizacao || '')}
                                </p>
                            </>
                        ) : (
                            <p className="text-sm text-muted-foreground">Sem dados</p>
                        )}
                    </button>
                ))}
            </div>

            {/* Gráfico detalhado */}
            {indiceInfo && (
                <div className="bg-card border border-border rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4 flex-wrap gap-4">
                        <div>
                            <h2 className="text-xl font-bold">{indiceInfo.nome}</h2>
                            <p className="text-sm text-muted-foreground">
                                Fonte: {indiceInfo.fonte_oficial}
                            </p>
                        </div>

                        <div className="flex items-center gap-2">
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
                        </div>
                    </div>

                    {/* Gráfico */}
                    <IndicesChart
                        indiceId={indiceInfo.id}
                        indiceName={indiceInfo.nome}
                    />

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

            {/* Footer Info */}
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
                <div className="flex items-start gap-3">
                    <Calendar className="w-5 h-5 text-blue-400 mt-0.5" />
                    <div className="text-sm">
                        <p className="font-medium text-blue-300 mb-1">Fonte: Banco Central do Brasil</p>
                        <p className="text-blue-200/80">
                            APIs: SGS (Séries Temporais), Olinda PTAX (Câmbio), Expectativas Focus (Top 5 e Média Mercado).
                            Dados atualizados diariamente às 8h ou sob demanda.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
