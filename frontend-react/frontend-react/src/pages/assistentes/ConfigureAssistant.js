import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { ArrowLeft, Save, Bot, Sliders, Zap } from 'lucide-react';
import api from '../../lib/api';
export default function ConfigureAssistant() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [config, setConfig] = useState({
        id: 0,
        nome: '',
        area_juridica: '',
        model: 'gpt-4-turbo-preview',
        temperature: 0.7,
        max_tokens: 2000,
        top_p: 1.0,
        frequency_penalty: 0.0,
        presence_penalty: 0.0,
        system_prompt: '',
        context_window: 8000,
        response_format: 'text'
    });
    useEffect(() => {
        if (id) {
            fetchConfig();
        }
    }, [id]);
    const fetchConfig = async () => {
        try {
            const response = await api.get(`/admin/assistentes/${id}/configurar`);
            setConfig(response.data);
        }
        catch (error) {
            console.error('Error fetching config:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            await api.post(`/admin/assistentes/${id}/configurar`, config);
            alert('Configuração salva com sucesso!');
            navigate('/assistentes');
        }
        catch (error) {
            console.error('Error saving config:', error);
            alert('Erro ao salvar configuração');
        }
        finally {
            setSaving(false);
        }
    };
    const handleChange = (field, value) => {
        setConfig(prev => ({ ...prev, [field]: value }));
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsxs("div", { className: "mb-6", children: [_jsxs(Link, { to: "/assistentes", className: "flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4", children: [_jsx(ArrowLeft, { className: "w-4 h-4" }), "Voltar para assistentes"] }), _jsx(PageHeader, { title: `Configurar: ${config.nome}`, description: config.area_juridica })] }), _jsxs("form", { onSubmit: handleSubmit, className: "space-y-6", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsxs("div", { className: "flex items-center gap-2 mb-4", children: [_jsx(Bot, { className: "w-5 h-5 text-blue-600" }), _jsx("h3", { className: "text-lg font-semibold text-gray-900", children: "Modelo de IA" })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-6", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Modelo" }), _jsxs("select", { value: config.model, onChange: (e) => handleChange('model', e.target.value), className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "gpt-4-turbo-preview", children: "GPT-4 Turbo" }), _jsx("option", { value: "gpt-4", children: "GPT-4" }), _jsx("option", { value: "gpt-3.5-turbo", children: "GPT-3.5 Turbo" }), _jsx("option", { value: "claude-3-opus", children: "Claude 3 Opus" }), _jsx("option", { value: "claude-3-sonnet", children: "Claude 3 Sonnet" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Formato de Resposta" }), _jsxs("select", { value: config.response_format, onChange: (e) => handleChange('response_format', e.target.value), className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "text", children: "Texto" }), _jsx("option", { value: "json", children: "JSON" }), _jsx("option", { value: "markdown", children: "Markdown" })] })] })] })] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsxs("div", { className: "flex items-center gap-2 mb-4", children: [_jsx(Sliders, { className: "w-5 h-5 text-blue-600" }), _jsx("h3", { className: "text-lg font-semibold text-gray-900", children: "Par\u00E2metros Avan\u00E7ados" })] }), _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsxs("div", { className: "flex justify-between mb-2", children: [_jsx("label", { className: "text-sm font-medium text-gray-700", children: "Temperature" }), _jsx("span", { className: "text-sm text-gray-600", children: config.temperature })] }), _jsx("input", { type: "range", min: "0", max: "2", step: "0.1", value: config.temperature, onChange: (e) => handleChange('temperature', parseFloat(e.target.value)), className: "w-full" }), _jsx("p", { className: "text-xs text-gray-500 mt-1", children: "Controla a criatividade. 0 = mais preciso, 2 = mais criativo" })] }), _jsxs("div", { children: [_jsxs("div", { className: "flex justify-between mb-2", children: [_jsx("label", { className: "text-sm font-medium text-gray-700", children: "M\u00E1ximo de Tokens" }), _jsx("span", { className: "text-sm text-gray-600", children: config.max_tokens })] }), _jsx("input", { type: "range", min: "100", max: "4000", step: "100", value: config.max_tokens, onChange: (e) => handleChange('max_tokens', parseInt(e.target.value)), className: "w-full" }), _jsx("p", { className: "text-xs text-gray-500 mt-1", children: "Tamanho m\u00E1ximo da resposta" })] }), _jsxs("div", { children: [_jsxs("div", { className: "flex justify-between mb-2", children: [_jsx("label", { className: "text-sm font-medium text-gray-700", children: "Top P" }), _jsx("span", { className: "text-sm text-gray-600", children: config.top_p })] }), _jsx("input", { type: "range", min: "0", max: "1", step: "0.1", value: config.top_p, onChange: (e) => handleChange('top_p', parseFloat(e.target.value)), className: "w-full" })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-6", children: [_jsxs("div", { children: [_jsxs("div", { className: "flex justify-between mb-2", children: [_jsx("label", { className: "text-sm font-medium text-gray-700", children: "Frequency Penalty" }), _jsx("span", { className: "text-sm text-gray-600", children: config.frequency_penalty })] }), _jsx("input", { type: "range", min: "-2", max: "2", step: "0.1", value: config.frequency_penalty, onChange: (e) => handleChange('frequency_penalty', parseFloat(e.target.value)), className: "w-full" })] }), _jsxs("div", { children: [_jsxs("div", { className: "flex justify-between mb-2", children: [_jsx("label", { className: "text-sm font-medium text-gray-700", children: "Presence Penalty" }), _jsx("span", { className: "text-sm text-gray-600", children: config.presence_penalty })] }), _jsx("input", { type: "range", min: "-2", max: "2", step: "0.1", value: config.presence_penalty, onChange: (e) => handleChange('presence_penalty', parseFloat(e.target.value)), className: "w-full" })] })] })] })] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsxs("div", { className: "flex items-center gap-2 mb-4", children: [_jsx(Zap, { className: "w-5 h-5 text-blue-600" }), _jsx("h3", { className: "text-lg font-semibold text-gray-900", children: "System Prompt" })] }), _jsx("textarea", { value: config.system_prompt, onChange: (e) => handleChange('system_prompt', e.target.value), rows: 10, className: "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm", placeholder: "Digite o prompt do sistema..." }), _jsx("p", { className: "text-xs text-gray-500 mt-2", children: "Define o comportamento e personalidade do assistente" })] }), _jsxs("div", { className: "flex justify-end gap-4", children: [_jsx(Link, { to: "/assistentes", className: "px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Cancelar" }), _jsxs("button", { type: "submit", disabled: saving, className: "flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50", children: [_jsx(Save, { className: "w-4 h-4" }), saving ? 'Salvando...' : 'Salvar Configuração'] })] })] })] }));
}
