import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { Save, X } from 'lucide-react';
import api from '../../lib/api';
export default function NewClient() {
    const { slug } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        legal_name: '',
        document_number: '',
        document_type: 'cpf',
        email: '',
        phone: '',
        address_street: '',
        address_number: '',
        address_complement: '',
        address_neighborhood: '',
        address_city: '',
        address_state: '',
        address_zip: '',
        industry: '',
        size: 'small',
    });
    const handleChange = (e) => {
        setFormData(prev => ({
            ...prev,
            [e.target.name]: e.target.value
        }));
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await api.post(`/api/saas/tenancy/${slug}/clients`, formData);
            navigate(`/org/${slug}/clients`);
        }
        catch (error) {
            console.error('Error creating client:', error);
            alert('Erro ao criar cliente');
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Novo Cliente", description: "Adicionar novo cliente \u00E0 organiza\u00E7\u00E3o" }), _jsx("form", { onSubmit: handleSubmit, className: "max-w-4xl", children: _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6 space-y-6", children: [_jsxs("div", { children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Informa\u00E7\u00F5es B\u00E1sicas" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Nome *" }), _jsx("input", { type: "text", name: "name", value: formData.name, onChange: handleChange, required: true, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: "Nome do cliente" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Raz\u00E3o Social" }), _jsx("input", { type: "text", name: "legal_name", value: formData.legal_name, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: "Raz\u00E3o social (se empresa)" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Tipo de Documento" }), _jsxs("select", { name: "document_type", value: formData.document_type, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "cpf", children: "CPF" }), _jsx("option", { value: "cnpj", children: "CNPJ" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: formData.document_type === 'cpf' ? 'CPF' : 'CNPJ' }), _jsx("input", { type: "text", name: "document_number", value: formData.document_number, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: formData.document_type === 'cpf' ? '000.000.000-00' : '00.000.000/0000-00' })] })] })] }), _jsxs("div", { children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Contato" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Email" }), _jsx("input", { type: "email", name: "email", value: formData.email, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: "email@exemplo.com" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Telefone" }), _jsx("input", { type: "tel", name: "phone", value: formData.phone, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: "(00) 00000-0000" })] })] })] }), _jsxs("div", { children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Endere\u00E7o" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { className: "md:col-span-2", children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Logradouro" }), _jsx("input", { type: "text", name: "address_street", value: formData.address_street, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: "Rua, Avenida, etc" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "N\u00FAmero" }), _jsx("input", { type: "text", name: "address_number", value: formData.address_number, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Complemento" }), _jsx("input", { type: "text", name: "address_complement", value: formData.address_complement, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Bairro" }), _jsx("input", { type: "text", name: "address_neighborhood", value: formData.address_neighborhood, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Cidade" }), _jsx("input", { type: "text", name: "address_city", value: formData.address_city, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Estado (UF)" }), _jsx("input", { type: "text", name: "address_state", value: formData.address_state, onChange: handleChange, maxLength: 2, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: "SP" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "CEP" }), _jsx("input", { type: "text", name: "address_zip", value: formData.address_zip, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: "00000-000" })] })] })] }), _jsxs("div", { children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Informa\u00E7\u00F5es Comerciais" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Setor" }), _jsx("input", { type: "text", name: "industry", value: formData.industry, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: "Tecnologia, Sa\u00FAde, etc" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Porte" }), _jsxs("select", { name: "size", value: formData.size, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "startup", children: "Startup" }), _jsx("option", { value: "small", children: "Pequeno" }), _jsx("option", { value: "medium", children: "M\u00E9dio" }), _jsx("option", { value: "large", children: "Grande" }), _jsx("option", { value: "enterprise", children: "Enterprise" })] })] })] })] }), _jsxs("div", { className: "flex gap-3 pt-4 border-t border-gray-200", children: [_jsxs("button", { type: "submit", disabled: loading, className: "flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50", children: [_jsx(Save, { className: "w-4 h-4" }), loading ? 'Salvando...' : 'Salvar Cliente'] }), _jsxs("button", { type: "button", onClick: () => navigate(`/org/${slug}/clients`), className: "flex items-center gap-2 px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: [_jsx(X, { className: "w-4 h-4" }), "Cancelar"] })] })] }) })] }));
}
