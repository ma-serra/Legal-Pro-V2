import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { Plus, Edit, Trash2, FolderPlus, Folder } from 'lucide-react';
import api from '../../lib/api';
export default function TemplateCategories() {
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isEditing, setIsEditing] = useState(false);
    const [currentCategory, setCurrentCategory] = useState({});
    useEffect(() => {
        fetchCategories();
    }, []);
    const fetchCategories = async () => {
        try {
            const response = await api.get('/api/templates/categorias');
            setCategories(response.data);
        }
        catch (error) {
            console.error('Error fetching categories:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const handleSave = async () => {
        try {
            if (currentCategory.id) {
                await api.put(`/api/templates/categorias/${currentCategory.id}`, currentCategory);
            }
            else {
                await api.post('/api/templates/categorias', currentCategory);
            }
            await fetchCategories();
            setIsEditing(false);
            setCurrentCategory({});
        }
        catch (error) {
            console.error('Error saving category:', error);
            alert('Erro ao salvar categoria');
        }
    };
    const handleDelete = async (id) => {
        if (!confirm('Tem certeza que deseja excluir esta categoria?'))
            return;
        try {
            await api.delete(`/api/templates/categorias/${id}`);
            await fetchCategories();
        }
        catch (error) {
            console.error('Error deleting category:', error);
            alert('Erro ao excluir categoria. Verifique se não há templates vinculados.');
        }
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Categorias de Templates", description: "Organize os templates em categorias", action: _jsxs("button", { onClick: () => {
                        setCurrentCategory({});
                        setIsEditing(true);
                    }, className: "flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: [_jsx(Plus, { className: "w-4 h-4" }), "Nova Categoria"] }) }), isEditing && (_jsx("div", { className: "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4", children: _jsxs("div", { className: "bg-white rounded-lg max-w-md w-full", children: [_jsx("div", { className: "p-6 border-b border-gray-200", children: _jsx("h2", { className: "text-xl font-semibold text-gray-900", children: currentCategory.id ? 'Editar Categoria' : 'Nova Categoria' }) }), _jsxs("div", { className: "p-6 space-y-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Nome da Categoria" }), _jsx("input", { type: "text", value: currentCategory.nome || '', onChange: (e) => setCurrentCategory({ ...currentCategory, nome: e.target.value }), className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Descri\u00E7\u00E3o" }), _jsx("textarea", { value: currentCategory.descricao || '', onChange: (e) => setCurrentCategory({ ...currentCategory, descricao: e.target.value }), rows: 3, className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Categoria Pai (Opcional)" }), _jsxs("select", { value: currentCategory.parent_id || '', onChange: (e) => setCurrentCategory({
                                                ...currentCategory,
                                                parent_id: e.target.value ? parseInt(e.target.value) : null
                                            }), className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "", children: "Nenhuma (Categoria Raiz)" }), categories.filter(c => c.id !== currentCategory.id).map((cat) => (_jsx("option", { value: cat.id, children: cat.nome }, cat.id)))] })] })] }), _jsxs("div", { className: "p-6 border-t border-gray-200 flex justify-end gap-4", children: [_jsx("button", { onClick: () => {
                                        setIsEditing(false);
                                        setCurrentCategory({});
                                    }, className: "px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Cancelar" }), _jsx("button", { onClick: handleSave, className: "px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: "Salvar" })] })] }) })), categories.length > 0 ? (_jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6", children: categories.map((category) => (_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow", children: [_jsxs("div", { className: "flex items-start justify-between mb-4", children: [_jsxs("div", { className: "flex items-center gap-3", children: [category.parent_id ? (_jsx(FolderPlus, { className: "w-8 h-8 text-blue-600" })) : (_jsx(Folder, { className: "w-8 h-8 text-blue-600" })), _jsxs("div", { children: [_jsx("h3", { className: "font-semibold text-gray-900", children: category.nome }), category.parent_id && (_jsx("p", { className: "text-xs text-gray-500", children: "Subcategoria" }))] })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("button", { onClick: () => {
                                                setCurrentCategory(category);
                                                setIsEditing(true);
                                            }, className: "p-1 text-blue-600 hover:bg-blue-50 rounded", title: "Editar", children: _jsx(Edit, { className: "w-4 h-4" }) }), _jsx("button", { onClick: () => handleDelete(category.id), className: "p-1 text-red-600 hover:bg-red-50 rounded", title: "Excluir", children: _jsx(Trash2, { className: "w-4 h-4" }) })] })] }), _jsx("p", { className: "text-sm text-gray-600 mb-4", children: category.descricao || 'Sem descrição' }), _jsx("div", { className: "pt-4 border-t border-gray-100", children: _jsxs("div", { className: "flex items-center justify-between text-sm", children: [_jsx("span", { className: "text-gray-600", children: "Templates:" }), _jsx("span", { className: "font-semibold text-blue-600", children: category.total_templates || 0 })] }) })] }, category.id))) })) : (_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-12 text-center", children: [_jsx(Folder, { className: "w-16 h-16 text-gray-400 mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-medium text-gray-900 mb-2", children: "Nenhuma categoria encontrada" }), _jsx("p", { className: "text-gray-600 mb-4", children: "Crie categorias para organizar seus templates" }), _jsxs("button", { onClick: () => {
                            setCurrentCategory({});
                            setIsEditing(true);
                        }, className: "inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: [_jsx(Plus, { className: "w-4 h-4" }), "Criar Primeira Categoria"] })] })), categories.length > 0 && (_jsxs("div", { className: "mt-8 bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Hierarquia de Categorias" }), _jsx("div", { className: "space-y-2", children: categories.filter(c => !c.parent_id).map((parent) => (_jsxs("div", { children: [_jsxs("div", { className: "flex items-center gap-2 text-gray-900 font-medium", children: [_jsx(Folder, { className: "w-4 h-4 text-blue-600" }), _jsx("span", { children: parent.nome }), _jsxs("span", { className: "text-sm text-gray-500", children: ["(", parent.total_templates, ")"] })] }), categories.filter(c => c.parent_id === parent.id).length > 0 && (_jsx("div", { className: "ml-6 mt-2 space-y-1", children: categories.filter(c => c.parent_id === parent.id).map((child) => (_jsxs("div", { className: "flex items-center gap-2 text-sm text-gray-700", children: [_jsx(FolderPlus, { className: "w-3 h-3 text-blue-500" }), _jsx("span", { children: child.nome }), _jsxs("span", { className: "text-xs text-gray-500", children: ["(", child.total_templates, ")"] })] }, child.id))) }))] }, parent.id))) })] }))] }));
}
