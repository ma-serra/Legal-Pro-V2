import { useState, useEffect } from 'react';
import { TrendingUp, Save, AlertCircle, Calculator, RefreshCw } from 'lucide-react';
import api from '../../lib/api';

interface PrognosticoData {
    tese_provavel?: string;
    probabilidade_provavel?: number;
    valor_provavel?: number;
    tese_possivel?: string;
    probabilidade_possivel?: number;
    valor_possivel?: number;
    tese_remota?: string;
    probabilidade_remota?: number;
    valor_remoto?: number;
}

interface Props {
    processoId: number;
}

export default function PrognosticoTab({ processoId }: Props) {
    const [prognostico, setPrognostico] = useState<PrognosticoData>({});
    const [valorEsperado, setValorEsperado] = useState<number | null>(null);
    const [loading, setLoading] = useState(true);
    const [salvando, setSalvando] = useState(false);
    const [erro, setErro] = useState<string | null>(null);

    useEffect(() => {
        carregarPrognostico();
    }, [processoId]);

    useEffect(() => {
        calcularValorEsperado();
    }, [prognostico]);

    const carregarPrognostico = async () => {
        setLoading(true);
        try {
            const response = await api.get(`/api/tributario/processos/${processoId}/prognostico`);
            setPrognostico(response.data || {});

            // Carregar valor esperado
            try {
                const veResponse = await api.get(`/api/tributario/processos/${processoId}/valor-esperado`);
                setValorEsperado(veResponse.data?.valor_esperado);
            } catch {
                // Ignorar erro valor esperado
            }
        } catch (error: any) {
            if (error.response?.status !== 404) {
                console.error('Erro ao carregar prognóstico:', error);
            }
        } finally {
            setLoading(false);
        }
    };

    const calcularValorEsperado = () => {
        const probProv = prognostico.probabilidade_provavel || 0;
        const probPoss = prognostico.probabilidade_possivel || 0;
        const probRem = prognostico.probabilidade_remota || 0;

        const valProv = prognostico.valor_provavel || 0;
        const valPoss = prognostico.valor_possivel || 0;
        const valRem = prognostico.valor_remoto || 0;

        if (probProv === 0 && probPoss === 0 && probRem === 0) {
            setValorEsperado(null);
            return;
        }

        const ve = (probProv * valProv + probPoss * valPoss + probRem * valRem) / 100;
        setValorEsperado(ve);
    };

    const handleChange = (field: keyof PrognosticoData, value: string | number) => {
        setPrognostico(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const validarPrognostico = (): boolean => {
        const probProv = prognostico.probabilidade_provavel || 0;
        const probPoss = prognostico.probabilidade_possivel || 0;
        const probRem = prognostico.probabilidade_remota || 0;

        const soma = probProv + probPoss + probRem;

        if (soma > 100) {
            setErro('A soma das probabilidades não pode exceder 100%');
            return false;
        }

        if (soma === 0) {
            setErro('Preencha pelo menos uma probabilidade');
            return false;
        }

        setErro(null);
        return true;
    };

    const salvarPrognostico = async () => {
        if (!validarPrognostico()) return;

        setSalvando(true);
        try {
            await api.post(`/api/tributario/processos/${processoId}/prognostico`, prognostico);

            // Recarregar valor esperado do backend
            const response = await api.get(`/api/tributario/processos/${processoId}/valor-esperado`);
            setValorEsperado(response.data?.valor_esperado);

            alert('Prognóstico salvo com sucesso!');
        } catch (error: any) {
            console.error('Erro ao salvar prognóstico:', error);
            setErro(error.response?.data?.error || 'Erro ao salvar prognóstico');
        } finally {
            setSalvando(false);
        }
    };

    const formatarMoeda = (valor: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <RefreshCw className="w-6 h-6 animate-spin text-muted-foreground" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {erro && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-400">{erro}</p>
                </div>
            )}

            {/* Cenário Provável */}
            <div className="bg-green-500/5 border border-green-500/20 rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <h3 className="font-semibold text-lg">Cenário Provável</h3>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">Tese/Descrição</label>
                        <textarea
                            value={prognostico.tese_provavel || ''}
                            onChange={(e) => handleChange('tese_provavel', e.target.value)}
                            className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
                            rows={3}
                            placeholder="Descreva a tese..."
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">Probabilidade (%)</label>
                            <input
                                type="range"
                                min="0"
                                max="100"
                                value={prognostico.probabilidade_provavel || 0}
                                onChange={(e) => handleChange('probabilidade_provavel', parseInt(e.target.value))}
                                className="w-full mb-2"
                            />
                            <div className="text-center text-2xl font-bold text-green-500">
                                {prognostico.probabilidade_provavel || 0}%
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Valor (R$)</label>
                            <input
                                type="number"
                                value={prognostico.valor_provavel || ''}
                                onChange={(e) => handleChange('valor_provavel', parseFloat(e.target.value) || 0)}
                                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
                                placeholder="0,00"
                                step="0.01"
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Cenário Possível */}
            <div className="bg-yellow-500/5 border border-yellow-500/20 rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                    <h3 className="font-semibold text-lg">Cenário Possível</h3>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">Tese/Descrição</label>
                        <textarea
                            value={prognostico.tese_possivel || ''}
                            onChange={(e) => handleChange('tese_possivel', e.target.value)}
                            className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
                            rows={3}
                            placeholder="Descreva a tese..."
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">Probabilidade (%)</label>
                            <input
                                type="range"
                                min="0"
                                max="100"
                                value={prognostico.probabilidade_possivel || 0}
                                onChange={(e) => handleChange('probabilidade_possivel', parseInt(e.target.value))}
                                className="w-full mb-2"
                            />
                            <div className="text-center text-2xl font-bold text-yellow-500">
                                {prognostico.probabilidade_possivel || 0}%
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Valor (R$)</label>
                            <input
                                type="number"
                                value={prognostico.valor_possivel || ''}
                                onChange={(e) => handleChange('valor_possivel', parseFloat(e.target.value) || 0)}
                                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
                                placeholder="0,00"
                                step="0.01"
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Cenário Remoto */}
            <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                    <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                    <h3 className="font-semibold text-lg">Cenário Remoto</h3>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">Tese/Descrição</label>
                        <textarea
                            value={prognostico.tese_remota || ''}
                            onChange={(e) => handleChange('tese_remota', e.target.value)}
                            className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
                            rows={3}
                            placeholder="Descreva a tese..."
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">Probabilidade (%)</label>
                            <input
                                type="range"
                                min="0"
                                max="100"
                                value={prognostico.probabilidade_remota || 0}
                                onChange={(e) => handleChange('probabilidade_remota', parseInt(e.target.value))}
                                className="w-full mb-2"
                            />
                            <div className="text-center text-2xl font-bold text-red-500">
                                {prognostico.probabilidade_remota || 0}%
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Valor (R$)</label>
                            <input
                                type="number"
                                value={prognostico.valor_remoto || ''}
                                onChange={(e) => handleChange('valor_remoto', parseFloat(e.target.value) || 0)}
                                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
                                placeholder="0,00"
                                step="0.01"
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Valor Esperado */}
            {valorEsperado !== null && (
                <div className="bg-gradient-to-br from-primary/10 to-primary/5 border-2 border-primary/30 rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <Calculator className="w-6 h-6 text-primary" />
                        <h3 className="font-semibold text-lg">Valor Esperado Calculado</h3>
                    </div>

                    <div className="text-center">
                        <div className="text-4xl font-bold text-primary mb-4">
                            {formatarMoeda(valorEsperado)}
                        </div>

                        <div className="text-sm text-muted-foreground space-y-1">
                            <p>Cálculo: (Prob × Valor) de cada cenário</p>
                            <p className="font-mono text-xs">
                                = ({prognostico.probabilidade_provavel || 0}% × {formatarMoeda(prognostico.valor_provavel || 0)}) +
                                ({prognostico.probabilidade_possivel || 0}% × {formatarMoeda(prognostico.valor_possivel || 0)}) +
                                ({prognostico.probabilidade_remota || 0}% × {formatarMoeda(prognostico.valor_remoto || 0)})
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Botão Salvar */}
            <div className="flex justify-end pt-4">
                <button
                    onClick={salvarPrognostico}
                    disabled={salvando}
                    className="px-6 py-3 bg-primary hover:bg-primary/90 text-white rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 font-semibold"
                >
                    {salvando ? (
                        <>
                            <RefreshCw className="w-5 h-5 animate-spin" />
                            Salvando...
                        </>
                    ) : (
                        <>
                            <Save className="w-5 h-5" />
                            Salvar Prognóstico
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}
