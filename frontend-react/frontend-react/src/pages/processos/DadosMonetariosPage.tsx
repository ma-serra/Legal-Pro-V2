/**
 * DadosMonetariosPage - Dashboard Completo BCB
 * Integração com APIs do Banco Central do Brasil
 * - SGS: Índices históricos
 * - Olinda PTAX: Cotações de câmbio
 * - Expectativas de Mercado (Focus)
 */
import { useState, useEffect } from 'react';
import {
    TrendingUp, TrendingDown, DollarSign, Percent,
    RefreshCw, Calendar, BarChart3, Globe, Target,
    ArrowUpRight, ArrowDownRight
} from 'lucide-react';
import api from '../../lib/api';

interface CotacaoPTAX {
    moeda: string;
    data: string;
    cotacao_compra: number;
    cotacao_venda: number;
    tipo?: string;
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

interface IndiceResumo {
    id: number;
    nome: string;
    descricao: string;
    ultimo_valor: number | null;
    ultima_atualizacao: string | null;
    total_registros: number;
}

export default function DadosMonetariosPage() {
    const [indices, setIndices] = useState<IndiceResumo[]>([]);
    const [ptaxUSD, setPtaxUSD] = useState<CotacaoPTAX | null>(null);
    const [ptaxEUR, setPtaxEUR] = useState<CotacaoPTAX | null>(null);
    const [expectativas, setExpectativas] = useState<{
        selic: Expectativa[];
        ipca: Expectativa[];
        pib: Expectativa[];
        cambio: Expectativa[];
    }>({ selic: [], ipca: [], pib: [], cambio: [] });
    const [loading, setLoading] = useState(true);
    const [atualizando, setAtualizando] = useState(false);
    const [ultimaAtualizacao, setUltimaAtualizacao] = useState<Date | null>(null);

    useEffect(() => {
        carregarDados();
    }, []);

    const carregarDados = async () => {
        setLoading(true);
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
            }
            if (ptaxUSDRes.status === 'fulfilled') {
                setPtaxUSD(ptaxUSDRes.value.data);
            }
            if (ptaxEURRes.status === 'fulfilled') {
                setPtaxEUR(ptaxEURRes.value.data);
            }
            if (expectativasRes.status === 'fulfilled') {
                setExpectativas(expectativasRes.value.data);
            }

            setUltimaAtualizacao(new Date());
        } catch (error) {
            console.error('Erro ao carregar dados:', error);
        } finally {
            setLoading(false);
        }
    };

    const atualizarIndices = async () => {
        setAtualizando(true);
        try {
            await api.post('/api/atualizacao-monetaria/atualizar/recentes', { dias: 30 });
            await carregarDados();
        } catch (error) {
            console.error('Erro ao atualizar:', error);
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

    const formatarPercentual = (valor: number, casas: number = 2) => {
        return `${valor.toLocaleString('pt-BR', {
            minimumFractionDigits: casas,
            maximumFractionDigits: casas
        })}%`;
    };

    const formatarData = (data: string) => {
        if (!data) return '-';
        return new Date(data).toLocaleDateString('pt-BR');
    };

    const formatarDataHora = (data: Date) => {
        return data.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    // Converter valor baseado no tipo
    const formatarValorIndice = (valor: number | null, nome: string) => {
        if (valor === null) return '-';

        // SELIC/CDI: taxa diária → anual
        if (nome === 'SELIC' || nome === 'CDI' || nome === 'SELIC-EFETIVA') {
            const anual = valor * 252;
            return `${formatarMoeda(anual, 2)}% a.a.`;
        }

        // TJLP já vem anual
        if (nome === 'TJLP') {
            return `${formatarMoeda(valor, 2)}% a.a.`;
        }

        // Câmbio
        if (nome.includes('DOLAR') || nome.includes('EURO')) {
            return `R$ ${formatarMoeda(valor, 4)}`;
        }

        // Demais: percentual mensal
        return `${formatarMoeda(valor, 2)}%`;
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <RefreshCw className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
                    <p className="text-muted-foreground">Carregando dados do Banco Central...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-[1800px] mx-auto space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <BarChart3 className="w-8 h-8 text-primary" />
                        Dados Monetários BCB
                    </h1>
                    <p className="text-muted-foreground mt-1">
                        Dados oficiais do Banco Central do Brasil
                        {ultimaAtualizacao && (
                            <span className="ml-2 text-xs">
                                • Última atualização: {formatarDataHora(ultimaAtualizacao)}
                            </span>
                        )}
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

            {/* Cotações PTAX - Destaque */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Dólar */}
                <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/10 border border-green-500/30 rounded-2xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-green-500/20 rounded-xl">
                                <DollarSign className="w-8 h-8 text-green-400" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold">Dólar PTAX</h2>
                                <p className="text-sm text-muted-foreground">
                                    {ptaxUSD ? formatarData(ptaxUSD.data) : 'Carregando...'}
                                </p>
                            </div>
                        </div>
                        <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-medium">
                            USD/BRL
                        </span>
                    </div>

                    {ptaxUSD ? (
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-background/50 rounded-xl p-4">
                                <p className="text-sm text-muted-foreground mb-1">Compra</p>
                                <p className="text-3xl font-bold text-green-400">
                                    R$ {formatarMoeda(ptaxUSD.cotacao_compra)}
                                </p>
                            </div>
                            <div className="bg-background/50 rounded-xl p-4">
                                <p className="text-sm text-muted-foreground mb-1">Venda</p>
                                <p className="text-3xl font-bold">
                                    R$ {formatarMoeda(ptaxUSD.cotacao_venda)}
                                </p>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-8 text-muted-foreground">
                            Cotação não disponível
                        </div>
                    )}
                </div>

                {/* Euro */}
                <div className="bg-gradient-to-br from-blue-500/20 to-indigo-500/10 border border-blue-500/30 rounded-2xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-blue-500/20 rounded-xl">
                                <Globe className="w-8 h-8 text-blue-400" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold">Euro PTAX</h2>
                                <p className="text-sm text-muted-foreground">
                                    {ptaxEUR ? formatarData(ptaxEUR.data) : 'Carregando...'}
                                </p>
                            </div>
                        </div>
                        <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm font-medium">
                            EUR/BRL
                        </span>
                    </div>

                    {ptaxEUR ? (
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-background/50 rounded-xl p-4">
                                <p className="text-sm text-muted-foreground mb-1">Compra</p>
                                <p className="text-3xl font-bold text-blue-400">
                                    R$ {formatarMoeda(ptaxEUR.cotacao_compra)}
                                </p>
                            </div>
                            <div className="bg-background/50 rounded-xl p-4">
                                <p className="text-sm text-muted-foreground mb-1">Venda</p>
                                <p className="text-3xl font-bold">
                                    R$ {formatarMoeda(ptaxEUR.cotacao_venda)}
                                </p>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-8 text-muted-foreground">
                            Cotação não disponível
                        </div>
                    )}
                </div>
            </div>

            {/* Expectativas de Mercado - Focus */}
            <div className="bg-card border border-border rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 bg-primary/20 rounded-lg">
                        <Target className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold">Expectativas de Mercado</h2>
                        <p className="text-sm text-muted-foreground">Relatório Focus - Projeções dos analistas</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {/* SELIC */}
                    <div className="bg-background border border-border rounded-xl p-4">
                        <h3 className="font-semibold text-orange-400 mb-3 flex items-center gap-2">
                            <Percent className="w-4 h-4" />
                            SELIC
                        </h3>
                        {expectativas.selic[0] ? (
                            <>
                                <p className="text-2xl font-bold">{formatarPercentual(expectativas.selic[0].mediana)} a.a.</p>
                                <p className="text-sm text-muted-foreground">
                                    Ref: {expectativas.selic[0].data_referencia}
                                </p>
                                <div className="mt-2 text-xs text-muted-foreground">
                                    Mín: {formatarPercentual(expectativas.selic[0].minimo)} |
                                    Máx: {formatarPercentual(expectativas.selic[0].maximo)}
                                </div>
                            </>
                        ) : <p className="text-muted-foreground">Sem dados</p>}
                    </div>

                    {/* IPCA */}
                    <div className="bg-background border border-border rounded-xl p-4">
                        <h3 className="font-semibold text-red-400 mb-3 flex items-center gap-2">
                            <TrendingUp className="w-4 h-4" />
                            IPCA
                        </h3>
                        {expectativas.ipca[0] ? (
                            <>
                                <p className="text-2xl font-bold">{formatarPercentual(expectativas.ipca[0].mediana)}</p>
                                <p className="text-sm text-muted-foreground">
                                    Ref: {expectativas.ipca[0].data_referencia}
                                </p>
                                <div className="mt-2 text-xs text-muted-foreground">
                                    Mín: {formatarPercentual(expectativas.ipca[0].minimo)} |
                                    Máx: {formatarPercentual(expectativas.ipca[0].maximo)}
                                </div>
                            </>
                        ) : <p className="text-muted-foreground">Sem dados</p>}
                    </div>

                    {/* PIB */}
                    <div className="bg-background border border-border rounded-xl p-4">
                        <h3 className="font-semibold text-green-400 mb-3 flex items-center gap-2">
                            <BarChart3 className="w-4 h-4" />
                            PIB
                        </h3>
                        {expectativas.pib[0] ? (
                            <>
                                <p className="text-2xl font-bold">{formatarPercentual(expectativas.pib[0].mediana)}</p>
                                <p className="text-sm text-muted-foreground">
                                    Ref: {expectativas.pib[0].data_referencia}
                                </p>
                                <div className="mt-2 text-xs text-muted-foreground">
                                    Mín: {formatarPercentual(expectativas.pib[0].minimo)} |
                                    Máx: {formatarPercentual(expectativas.pib[0].maximo)}
                                </div>
                            </>
                        ) : <p className="text-muted-foreground">Sem dados</p>}
                    </div>

                    {/* Câmbio */}
                    <div className="bg-background border border-border rounded-xl p-4">
                        <h3 className="font-semibold text-blue-400 mb-3 flex items-center gap-2">
                            <DollarSign className="w-4 h-4" />
                            Câmbio (USD)
                        </h3>
                        {expectativas.cambio[0] ? (
                            <>
                                <p className="text-2xl font-bold">R$ {formatarMoeda(expectativas.cambio[0].mediana, 2)}</p>
                                <p className="text-sm text-muted-foreground">
                                    Ref: {expectativas.cambio[0].data_referencia}
                                </p>
                                <div className="mt-2 text-xs text-muted-foreground">
                                    Mín: R$ {formatarMoeda(expectativas.cambio[0].minimo, 2)} |
                                    Máx: R$ {formatarMoeda(expectativas.cambio[0].maximo, 2)}
                                </div>
                            </>
                        ) : <p className="text-muted-foreground">Sem dados</p>}
                    </div>
                </div>
            </div>

            {/* Índices SGS */}
            <div className="bg-card border border-border rounded-2xl p-6">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-primary/20 rounded-lg">
                            <TrendingUp className="w-6 h-6 text-primary" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold">Índices Econômicos (SGS)</h2>
                            <p className="text-sm text-muted-foreground">Sistema Gerenciador de Séries Temporais</p>
                        </div>
                    </div>
                    <a
                        href="/processos/indices"
                        className="text-primary hover:underline text-sm"
                    >
                        Ver histórico completo →
                    </a>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                    {indices.map(indice => (
                        <div
                            key={indice.id}
                            className="bg-background border border-border rounded-xl p-4 hover:border-primary/50 transition-colors"
                        >
                            <h3 className="font-semibold text-sm mb-2 truncate" title={indice.nome}>
                                {indice.nome}
                            </h3>
                            <p className="text-xl font-bold text-primary mb-1">
                                {formatarValorIndice(indice.ultimo_valor, indice.nome)}
                            </p>
                            <p className="text-xs text-muted-foreground">
                                {indice.ultima_atualizacao ? formatarData(indice.ultima_atualizacao) : 'Sem dados'}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">
                                {indice.total_registros} registros
                            </p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Fonte */}
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
                <div className="flex items-start gap-3">
                    <Globe className="w-5 h-5 text-blue-400 mt-0.5" />
                    <div className="text-sm">
                        <p className="font-medium text-blue-300 mb-1">Fonte Oficial: Banco Central do Brasil</p>
                        <p className="text-blue-200/80">
                            Dados obtidos via APIs oficiais: SGS (Séries Temporais) e Olinda (PTAX, Expectativas Focus).
                            Os valores são fornecidos com a mesma precisão das fontes originais.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
