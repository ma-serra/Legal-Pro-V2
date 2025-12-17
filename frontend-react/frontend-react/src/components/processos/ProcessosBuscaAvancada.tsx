import { useState } from 'react';
import { Search, X, Calendar, Building2, Scale, Filter, RefreshCw } from 'lucide-react';
import { Processo } from '../../types/processos';
import api from '../../lib/api';

interface BuscaAvancadaFilters {
    cnj?: string;
    pasta?: string;
    cliente?: string;
    natureza_id?: number;
    status_id?: number;
    data_inicio?: string;
    data_fim?: string;
    valor_min?: number;
    valor_max?: number;
}

interface Props {
    onClose: () => void;
    onResultados: (processos: Processo[]) => void;
}

export default function ProcessosBuscaAvancada({ onClose, onResultados }: Props) {
    const [filtros, setFiltros] = useState<BuscaAvancadaFilters>({});
    const [buscando, setBuscando] = useState(false);
    const [totalResultados, setTotalResultados] = useState<number | null>(null);

    const handleBuscar = async () => {
        setBuscando(true);
        try {
            const params = { ...filtros };
            const response = await api.get('/api/processos/buscar', { params });

            const processos = response.data.processos || response.data || [];
            setTotalResultados(processos.length);
            onResultados(processos);
        } catch (error) {
            console.error('Erro ao buscar:', error);
            alert('Erro ao realizar busca. Tente novamente.');
        } finally {
            setBuscando(false);
        }
    };

    const handleLimpar = () => {
        setFiltros({});
        setTotalResultados(null);
    };

    const handleChange = (field: keyof BuscaAvancadaFilters, value: any) => {
        setFiltros(prev => ({
            ...prev,
            [field]: value || undefined
        }));
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-card border border-border rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="bg-gradient-to-r from-primary/20 to-primary/5 border-b border-border p-6">
                    <div className="flex items-start justify-between">
                        <div>
                            <div className="flex items-center gap-3 mb-2">
                                <Search className="w-6 h-6 text-primary" />
                                <h2 className="text-2xl font-bold">Busca Avançada de Processos</h2>
                            </div>
                            <p className="text-muted-foreground">
                                Pesquise processos por múltiplos critérios
                            </p>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-accent rounded-lg transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* CNJ */}
                        <div>
                            <label className="block text-sm font-medium mb-2">Número CNJ</label>
                            <input
                                type="text"
                                value={filtros.cnj || ''}
                                onChange={(e) => handleChange('cnj', e.target.value)}
                                placeholder="0000000-00.0000.0.00.0000"
                                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
                            />
                        </div>

                        {/* Pasta */}
                        <div>
                            <label className="block text-sm font-medium mb-2">Pasta</label>
                            <input
                                type="text"
                                value={filtros.pasta || ''}
                                onChange={(e) => handleChange('pasta', e.target.value)}
                                placeholder="Nome da pasta..."
                                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
                            />
                        </div>

                        {/* Cliente */}
                        <div>
                            <label className="block text-sm font-medium mb-2">Cliente</label>
                            <input
                                type="text"
                                value={filtros.cliente || ''}
                                onChange={(e) => handleChange('cliente', e.target.value)}
                                placeholder="Nome do cliente..."
                                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
                            />
                        </div>

                        {/* Natureza */}
                        <div>
                            <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                                <Scale className="w-4 h-4" />
                                Natureza
                            </label>
                            <select
                                value={filtros.natureza_id || ''}
                                onChange={(e) => handleChange('natureza_id', e.target.value ? Number(e.target.value) : undefined)}
                                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
                            >
                                <option value="">Todas</option>
                                <option value="1">Tributário</option>
                                <option value="2">Trabalhista</option>
                                <option value="3">Cível</option>
                            </select>
                        </div>

                        {/* Status */}
                        <div>
                            <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                                <Building2 className="w-4 h-4" />
                                Status
                            </label>
                            <select
                                value={filtros.status_id || ''}
                                onChange={(e) => handleChange('status_id', e.target.value ? Number(e.target.value) : undefined)}
                                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
                            >
                                <option value="">Todos</option>
                                <option value="1">Ativo</option>
                                <option value="2">Arquivado</option>
                                <option value="3">Suspenso</option>
                            </select>
                        </div>

                        {/* Data Início */}
                        <div>
                            <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                                <Calendar className="w-4 h-4" />
                                Data Início (a partir de)
                            </label>
                            <input
                                type="date"
                                value={filtros.data_inicio || ''}
                                onChange={(e) => handleChange('data_inicio', e.target.value)}
                                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
                            />
                        </div>

                        {/* Data Fim */}
                        <div>
                            <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                                <Calendar className="w-4 h-4" />
                                Data Fim (até)
                            </label>
                            <input
                                type="date"
                                value={filtros.data_fim || ''}
                                onChange={(e) => handleChange('data_fim', e.target.value)}
                                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
                            />
                        </div>

                        {/* Valor Mínimo */}
                        <div>
                            <label className="block text-sm font-medium mb-2">Valor Mínimo (R$)</label>
                            <input
                                type="number"
                                value={filtros.valor_min || ''}
                                onChange={(e) => handleChange('valor_min', e.target.value ? parseFloat(e.target.value) : undefined)}
                                placeholder="0.00"
                                step="0.01"
                                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
                            />
                        </div>

                        {/* Valor Máximo */}
                        <div>
                            <label className="block text-sm font-medium mb-2">Valor Máximo (R$)</label>
                            <input
                                type="number"
                                value={filtros.valor_max || ''}
                                onChange={(e) => handleChange('valor_max', e.target.value ? parseFloat(e.target.value) : undefined)}
                                placeholder="0.00"
                                step="0.01"
                                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
                            />
                        </div>
                    </div>

                    {/* Resultado Info */}
                    {totalResultados !== null && (
                        <div className="mt-6 p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                            <p className="text-sm font-semibold text-green-400">
                                ✓ Encontrados {totalResultados} processo(s)
                            </p>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="border-t border-border p-6 bg-accent/20">
                    <div className="flex items-center justify-between">
                        <button
                            onClick={handleLimpar}
                            className="px-4 py-2 border border-border hover:bg-accent rounded-lg transition-colors flex items-center gap-2"
                        >
                            <RefreshCw className="w-4 h-4" />
                            Limpar Filtros
                        </button>

                        <div className="flex gap-3">
                            <button
                                onClick={onClose}
                                className="px-6 py-2 border border-border hover:bg-accent rounded-lg transition-colors"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleBuscar}
                                disabled={buscando}
                                className="px-6 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg font-semibold transition-colors disabled:opacity-50 flex items-center gap-2"
                            >
                                {buscando ? (
                                    <>
                                        <RefreshCw className="w-4 h-4 animate-spin" />
                                        Buscando...
                                    </>
                                ) : (
                                    <>
                                        <Search className="w-4 h-4" />
                                        Buscar
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
