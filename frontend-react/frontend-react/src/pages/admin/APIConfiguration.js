import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { Settings, CheckCircle, XCircle, Loader } from 'lucide-react';
import api from '../../lib/api';
export default function APIConfiguration() {
    const [configs, setConfigs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [testing, setTesting] = useState(null);
    useEffect(() => {
        fetchConfigs();
    }, []);
    // Endpoint: GET /admin/apis
    const fetchConfigs = async () => {
        try {
            const response = await api.get('/admin/apis');
            setConfigs(response.data || [
                { provider: 'openai', name: 'OpenAI GPT-4', status: 'active' },
                { provider: 'anthropic', name: 'Claude', status: 'active' },
                { provider: 'google', name: 'Google AI', status: 'inactive' },
                { provider: 'azure', name: 'Azure OpenAI', status: 'active' },
            ]);
        }
        catch (error) {
            console.error('Error fetching API configs:', error);
        }
        finally {
            setLoading(false);
        }
    };
    // Endpoint: POST /admin/apis/config
    const handleSaveConfig = async (provider, config) => {
        try {
            await api.post('/admin/apis/config', {
                provider,
                ...config
            });
            fetchConfigs();
            alert('Configuração salva!');
        }
        catch (error) {
            console.error('Error saving config:', error);
            alert('Erro ao salvar configuração');
        }
    };
    // Endpoint: POST /admin/apis/test/:provider
    const handleTestAPI = async (provider) => {
        setTesting(provider);
        try {
            const response = await api.post(`/admin/apis/test/${provider}`);
            if (response.data.success) {
                alert(`✅ ${provider} funcionando corretamente!`);
            }
            else {
                alert(`❌ Erro ao testar ${provider}`);
            }
        }
        catch (error) {
            console.error('Error testing API:', error);
            alert('Erro no teste');
        }
        finally {
            setTesting(null);
        }
    };
    const getStatusIcon = (status) => {
        switch (status) {
            case 'active':
                return _jsx(CheckCircle, { className: "w-5 h-5 text-green-600" });
            case 'error':
                return _jsx(XCircle, { className: "w-5 h-5 text-red-600" });
            default:
                return _jsx("div", { className: "w-5 h-5 rounded-full bg-gray-400" });
        }
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Configura\u00E7\u00E3o de APIs", description: "Gerenciar integra\u00E7\u00F5es e APIs externas" }), _jsxs("div", { className: "space-y-6", children: [configs.map((config) => (_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsxs("div", { className: "flex items-center justify-between mb-4", children: [_jsxs("div", { className: "flex items-center gap-3", children: [getStatusIcon(config.status), _jsxs("div", { children: [_jsx("h3", { className: "font-semibold text-gray-900", children: config.name }), _jsx("p", { className: "text-sm text-gray-500", children: config.provider })] })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("span", { className: `px-3 py-1 rounded-full text-xs font-medium ${config.status === 'active' ? 'bg-green-100 text-green-800' :
                                                    config.status === 'error' ? 'bg-red-100 text-red-800' :
                                                        'bg-gray-100 text-gray-800'}`, children: config.status }), _jsx("button", { onClick: () => handleTestAPI(config.provider), disabled: testing === config.provider, className: "px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 flex items-center gap-2", children: testing === config.provider ? (_jsxs(_Fragment, { children: [_jsx(Loader, { className: "w-4 h-4 animate-spin" }), "Testando..."] })) : ('Testar') })] })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "API Key" }), _jsx("input", { type: "password", defaultValue: config.api_key, className: "w-full px-4 py-2 border border-gray-300 rounded-lg", placeholder: "sk-..." })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Endpoint" }), _jsx("input", { type: "text", defaultValue: config.endpoint, className: "w-full px-4 py-2 border border-gray-300 rounded-lg", placeholder: "https://api.example.com" })] })] }), config.last_checked && (_jsxs("p", { className: "text-sm text-gray-500 mt-4", children: ["\u00DAltimo teste: ", new Date(config.last_checked).toLocaleString('pt-BR')] })), _jsx("div", { className: "flex gap-3 mt-4 pt-4 border-t border-gray-200", children: _jsx("button", { onClick: () => handleSaveConfig(config.provider, config), className: "px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: "Salvar" }) })] }, config.provider))), _jsxs("div", { className: "bg-blue-50 border border-blue-200 rounded-lg p-6", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx(Settings, { className: "w-6 h-6 text-blue-600" }), _jsxs("div", { children: [_jsx("h3", { className: "font-semibold text-blue-900", children: "Adicionar Nova API" }), _jsx("p", { className: "text-sm text-blue-700", children: "Configure integra\u00E7\u00F5es com novos provedores de IA e servi\u00E7os externos" })] })] }), _jsx("button", { className: "mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: "Adicionar API" })] })] })] }));
}
