import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { DataTable, SearchBar, PageHeader } from '../../components/ui/AdminComponents';
import { Plus, FileText, Download, Edit, Trash2 } from 'lucide-react';
import api from '../../lib/api';
export default function TemplatesList() {
    const navigate = useNavigate();
    const [templates, setTemplates] = useState([]);
    const [filtered, setFiltered] = useState([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchTemplates();
    }, []);
    // Endpoint: GET /api/templates
    const fetchTemplates = async () => {
        try {
            const response = await api.get('/api/templates');
            setTemplates(response.data);
            setFiltered(response.data);
        }
        catch (error) {
            console.error('Error fetching templates:', error);
        }
        finally {
            setLoading(false);
        }
    };
    // Endpoint: DELETE /api/templates/:id
    const handleDeleteTemplate = async (id) => {
        if (!confirm('Deseja excluir este template?'))
            return;
        try {
            await api.delete(`/api/templates/${id}`);
            fetchTemplates();
            alert('Template excluído!');
        }
        catch (error) {
            console.error('Error deleting template:', error);
            alert('Erro ao excluir template');
        }
    };
    // Endpoint: GET /api/templates/:id/download
    const handleDownloadTemplate = async (id, nome) => {
        try {
            const response = await api.get(`/api/templates/${id}/download`, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', nome);
            document.body.appendChild(link);
            link.click();
            link.remove();
        }
        catch (error) {
            console.error('Error downloading template:', error);
            alert('Erro ao baixar template');
        }
    };
    const handleSearch = (query) => {
        const result = templates.filter(t => t.nome.toLowerCase().includes(query.toLowerCase()) ||
            t.categoria.toLowerCase().includes(query.toLowerCase()) ||
            t.descricao?.toLowerCase().includes(query.toLowerCase()));
        setFiltered(result);
    };
    const columns = [
        {
            key: 'nome',
            label: 'Nome',
            render: (value, row) => (_jsxs("div", { children: [_jsx("div", { className: "font-medium text-gray-900", children: value }), row.descricao && (_jsx("div", { className: "text-sm text-gray-500", children: row.descricao }))] }))
        },
        {
            key: 'categoria',
            label: 'Categoria',
            render: (value) => (_jsx("span", { className: "px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium", children: value }))
        },
        {
            key: 'tipo_arquivo',
            label: 'Tipo',
            render: (value) => value.toUpperCase()
        },
        {
            key: 'num_usos',
            label: 'Usos',
        },
        {
            key: 'created_at',
            label: 'Criado em',
            render: (value) => new Date(value).toLocaleDateString('pt-BR')
        },
        {
            key: 'actions',
            label: 'Ações',
            render: (_, row) => (_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("button", { onClick: (e) => {
                            e.stopPropagation();
                            handleDownloadTemplate(row.id, row.nome);
                        }, className: "p-1 text-green-600 hover:bg-green-50 rounded", title: "Download", children: _jsx(Download, { className: "w-4 h-4" }) }), _jsx("button", { onClick: (e) => {
                            e.stopPropagation();
                            navigate(`/templates/${row.id}/edit`);
                        }, className: "p-1 text-blue-600 hover:bg-blue-50 rounded", title: "Editar", children: _jsx(Edit, { className: "w-4 h-4" }) }), _jsx("button", { onClick: (e) => {
                            e.stopPropagation();
                            handleDeleteTemplate(row.id);
                        }, className: "p-1 text-red-600 hover:bg-red-50 rounded", title: "Excluir", children: _jsx(Trash2, { className: "w-4 h-4" }) })] }))
        },
    ];
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Templates de Documentos", description: `${filtered.length} templates disponíveis`, action: _jsxs("button", { onClick: () => navigate('/templates/novo'), className: "flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: [_jsx(Plus, { className: "w-4 h-4" }), "Novo Template"] }) }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200", children: [_jsx("div", { className: "p-4 border-b border-gray-200", children: _jsx(SearchBar, { placeholder: "Buscar por nome, categoria ou descri\u00E7\u00E3o...", onSearch: handleSearch }) }), filtered.length > 0 ? (_jsxs(_Fragment, { children: [_jsx(DataTable, { columns: columns, data: filtered, onRowClick: (row) => handleDownloadTemplate(row.id, row.nome) }), _jsx("div", { className: "p-4 border-t border-gray-200 flex items-center justify-between", children: _jsxs("p", { className: "text-sm text-gray-600", children: ["Mostrando ", filtered.length, " de ", templates.length, " templates"] }) })] })) : (_jsxs("div", { className: "p-12 text-center", children: [_jsx(FileText, { className: "w-12 h-12 text-gray-400 mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-medium text-gray-900 mb-2", children: "Nenhum template encontrado" }), _jsx("p", { className: "text-gray-600 mb-4", children: "Crie templates para agilizar a cria\u00E7\u00E3o de documentos" }), _jsxs("button", { onClick: () => navigate('/templates/novo'), className: "inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: [_jsx(Plus, { className: "w-4 h-4" }), "Criar Template"] })] }))] })] }));
}
