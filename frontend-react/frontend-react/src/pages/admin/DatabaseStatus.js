import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader, StatCard } from '../../components/ui/AdminComponents';
import { Database, Activity, HardDrive } from 'lucide-react';
export default function DatabaseStatus() {
    // Mock data - replace with real API calls
    const dbStats = {
        status: 'healthy',
        uptime: '15d 8h 32m',
        connections: { active: 8, max: 100 },
        size: { used: 2.4, total: 10 },
        tables: 45,
        indexes: 123
    };
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Status do Banco de Dados", description: "PostgreSQL Railway Database" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8", children: [_jsx(StatCard, { title: "Status", value: "Online", icon: Database }), _jsx(StatCard, { title: "Uptime", value: dbStats.uptime, icon: Activity }), _jsx(StatCard, { title: "Conex\u00F5es", value: `${dbStats.connections.active}/${dbStats.connections.max}`, icon: Activity }), _jsx(StatCard, { title: "Tamanho", value: `${dbStats.size.used}/${dbStats.size.total} GB`, icon: HardDrive })] }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Tabelas" }), _jsxs("div", { className: "space-y-3", children: [_jsxs("div", { className: "flex justify-between", children: [_jsx("span", { className: "text-gray-600", children: "Total de tabelas" }), _jsx("span", { className: "font-medium", children: dbStats.tables })] }), _jsxs("div", { className: "flex justify-between", children: [_jsx("span", { className: "text-gray-600", children: "\u00CDndices" }), _jsx("span", { className: "font-medium", children: dbStats.indexes })] })] })] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Performance" }), _jsxs("div", { className: "space-y-3", children: [_jsxs("div", { className: "flex justify-between", children: [_jsx("span", { className: "text-gray-600", children: "Query m\u00E9dio" }), _jsx("span", { className: "font-medium", children: "45ms" })] }), _jsxs("div", { className: "flex justify-between", children: [_jsx("span", { className: "text-gray-600", children: "Cache hit rate" }), _jsx("span", { className: "font-medium", children: "98.5%" })] })] })] })] })] }));
}
