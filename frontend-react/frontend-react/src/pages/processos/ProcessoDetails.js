import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader, StatCard } from '../../components/ui/AdminComponents';
import { FileText, Calendar, DollarSign, User, Download, Brain, Paperclip, ArrowLeft } from 'lucide-react';
import api from '../../lib/api';
export default function ProcessoDetails() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [processo, setProcesso] = useState(null);
    const [anexos, setAnexos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [generatingAnalysis, setGeneratingAnalysis] = useState(false);
    useEffect(() => {
        fetchProcesso();
        fetchAnexos();
    }, [id]);
    // Endpoint: GET /processos/:processo_id
    const fetchProcesso = async () => {
        try {
            const response = await api.get(`/processos/${id}`);
            setProcesso(response.data);
        }
        catch (error) {
            console.error('Error fetching processo:', error);
        }
        finally {
            setLoading(false);
        }
    };
    // Endpoint: GET /api/processos/:processo_id/anexos
    const fetchAnexos = async () => {
        try {
            const response = await api.get(`/api/processos/${id}/anexos`);
            setAnexos(response.data);
        }
        catch (error) {
            console.error('Error fetching anexos:', error);
        }
    };
    // Endpoint: POST /api/processos/:processo_id/gerar-analise-ia
    const handleGenerateAnalysis = async () => {
        setGeneratingAnalysis(true);
        try {
            const response = await api.post(`/api/processos/${id}/gerar-analise-ia`);
            alert('Análise gerada com sucesso!');
            // Optionally download or display the analysis
        }
        catch (error) {
            console.error('Error generating analysis:', error);
            alert('Erro ao gerar análise');
        }
        finally {
            setGeneratingAnalysis(false);
        }
    };
    // Endpoint: POST /api/processos/:processo_id/exportar-analise-docx
    const handleExportAnalysis = async () => {
        try {
            const response = await api.post(`/api/processos/${id}/exportar-analise-docx`, {}, {
                responseType: 'blob'
            });
            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `analise-processo-${processo?.numero_processo}.docx`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        }
        catch (error) {
            console.error('Error exporting analysis:', error);
            alert('Erro ao exportar análise');
        }
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    if (!processo) {
        return (_jsx(AdminLayout, { children: _jsxs("div", { className: "text-center py-12", children: [_jsx("p", { className: "text-gray-600", children: "Processo n\u00E3o encontrado" }), _jsx(Link, { to: "/processos/lista", className: "text-blue-600 hover:text-blue-700 mt-4 inline-block", children: "Voltar para lista" })] }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsxs("div", { className: "mb-6", children: [_jsxs("button", { onClick: () => navigate('/processos/lista'), className: "flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4", children: [_jsx(ArrowLeft, { className: "w-4 h-4" }), "Voltar para lista"] }), _jsx(PageHeader, { title: `Processo ${processo.numero_processo}`, description: processo.area_direito, action: _jsxs("div", { className: "flex gap-2", children: [_jsxs("button", { onClick: handleGenerateAnalysis, disabled: generatingAnalysis, className: "flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50", children: [_jsx(Brain, { className: "w-4 h-4" }), generatingAnalysis ? 'Gerando...' : 'Gerar Análise IA'] }), _jsxs("button", { onClick: handleExportAnalysis, className: "flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: [_jsx(Download, { className: "w-4 h-4" }), "Exportar DOCX"] })] }) })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-4 gap-6 mb-8", children: [_jsx(StatCard, { title: "Status", value: processo.status || 'Ativo', icon: FileText }), _jsx(StatCard, { title: "Valor da Causa", value: processo.valor_causa ? `R$ ${processo.valor_causa.toLocaleString('pt-BR')}` : 'Não informado', icon: DollarSign }), _jsx(StatCard, { title: "Data Distribui\u00E7\u00E3o", value: new Date(processo.data_distribuicao).toLocaleDateString('pt-BR'), icon: Calendar }), _jsx(StatCard, { title: "Cliente", value: processo.client_name || 'Não atribuído', icon: User })] }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-3 gap-6", children: [_jsxs("div", { className: "lg:col-span-2 space-y-6", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Informa\u00E7\u00F5es B\u00E1sicas" }), _jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "text-sm text-gray-600", children: "N\u00FAmero do Processo" }), _jsx("p", { className: "font-mono font-medium", children: processo.numero_processo })] }), _jsxs("div", { children: [_jsx("label", { className: "text-sm text-gray-600", children: "\u00C1rea do Direito" }), _jsx("p", { className: "font-medium", children: processo.area_direito })] }), _jsxs("div", { children: [_jsx("label", { className: "text-sm text-gray-600", children: "Vara" }), _jsx("p", { className: "font-medium", children: processo.vara || '-' })] }), _jsxs("div", { children: [_jsx("label", { className: "text-sm text-gray-600", children: "Comarca" }), _jsx("p", { className: "font-medium", children: processo.comarca || '-' })] }), processo.autor && (_jsxs("div", { children: [_jsx("label", { className: "text-sm text-gray-600", children: "Autor" }), _jsx("p", { className: "font-medium", children: processo.autor })] })), processo.reu && (_jsxs("div", { children: [_jsx("label", { className: "text-sm text-gray-600", children: "R\u00E9u" }), _jsx("p", { className: "font-medium", children: processo.reu })] }))] }), processo.descricao && (_jsxs("div", { className: "mt-4 pt-4 border-t border-gray-200", children: [_jsx("label", { className: "text-sm text-gray-600", children: "Descri\u00E7\u00E3o" }), _jsx("p", { className: "mt-2 text-gray-700", children: processo.descricao })] }))] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsxs("h3", { className: "text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2", children: [_jsx(Paperclip, { className: "w-5 h-5" }), "Anexos (", anexos.length, ")"] }), anexos.length > 0 ? (_jsx("div", { className: "space-y-2", children: anexos.map(anexo => (_jsxs("div", { className: "flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx(FileText, { className: "w-5 h-5 text-gray-400" }), _jsxs("div", { children: [_jsx("p", { className: "font-medium text-gray-900", children: anexo.nome }), _jsxs("p", { className: "text-sm text-gray-500", children: [anexo.tipo, " \u2022 ", (anexo.tamanho / 1024).toFixed(2), " KB"] })] })] }), _jsx("button", { className: "text-blue-600 hover:text-blue-700", children: _jsx(Download, { className: "w-4 h-4" }) })] }, anexo.id))) })) : (_jsx("p", { className: "text-gray-500 text-center py-4", children: "Nenhum anexo encontrado" }))] })] }), _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Timeline" }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "flex gap-3", children: [_jsx("div", { className: "flex-shrink-0 w-2 h-2 mt-2 bg-blue-600 rounded-full" }), _jsxs("div", { children: [_jsx("p", { className: "font-medium text-gray-900", children: "Distribui\u00E7\u00E3o" }), _jsx("p", { className: "text-sm text-gray-500", children: new Date(processo.data_distribuicao).toLocaleDateString('pt-BR') })] })] }), processo.data_ultima_movimentacao && (_jsxs("div", { className: "flex gap-3", children: [_jsx("div", { className: "flex-shrink-0 w-2 h-2 mt-2 bg-gray-400 rounded-full" }), _jsxs("div", { children: [_jsx("p", { className: "font-medium text-gray-900", children: "\u00DAltima Movimenta\u00E7\u00E3o" }), _jsx("p", { className: "text-sm text-gray-500", children: new Date(processo.data_ultima_movimentacao).toLocaleDateString('pt-BR') })] })] }))] })] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "A\u00E7\u00F5es R\u00E1pidas" }), _jsxs("div", { className: "space-y-2", children: [_jsx(Link, { to: `/processos/${id}/edit`, className: "block w-full px-4 py-2 text-center border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Editar Processo" }), _jsx("button", { className: "w-full px-4 py-2 text-center border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Adicionar Movimenta\u00E7\u00E3o" }), _jsx("button", { className: "w-full px-4 py-2 text-center border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Upload Documento" })] })] })] })] })] }));
}
