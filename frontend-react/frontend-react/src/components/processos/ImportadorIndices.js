import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * ImportadorIndices - Interface para Importação de Índices BACEN
 * Integra com API de Atualização Monetária
 */
import { useState, useEffect } from 'react';
import api from '../../lib/api';
import { Download, TrendingUp, Calendar, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react';
export default function ImportadorIndices() {
    const [indices, setIndices] = useState([]);
    const [loading, setLoading] = useState(false);
    const [importing, setImporting] = useState(null);
    const [resultado, setResultado] = useState(null);
    useEffect(() => {
        fetchIndices();
    }, []);
    const fetchIndices = async () => {
        try {
            const response = await api.get('/api/atualizacao-monetaria/indices');
            setIndices(response.data || []);
        }
        catch (error) {
            console.error('Erro ao carregar índices:', error);
        }
    };
    const importarIndice = async (indice) => {
        setImporting(indice);
        setResultado(null);
        try {
            const response = await api.post(`/api/atualizacao-monetaria/importar/${indice}`);
            setResultado({
                sucesso: true,
                indice,
                registros: response.data.registros_importados
            });
            fetchIndices();
        }
        catch (error) {
            setResultado({
                sucesso: false,
                indice,
                erro: error.response?.data?.error || 'Erro ao importar'
            });
        }
        finally {
            setImporting(null);
        }
    };
    const importarTodos = async () => {
        setLoading(true);
        setResultado(null);
        try {
            const response = await api.post('/api/atualizacao-monetaria/importar/todos');
            setResultado({
                sucesso: true,
                todos: true,
                resultados: response.data.resultados,
                total: response.data.total_registros
            });
            fetchIndices();
        }
        catch (error) {
            setResultado({
                sucesso: false,
                todos: true,
                erro: error.response?.data?.error || 'Erro ao importar'
            });
        }
        finally {
            setLoading(false);
        }
    };
    const formatDate = (dateString) => {
        if (!dateString)
            return 'Nunca';
        return new Date(dateString).toLocaleDateString('pt-BR');
    };
    return (_jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsxs("h2", { className: "text-2xl font-bold flex items-center gap-3", children: [_jsx(Download, { className: "w-7 h-7 text-primary" }), "Importador de \u00CDndices"] }), _jsx("p", { className: "text-muted-foreground mt-1", children: "Dados oficiais do Banco Central do Brasil" })] }), _jsxs("button", { onClick: importarTodos, disabled: loading, className: "flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary/90 rounded-lg transition-colors font-medium disabled:opacity-50", children: [_jsx(RefreshCw, { className: `w-4 h-4 ${loading ? 'animate-spin' : ''}` }), "Importar Todos"] })] }), resultado && (_jsx("div", { className: `${resultado.sucesso ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20'} border rounded-xl p-4`, children: _jsxs("div", { className: "flex items-start gap-3", children: [resultado.sucesso ? (_jsx(CheckCircle, { className: "w-5 h-5 text-green-500 mt-0.5" })) : (_jsx(AlertCircle, { className: "w-5 h-5 text-red-500 mt-0.5" })), _jsxs("div", { className: "flex-1", children: [_jsx("h4", { className: `font-semibold ${resultado.sucesso ? 'text-green-400' : 'text-red-400'}`, children: resultado.sucesso ? 'Importação Concluída!' : 'Erro na Importação' }), resultado.todos ? (_jsx("p", { className: "text-sm text-muted-foreground mt-1", children: resultado.sucesso
                                        ? `${resultado.total} registros importados`
                                        : resultado.erro })) : (_jsx("p", { className: "text-sm text-muted-foreground mt-1", children: resultado.sucesso
                                        ? `${resultado.indice}: ${resultado.registros} novos registros`
                                        : `${resultado.indice}: ${resultado.erro}` }))] })] }) })), _jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4", children: indices.map(indice => (_jsxs("div", { className: "bg-card border border-border rounded-xl p-6 hover:shadow-lg transition-all", children: [_jsxs("div", { className: "flex items-start justify-between mb-4", children: [_jsx("div", { className: "p-3 bg-primary/20 rounded-lg", children: _jsx(TrendingUp, { className: "w-6 h-6 text-primary" }) }), _jsx("span", { className: "px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-medium", children: "Ativo" })] }), _jsx("h3", { className: "font-bold text-lg mb-2", children: indice.nome }), _jsx("p", { className: "text-sm text-muted-foreground mb-4 line-clamp-2", children: indice.descricao }), _jsxs("div", { className: "space-y-2 mb-4 text-sm", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx(Calendar, { className: "w-4 h-4 text-muted-foreground" }), _jsxs("span", { className: "text-muted-foreground", children: ["\u00DAltima: ", formatDate(indice.ultima_atualizacao)] })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx(Download, { className: "w-4 h-4 text-muted-foreground" }), _jsxs("span", { className: "text-muted-foreground", children: [indice.total_registros || 0, " registros"] })] }), indice.ultimo_valor && (_jsxs("div", { className: "flex items-center gap-2", children: [_jsx(TrendingUp, { className: "w-4 h-4 text-primary" }), _jsxs("span", { className: "font-medium text-primary", children: [indice.ultimo_valor, "%"] })] }))] }), _jsxs("button", { onClick: () => importarIndice(indice.nome), disabled: importing === indice.nome, className: "w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary/20 hover:bg-primary/30 rounded-lg transition-colors text-primary disabled:opacity-50", children: [_jsx(Download, { className: `w-4 h-4 ${importing === indice.nome ? 'animate-bounce' : ''}` }), importing === indice.nome ? 'Importando...' : 'Importar'] })] }, indice.id_indice))) }), _jsx("div", { className: "bg-blue-500/10 border border-blue-500/20 rounded-xl p-6", children: _jsxs("div", { className: "flex gap-3", children: [_jsx(AlertCircle, { className: "w-5 h-5 text-blue-400 mt-0.5" }), _jsxs("div", { children: [_jsx("h4", { className: "font-semibold text-blue-400 mb-1", children: "Fonte Oficial" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Dados importados diretamente da API do Banco Central do Brasil (BACEN)" })] })] }) })] }));
}
