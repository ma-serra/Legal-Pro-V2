import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { StatCard, PageHeader } from '../../components/ui/AdminComponents';
import { Activity, Cpu, HardDrive, Network, Clock, AlertTriangle } from 'lucide-react';
import api from '../../lib/api';
export default function SystemMonitoring() {
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 5000); // Update every 5s
        return () => clearInterval(interval);
    }, []);
    const fetchMetrics = async () => {
        try {
            const response = await api.get('/api/admin/api/admin/vectorial/metrics');
            setMetrics({
                cpu: Math.random() * 100,
                memory: Math.random() * 100,
                disk: Math.random() * 100,
                network: Math.random() * 100,
                uptime: '5d 12h 34m',
                requests24h: Math.floor(Math.random() * 10000),
            });
        }
        catch (error) {
            console.error('Error fetching metrics:', error);
        }
        finally {
            setLoading(false);
        }
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Monitoramento do Sistema", description: "M\u00E9tricas em tempo real do servidor e servi\u00E7os" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8", children: [_jsx(StatCard, { title: "CPU", value: `${metrics?.cpu.toFixed(1)}%`, icon: Cpu }), _jsx(StatCard, { title: "Mem\u00F3ria", value: `${metrics?.memory.toFixed(1)}%`, icon: HardDrive }), _jsx(StatCard, { title: "Disco", value: `${metrics?.disk.toFixed(1)}%`, icon: HardDrive }), _jsx(StatCard, { title: "Rede", value: `${metrics?.network.toFixed(1)} MB/s`, icon: Network })] }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsxs("div", { className: "flex items-center gap-3 mb-4", children: [_jsx(Clock, { className: "w-6 h-6 text-green-600" }), _jsx("h2", { className: "text-lg font-semibold text-gray-900", children: "Uptime" })] }), _jsx("p", { className: "text-3xl font-bold text-gray-900", children: metrics?.uptime }), _jsx("p", { className: "text-sm text-gray-600 mt-2", children: "Sistema est\u00E1vel e operacional" })] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsxs("div", { className: "flex items-center gap-3 mb-4", children: [_jsx(Activity, { className: "w-6 h-6 text-blue-600" }), _jsx("h2", { className: "text-lg font-semibold text-gray-900", children: "Requisi\u00E7\u00F5es (24h)" })] }), _jsx("p", { className: "text-3xl font-bold text-gray-900", children: metrics?.requests24h.toLocaleString() }), _jsx("p", { className: "text-sm text-gray-600 mt-2", children: "M\u00E9dia de 416 req/hora" })] })] }), _jsxs("div", { className: "bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3", children: [_jsx(AlertTriangle, { className: "w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" }), _jsxs("div", { children: [_jsx("h3", { className: "font-medium text-yellow-900", children: "Aviso" }), _jsx("p", { className: "text-sm text-yellow-800 mt-1", children: "M\u00E9tricas s\u00E3o simuladas para demonstra\u00E7\u00E3o. Configure monitoramento real para produ\u00E7\u00E3o." })] })] })] }));
}
