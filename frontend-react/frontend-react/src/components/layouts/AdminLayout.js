import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Link, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Users, Settings, Database, Activity, FileText, Palette, Shield, Cloud, LogOut } from 'lucide-react';
export function AdminLayout({ children }) {
    const navigate = useNavigate();
    const menuItems = [
        { icon: LayoutDashboard, label: 'Dashboard', path: '/admin' },
        { icon: Activity, label: 'Monitoramento', path: '/admin/monitoring' },
        { icon: Database, label: 'Banco de Dados', path: '/admin/database' },
        { icon: Users, label: 'Agentes', path: '/admin/agents' },
        { icon: Shield, label: 'Usuários', path: '/admin/users' },
        { icon: Settings, label: 'APIs', path: '/admin/api-config' },
        { icon: FileText, label: 'Templates', path: '/admin/templates' },
        { icon: Palette, label: 'Temas', path: '/admin/themes' },
        { icon: Cloud, label: 'Vector DB', path: '/admin/vector-status' },
    ];
    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/login');
    };
    return (_jsxs("div", { className: "min-h-screen bg-gray-50 flex", children: [_jsxs("aside", { className: "w-64 bg-white border-r border-gray-200 flex flex-col", children: [_jsx("div", { className: "h-16 flex items-center px-6 border-b border-gray-200", children: _jsx("h1", { className: "text-xl font-bold text-gray-900", children: "Legal Pro Admin" }) }), _jsx("nav", { className: "flex-1 px-3 py-4 space-y-1 overflow-y-auto", children: menuItems.map((item) => (_jsxs(Link, { to: item.path, className: "flex items-center gap-3 px-3 py-2 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors", children: [_jsx(item.icon, { className: "w-5 h-5" }), _jsx("span", { className: "text-sm font-medium", children: item.label })] }, item.path))) }), _jsx("div", { className: "p-4 border-t border-gray-200", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold", children: "A" }), _jsxs("div", { children: [_jsx("p", { className: "text-sm font-medium text-gray-900", children: "Admin" }), _jsx("p", { className: "text-xs text-gray-500", children: "Administrador" })] })] }), _jsx("button", { onClick: handleLogout, className: "p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100", title: "Sair", children: _jsx(LogOut, { className: "w-4 h-4" }) })] }) })] }), _jsx("main", { className: "flex-1 overflow-auto", children: _jsx("div", { className: "p-8", children: children }) })] }));
}
