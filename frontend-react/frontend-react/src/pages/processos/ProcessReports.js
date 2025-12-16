import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { FileText, Download, Eye, Calendar, Filter } from 'lucide-react';
import api from '../../lib/api';
export default function ProcessReports() {
    const [filters, setFilters] = useState({
        data_inicio: '',
        data_fim: '',
        area_direito: '',
        status: '',
        tipo_relatorio: 'completo'
    });
    const [previewUrl, setPreviewUrl] = useState(null);
    const [generating, setGenerating] = useState(false);
    const handleFilterChange = (field, value) => {
        setFilters(prev => ({ ...prev, [field]: value }));
    };
    // Endpoint: POST /processos/relatorios/gerar-previa
    const handleGeneratePreview = async () => {
        setGenerating(true);
        try {
            const response = await api.post('/processos/relatorios/gerar-previa', filters);
            setPreviewUrl(response.data.preview_url);
        }
        catch (error) {
            console.error('Error generating preview:', error);
            alert('Erro ao gerar prévia');
        }
        finally {
            setGenerating(false);
        }
    };
    // Endpoint: POST /processos/relatorios/exportar
    const handleExportReport = async (formato) => {
        try {
            const response = await api.post('/processos/relatorios/exportar', {
                ...filters,
                formato
            }, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            const extension = formato === 'excel' ? 'xlsx' : formato === 'word' ? 'docx' : formato;
            link.setAttribute('download', `relatorio-processos.${extension}`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        }
        catch (error) {
            console.error('Error exporting report:', error);
            alert('Erro ao exportar relatório');
        }
    };
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Relat\u00F3rios de Processos", description: "Gere relat\u00F3rios personalizados dos seus processos" }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-3 gap-6", children: [_jsx("div", { className: "lg:col-span-1", children: _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsxs("h3", { className: "text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2", children: [_jsx(Filter, { className: "w-5 h-5" }), "Filtros"] }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsxs("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: [_jsx(Calendar, { className: "w-4 h-4 inline mr-1" }), "Per\u00EDodo"] }), _jsxs("div", { className: "space-y-2", children: [_jsx("input", { type: "date", value: filters.data_inicio, onChange: (e) => handleFilterChange('data_inicio', e.target.value), className: "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm", placeholder: "Data in\u00EDcio" }), _jsx("input", { type: "date", value: filters.data_fim, onChange: (e) => handleFilterChange('data_fim', e.target.value), className: "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm", placeholder: "Data fim" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "\u00C1rea do Direito" }), _jsxs("select", { value: filters.area_direito, onChange: (e) => handleFilterChange('area_direito', e.target.value), className: "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm", children: [_jsx("option", { value: "", children: "Todas" }), _jsx("option", { value: "civel", children: "C\u00EDvel" }), _jsx("option", { value: "trabalhista", children: "Trabalhista" }), _jsx("option", { value: "criminal", children: "Criminal" }), _jsx("option", { value: "tributario", children: "Tribut\u00E1rio" }), _jsx("option", { value: "familia", children: "Fam\u00EDlia" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Status" }), _jsxs("select", { value: filters.status, onChange: (e) => handleFilterChange('status', e.target.value), className: "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm", children: [_jsx("option", { value: "", children: "Todos" }), _jsx("option", { value: "ativo", children: "Ativo" }), _jsx("option", { value: "suspenso", children: "Suspenso" }), _jsx("option", { value: "arquivado", children: "Arquivado" }), _jsx("option", { value: "finalizado", children: "Finalizado" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Tipo de Relat\u00F3rio" }), _jsxs("select", { value: filters.tipo_relatorio, onChange: (e) => handleFilterChange('tipo_relatorio', e.target.value), className: "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm", children: [_jsx("option", { value: "completo", children: "Completo" }), _jsx("option", { value: "resumido", children: "Resumido" }), _jsx("option", { value: "estatistico", children: "Estat\u00EDstico" }), _jsx("option", { value: "financeiro", children: "Financeiro" })] })] }), _jsx("div", { className: "pt-4 space-y-2", children: _jsxs("button", { onClick: handleGeneratePreview, disabled: generating, className: "w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50", children: [_jsx(Eye, { className: "w-4 h-4" }), generating ? 'Gerando...' : 'Gerar Prévia'] }) })] })] }) }), _jsx("div", { className: "lg:col-span-2", children: _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Pr\u00E9via e Exporta\u00E7\u00E3o" }), previewUrl ? (_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "border border-gray-300 rounded-lg p-4 bg-gray-50 min-h-[400px]", children: [_jsx("p", { className: "text-sm text-gray-600 mb-2", children: "Pr\u00E9via do relat\u00F3rio:" }), _jsxs("div", { className: "bg-white p-6 rounded", children: [_jsx("h4", { className: "font-bold mb-4", children: "Relat\u00F3rio de Processos Jur\u00EDdicos" }), _jsxs("div", { className: "space-y-2 text-sm", children: [_jsxs("p", { children: [_jsx("strong", { children: "Per\u00EDodo:" }), " ", filters.data_inicio || 'Não especificado', " a ", filters.data_fim || 'Não especificado'] }), _jsxs("p", { children: [_jsx("strong", { children: "\u00C1rea:" }), " ", filters.area_direito || 'Todas'] }), _jsxs("p", { children: [_jsx("strong", { children: "Status:" }), " ", filters.status || 'Todos'] }), _jsxs("p", { children: [_jsx("strong", { children: "Tipo:" }), " ", filters.tipo_relatorio] })] }), _jsx("div", { className: "mt-6 p-4 bg-gray-50 rounded", children: _jsx("p", { className: "text-sm text-gray-500", children: "[Conte\u00FAdo do relat\u00F3rio ser\u00E1 exibido aqui]" }) })] })] }), _jsxs("div", { children: [_jsx("p", { className: "text-sm font-medium text-gray-700 mb-3", children: "Exportar como:" }), _jsxs("div", { className: "flex gap-3", children: [_jsxs("button", { onClick: () => handleExportReport('pdf'), className: "flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: [_jsx(Download, { className: "w-4 h-4" }), "PDF"] }), _jsxs("button", { onClick: () => handleExportReport('excel'), className: "flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: [_jsx(Download, { className: "w-4 h-4" }), "Excel"] }), _jsxs("button", { onClick: () => handleExportReport('word'), className: "flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: [_jsx(Download, { className: "w-4 h-4" }), "Word"] })] })] })] })) : (_jsx("div", { className: "flex items-center justify-center h-[400px] text-center", children: _jsxs("div", { children: [_jsx(FileText, { className: "w-16 h-16 text-gray-400 mx-auto mb-4" }), _jsx("h4", { className: "text-lg font-medium text-gray-900 mb-2", children: "Nenhuma pr\u00E9via gerada" }), _jsx("p", { className: "text-gray-600", children: "Configure os filtros e clique em \"Gerar Pr\u00E9via\"" })] }) }))] }) })] })] }));
}
