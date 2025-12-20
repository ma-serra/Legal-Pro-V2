/**
 * Listagem de Processos Dinâmicos - UX Premium
 * Integração com 43 APIs REST (Fases 2-4)
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Gavel, Plus, Filter, Download, RefreshCw,
    FileText, TrendingUp, AlertCircle, CheckCircle,
    Calendar, DollarSign, Scale, Building2, Brain, Search, AlertTriangle, Users
} from 'lucide-react';
import { Processo, FiltroPesquisa } from '../../types/processos';
import api from '../../lib/api';
import BatchPredictModal from '../../components/processos/BatchPredictModal';
import ProcessosBuscaAvancada from '../../components/processos/ProcessosBuscaAvancada';

export default function ProcessosDinamicosList() {
    const navigate = useNavigate();
    const [processos, setProcessos] = useState<Processo[]>([]);
    const [loading, setLoading] = useState(true);
    const [filtros, setFiltros] = useState<FiltroPesquisa>({
        page: 1,
        per_page: 20,
        ordem: 'desc',
        ordenacao: 'data_criacao'
    });

    const [stats, setStats] = useState({
        total: 0,
        tributario: 0,
        trabalhista: 0,
        civel: 0,
        previdenciario: 0,
        penal: 0,
        administrativo: 0,
        constitucional: 0,
        valorTotal: 0
    });

    // States para features avançadas
    const [selecionados, setSelecionados] = useState<number[]>([]);
    const [showBatchModal, setShowBatchModal] = useState(false);
    const [showBuscaAvancada, setShowBuscaAvancada] = useState(false);

    // Dados auxiliares para filtros
    const [advogados, setAdvogados] = useState<any[]>([]);
    const [fases, setFases] = useState<any[]>([]);
    const [comarcas, setComarcas] = useState<any[]>([]);

    useEffect(() => {
        fetchAuxiliaryData();
        fetchProcessos();
        setSelecionados([]);
    }, [filtros]);

    const fetchAuxiliaryData = async () => {
        try {
            const [advRes, faseRes, comarcaRes, statsRes] = await Promise.all([
                api.get('/api/processos/advogados'),
                api.get('/api/processos/fases'),
                api.get('/api/processos/comarcas'),
                api.get('/api/processos/estatisticas')
            ]);
            setAdvogados(advRes.data || []);
            setFases(faseRes.data || []);
            setComarcas(comarcaRes.data || []);

            // Stats from /api/processos/estatisticas - use real database totals
            if (statsRes.data) {
                const porNatureza = statsRes.data.por_natureza || {};
                setStats({
                    total: statsRes.data.total_processos || 0,
                    tributario: porNatureza['1'] || 0,
                    trabalhista: porNatureza['2'] || 0,
                    civel: porNatureza['3'] || 0,
                    previdenciario: porNatureza['4'] || 0,
                    penal: porNatureza['10'] || 0,
                    administrativo: porNatureza['14'] || 0,
                    constitucional: porNatureza['15'] || 0,
                    valorTotal: statsRes.data.valores_financeiros?.total_valor_causa || 0
                });
            }
        } catch (error) {
            console.error('Erro ao carregar filtros:', error);
        }
    };

    const fetchProcessos = async () => {
        setLoading(true);
        try {
            const response = await api.get('/api/processos', { params: filtros });

            if (response.data) {
                setProcessos(response.data.processos || []);
                // Stats are loaded separately from /api/processos/estatisticas in fetchAuxiliaryData
            }
        } catch (error) {
            console.error('Erro ao carregar processos:', error);
        } finally {
            setLoading(false);
        }
    };

    const getNaturezaBadge = (natureza_id: number) => {
        const badges: Record<number, { label: string; color: string }> = {
            1: { label: 'Tributário', color: 'bg-orange-500/20 text-orange-400 border-orange-500/30' },
            2: { label: 'Trabalhista', color: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
            3: { label: 'Cível', color: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30' },
            4: { label: 'Previdenciário', color: 'bg-teal-500/20 text-teal-400 border-teal-500/30' },
            10: { label: 'Penal', color: 'bg-red-500/20 text-red-400 border-red-500/30' },
            14: { label: 'Administrativo', color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' },
            15: { label: 'Constitucional', color: 'bg-pink-500/20 text-pink-400 border-pink-500/30' }
        };
        const badge = badges[natureza_id] || { label: 'Outro', color: 'bg-gray-500/20 text-gray-400 border-gray-500/30' };

        return (
            <span className={`px-2 py-1 rounded text-xs font-medium border ${badge.color}`}>
                {badge.label}
            </span>
        );
    };

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('pt-BR');
    };

    const handleExportar = () => {
        const csvContent = [
            ['Pasta', 'CNJ', 'Natureza', 'Valor', 'Data'].join(';'),
            ...processos.map(p => [
                p.pasta,
                p.numero_cnj || '',
                { 1: 'Tributário', 2: 'Trabalhista', 3: 'Cível', 4: 'Previdenciário', 10: 'Penal', 14: 'Administrativo', 15: 'Constitucional' }[p.natureza_id] || 'Outro',
                p.valor_causa || 0,
                formatDate(p.data_criacao)
            ].join(';'))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `processos_${new Date().toISOString().split('T')[0]}.csv`;
        link.click();
    };

    const handleNovoProcesso = () => {
        navigate('/processos/novo');
    };

    const handleVerDetalhes = (processoId: number) => {
        navigate(`/processos/${processoId}`);
    };

    // Novos Handlers
    const handleToggleSelecao = (id: number, e: React.SyntheticEvent) => {
        e.stopPropagation();
        setSelecionados(prev =>
            prev.includes(id) ? prev.filter(pid => pid !== id) : [...prev, id]
        );
    };

    const handleBatchPredict = () => {
        if (selecionados.length === 0) return;
        setShowBatchModal(true);
    };

    const handleBatchSuccess = () => {
        setSelecionados([]);
        fetchProcessos();
    };

    const handleBuscaResultados = (res: Processo[]) => {
        setProcessos(res);
        setShowBuscaAvancada(false);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="text-center space-y-4">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent"></div>
                    <p className="text-muted-foreground">Carregando processos...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <Scale className="w-8 h-8 text-primary" />
                        Processos Dinâmicos
                    </h1>
                    <p className="text-muted-foreground mt-1">
                        Sistema integrado de gestão processual
                    </p>
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={() => setShowBuscaAvancada(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-lg transition-all font-medium shadow-md"
                    >
                        <Search className="w-4 h-4" />
                        Busca Avançada
                    </button>

                    <button
                        onClick={fetchProcessos}
                        className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Atualizar
                    </button>

                    <button
                        onClick={handleExportar}
                        className="flex items-center gap-2 px-4 py-2 bg-secondary hover:bg-secondary/80 rounded-lg transition-colors"
                    >
                        <Download className="w-4 h-4" />
                        Exportar
                    </button>

                    {selecionados.length > 0 && (
                        <button
                            onClick={handleBatchPredict}
                            className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-lg transition-all font-semibold shadow-lg animate-pulse"
                        >
                            <Brain className="w-5 h-5" />
                            Analisar ML ({selecionados.length})
                        </button>
                    )}

                    <button
                        onClick={handleNovoProcesso}
                        className="flex items-center gap-2 px-6 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors font-medium"
                    >
                        <Plus className="w-4 h-4" />
                        Novo Processo
                    </button>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/5 border border-blue-500/20 rounded-xl p-6 hover:shadow-lg hover:scale-105 transition-all duration-300">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Total de Processos</p>
                            <p className="text-3xl font-bold text-blue-400">{stats.total}</p>
                        </div>
                        <div className="p-3 bg-blue-500/20 rounded-lg">
                            <Gavel className="w-6 h-6 text-blue-400" />
                        </div>
                    </div>
                </div>

                <div className="bg-gradient-to-br from-orange-500/10 to-orange-600/5 border border-orange-500/20 rounded-xl p-6 hover:shadow-lg hover:scale-105 transition-all duration-300">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Tributário</p>
                            <p className="text-3xl font-bold text-orange-400">{stats.tributario}</p>
                        </div>
                        <div className="p-3 bg-orange-500/20 rounded-lg">
                            <Building2 className="w-6 h-6 text-orange-400" />
                        </div>
                    </div>
                </div>

                <div className="bg-gradient-to-br from-purple-500/10 to-purple-600/5 border border-purple-500/20 rounded-xl p-6 hover:shadow-lg hover:scale-105 transition-all duration-300">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Trabalhista</p>
                            <p className="text-3xl font-bold text-purple-400">{stats.trabalhista}</p>
                        </div>
                        <div className="p-3 bg-purple-500/20 rounded-lg">
                            <FileText className="w-6 h-6 text-purple-400" />
                        </div>
                    </div>
                </div>

                <div className="bg-gradient-to-br from-indigo-500/10 to-indigo-600/5 border border-indigo-500/20 rounded-xl p-6 hover:shadow-lg hover:scale-105 transition-all duration-300">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Cível</p>
                            <p className="text-3xl font-bold text-indigo-400">{stats.civel}</p>
                        </div>
                        <div className="p-3 bg-indigo-500/20 rounded-lg">
                            <Scale className="w-6 h-6 text-indigo-400" />
                        </div>
                    </div>
                </div>

                <div className="bg-gradient-to-br from-yellow-500/10 to-yellow-600/5 border border-yellow-500/20 rounded-xl p-6 hover:shadow-lg hover:scale-105 transition-all duration-300">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Administrativo</p>
                            <p className="text-3xl font-bold text-yellow-400">{stats.administrativo}</p>
                        </div>
                        <div className="p-3 bg-yellow-500/20 rounded-lg">
                            <Building2 className="w-6 h-6 text-yellow-400" />
                        </div>
                    </div>
                </div>

                <div className="bg-gradient-to-br from-red-500/10 to-red-600/5 border border-red-500/20 rounded-xl p-6 hover:shadow-lg hover:scale-105 transition-all duration-300">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Penal</p>
                            <p className="text-3xl font-bold text-red-400">{stats.penal}</p>
                        </div>
                        <div className="p-3 bg-red-500/20 rounded-lg">
                            <AlertTriangle className="w-6 h-6 text-red-400" />
                        </div>
                    </div>
                </div>

                <div className="bg-gradient-to-br from-teal-500/10 to-teal-600/5 border border-teal-500/20 rounded-xl p-6 hover:shadow-lg hover:scale-105 transition-all duration-300">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Previdenciário</p>
                            <p className="text-3xl font-bold text-teal-400">{stats.previdenciario}</p>
                        </div>
                        <div className="p-3 bg-teal-500/20 rounded-lg">
                            <Users className="w-6 h-6 text-teal-400" />
                        </div>
                    </div>
                </div>

                <div className="bg-gradient-to-br from-pink-500/10 to-pink-600/5 border border-pink-500/20 rounded-xl p-6 hover:shadow-lg hover:scale-105 transition-all duration-300">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Constitucional</p>
                            <p className="text-3xl font-bold text-pink-400">{stats.constitucional}</p>
                        </div>
                        <div className="p-3 bg-pink-500/20 rounded-lg">
                            <FileText className="w-6 h-6 text-pink-400" />
                        </div>
                    </div>
                </div>

                <div className="bg-gradient-to-br from-green-500/10 to-green-600/5 border border-green-500/20 rounded-xl p-6 hover:shadow-lg hover:scale-105 transition-all duration-300">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Valor Total</p>
                            <p className="text-2xl font-bold text-green-400">{formatCurrency(stats.valorTotal)}</p>
                        </div>
                        <div className="p-3 bg-green-500/20 rounded-lg">
                            <DollarSign className="w-6 h-6 text-green-400" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Filters Bar */}
            <div className="bg-card border border-border rounded-xl p-4">
                <div className="flex flex-wrap gap-3 items-center">
                    <Filter className="w-5 h-5 text-muted-foreground" />

                    <input
                        type="text"
                        placeholder="Buscar por CNJ, pasta, título..."
                        className="flex-1 min-w-[200px] bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                        onChange={(e) => setFiltros({ ...filtros, busca: e.target.value, page: 1 })}
                    />

                    <select
                        className="bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                        onChange={(e) => setFiltros({ ...filtros, natureza_id: e.target.value ? Number(e.target.value) : undefined, page: 1 })}
                    >
                        <option value="">Todas as Naturezas</option>
                        <option value="1">Tributário</option>
                        <option value="2">Trabalhista</option>
                        <option value="3">Cível</option>
                        <option value="4">Previdenciário</option>
                        <option value="10">Penal</option>
                        <option value="14">Administrativo</option>
                        <option value="15">Constitucional</option>
                    </select>

                    <select
                        className="bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                        onChange={(e) => setFiltros({ ...filtros, status_id: e.target.value ? Number(e.target.value) : undefined, page: 1 })}
                    >
                        <option value="">Todos os Status</option>
                        <option value="1">Ativo</option>
                        <option value="2">Arquivado</option>
                        <option value="3">Suspenso</option>
                    </select>

                    <select
                        className="bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                        onChange={(e) => setFiltros({ ...filtros, fase_id: e.target.value ? Number(e.target.value) : undefined, page: 1 })}
                    >
                        <option value="">Todas as Fases</option>
                        {fases.map(f => (
                            <option key={f.id} value={f.id}>{f.nome}</option>
                        ))}
                    </select>

                    <select
                        className="bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                        onChange={(e) => setFiltros({ ...filtros, comarca_id: e.target.value ? Number(e.target.value) : undefined, page: 1 })}
                    >
                        <option value="">Todas as Comarcas</option>
                        {comarcas.map(c => (
                            <option key={c.id} value={c.id}>{c.nome}</option>
                        ))}
                    </select>

                    <select
                        className="bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                        onChange={(e) => setFiltros({ ...filtros, advogado_id: e.target.value ? Number(e.target.value) : undefined, page: 1 })}
                    >
                        <option value="">Todos os Advogados</option>
                        {advogados.map(a => (
                            <option key={a.id} value={a.id}>{a.nome}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Processos Grid */}
            {processos.length === 0 ? (
                <div className="bg-card border border-border rounded-xl p-12 text-center">
                    <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-medium mb-2">Nenhum processo encontrado</h3>
                    <p className="text-muted-foreground">
                        Crie seu primeiro processo ou ajuste os filtros
                    </p>
                </div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
                    {processos.map((processo) => (
                        <div
                            key={processo.id_processo}
                            className="relative group bg-card border border-border rounded-xl p-6 hover:shadow-xl hover:scale-[1.02] transition-all duration-300"
                        >
                            {/* Checkbox Overlay */}
                            {processo.natureza_id === 1 && (
                                <div
                                    className="absolute top-4 right-4 z-10"
                                    onClick={(e) => e.stopPropagation()}
                                >
                                    <input
                                        type="checkbox"
                                        checked={selecionados.includes(processo.id_processo)}
                                        onChange={(e) => handleToggleSelecao(processo.id_processo, e)}
                                        className="w-5 h-5 rounded border-2 border-primary text-primary focus:ring-2 focus:ring-primary/50 cursor-pointer"
                                    />
                                </div>
                            )}

                            <div
                                onClick={() => handleVerDetalhes(processo.id_processo)}
                                className="cursor-pointer"
                            >
                                {/* Header do Card */}
                                <div className="flex items-start justify-between mb-4 pr-8">
                                    <div className="flex-1 px-1">
                                        <div className="flex items-center gap-2 mb-2">
                                            {getNaturezaBadge(processo.natureza_id)}
                                            {processo.ativo && (
                                                <CheckCircle className="w-4 h-4 text-green-500" />
                                            )}
                                        </div>
                                        <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">
                                            {processo.titulo || processo.pasta}
                                        </h3>
                                    </div>
                                </div>

                                {/* Info */}
                                <div className="space-y-3 text-sm">
                                    {processo.numero_cnj && (
                                        <div className="flex items-center gap-2 text-muted-foreground">
                                            <FileText className="w-4 h-4" />
                                            <span className="font-mono">{processo.numero_cnj}</span>
                                        </div>
                                    )}

                                    <div className="flex items-center gap-2 text-muted-foreground">
                                        <Scale className="w-4 h-4" />
                                        <span>{processo.pasta}</span>
                                    </div>

                                    {processo.cliente && (
                                        <div className="flex items-center gap-2 text-muted-foreground">
                                            <Building2 className="w-4 h-4" />
                                            <span>{processo.cliente}</span>
                                        </div>
                                    )}

                                    {processo.valor_causa && (
                                        <div className="flex items-center gap-2">
                                            <DollarSign className="w-4 h-4 text-green-500" />
                                            <span className="font-medium">{formatCurrency(processo.valor_causa)}</span>
                                        </div>
                                    )}

                                    <div className="flex items-center gap-2 text-muted-foreground">
                                        <Calendar className="w-4 h-4" />
                                        <span>{formatDate(processo.data_criacao)}</span>
                                    </div>
                                </div>

                                {/* Footer */}
                                <div className="mt-4 pt-4 border-t border-border flex items-center justify-between">
                                    <span className="text-xs text-primary font-medium group-hover:underline">
                                        Ver Detalhes →
                                    </span>
                                    <TrendingUp className="w-4 h-4 text-muted-foreground" />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Pagination */}
            {processos.length > 0 && (
                <div className="flex items-center justify-between bg-card border border-border rounded-xl p-4">
                    <p className="text-sm text-muted-foreground">
                        Mostrando {processos.length} de {stats.total} processos
                    </p>

                    <div className="flex gap-2">
                        <button
                            disabled={filtros.page === 1}
                            onClick={() => setFiltros({ ...filtros, page: (filtros.page || 1) - 1 })}
                            className="px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            Anterior
                        </button>

                        <button
                            onClick={() => setFiltros({ ...filtros, page: (filtros.page || 1) + 1 })}
                            className="px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors"
                        >
                            Próxima
                        </button>
                    </div>
                </div>
            )}

            {/* Modals Avançados */}
            {showBatchModal && (
                <BatchPredictModal
                    processoIds={selecionados}
                    onClose={() => setShowBatchModal(false)}
                    onSuccess={handleBatchSuccess}
                />
            )}

            {showBuscaAvancada && (
                <ProcessosBuscaAvancada
                    onClose={() => setShowBuscaAvancada(false)}
                    onResultados={handleBuscaResultados}
                />
            )}
        </div>
    );
}
