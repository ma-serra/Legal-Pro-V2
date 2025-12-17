/**
 * Listagem de Processos Dinâmicos - UX Premium
 * Integração com 43 APIs REST (Fases 2-4)
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Gavel, Plus, Filter, Download, RefreshCw,
    FileText, TrendingUp, AlertCircle, CheckCircle,
    Calendar, DollarSign, Scale, Building2, Brain, Search
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
        valorTotal: 0
    });

    const [selecionados, setSelecionados] = useState<number[]>([]);
    const [showBatchModal, setShowBatchModal] = useState(false);
    const [showBuscaAvancada, setShowBuscaAvancada] = useState(false);

    useEffect(() => {
        fetchProcessos();
        setSelecionados([]);
    }, [filtros]);

    const fetchProcessos = async () => {
        setLoading(true);
        try {
            const response = await api.get('/api/processos', { params: filtros });

            if (response.data) {
                setProcessos(response.data.processos || []);
                setStats({
                    total: response.data.total || 0,
                    tributario: response.data.processos?.filter((p: Processo) => p.natureza_id === 1).length || 0,
                    trabalhista: response.data.processos?.filter((p: Processo) => p.natureza_id === 2).length || 0,
                    civel: response.data.processos?.filter((p: Processo) => p.natureza_id === 3).length || 0,
                    valorTotal: response.data.processos?.reduce((sum: number, p: Processo) => sum + (p.valor_causa || 0), 0) || 0
                });
            }
        } catch (error) {
            console.error('Erro ao carregar processos:', error);
        } finally {
            setLoading(false);
        }
    };

    const getNaturezaBadge = (natureza_id: number) => {
        const naturezas = {
            1: { label: 'Tributário', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
            2: { label: 'Trabalhista', color: 'bg-orange-500/20 text-orange-400 border-orange-500/30' },
            3: { label: 'Cível', color: 'bg-purple-500/20 text- border-purple-500/30' }
        };

        const natureza = naturezas[natureza_id as keyof typeof naturezas] || naturezas[3];

        return (
            <span className={`px-3 py-1 rounded-full text-xs font-medium border ${natureza.color}`}>
                {natureza.label}
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
        // Exportar para CSV
        const csvContent = [
            ['Pasta', 'CNJ', 'Natureza', 'Valor', 'Data'].join(';'),
            ...processos.map(p => [
                p.pasta,
                p.numero_cnj || '',
                p.natureza_id === 1 ? 'Tributário' : p.natureza_id === 2 ? 'Trabalhista' : 'Cível',
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

    const handleToggleSelecao = (id: number, e: React.MouseEvent) => {
        e.stopPropagation();
        setSelecionados(prev =>
            prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
        );
    };

    const handleToggleTodos = () => {
        if (selecionados.length === processos.length && processos.length > 0) {
            setSelecionados([]);
        } else {
            const tributarios = processos.filter(p => p.natureza_id === 1);
            setSelecionados(tributarios.map(p => p.id_processo));
        }
    };

    const handleBatchPredict = () => {
        if (selecionados.length === 0) {
            alert('Selecione pelo menos um processo tributário');
            return;
        }
        setShowBatchModal(true);
    };

    const handleBatchSuccess = () => {
        setSelecionados([]);
        fetchProcessos();
    };

    const handleBuscaResultados = (processos: Processo[]) => {
        setProcessos(processos);
        setStats({
            total: processos.length,
            tributario: processos.filter(p => p.natureza_id === 1).length,
            trabalhista: processos.filter(p => p.natureza_id === 2).length,
            civel: processos.filter(p => p.natureza_id === 3).length,
            valorTotal: processos.reduce((sum, p) => sum + (p.valor_causa || 0), 0)
        });
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

                    {stats.tributario > 0 && (
                        <>
                            <button
                                onClick={handleToggleTodos}
                                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${selecionados.length === processos.filter(p => p.natureza_id === 1).length && selecionados.length > 0
                                    ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                                    : 'bg-accent hover:bg-accent/80'
                                    }`}
                                title="Selecionar todos tributários"
                            >
                                <CheckCircle className="w-4 h-4" />
                                {selecionados.length === processos.filter(p => p.natureza_id === 1).length && selecionados.length > 0
                                    ? 'Desmarcar'
                                    : 'Selec. Tributários'
                                }
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
                        </>
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
                            <p className="text-sm text-muted-foreground mb-1">Trabalhista + Cível</p>
                            <p className="text-3xl font-bold text-purple-400">{stats.trabalhista + stats.civel}</p>
                        </div>
                        <div className="p-3 bg-purple-500/20 rounded-lg">
                            <FileText className="w-6 h-6 text purple-400" />
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
                            className="bg-card border border-border rounded-xl p-6 hover:shadow-xl hover:scale-[1.02] transition-all duration-300 group relative"
                        >
                            {processo.natureza_id === 1 && (
                                <div
                                    className="absolute top-4 right-4 z-10"
                                    onClick={(e) => e.stopPropagation()}
                                >
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={selecionados.includes(processo.id_processo)}
                                            onChange={(e) => handleToggleSelecao(processo.id_processo, e as any)}
                                            className="w-5 h-5 rounded border-2 border-primary text-primary focus:ring-2 focus:ring-primary/50 cursor-pointer transition-all hover:scale-110"
                                        />
                                        <span className="text-xs text-muted-foreground hidden group-hover:inline">
                                            ML
                                        </span>
                                    </label>
                                </div>
                            )}

                            <div
                                onClick={() => handleVerDetalhes(processo.id_processo)}
                                className="cursor-pointer"
                            >
                                {/* Header do Card */}
                                <div className="flex items-start justify-between mb-4 pr-10">
                                    <div className="flex-1">
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

                    {showBatchModal && (
                        <BatchPredictModal
                            processoIds={selecionados}
                            onClose={() => setShowBatchModal(false)}
                            onSuccess={handleBatchSuccess}
                        />
                    )}
                </div>
            );
}
