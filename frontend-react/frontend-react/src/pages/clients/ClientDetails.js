import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { Building2, Mail, Phone, MapPin, Calendar, FileText, Edit, Trash2, Plus, ArrowLeft, User } from 'lucide-react';
import api from '../../lib/api';
export default function ClientDetails() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [client, setClient] = useState(null);
    const [processes, setProcesses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('info');
    useEffect(() => {
        if (id) {
            fetchClientDetails();
            fetchClientProcesses();
        }
    }, [id]);
    const fetchClientDetails = async () => {
        try {
            const response = await api.get(`/api/clientes/${id}`);
            setClient(response.data);
        }
        catch (error) {
            console.error('Error fetching client:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const fetchClientProcesses = async () => {
        try {
            const response = await api.get(`/api/clientes/${id}/processos`);
            setProcesses(response.data);
        }
        catch (error) {
            console.error('Error fetching processes:', error);
        }
    };
    const handleDelete = async () => {
        if (!confirm('Tem certeza que deseja excluir este cliente?'))
            return;
        try {
            await api.delete(`/api/clientes/${id}`);
            navigate('/clientes');
        }
        catch (error) {
            console.error('Error deleting client:', error);
            alert('Erro ao excluir cliente');
        }
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto" }) }));
    }
    if (!client) {
        return (_jsx(AdminLayout, { children: _jsxs("div", { className: "text-center py-12", children: [_jsx("p", { className: "text-gray-500", children: "Cliente n\u00E3o encontrado" }), _jsx(Link, { to: "/clientes", className: "text-blue-600 hover:underline mt-4 inline-block", children: "Voltar para lista" })] }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsxs("div", { className: "mb-6", children: [_jsxs("button", { onClick: () => navigate('/clientes'), className: "flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4", children: [_jsx(ArrowLeft, { className: "w-4 h-4" }), "Voltar para clientes"] }), _jsx(PageHeader, { title: client.name, description: client.legal_name || 'Cliente', action: _jsxs("div", { className: "flex gap-2", children: [_jsxs(Link, { to: `/clientes/${id}/editar`, className: "flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: [_jsx(Edit, { className: "w-4 h-4" }), "Editar"] }), _jsxs("button", { onClick: handleDelete, className: "flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700", children: [_jsx(Trash2, { className: "w-4 h-4" }), "Excluir"] })] }) })] }), _jsx("div", { className: "border-b border-gray-200 mb-6", children: _jsxs("nav", { className: "flex gap-8", children: [_jsx("button", { onClick: () => setActiveTab('info'), className: `pb-4 border-b-2 font-medium ${activeTab === 'info'
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'}`, children: "Informa\u00E7\u00F5es" }), _jsxs("button", { onClick: () => setActiveTab('processes'), className: `pb-4 border-b-2 font-medium ${activeTab === 'processes'
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'}`, children: ["Processos (", processes.length, ")"] }), _jsx("button", { onClick: () => setActiveTab('documents'), className: `pb-4 border-b-2 font-medium ${activeTab === 'documents'
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'}`, children: "Documentos" })] }) }), activeTab === 'info' && (_jsx("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-6", children: [_jsxs("div", { children: [_jsx("h3", { className: "text-sm font-medium text-gray-500 mb-4", children: "Informa\u00E7\u00F5es B\u00E1sicas" }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsxs("label", { className: "flex items-center gap-2 text-sm text-gray-600 mb-1", children: [_jsx(User, { className: "w-4 h-4" }), "Nome"] }), _jsx("p", { className: "text-gray-900", children: client.name })] }), _jsxs("div", { children: [_jsxs("label", { className: "flex items-center gap-2 text-sm text-gray-600 mb-1", children: [_jsx(Building2, { className: "w-4 h-4" }), "Raz\u00E3o Social"] }), _jsx("p", { className: "text-gray-900", children: client.legal_name || '-' })] }), _jsxs("div", { children: [_jsxs("label", { className: "flex items-center gap-2 text-sm text-gray-600 mb-1", children: [_jsx(FileText, { className: "w-4 h-4" }), "CPF/CNPJ"] }), _jsx("p", { className: "text-gray-900", children: client.document_number })] })] })] }), _jsxs("div", { children: [_jsx("h3", { className: "text-sm font-medium text-gray-500 mb-4", children: "Contato" }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsxs("label", { className: "flex items-center gap-2 text-sm text-gray-600 mb-1", children: [_jsx(Mail, { className: "w-4 h-4" }), "Email"] }), _jsx("p", { className: "text-gray-900", children: client.email || '-' })] }), _jsxs("div", { children: [_jsxs("label", { className: "flex items-center gap-2 text-sm text-gray-600 mb-1", children: [_jsx(Phone, { className: "w-4 h-4" }), "Telefone"] }), _jsx("p", { className: "text-gray-900", children: client.phone || '-' })] }), _jsxs("div", { children: [_jsxs("label", { className: "flex items-center gap-2 text-sm text-gray-600 mb-1", children: [_jsx(MapPin, { className: "w-4 h-4" }), "Endere\u00E7o"] }), _jsxs("p", { className: "text-gray-900", children: [client.address && `${client.address}, ${client.city} - ${client.state}`, !client.address && '-'] })] })] })] }), _jsxs("div", { children: [_jsx("h3", { className: "text-sm font-medium text-gray-500 mb-4", children: "Status" }), _jsx("span", { className: `inline-flex px-3 py-1 rounded-full text-sm font-medium ${client.status === 'active'
                                        ? 'bg-green-100 text-green-800'
                                        : 'bg-gray-100 text-gray-800'}`, children: client.status === 'active' ? 'Ativo' : 'Inativo' })] }), _jsxs("div", { children: [_jsx("h3", { className: "text-sm font-medium text-gray-500 mb-4", children: "Datas" }), _jsxs("div", { className: "space-y-2", children: [_jsxs("p", { className: "text-sm text-gray-600", children: [_jsx(Calendar, { className: "w-4 h-4 inline mr-2" }), "Cadastrado em: ", new Date(client.created_at).toLocaleDateString('pt-BR')] }), client.updated_at && (_jsxs("p", { className: "text-sm text-gray-600", children: ["Atualizado em: ", new Date(client.updated_at).toLocaleDateString('pt-BR')] }))] })] })] }) })), activeTab === 'processes' && (_jsx("div", { className: "bg-white rounded-lg border border-gray-200", children: processes.length > 0 ? (_jsx("div", { className: "divide-y divide-gray-200", children: processes.map((process) => (_jsx("div", { className: "p-4 hover:bg-gray-50", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("h4", { className: "font-medium text-gray-900", children: process.titulo }), _jsxs("p", { className: "text-sm text-gray-600", children: ["N\u00BA ", process.numero] })] }), _jsxs("div", { className: "flex items-center gap-4", children: [_jsx("span", { className: "px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800", children: process.status }), _jsx(Link, { to: `/processos/${process.id}`, className: "text-blue-600 hover:text-blue-700", children: "Ver detalhes" })] })] }) }, process.id))) })) : (_jsxs("div", { className: "p-12 text-center", children: [_jsx(FileText, { className: "w-12 h-12 text-gray-400 mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-medium text-gray-900 mb-2", children: "Nenhum processo encontrado" }), _jsx("p", { className: "text-gray-600 mb-4", children: "Este cliente ainda n\u00E3o possui processos cadastrados" }), _jsxs(Link, { to: "/processos/novo", className: "inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: [_jsx(Plus, { className: "w-4 h-4" }), "Adicionar Processo"] })] })) })), activeTab === 'documents' && (_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-12 text-center", children: [_jsx(FileText, { className: "w-12 h-12 text-gray-400 mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-medium text-gray-900 mb-2", children: "Gerenciamento de Documentos" }), _jsx("p", { className: "text-gray-600", children: "Funcionalidade em desenvolvimento" })] }))] }));
}
