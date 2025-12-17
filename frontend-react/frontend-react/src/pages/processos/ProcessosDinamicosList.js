import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * Listagem de Processos Dinâmicos - UX Premium
 * Features: Batch Predict ML, Busca Avançada, Seleção Múltipla
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Gavel, Plus, Download, RefreshCw, FileText, TrendingUp, AlertCircle, CheckCircle, Calendar, DollarSign, Scale, Building2, Brain, Search } from 'lucide-react';
import api from '../../lib/api';
import BatchPredictModal from '../../components/processos/BatchPredictModal';
import ProcessosBuscaAvancada from '../../components/processos/ProcessosBuscaAvancada';
export default function ProcessosDinamicosList() {
    const navigate = useNavigate();
    const [processos, setProcessos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filtros, setFiltros] = useState({
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
    const [selecionados, setSelecionados] = useState([]);
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
        }
        catch (error) {
            console.error('Erro ao carregar processos:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const getNaturezaBadge = (naturezaId) => {
        const badges = {
            1: { label: 'Tributário', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
            2: { label: 'Trabalhista', color: 'bg-green-500/20 text-green-400 border-green-500/30' },
            3: { label: 'Cível', color: 'bg-purple-500/20 text-purple-400 border-purple-500/30' }
        };
        const badge = badges[naturezaId] || { label: 'Outro', color: 'bg-gray-500/20 text-gray-400 border-gray-500/30' };
        return (_jsx("span", { className: `px-2 py-1 rounded text-xs font-medium border ${badge.color}`, children: badge.label }));
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
    const handleVerDetalhes = (processoId) => {
        navigate(`/processos/${processoId}`);
    };
    const handleToggleSelecao = (id, e) => {
        e.stopPropagation();
        setSelecionados(prev => prev.includes(id) ? prev.filter(pid => pid !== id) : [...prev, id]);
    };
    const handleToggleTodos = () => {
        const tributarios = processos.filter(p => p.natureza_id === 1);
        if (selecionados.length === tributarios.length && selecionados.length > 0) {
            setSelecionados([]);
        }
        else {
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
    const handleBuscaResultados = (processos) => {
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
        return (_jsx("div", { className: "flex items-center justify-center min-h-[60vh]", children: _jsxs("div", { className: "text-center space-y-4", children: [_jsx("div", { className: "inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent" }), _jsx("p", { className: "text-muted-foreground", children: "Carregando processos..." })] }) }));
    }
    return (_jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsxs("h1", { className: "text-3xl font-bold flex items-center gap-3", children: [_jsx(Scale, { className: "w-8 h-8 text-primary" }), "Processos Din\u00E2micos"] }), _jsx("p", { className: "text-muted-foreground mt-1", children: "Sistema integrado de gest\u00E3o processual" })] }), _jsxs("div", { className: "flex gap-3", children: [_jsxs("button", { onClick: () => setShowBuscaAvancada(true), className: "flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-lg transition-all font-medium shadow-md", children: [_jsx(Search, { className: "w-4 h-4" }), "Busca Avan\u00E7ada"] }), _jsxs("button", { onClick: fetchProcessos, className: "flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors", children: [_jsx(RefreshCw, { className: "w-4 h-4" }), "Atualizar"] }), _jsxs("button", { onClick: handleExportar, className: "flex items-center gap-2 px-4 py-2 bg-secondary hover:bg-secondary/80 rounded-lg transition-colors", children: [_jsx(Download, { className: "w-4 h-4" }), "Exportar"] }), stats.tributario > 0 && (_jsxs(_Fragment, { children: [_jsxs("button", { onClick: handleToggleTodos, className: `flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${selecionados.length === processos.filter(p => p.natureza_id === 1).length && selecionados.length > 0
                                            ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                                            : 'bg-accent hover:bg-accent/80'}`, title: "Selecionar todos tribut\u00E1rios", children: [_jsx(CheckCircle, { className: "w-4 h-4" }), selecionados.length === processos.filter(p => p.natureza_id === 1).length && selecionados.length > 0
                                                ? 'Desmarcar'
                                                : 'Selec. Tributários'] }), selecionados.length > 0 && (_jsxs("button", { onClick: handleBatchPredict, className: "flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-lg transition-all font-semibold shadow-lg animate-pulse", children: [_jsx(Brain, { className: "w-5 h-5" }), "Analisar ML (", selecionados.length, ")"] }))] })), _jsxs("button", { onClick: handleNovoProcesso, className: "flex items-center gap-2 px-6 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors font-medium", children: [_jsx(Plus, { className: "w-4 h-4" }), "Novo Processo"] })] })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-4 gap-4", children: [_jsx("div", { className: "bg-card border border-border rounded-xl p-4", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-muted-foreground", children: "Total" }), _jsx("h3", { className: "text-2xl font-bold", children: stats.total })] }), _jsx(FileText, { className: "w-8 h-8 text-primary opacity-50" })] }) }), _jsx("div", { className: "bg-card border border-border rounded-xl p-4", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-muted-foreground", children: "Tribut\u00E1rio" }), _jsx("h3", { className: "text-2xl font-bold", children: stats.tributario })] }), _jsx(TrendingUp, { className: "w-8 h-8 text-blue-500 opacity-50" })] }) }), _jsx("div", { className: "bg-card border border-border rounded-xl p-4", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-muted-foreground", children: "Trabalhista" }), _jsx("h3", { className: "text-2xl font-bold", children: stats.trabalhista })] }), _jsx(Building2, { className: "w-8 h-8 text-green-500 opacity-50" })] }) }), _jsx("div", { className: "bg-card border border-border rounded-xl p-4", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-muted-foreground", children: "C\u00EDvel" }), _jsx("h3", { className: "text-2xl font-bold", children: stats.civel })] }), _jsx(Gavel, { className: "w-8 h-8 text-purple-500 opacity-50" })] }) })] }), processos.length === 0 ? (_jsxs("div", { className: "bg-card border border-border rounded-xl p-12 text-center", children: [_jsx(AlertCircle, { className: "w-12 h-12 text-muted-foreground mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-medium mb-2", children: "Nenhum processo encontrado" }), _jsx("p", { className: "text-muted-foreground", children: "Crie seu primeiro processo ou ajuste os filtros" })] })) : (_jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4", children: [processos.map((processo) => (_jsxs("div", { className: "bg-card border border-border rounded-xl p-6 hover:shadow-xl hover:scale-[1.02] transition-all duration-300 group relative", children: [processo.natureza_id === 1 && (_jsx("div", { className: "absolute top-4 right-4 z-10", onClick: (e) => e.stopPropagation(), children: _jsxs("label", { className: "flex items-center gap-2 cursor-pointer", children: [_jsx("input", { type: "checkbox", checked: selecionados.includes(processo.id_processo), onChange: (e) => handleToggleSelecao(processo.id_processo, e), className: "w-5 h-5 rounded border-2 border-primary text-primary focus:ring-2 focus:ring-primary/50 cursor-pointer transition-all hover:scale-110" }), _jsx("span", { className: "text-xs text-muted-foreground hidden group-hover:inline", children: "ML" })] }) })), _jsxs("div", { onClick: () => handleVerDetalhes(processo.id_processo), className: "cursor-pointer", children: [_jsx("div", { className: "flex items-start justify-between mb-4 pr-10", children: _jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "flex items-center gap-2 mb-2", children: [getNaturezaBadge(processo.natureza_id), processo.ativo && (_jsx(CheckCircle, { className: "w-4 h-4 text-green-500" }))] }), _jsx("h3", { className: "font-semibold text-lg group-hover:text-primary transition-colors", children: processo.titulo || processo.pasta })] }) }), _jsxs("div", { className: "space-y-2 text-sm", children: [processo.cnj && (_jsxs("div", { className: "flex items-center gap-2", children: [_jsx(FileText, { className: "w-4 h-4 text-muted-foreground" }), _jsx("span", { className: "text-muted-foreground", children: processo.cnj })] })), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx(Calendar, { className: "w-4 h-4 text-muted-foreground" }), _jsx("span", { children: new Date(processo.data_criacao).toLocaleDateString('pt-BR') })] }), processo.valor_causa && (_jsxs("div", { className: "flex items-center gap-2", children: [_jsx(DollarSign, { className: "w-4 h-4 text-muted-foreground" }), _jsxs("span", { className: "font-semibold text-primary", children: ["R$ ", processo.valor_causa.toLocaleString('pt-BR', { minimumFractionDigits: 2 })] })] })), _jsxs("div", { className: "mt-4 pt-4 border-t border-border flex items-center justify-between", children: [_jsx("span", { className: "text-xs text-primary font-medium group-hover:underline", children: "Ver Detalhes \u2192" }), _jsx(TrendingUp, { className: "w-4 h-4 text-muted-foreground" })] })] })] }), "))}"] }, processo.id_processo))), processos.length > 0 && (_jsxs("div", { className: "flex items-center justify-between bg-card border border-border rounded-xl p-4", children: [_jsxs("p", { className: "text-sm text-muted-foreground", children: ["Mostrando ", processos.length, " de ", stats.total, " processos"] }), _jsxs("div", { className: "flex gap-2", children: [_jsx("button", { disabled: filtros.page === 1, onClick: () => setFiltros({ ...filtros, page: (filtros.page || 1) - 1 }), className: "px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors", children: "Anterior" }), _jsx("button", { onClick: () => setFiltros({ ...filtros, page: (filtros.page || 1) + 1 }), className: "px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors", children: "Pr\u00F3xima" })] })] })), showBatchModal && (_jsx(BatchPredictModal, { processoIds: selecionados, onClose: () => setShowBatchModal(false), onSuccess: handleBatchSuccess })), showBuscaAvancada && (_jsx(ProcessosBuscaAvancada, { onClose: () => setShowBuscaAvancada(false), onResultados: handleBuscaResultados }))] })), "; }"] }));
}
