import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { Plus, Edit, Trash2, Copy, FileText } from 'lucide-react';
import api from '../../lib/api';
export default function PromptsManagement() {
    const [prompts, setPrompts] = useState([]);
    const [filteredPrompts, setFilteredPrompts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [isEditing, setIsEditing] = useState(false);
    const [currentPrompt, setCurrentPrompt] = useState({});
    useEffect(() => {
        fetchPrompts();
    }, []);
    useEffect(() => {
        filterPrompts();
    }, [selectedCategory, prompts]);
    const fetchPrompts = async () => {
        try {
            const response = await api.get('/api/admin/prompts/listar');
            setPrompts(response.data);
        }
        catch (error) {
            console.error('Error fetching prompts:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const filterPrompts = () => {
        if (selectedCategory === 'all') {
            setFilteredPrompts(prompts);
        }
        else {
            setFilteredPrompts(prompts.filter(p => p.categoria === selectedCategory));
        }
    };
    const handleSave = async () => {
        try {
            if (currentPrompt.id) {
                await api.put(`/api/admin/prompts/${currentPrompt.id}`, currentPrompt);
            }
            else {
                await api.post('/api/admin/prompts/salvar', currentPrompt);
            }
            await fetchPrompts();
            setIsEditing(false);
            setCurrentPrompt({});
        }
        catch (error) {
            console.error('Error saving prompt:', error);
            alert('Erro ao salvar prompt');
        }
    };
    const handleDelete = async (id) => {
        if (!confirm('Tem certeza que deseja excluir este prompt?'))
            return;
        try {
            await api.delete(`/api/admin/prompts/excluir/${id}`);
            await fetchPrompts();
        }
        catch (error) {
            console.error('Error deleting prompt:', error);
            alert('Erro ao excluir prompt');
        }
    };
    const handleCopy = (content) => {
        navigator.clipboard.writeText(content);
        alert('Prompt copiado para área de transferência!');
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Gerenciamento de Prompts", description: "Gerencie os prompts dos assistentes jur\u00EDdicos", action: _jsxs("button", { onClick: () => {
                        setCurrentPrompt({});
                        setIsEditing(true);
                    }, className: "flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: [_jsx(Plus, { className: "w-4 h-4" }), "Novo Prompt"] }) }), isEditing && (_jsx("div", { className: "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4", children: _jsxs("div", { className: "bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto", children: [_jsx("div", { className: "p-6 border-b border-gray-200", children: _jsx("h2", { className: "text-xl font-semibold text-gray-900", children: currentPrompt.id ? 'Editar Prompt' : 'Novo Prompt' }) }), _jsxs("div", { className: "p-6 space-y-4", children: [_jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Nome do Prompt" }), _jsx("input", { type: "text", value: currentPrompt.nome || '', onChange: (e) => setCurrentPrompt({ ...currentPrompt, nome: e.target.value }), className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Categoria" }), _jsxs("select", { value: currentPrompt.categoria || '', onChange: (e) => setCurrentPrompt({ ...currentPrompt, categoria: e.target.value }), className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "", children: "Selecione..." }), _jsx("option", { value: "system", children: "System" }), _jsx("option", { value: "user", children: "User" }), _jsx("option", { value: "assistant", children: "Assistant" }), _jsx("option", { value: "template", children: "Template" })] })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "\u00C1rea Jur\u00EDdica" }), _jsx("input", { type: "text", value: currentPrompt.area_juridica || '', onChange: (e) => setCurrentPrompt({ ...currentPrompt, area_juridica: e.target.value }), placeholder: "Ex: Direito Penal, Empresarial, etc.", className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Conte\u00FAdo do Prompt" }), _jsx("textarea", { value: currentPrompt.conteudo || '', onChange: (e) => setCurrentPrompt({ ...currentPrompt, conteudo: e.target.value }), rows: 12, className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm", placeholder: "Digite o conte\u00FAdo do prompt... Use {variavel} para vari\u00E1veis" }), _jsxs("p", { className: "text-xs text-gray-500 mt-1", children: ["Use chaves para vari\u00E1veis: ", '{nome}', ", ", '{area}', ", ", '{contexto}'] })] })] }), _jsxs("div", { className: "p-6 border-t border-gray-200 flex justify-end gap-4", children: [_jsx("button", { onClick: () => {
                                        setIsEditing(false);
                                        setCurrentPrompt({});
                                    }, className: "px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Cancelar" }), _jsx("button", { onClick: handleSave, className: "px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: "Salvar" })] })] }) })), _jsx("div", { className: "bg-white rounded-lg border border-gray-200 p-4 mb-6", children: _jsxs("select", { value: selectedCategory, onChange: (e) => setSelectedCategory(e.target.value), className: "px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "all", children: "Todas as Categorias" }), _jsx("option", { value: "system", children: "System" }), _jsx("option", { value: "user", children: "User" }), _jsx("option", { value: "assistant", children: "Assistant" }), _jsx("option", { value: "template", children: "Template" })] }) }), filteredPrompts.length > 0 ? (_jsx("div", { className: "grid grid-cols-1 gap-4", children: filteredPrompts.map((prompt) => (_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsxs("div", { className: "flex items-start justify-between mb-4", children: [_jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "flex items-center gap-3 mb-2", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900", children: prompt.nome }), _jsx("span", { className: "px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded", children: prompt.categoria })] }), _jsx("p", { className: "text-sm text-gray-600 mb-3", children: prompt.area_juridica })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("button", { onClick: () => handleCopy(prompt.conteudo), className: "p-2 text-gray-600 hover:bg-gray-100 rounded", title: "Copiar", children: _jsx(Copy, { className: "w-4 h-4" }) }), _jsx("button", { onClick: () => {
                                                setCurrentPrompt(prompt);
                                                setIsEditing(true);
                                            }, className: "p-2 text-blue-600 hover:bg-blue-50 rounded", title: "Editar", children: _jsx(Edit, { className: "w-4 h-4" }) }), _jsx("button", { onClick: () => handleDelete(prompt.id), className: "p-2 text-red-600 hover:bg-red-50 rounded", title: "Excluir", children: _jsx(Trash2, { className: "w-4 h-4" }) })] })] }), _jsxs("div", { className: "bg-gray-50 rounded-lg p-4 font-mono text-sm text-gray-700 whitespace-pre-wrap", children: [prompt.conteudo.substring(0, 300), prompt.conteudo.length > 300 && '...'] }), prompt.variables && prompt.variables.length > 0 && (_jsxs("div", { className: "mt-3 flex items-center gap-2", children: [_jsx("span", { className: "text-xs text-gray-500", children: "Vari\u00E1veis:" }), prompt.variables.map((v, i) => (_jsx("span", { className: "px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded", children: v }, i)))] }))] }, prompt.id))) })) : (_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-12 text-center", children: [_jsx(FileText, { className: "w-16 h-16 text-gray-400 mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-medium text-gray-900 mb-2", children: "Nenhum prompt encontrado" }), _jsx("p", { className: "text-gray-600 mb-4", children: "Crie seu primeiro prompt para come\u00E7ar" }), _jsxs("button", { onClick: () => {
                            setCurrentPrompt({});
                            setIsEditing(true);
                        }, className: "inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: [_jsx(Plus, { className: "w-4 h-4" }), "Criar Primeiro Prompt"] })] }))] }));
}
