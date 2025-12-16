import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { ArrowLeft, Save } from 'lucide-react';
import api from '../../lib/api';
export default function NewTemplate() {
    const navigate = useNavigate();
    const [saving, setSaving] = useState(false);
    const [formData, setFormData] = useState({
        nome: '',
        categoria: '',
        area_juridica: '',
        descricao: '',
        conteudo: '',
        campos_variaveis: []
    });
    const [newVariable, setNewVariable] = useState('');
    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            await api.post('/api/templates', formData);
            navigate('/templates');
        }
        catch (error) {
            console.error('Error creating template:', error);
            alert('Erro ao criar template');
        }
        finally {
            setSaving(false);
        }
    };
    const handleAddVariable = () => {
        if (newVariable && !formData.campos_variaveis.includes(newVariable)) {
            setFormData(prev => ({
                ...prev,
                campos_variaveis: [...prev.campos_variaveis, newVariable]
            }));
            setNewVariable('');
        }
    };
    const handleRemoveVariable = (variable) => {
        setFormData(prev => ({
            ...prev,
            campos_variaveis: prev.campos_variaveis.filter(v => v !== variable)
        }));
    };
    return (_jsxs(AdminLayout, { children: [_jsxs("div", { className: "mb-6", children: [_jsxs(Link, { to: "/templates", className: "flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4", children: [_jsx(ArrowLeft, { className: "w-4 h-4" }), "Voltar para templates"] }), _jsx(PageHeader, { title: "Novo Template", description: "Criar novo template jur\u00EDdico" })] }), _jsxs("form", { onSubmit: handleSubmit, className: "space-y-6", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Informa\u00E7\u00F5es B\u00E1sicas" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-6", children: [_jsxs("div", { className: "md:col-span-2", children: [_jsxs("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: ["Nome do Template ", _jsx("span", { className: "text-red-500", children: "*" })] }), _jsx("input", { type: "text", value: formData.nome, onChange: (e) => setFormData({ ...formData, nome: e.target.value }), required: true, placeholder: "Ex: Peti\u00E7\u00E3o Inicial - A\u00E7\u00E3o de Cobran\u00E7a", className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsxs("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: ["Categoria ", _jsx("span", { className: "text-red-500", children: "*" })] }), _jsxs("select", { value: formData.categoria, onChange: (e) => setFormData({ ...formData, categoria: e.target.value }), required: true, className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "", children: "Selecione..." }), _jsx("option", { value: "peticoes", children: "Peti\u00E7\u00F5es" }), _jsx("option", { value: "contratos", children: "Contratos" }), _jsx("option", { value: "pareceres", children: "Pareceres" }), _jsx("option", { value: "recursos", children: "Recursos" }), _jsx("option", { value: "outros", children: "Outros" })] })] }), _jsxs("div", { children: [_jsxs("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: ["\u00C1rea Jur\u00EDdica ", _jsx("span", { className: "text-red-500", children: "*" })] }), _jsxs("select", { value: formData.area_juridica, onChange: (e) => setFormData({ ...formData, area_juridica: e.target.value }), required: true, className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "", children: "Selecione..." }), _jsx("option", { value: "penal", children: "Direito Penal" }), _jsx("option", { value: "civil", children: "Direito Civil" }), _jsx("option", { value: "trabalhista", children: "Direito Trabalhista" }), _jsx("option", { value: "empresarial", children: "Direito Empresarial" }), _jsx("option", { value: "consumidor", children: "Direito do Consumidor" }), _jsx("option", { value: "tributario", children: "Direito Tribut\u00E1rio" })] })] }), _jsxs("div", { className: "md:col-span-2", children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Descri\u00E7\u00E3o" }), _jsx("textarea", { value: formData.descricao, onChange: (e) => setFormData({ ...formData, descricao: e.target.value }), rows: 3, placeholder: "Breve descri\u00E7\u00E3o do template e quando utiliz\u00E1-lo", className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] })] })] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Campos Vari\u00E1veis" }), _jsxs("p", { className: "text-sm text-gray-600 mb-4", children: ["Defina as vari\u00E1veis que ser\u00E3o utilizadas no template. Use ", '{nome_variavel}', " no conte\u00FAdo."] }), _jsxs("div", { className: "flex gap-2 mb-4", children: [_jsx("input", { type: "text", value: newVariable, onChange: (e) => setNewVariable(e.target.value), onKeyPress: (e) => e.key === 'Enter' && (e.preventDefault(), handleAddVariable()), placeholder: "Nome da vari\u00E1vel (ex: nome_cliente)", className: "flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" }), _jsx("button", { type: "button", onClick: handleAddVariable, className: "px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: "Adicionar" })] }), formData.campos_variaveis.length > 0 && (_jsx("div", { className: "flex flex-wrap gap-2", children: formData.campos_variaveis.map((variable) => (_jsxs("div", { className: "flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-lg", children: [_jsx("span", { className: "text-sm font-mono", children: `{${variable}}` }), _jsx("button", { type: "button", onClick: () => handleRemoveVariable(variable), className: "text-blue-600 hover:text-blue-800", children: "\u00D7" })] }, variable))) }))] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Conte\u00FAdo do Template" }), _jsx("textarea", { value: formData.conteudo, onChange: (e) => setFormData({ ...formData, conteudo: e.target.value }), required: true, rows: 20, placeholder: `Digite o conteúdo do template...\n\nExemplo:\n\nEXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO\n\nO(A) {nome_cliente}, {qualificacao}, vem, por seu advogado...\n\nUse {variavel} para inserir campos variáveis.`, className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm" })] }), _jsxs("div", { className: "flex justify-end gap-4", children: [_jsx(Link, { to: "/templates", className: "px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Cancelar" }), _jsxs("button", { type: "submit", disabled: saving, className: "flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50", children: [_jsx(Save, { className: "w-4 h-4" }), saving ? 'Salvando...' : 'Criar Template'] })] })] })] }));
}
