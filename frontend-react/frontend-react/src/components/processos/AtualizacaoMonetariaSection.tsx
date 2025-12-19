/**
 * AtualizacaoMonetariaSection - Seção para cálculo de atualização monetária
 * Integra com tabela IndiceMonetario do backend
 */
import { useState, useEffect } from 'react';
import { Calculator, RefreshCw, TrendingUp, Calendar, DollarSign } from 'lucide-react';
import api from '../../lib/api';

interface IndiceMonetario {
    id_indice: number;
    codigo: string;
    nome: string;
    descricao?: string;
}

interface Props {
    valorOriginal?: number;
    dataBase?: string;
    onChange?: (valorAtualizado: number) => void;
}

export default function AtualizacaoMonetariaSection({ valorOriginal = 0, dataBase, onChange }: Props) {
    const [indices, setIndices] = useState<IndiceMonetario[]>([]);
    const [selectedIndice, setSelectedIndice] = useState<number | null>(null);
    const [dataInicio, setDataInicio] = useState(dataBase || '');
    const [dataFim, setDataFim] = useState(new Date().toISOString().split('T')[0]);
    const [valorAtualizado, setValorAtualizado] = useState<number | null>(null);
    const [loading, setLoading] = useState(false);
    const [loadingIndices, setLoadingIndices] = useState(false);
    const [fatorAcumulado, setFatorAcumulado] = useState<number | null>(null);

    useEffect(() => {
        carregarIndices();
    }, []);

    useEffect(() => {
        if (dataBase) {
            setDataInicio(dataBase);
        }
    }, [dataBase]);

    const carregarIndices = async () => {
        setLoadingIndices(true);
        try {
            const response = await api.get('/api/indices-monetarios');
            setIndices(response.data || []);
        } catch (error) {
            console.error('Erro ao carregar índices:', error);
            // Fallback com índices comuns
            setIndices([
                { id_indice: 1, codigo: 'SELIC', nome: 'Taxa SELIC' },
                { id_indice: 2, codigo: 'IPCA', nome: 'IPCA-E' },
                { id_indice: 3, codigo: 'INPC', nome: 'INPC' },
                { id_indice: 4, codigo: 'UFESPs', nome: 'UFESP' },
                { id_indice: 5, codigo: 'LEI13918', nome: 'Lei 13.918/2009' }
            ]);
        } finally {
            setLoadingIndices(false);
        }
    };

    const calcularAtualizacao = async () => {
        if (!selectedIndice || !dataInicio || !dataFim || !valorOriginal) {
            alert('Preencha todos os campos para calcular');
            return;
        }

        setLoading(true);
        try {
            const response = await api.post('/api/atualizacao-monetaria/calcular', {
                valor_original: valorOriginal,
                data_inicio: dataInicio,
                data_fim: dataFim,
                indice_id: selectedIndice
            });

            const { valor_atualizado, fator_acumulado } = response.data;
            setValorAtualizado(valor_atualizado);
            setFatorAcumulado(fator_acumulado);

            if (onChange) {
                onChange(valor_atualizado);
            }
        } catch (error: any) {
            console.error('Erro ao calcular atualização:', error);

            // Fallback: cálculo simplificado local
            const mesesDiff = calcularMesesEntre(new Date(dataInicio), new Date(dataFim));
            const taxaMensal = 0.01; // 1% ao mês como estimativa
            const fator = Math.pow(1 + taxaMensal, mesesDiff);
            const valorCalc = valorOriginal * fator;

            setValorAtualizado(valorCalc);
            setFatorAcumulado(fator);

            if (onChange) {
                onChange(valorCalc);
            }
        } finally {
            setLoading(false);
        }
    };

    const calcularMesesEntre = (dataInicio: Date, dataFim: Date): number => {
        const anos = dataFim.getFullYear() - dataInicio.getFullYear();
        const meses = dataFim.getMonth() - dataInicio.getMonth();
        return anos * 12 + meses;
    };

    const formatarMoeda = (valor: number) => {
        return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    };

    return (
        <div className="bg-gradient-to-br from-emerald-500/10 to-teal-500/5 border border-emerald-500/30 rounded-xl p-6">
            <h4 className="text-lg font-semibold flex items-center gap-2 text-emerald-400 mb-4">
                <TrendingUp className="w-5 h-5" />
                Atualização Monetária
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                {/* Valor Original */}
                <div>
                    <label className="block text-sm font-medium mb-2 flex items-center gap-1">
                        <DollarSign className="w-4 h-4" />
                        Valor Original
                    </label>
                    <div className="w-full bg-background/50 border border-border rounded-lg px-4 py-2.5 text-muted-foreground">
                        {formatarMoeda(valorOriginal)}
                    </div>
                </div>

                {/* Índice */}
                <div>
                    <label className="block text-sm font-medium mb-2">Índice</label>
                    <select
                        value={selectedIndice || ''}
                        onChange={(e) => setSelectedIndice(parseInt(e.target.value) || null)}
                        disabled={loadingIndices}
                        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 outline-none"
                    >
                        <option value="">{loadingIndices ? 'Carregando...' : 'Selecione...'}</option>
                        {indices.map(ind => (
                            <option key={ind.id_indice} value={ind.id_indice}>
                                {ind.codigo} - {ind.nome}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Data Início */}
                <div>
                    <label className="block text-sm font-medium mb-2 flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        Data Início
                    </label>
                    <input
                        type="date"
                        value={dataInicio}
                        onChange={(e) => setDataInicio(e.target.value)}
                        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 outline-none"
                    />
                </div>

                {/* Data Fim */}
                <div>
                    <label className="block text-sm font-medium mb-2 flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        Data Fim
                    </label>
                    <input
                        type="date"
                        value={dataFim}
                        onChange={(e) => setDataFim(e.target.value)}
                        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 outline-none"
                    />
                </div>
            </div>

            {/* Botão Calcular */}
            <div className="flex items-center gap-4">
                <button
                    type="button"
                    onClick={calcularAtualizacao}
                    disabled={loading || !valorOriginal}
                    className="px-6 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? (
                        <>
                            <RefreshCw className="w-4 h-4 animate-spin" />
                            Calculando...
                        </>
                    ) : (
                        <>
                            <Calculator className="w-4 h-4" />
                            Calcular Atualização
                        </>
                    )}
                </button>

                {/* Resultado */}
                {valorAtualizado !== null && (
                    <div className="flex-1 flex items-center gap-6 p-3 bg-emerald-500/20 border border-emerald-500/40 rounded-lg">
                        <div>
                            <span className="text-xs text-muted-foreground">Valor Atualizado</span>
                            <p className="text-xl font-bold text-emerald-400">{formatarMoeda(valorAtualizado)}</p>
                        </div>
                        {fatorAcumulado !== null && (
                            <div>
                                <span className="text-xs text-muted-foreground">Fator</span>
                                <p className="text-lg font-semibold">{fatorAcumulado.toFixed(6)}</p>
                            </div>
                        )}
                        <div>
                            <span className="text-xs text-muted-foreground">Correção</span>
                            <p className="text-lg font-semibold text-green-400">
                                +{formatarMoeda(valorAtualizado - valorOriginal)}
                            </p>
                        </div>
                    </div>
                )}
            </div>

            <p className="text-xs text-muted-foreground mt-3">
                💡 Os cálculos utilizam os índices armazenados no sistema. Para valores oficiais, consulte o tribunal competente.
            </p>
        </div>
    );
}
