import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { Save, X, ArrowLeft } from 'lucide-react';
import api from '../../lib/api';
export default function EditProcesso() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
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
        autor: '',
        reu: '',
    });
    useEffect(() => {
        fetchProcesso();
    }, [id]);
    // Endpoint: GET /processos/:processo_id
    const fetchProcesso = async () => {
        try {
            const response = await api.get(`/processos/${id}`);
            setFormData(response.data);
        }
        catch (error) {
            console.error('Error fetching processo:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const handleChange = (e) => {
        setFormData(prev => ({
            ...prev,
            [e.target.name]: e.target.value
        }));
    };
    // Endpoint: POST /processos/:processo_id/editar
    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            await api.post(`/processos/${id}/editar`, {
                ...formData,
                valor_causa: formData.valor_causa ? parseFloat(formData.valor_causa) : null
            });
            navigate(`/processos/${id}`);
        }
        catch (error) {
            console.error('Error updating processo:', error);
            alert('Erro ao atualizar processo');
        }
        finally {
            setSaving(false);
        }
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsxs("div", { className: "mb-6", children: [_jsxs("button", { onClick: () => navigate(`/processos/${id}`), className: "flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4", children: [_jsx(ArrowLeft, { className: "w-4 h-4" }), "Voltar"] }), _jsx(PageHeader, { title: `Editar Processo ${formData.numero_processo}`, description: "Atualizar informa\u00E7\u00F5es do processo" })] }), _jsx("form", { onSubmit: handleSubmit, className: "max-w-4xl", children: _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6 space-y-6", children: [_jsxs("div", { children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Informa\u00E7\u00F5es B\u00E1sicas" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { className: "md:col-span-2", children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "N\u00FAmero do Processo *" }), _jsx("input", { type: "text", name: "numero_processo", value: formData.numero_processo, onChange: handleChange, required: true, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "\u00C1rea do Direito *" }), _jsxs("select", { name: "area_direito", value: formData.area_direito, onChange: handleChange, required: true, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "civel", children: "C\u00EDvel" }), _jsx("option", { value: "trabalhista", children: "Trabalhista" }), _jsx("option", { value: "criminal", children: "Criminal" }), _jsx("option", { value: "tributario", children: "Tribut\u00E1rio" }), _jsx("option", { value: "familia", children: "Fam\u00EDlia" }), _jsx("option", { value: "empresarial", children: "Empresarial" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Status" }), _jsxs("select", { name: "status", value: formData.status, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "ativo", children: "Ativo" }), _jsx("option", { value: "suspenso", children: "Suspenso" }), _jsx("option", { value: "arquivado", children: "Arquivado" }), _jsx("option", { value: "finalizado", children: "Finalizado" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Valor da Causa" }), _jsx("input", { type: "number", name: "valor_causa", value: formData.valor_causa, onChange: handleChange, step: "0.01", className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Data de Distribui\u00E7\u00E3o" }), _jsx("input", { type: "date", name: "data_distribuicao", value: formData.data_distribuicao, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] })] })] }), _jsxs("div", { children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Partes" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Autor" }), _jsx("input", { type: "text", name: "autor", value: formData.autor, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "R\u00E9u" }), _jsx("input", { type: "text", name: "reu", value: formData.reu, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] })] })] }), _jsxs("div", { children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Localiza\u00E7\u00E3o" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Vara" }), _jsx("input", { type: "text", name: "vara", value: formData.vara, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Comarca" }), _jsx("input", { type: "text", name: "comarca", value: formData.comarca, onChange: handleChange, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Descri\u00E7\u00E3o/Observa\u00E7\u00F5es" }), _jsx("textarea", { name: "descricao", value: formData.descricao, onChange: handleChange, rows: 4, className: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { className: "flex gap-3 pt-4 border-t border-gray-200", children: [_jsxs("button", { type: "submit", disabled: saving, className: "flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50", children: [_jsx(Save, { className: "w-4 h-4" }), saving ? 'Salvando...' : 'Salvar Alterações'] }), _jsxs("button", { type: "button", onClick: () => navigate(`/processos/${id}`), className: "flex items-center gap-2 px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: [_jsx(X, { className: "w-4 h-4" }), "Cancelar"] })] })] }) })] }));
}
