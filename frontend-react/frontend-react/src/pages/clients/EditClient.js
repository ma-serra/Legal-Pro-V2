import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { ArrowLeft, Save } from 'lucide-react';
import api from '../../lib/api';
export default function EditClient() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        legal_name: '',
        document_number: '',
        email: '',
        phone: '',
        address: '',
        city: '',
        state: '',
        zipcode: '',
        status: 'active'
    });
    useEffect(() => {
        if (id) {
            fetchClient();
        }
    }, [id]);
    const fetchClient = async () => {
        try {
            const response = await api.get(`/api/clientes/${id}`);
            setFormData(response.data);
        }
        catch (error) {
            console.error('Error fetching client:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            await api.put(`/api/clientes/${id}`, formData);
            navigate(`/clientes/${id}`);
        }
        catch (error) {
            console.error('Error updating client:', error);
            alert('Erro ao atualizar cliente');
        }
        finally {
            setSaving(false);
        }
    };
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto" }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsxs("div", { className: "mb-6", children: [_jsxs(Link, { to: `/clientes/${id}`, className: "flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4", children: [_jsx(ArrowLeft, { className: "w-4 h-4" }), "Voltar para detalhes"] }), _jsx(PageHeader, { title: "Editar Cliente", description: "Atualize as informa\u00E7\u00F5es do cliente" })] }), _jsxs("form", { onSubmit: handleSubmit, className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-6", children: [_jsx("div", { className: "md:col-span-2", children: _jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Informa\u00E7\u00F5es B\u00E1sicas" }) }), _jsxs("div", { children: [_jsxs("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: ["Nome / Nome Fantasia ", _jsx("span", { className: "text-red-500", children: "*" })] }), _jsx("input", { type: "text", name: "name", value: formData.name, onChange: handleChange, required: true, className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Raz\u00E3o Social" }), _jsx("input", { type: "text", name: "legal_name", value: formData.legal_name, onChange: handleChange, className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" })] }), _jsxs("div", { children: [_jsxs("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: ["CPF/CNPJ ", _jsx("span", { className: "text-red-500", children: "*" })] }), _jsx("input", { type: "text", name: "document_number", value: formData.document_number, onChange: handleChange, required: true, placeholder: "000.000.000-00", className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" })] }), _jsxs("div", { children: [_jsxs("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: ["Status ", _jsx("span", { className: "text-red-500", children: "*" })] }), _jsxs("select", { name: "status", value: formData.status, onChange: handleChange, required: true, className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent", children: [_jsx("option", { value: "active", children: "Ativo" }), _jsx("option", { value: "inactive", children: "Inativo" })] })] }), _jsx("div", { className: "md:col-span-2 mt-6", children: _jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Contato" }) }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Email" }), _jsx("input", { type: "email", name: "email", value: formData.email, onChange: handleChange, placeholder: "cliente@email.com", className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Telefone" }), _jsx("input", { type: "tel", name: "phone", value: formData.phone, onChange: handleChange, placeholder: "(00) 00000-0000", className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" })] }), _jsx("div", { className: "md:col-span-2 mt-6", children: _jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Endere\u00E7o" }) }), _jsxs("div", { className: "md:col-span-2", children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Logradouro" }), _jsx("input", { type: "text", name: "address", value: formData.address, onChange: handleChange, placeholder: "Rua, Avenida, etc.", className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Cidade" }), _jsx("input", { type: "text", name: "city", value: formData.city, onChange: handleChange, className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Estado" }), _jsx("input", { type: "text", name: "state", value: formData.state, onChange: handleChange, placeholder: "UF", maxLength: 2, className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "CEP" }), _jsx("input", { type: "text", name: "zipcode", value: formData.zipcode, onChange: handleChange, placeholder: "00000-000", className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" })] })] }), _jsxs("div", { className: "flex justify-end gap-4 mt-8 pt-6 border-t border-gray-200", children: [_jsx(Link, { to: `/clientes/${id}`, className: "px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Cancelar" }), _jsxs("button", { type: "submit", disabled: saving, className: "flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed", children: [_jsx(Save, { className: "w-4 h-4" }), saving ? 'Salvando...' : 'Salvar Alterações'] })] })] })] }));
}
