/**
 * ProcessoFilters - Filtros Avançados de Processos
 * Componente reutilizável para filtrar listagem
 */
import { useState } from 'react';
import { Filter, X, Search, Calendar } from 'lucide-react';
import { FiltroPesquisa } from '../../types/processos';

interface ProcessoFiltersProps {
    onFilterChange: (filtros: FiltroPesquisa) => void;
    onClear: () => void;
}

export default function ProcessoFilters({ onFilterChange, onClear }: ProcessoFiltersProps) {
    const [expanded, setExpanded] = useState(false);
    const [filtros, setFiltros] = useState<FiltroPesquisa>({});

    const handleChange = (field: keyof FiltroPesquisa, value: any) => {
        const novosFiltros = { ...filtros, [field]: value };
        setFiltros(novosFiltros);
        onFilterChange(novosFiltros);
    };

    const handleClear = () => {
        setFiltros({});
        onClear();
    };

    const countActiveFilters = () => {
        return Object.values(filtros).filter(v => v !== undefined && v !== '' && v !== null).length;
    };

    return (
        <div className="bg-card border border-border rounded-xl overflow-hidden">
            {/* Header */}
            <div className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary/20 rounded-lg">
                        <Filter className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                        <h3 className="font-semibold">Filtros</h3>
                        {countActiveFilters() > 0 && (
                            <p className="text-xs text-muted-foreground">
                                {countActiveFilters()} filtro(s) ativo(s)
                            </p>
                        )}
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    {countActiveFilters() > 0 && (
                        <button
                            onClick={handleClear}
                            className="flex items-center gap-2 px-3 py-1.5 text-sm text-red-400 hover:bg-red-500/20 rounded-lg transition-colors"
                        >
                            <X className="w-4 h-4" />
                            Limpar
                        </button>
                    )}

                    <button
                        onClick={() => setExpanded(!expanded)}
                        className="px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors text-sm"
                    >
                        {expanded ? 'Recolher' : 'Expandir'}
                    </button>
                </div>
            </div>

            {/* Basic Search (Always Visible) */}
            <div className="px-4 pb-4">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <input
                        type="text"
                        value={filtros.busca || ''}
                        onChange={(e) => handleChange('busca', e.target.value)}
                        placeholder="Buscar por CNJ, pasta, título..."
                        className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                </div>
            </div>

            {/* Advanced Filters (Expandable) */}
            {expanded && (
                <div className="px-4 pb-4 pt-2 border-t border-border space-y-4">

                    {/* Row 1: Natureza e Status */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">Natureza</label>
                            <select
                                value={filtros.natureza_id || ''}
                                onChange={(e) => handleChange('natureza_id', e.target.value ? Number(e.target.value) : undefined)}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                            >
                                <option value="">Todas</option>
                                <option value="1">Tributário</option>
                                <option value="2">Trabalhista</option>
                                <option value="3">Cível</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Status</label>
                            <select
                                value={filtros.status_id || ''}
                                onChange={(e) => handleChange('status_id', e.target.value ? Number(e.target.value) : undefined)}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                            >
                                <option value="">Todos</option>
                                <option value="1">Ativo</option>
                                <option value="2">Arquivado</option>
                                <option value="3">Suspenso</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Cliente</label>
                            <input
                                type="number"
                                value={filtros.cliente_id || ''}
                                onChange={(e) => handleChange('cliente_id', e.target.value ? Number(e.target.value) : undefined)}
                                placeholder="ID do cliente"
                                className="w-full bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                            />
                        </div>
                    </div>

                    {/* Row 2: Datas */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                                <Calendar className="w-4 h-4" />
                                Data Início
                            </label>
                            <input
                                type="date"
                                value={filtros.data_inicio || ''}
                                onChange={(e) => handleChange('data_inicio', e.target.value)}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                                <Calendar className="w-4 h-4" />
                                Data Fim
                            </label>
                            <input
                                type="date"
                                value={filtros.data_fim || ''}
                                onChange={(e) => handleChange('data_fim', e.target.value)}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                            />
                        </div>
                    </div>

                    {/* Row 3: Ordenação */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">Ordenar por</label>
                            <select
                                value={filtros.ordenacao || 'data_criacao'}
                                onChange={(e) => handleChange('ordenacao', e.target.value)}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                            >
                                <option value="data_criacao">Data Criação</option>
                                <option value="data_distribuicao">Data Distribuição</option>
                                <option value="numero_cnj">Número CNJ</option>
                                <option value="pasta">Pasta</option>
                                <option value="valor_causa">Valor da Causa</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Ordem</label>
                            <select
                                value={filtros.ordem || 'desc'}
                                onChange={(e) => handleChange('ordem', e.target.value as 'asc' | 'desc')}
                                className="w-full bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                            >
                                <option value="asc">Crescente (A-Z, 0-9)</option>
                                <option value="desc">Decrescente (Z-A, 9-0)</option>
                            </select>
                        </div>
                    </div>

                    {/* Active Filters Summary */}
                    {countActiveFilters() > 0 && (
                        <div className="bg-primary/10 border border-primary/20 rounded-lg p-4">
                            <div className="flex items-start gap-3">
                                <Filter className="w-5 h-5 text-primary mt-0.5" />
                                <div className="flex-1">
                                    <h4 className="font-semibold text-primary mb-2">Filtros Ativos</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {Object.entries(filtros).map(([key, value]) => {
                                            if (!value) return null;

                                            const labels: Record<string, string> = {
                                                busca: 'Busca',
                                                natureza_id: 'Natureza',
                                                status_id: 'Status',
                                                cliente_id: 'Cliente',
                                                data_inicio: 'Data Início',
                                                data_fim: 'Data Fim',
                                                ordenacao: 'Ordenação',
                                                ordem: 'Ordem'
                                            };

                                            return (
                                                <span
                                                    key={key}
                                                    className="inline-flex items-center gap-2 px-3 py-1 bg-primary/20 text-primary rounded-full text-xs"
                                                >
                                                    <span className="font-medium">{labels[key]}:</span>
                                                    <span>{value.toString()}</span>
                                                    <button
                                                        onClick={() => handleChange(key as keyof FiltroPesquisa, undefined)}
                                                        className="hover:bg-primary/30 rounded-full p-0.5 transition-colors"
                                                    >
                                                        <X className="w-3 h-3" />
                                                    </button>
                                                </span>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
