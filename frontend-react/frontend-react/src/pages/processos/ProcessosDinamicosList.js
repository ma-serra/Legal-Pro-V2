import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * Listagem de Processos Dinâmicos - UX Premium
 * Integração com 43 APIs REST (Fases 2-4)
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Gavel, Plus, Filter, Download, RefreshCw, FileText, TrendingUp, AlertCircle, CheckCircle, Calendar, DollarSign, Scale, Building2, Brain, Search } from 'lucide-react';
import api from '../../lib/api';
import BatchPredictModal from '../../components/processos/BatchPredictModal';
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
                    tributario: response.data.processos?.filter((p) => p.natureza_id === 1).length || 0,
                    trabalhista: response.data.processos?.filter((p) => p.natureza_id === 2).length || 0,
                    civel: response.data.processos?.filter((p) => p.natureza_id === 3).length || 0,
                    valorTotal: response.data.processos?.reduce((sum, p) => sum + (p.valor_causa || 0), 0) || 0
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
    const getNaturezaBadge = (natureza_id) => {
        const naturezas = {
            1: { label: 'Tributário', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
            2: { label: 'Trabalhista', color: 'bg-orange-500/20 text-orange-400 border-orange-500/30' },
            3: { label: 'Cível', color: 'bg-purple-500/20 text- border-purple-500/30' }
        };
        const natureza = naturezas[natureza_id] || naturezas[3];
        return (_jsx("span", { className: `px-3 py-1 rounded-full text-xs font-medium border ${natureza.color}`, children: natureza.label }));
    };
    const formatCurrency = (value) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    };
    const formatDate = (dateString) => {
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
    const handleVerDetalhes = (processoId) => {
        navigate(`/processos/${processoId}`);
    };
    const handleToggleSelecao = (id, e) => {
        e.stopPropagation();
        setSelecionados(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
    };
    const handleToggleTodos = () => {
        if (selecionados.length === processos.length && processos.length > 0) {
            setSelecionados([]);
        }
        else {
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
                                                : 'Selec. Tributários'] }), selecionados.length > 0 && (_jsxs("button", { onClick: handleBatchPredict, className: "flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-lg transition-all font-semibold shadow-lg animate-pulse", children: [_jsx(Brain, { className: "w-5 h-5" }), "Analisar ML (", selecionados.length, ")"] }))] })), _jsxs("button", { onClick: handleNovoProcesso, className: "flex items-center gap-2 px-6 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors font-medium", children: [_jsx(Plus, { className: "w-4 h-4" }), "Novo Processo"] })] })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4", children: [_jsx("div", { className: "bg-gradient-to-br from-blue-500/10 to-blue-600/5 border border-blue-500/20 rounded-xl p-6 hover:shadow-lg hover:scale-105 transition-all duration-300", children: _jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-muted-foreground mb-1", children: "Total de Processos" }), _jsx("p", { className: "text-3xl font-bold text-blue-400", children: stats.total })] }), _jsx("div", { className: "p-3 bg-blue-500/20 rounded-lg", children: _jsx(Gavel, { className: "w-6 h-6 text-blue-400" }) })] }) }), _jsx("div", { className: "bg-gradient-to-br from-orange-500/10 to-orange-600/5 border border-orange-500/20 rounded-xl p-6 hover:shadow-lg hover:scale-105 transition-all duration-300", children: _jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-muted-foreground mb-1", children: "Tribut\u00E1rio" }), _jsx("p", { className: "text-3xl font-bold text-orange-400", children: stats.tributario })] }), _jsx("div", { className: "p-3 bg-orange-500/20 rounded-lg", children: _jsx(Building2, { className: "w-6 h-6 text-orange-400" }) })] }) }), _jsx("div", { className: "bg-gradient-to-br from-purple-500/10 to-purple-600/5 border border-purple-500/20 rounded-xl p-6 hover:shadow-lg hover:scale-105 transition-all duration-300", children: _jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-muted-foreground mb-1", children: "Trabalhista + C\u00EDvel" }), _jsx("p", { className: "text-3xl font-bold text-purple-400", children: stats.trabalhista + stats.civel })] }), _jsx("div", { className: "p-3 bg-purple-500/20 rounded-lg", children: _jsx(FileText, { className: "w-6 h-6 text purple-400" }) })] }) }), _jsx("div", { className: "bg-gradient-to-br from-green-500/10 to-green-600/5 border border-green-500/20 rounded-xl p-6 hover:shadow-lg hover:scale-105 transition-all duration-300", children: _jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-muted-foreground mb-1", children: "Valor Total" }), _jsx("p", { className: "text-2xl font-bold text-green-400", children: formatCurrency(stats.valorTotal) })] }), _jsx("div", { className: "p-3 bg-green-500/20 rounded-lg", children: _jsx(DollarSign, { className: "w-6 h-6 text-green-400" }) })] }) })] }), _jsx("div", { className: "bg-card border border-border rounded-xl p-4", children: _jsxs("div", { className: "flex flex-wrap gap-3 items-center", children: [_jsx(Filter, { className: "w-5 h-5 text-muted-foreground" }), _jsx("input", { type: "text", placeholder: "Buscar por CNJ, pasta, t\u00EDtulo...", className: "flex-1 min-w-[200px] bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary", onChange: (e) => setFiltros({ ...filtros, busca: e.target.value, page: 1 }) }), _jsxs("select", { className: "bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary", onChange: (e) => setFiltros({ ...filtros, natureza_id: e.target.value ? Number(e.target.value) : undefined, page: 1 }), children: [_jsx("option", { value: "", children: "Todas as Naturezas" }), _jsx("option", { value: "1", children: "Tribut\u00E1rio" }), _jsx("option", { value: "2", children: "Trabalhista" }), _jsx("option", { value: "3", children: "C\u00EDvel" })] }), _jsxs("select", { className: "bg-background border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary", onChange: (e) => setFiltros({ ...filtros, status_id: e.target.value ? Number(e.target.value) : undefined, page: 1 }), children: [_jsx("option", { value: "", children: "Todos os Status" }), _jsx("option", { value: "1", children: "Ativo" }), _jsx("option", { value: "2", children: "Arquivado" }), _jsx("option", { value: "3", children: "Suspenso" })] })] }) }), processos.length === 0 ? (_jsxs("div", { className: "bg-card border border-border rounded-xl p-12 text-center", children: [_jsx(AlertCircle, { className: "w-12 h-12 text-muted-foreground mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-medium mb-2", children: "Nenhum processo encontrado" }), _jsx("p", { className: "text-muted-foreground", children: "Crie seu primeiro processo ou ajuste os filtros" })] })) : (_jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4", children: [processos.map((processo) => (_jsxs("div", { className: "bg-card border border-border rounded-xl p-6 hover:shadow-xl hover:scale-[1.02] transition-all duration-300 group relative", children: [processo.natureza_id === 1 && (_jsx("div", { className: "absolute top-4 right-4 z-10", onClick: (e) => e.stopPropagation(), children: _jsxs("label", { className: "flex items-center gap-2 cursor-pointer", children: [_jsx("input", { type: "checkbox", checked: selecionados.includes(processo.id_processo), onChange: (e) => handleToggleSelecao(processo.id_processo, e), className: "w-5 h-5 rounded border-2 border-primary text-primary focus:ring-2 focus:ring-primary/50 cursor-pointer transition-all hover:scale-110" }), _jsx("span", { className: "text-xs text-muted-foreground hidden group-hover:inline", children: "ML" })] }) })), _jsxs("div", { onClick: () => handleVerDetalhes(processo.id_processo), className: "cursor-pointer", children: [_jsx("div", { className: "flex items-start justify-between mb-4 pr-10", children: _jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "flex items-center gap-2 mb-2", children: [getNaturezaBadge(processo.natureza_id), processo.ativo && (_jsx(CheckCircle, { className: "w-4 h-4 text-green-500" }))] }), _jsx("h3", { className: "font-semibold text-lg group-hover:text-primary transition-colors", children: processo.titulo || processo.pasta })] }) }), _jsxs("div", { className: "space-y-3 text-sm", children: [processo.numero_cnj && (_jsxs("div", { className: "flex items-center gap-2 text-muted-foreground", children: [_jsx(FileText, { className: "w-4 h-4" }), _jsx("span", { className: "font-mono", children: processo.numero_cnj })] })), _jsxs("div", { className: "flex items-center gap-2 text-muted-foreground", children: [_jsx(Scale, { className: "w-4 h-4" }), _jsx("span", { children: processo.pasta })] }), processo.valor_causa && (_jsxs("div", { className: "flex items-center gap-2", children: [_jsx(DollarSign, { className: "w-4 h-4 text-green-500" }), _jsx("span", { className: "font-medium", children: formatCurrency(processo.valor_causa) })] })), _jsxs("div", { className: "flex items-center gap-2 text-muted-foreground", children: [_jsx(Calendar, { className: "w-4 h-4" }), _jsx("span", { children: formatDate(processo.data_criacao) })] })] }), _jsxs("div", { className: "mt-4 pt-4 border-t border-border flex items-center justify-between", children: [_jsx("span", { className: "text-xs text-primary font-medium group-hover:underline", children: "Ver Detalhes \u2192" }), _jsx(TrendingUp, { className: "w-4 h-4 text-muted-foreground" })] })] }), "))}"] }, processo.id_processo))), processos.length > 0 && (_jsxs("div", { className: "flex items-center justify-between bg-card border border-border rounded-xl p-4", children: [_jsxs("p", { className: "text-sm text-muted-foreground", children: ["Mostrando ", processos.length, " de ", stats.total, " processos"] }), _jsxs("div", { className: "flex gap-2", children: [_jsx("button", { disabled: filtros.page === 1, onClick: () => setFiltros({ ...filtros, page: (filtros.page || 1) - 1 }), className: "px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors", children: "Anterior" }), _jsx("button", { onClick: () => setFiltros({ ...filtros, page: (filtros.page || 1) + 1 }), className: "px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors", children: "Pr\u00F3xima" })] })] })), showBatchModal && (_jsx(BatchPredictModal, { processoIds: selecionados, onClose: () => setShowBatchModal(false), onSuccess: handleBatchSuccess }))] })), "; }"] }));
}
