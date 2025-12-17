/**
 * Listagem de Processos Dinâmicos - UX Premium
 * Features: Batch Predict ML, Busca Avançada, Seleção Múltipla
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
                    tributario: response.data.tributario || 0,
                    trabalhista: response.data.trabalhista || 0,
                    civel: response.data.civel || 0,
                    valorTotal: response.data.valorTotal || 0
                });
            }
        } catch (error) {
            console.error('Erro ao carregar processos:', error);
        } finally {
            setLoading(false);
        }
    };

    const getNaturezaBadge = (naturezaId: number) => {
        const badges: Record<number, { label: string; color: string }> = {
            1: { label: 'Tributário', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
            2: { label: 'Trabalhista', color: 'bg-green-500/20 text-green-400 border-green-500/30' },
            3: { label: 'Cível', color: 'bg-purple-500/20 text-purple-400 border-purple-500/30' }
        };
        const badge = badges[naturezaId] || { label: 'Outro', color: 'bg-gray-500/20 text-gray-400 border-gray-500/30' };
        return (
            <span className={`px-2 py-1 rounded text-xs font-medium border ${badge.color}`}>
                {badge.label}
            </span>
        );
    };

    const handleExportar = () => {
        const csvContent = [
            ['CNJ', 'Pasta', 'Cliente', 'Natureza', 'Status', 'Valor Causa', 'Data Criação'].join(','),
            ...processos.map(p => [
                p.cnj || '',
                p.pasta || '',
                p.cliente || '',
                p.natureza_id === 1 ? 'Tributário' : p.natureza_id === 2 ? 'Trabalhista' : 'Cível',
                p.ativo ? 'Ativo' : 'Inativo',
                p.valor_causa || 0,
                new Date(p.data_criacao).toLocaleDateString('pt-BR')
            ].join(','))
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
            prev.includes(id) ? prev.filter(pid => pid !== id) : [...prev, id]
        );
    };

    const handleToggleTodos = () => {
        const tributarios = processos.filter(p => p.natureza_id === 1);
        if (selecionados.length === tributarios.length && selecionados.length > 0) {
            setSelecionados([]);
        } else {
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
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-card border border-border rounded-xl p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground">Total</p>
                            <h3 className="text-2xl font-bold">{stats.total}</h3>
                        </div>
                        <FileText className="w-8 h-8 text-primary opacity-50" />
                    </div>
                </div>

                <div className="bg-card border border-border rounded-xl p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground">Tributário</p>
                            <h3 className="text-2xl font-bold">{stats.tributario}</h3>
                        </div>
                        <TrendingUp className="w-8 h-8 text-blue-500 opacity-50" />
                    </div>
                </div>

                <div className="bg-card border border-border rounded-xl p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground">Trabalhista</p>
                            <h3 className="text-2xl font-bold">{stats.trabalhista}</h3>
                        </div>
                        <Building2 className="w-8 h-8 text-green-500 opacity-50" />
                    </div>
                </div>

                <div className="bg-card border border-border rounded-xl p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground">Cível</p>
                            <h3 className="text-2xl font-bold">{stats.civel}</h3>
                        </div>
                        <Gavel className="w-8 h-8 text-purple-500 opacity-50" />
                    </div>
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
                            {/* CHECKBOX SELECTION */}
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
                                {/* Header */}
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

                                {/* Content */}
                                <div className="space-y-2 text-sm">
                                    {processo.cnj && (
                                        <div className="flex items-center gap-2">
                                            <FileText className="w-4 h-4 text-muted-foreground" />
                                            <span className="text-muted-foreground">{processo.cnj}</span>
                                        </div>
                                    )}

                                    <div className="flex items-center gap-2">
                                        <Calendar className="w-4 h-4 text-muted-foreground" />
                                        <span>{new Date(processo.data_criacao).toLocaleDateString('pt-BR')}</span>
                                    </div>

                                    {processo.valor_causa && (
                                        <div className="flex items-center gap-2">
                                            <DollarSign className="w-4 h-4 text-muted-foreground" />
                                            <span className="font-semibold text-primary">
                                                R$ {processo.valor_causa.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                            </span>
                                        </div>
                                    )}

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

            {/* Modals */}
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
