import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { Calendar, Clock, MapPin, Users, FileSpreadsheet } from 'lucide-react';
import api from '../../lib/api';
export default function Hearings() {
    const navigate = useNavigate();
    const [audiencias, setAudiencias] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [exporting, setExporting] = useState(false);
    useEffect(() => {
        fetchAudiencias();
    }, []);
    const fetchAudiencias = async () => {
        try {
            const response = await api.get('/setorenergia/api/audiencias');
            setAudiencias(response.data);
        }
        catch (error) {
            console.error('Error fetching audiências:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const handleExport = async () => {
        setExporting(true);
        try {
            const response = await api.post('/setorenergia/api/export/audiencias/excel', {}, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `audiencias_${new Date().toISOString().split('T')[0]}.xlsx`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        }
        catch (error) {
            console.error('Error exporting:', error);
            alert('Erro ao exportar audiências');
        }
        finally {
            setExporting(false);
        }
    };
    const getStatusColor = (status) => {
        switch (status) {
            case 'agendada': return 'bg-blue-100 text-blue-800';
            case 'realizada': return 'bg-green-100 text-green-800';
            case 'cancelada': return 'bg-red-100 text-red-800';
            case 'remarcada': return 'bg-yellow-100 text-yellow-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };
    const filteredAudiencias = filter === 'all'
        ? audiencias
        : audiencias.filter(a => a.status === filter);
    // Agrupar por mês
    const audienciasPorMes = filteredAudiencias.reduce((acc, audiencia) => {
        const mes = new Date(audiencia.data_audiencia).toLocaleDateString('pt-BR', {
            year: 'numeric',
            month: 'long'
        });
        if (!acc[mes]) {
            acc[mes] = [];
        }
        acc[mes].push(audiencia);
        return acc;
    }, {});
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Gest\u00E3o de Audi\u00EAncias", description: "Calend\u00E1rio e gerenciamento de audi\u00EAncias do setor energia", action: _jsxs("button", { onClick: handleExport, disabled: exporting, className: "flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50", children: [_jsx(FileSpreadsheet, { className: "w-4 h-4" }), exporting ? 'Exportando...' : 'Exportar Excel'] }) }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-4 gap-6 mb-6", children: [_jsx("div", { className: "bg-white p-6 rounded-lg border border-gray-200", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-gray-600 mb-1", children: "Total" }), _jsx("p", { className: "text-3xl font-bold text-gray-900", children: audiencias.length })] }), _jsx(Calendar, { className: "w-10 h-10 text-blue-600" })] }) }), _jsx("div", { className: "bg-white p-6 rounded-lg border border-gray-200", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-gray-600 mb-1", children: "Agendadas" }), _jsx("p", { className: "text-3xl font-bold text-blue-600", children: audiencias.filter(a => a.status === 'agendada').length })] }), _jsx(Clock, { className: "w-10 h-10 text-blue-600" })] }) }), _jsx("div", { className: "bg-white p-6 rounded-lg border border-gray-200", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-gray-600 mb-1", children: "Realizadas" }), _jsx("p", { className: "text-3xl font-bold text-green-600", children: audiencias.filter(a => a.status === 'realizada').length })] }), _jsx(Users, { className: "w-10 h-10 text-green-600" })] }) }), _jsx("div", { className: "bg-white p-6 rounded-lg border border-gray-200", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-gray-600 mb-1", children: "Pr\u00F3ximos 7 dias" }), _jsx("p", { className: "text-3xl font-bold text-orange-600", children: audiencias.filter(a => {
                                                const diff = new Date(a.data_audiencia).getTime() - new Date().getTime();
                                                return diff > 0 && diff < 7 * 24 * 60 * 60 * 1000;
                                            }).length })] }), _jsx(Calendar, { className: "w-10 h-10 text-orange-600" })] }) })] }), _jsx("div", { className: "bg-white rounded-lg border border-gray-200 p-4 mb-6", children: _jsxs("div", { className: "flex gap-2", children: [_jsx("button", { onClick: () => setFilter('all'), className: `px-4 py-2 rounded-lg text-sm font-medium ${filter === 'all'
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`, children: "Todas" }), _jsx("button", { onClick: () => setFilter('agendada'), className: `px-4 py-2 rounded-lg text-sm font-medium ${filter === 'agendada'
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`, children: "Agendadas" }), _jsx("button", { onClick: () => setFilter('realizada'), className: `px-4 py-2 rounded-lg text-sm font-medium ${filter === 'realizada'
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`, children: "Realizadas" }), _jsx("button", { onClick: () => setFilter('remarcada'), className: `px-4 py-2 rounded-lg text-sm font-medium ${filter === 'remarcada'
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`, children: "Remarcadas" })] }) }), _jsxs("div", { className: "space-y-6", children: [Object.entries(audienciasPorMes).map(([mes, audienciasMes]) => (_jsxs("div", { className: "bg-white rounded-lg border border-gray-200", children: [_jsxs("div", { className: "p-4 border-b border-gray-200 bg-gray-50", children: [_jsx("h3", { className: "font-semibold text-gray-900 capitalize", children: mes }), _jsxs("p", { className: "text-sm text-gray-600", children: [audienciasMes.length, " audi\u00EAncias"] })] }), _jsx("div", { className: "divide-y divide-gray-100", children: audienciasMes.map((audiencia) => (_jsx("div", { className: "p-4 hover:bg-gray-50 cursor-pointer", onClick: () => navigate(`/processos/${audiencia.id}`), children: _jsx("div", { className: "flex items-start justify-between", children: _jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "flex items-center gap-3 mb-2", children: [_jsxs("div", { className: "flex items-center gap-2 text-sm text-gray-600", children: [_jsx(Calendar, { className: "w-4 h-4" }), _jsx("span", { children: new Date(audiencia.data_audiencia).toLocaleDateString('pt-BR') })] }), _jsxs("div", { className: "flex items-center gap-2 text-sm text-gray-600", children: [_jsx(Clock, { className: "w-4 h-4" }), _jsx("span", { children: audiencia.hora })] }), _jsx("span", { className: `px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(audiencia.status)}`, children: audiencia.status })] }), _jsx("h4", { className: "font-medium text-gray-900 mb-1", children: audiencia.processo_titulo }), _jsxs("p", { className: "text-sm text-gray-600 mb-2", children: ["Processo N\u00BA ", audiencia.processo_numero] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-4 text-sm", children: [_jsxs("div", { children: [_jsx("span", { className: "text-gray-600", children: "Tipo:" }), _jsx("p", { className: "font-medium text-gray-900", children: audiencia.tipo })] }), _jsxs("div", { children: [_jsx("span", { className: "text-gray-600", children: "Local:" }), _jsxs("div", { className: "flex items-center gap-1", children: [_jsx(MapPin, { className: "w-3 h-3 text-gray-400" }), _jsx("p", { className: "font-medium text-gray-900", children: audiencia.local })] })] }), _jsxs("div", { children: [_jsx("span", { className: "text-gray-600", children: "Juiz:" }), _jsx("p", { className: "font-medium text-gray-900", children: audiencia.juiz })] })] }), audiencia.observacoes && (_jsx("p", { className: "text-sm text-gray-600 mt-2 italic", children: audiencia.observacoes }))] }) }) }, audiencia.id))) })] }, mes))), filteredAudiencias.length === 0 && (_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-12 text-center", children: [_jsx(Calendar, { className: "w-16 h-16 text-gray-400 mx-auto mb-4" }), _jsx("h3", { className: "text-lg font-medium text-gray-900 mb-2", children: "Nenhuma audi\u00EAncia encontrada" }), _jsxs("p", { className: "text-gray-600", children: ["N\u00E3o h\u00E1 audi\u00EAncias ", filter !== 'all' ? `com status "${filter}"` : 'cadastradas'] })] }))] })] }));
}
