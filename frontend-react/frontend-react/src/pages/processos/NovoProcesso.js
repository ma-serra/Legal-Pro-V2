import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { Save, X } from 'lucide-react';
import api from '../../lib/api';
export default function NovoProcesso() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        numero_processo: '',
        client_id: '',
        area_direito: 'civel',
        status: 'ativo',
        valor_causa: '',
        data_distribuicao: '',
        vara: '',
        comarca: '',
        descricao: '',
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
            await api.post('/api/processos', {
                ...formData,
                valor_causa: formData.valor_causa ? parseFloat(formData.valor_causa) : null
            });
            navigate('/processos');
        }
        catch (error) {
            console.error('Error creating processo:', error);
            alert('Erro ao criar processo');
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Novo Processo", description: "Cadastrar novo processo jur\u00EDdico" }), _jsx("form", { onSubmit: handleSubmit, className: "max-w-4xl", children: _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6 space-y-6", children: [_jsxs("div", { children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Informa\u00E7\u00F5es B\u00E1sicas" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { className: "md:col-span-2", children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "N\u00FAmero do Processo *" }), _jsx("input", { type: "text", name: "numero_processo", value: formData.numero_processo, onChange: handleChange, required: true, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: "0000000-00.0000.0.00.0000" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "\u00C1rea do Direito *" }), _jsxs("select", { name: "area_direito", value: formData.area_direito, onChange: handleChange, required: true, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "civel", children: "C\u00EDvel" }), _jsx("option", { value: "trabalhista", children: "Trabalhista" }), _jsx("option", { value: "criminal", children: "Criminal" }), _jsx("option", { value: "tributario", children: "Tribut\u00E1rio" }), _jsx("option", { value: "familia", children: "Fam\u00EDlia" }), _jsx("option", { value: "empresarial", children: "Empresarial" }), _jsx("option", { value: "imobiliario", children: "Imobili\u00E1rio" }), _jsx("option", { value: "consumidor", children: "Consumidor" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Status" }), _jsxs("select", { name: "status", value: formData.status, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "ativo", children: "Ativo" }), _jsx("option", { value: "suspenso", children: "Suspenso" }), _jsx("option", { value: "arquivado", children: "Arquivado" }), _jsx("option", { value: "finalizado", children: "Finalizado" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Valor da Causa" }), _jsx("input", { type: "number", name: "valor_causa", value: formData.valor_causa, onChange: handleChange, step: "0.01", className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: "R$ 0,00" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Data de Distribui\u00E7\u00E3o" }), _jsx("input", { type: "date", name: "data_distribuicao", value: formData.data_distribuicao, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] })] })] }), _jsxs("div", { children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Localiza\u00E7\u00E3o" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Vara" }), _jsx("input", { type: "text", name: "vara", value: formData.vara, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: "1\u00AA Vara C\u00EDvel" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Comarca" }), _jsx("input", { type: "text", name: "comarca", value: formData.comarca, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: "S\u00E3o Paulo" })] })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Descri\u00E7\u00E3o/Observa\u00E7\u00F5es" }), _jsx("textarea", { name: "descricao", value: formData.descricao, onChange: handleChange, rows: 4, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", placeholder: "Informa\u00E7\u00F5es adicionais sobre o processo..." })] }), _jsxs("div", { className: "flex gap-3 pt-4 border-t border-gray-200", children: [_jsxs("button", { type: "submit", disabled: loading, className: "flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50", children: [_jsx(Save, { className: "w-4 h-4" }), loading ? 'Salvando...' : 'Salvar Processo'] }), _jsxs("button", { type: "button", onClick: () => navigate('/processos'), className: "flex items-center gap-2 px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: [_jsx(X, { className: "w-4 h-4" }), "Cancelar"] })] })] }) })] }));
}
