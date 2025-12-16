import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { LogOut, LayoutDashboard, Gavel, FileSearch, Users, FileUp, Scale, TrendingUp, Menu, X } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useState } from 'react';
const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    {
        path: '/processos',
        label: 'Processos',
        icon: Gavel,
        subItems: [
            { path: '/processos', label: 'Lista de Processos' },
            { path: '/processos/importar', label: 'Importar Planilha', icon: FileUp },
            { path: '/processos/teses', label: 'Teses Tributárias', icon: Scale },
            { path: '/processos/indices', label: 'Índices Monetários', icon: TrendingUp }
        ]
    },
    { path: '/analises', label: 'Análises', icon: FileSearch },
    { path: '/assistentes', label: 'Assistentes', icon: Users }
];
export default function Navigation() {
    const { logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [openSubmenu, setOpenSubmenu] = useState(null);
    const handleLogout = () => {
        logout();
        navigate('/login');
    };
    const isActivePath = (path) => {
        if (path === '/processos') {
            return location.pathname.startsWith('/processos');
        }
        return location.pathname === path;
    };
    return (_jsx("nav", { className: "border-b border-border bg-card shadow-sm sticky top-0 z-50", children: _jsxs("div", { className: "container mx-auto px-4 py-3", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs(Link, { to: "/dashboard", className: "flex items-center gap-2", children: [_jsx("div", { className: "p-1.5 bg-primary/10 rounded-lg", children: _jsx(Scale, { className: "w-5 h-5 text-primary" }) }), _jsx("span", { className: "text-xl font-bold text-primary hidden sm:inline", children: "Legal Pro" })] }), _jsxs("div", { className: "hidden md:flex items-center gap-1", children: [navItems.map((item) => {
                                    const Icon = item.icon;
                                    const isActive = isActivePath(item.path);
                                    if (item.subItems) {
                                        return (_jsxs("div", { className: "relative group", children: [_jsxs(Link, { to: item.path, className: `flex items-center gap-2 px-3 py-2 rounded-md transition ${isActive
                                                        ? 'bg-primary/10 text-primary'
                                                        : 'text-foreground hover:bg-accent hover:text-primary'}`, children: [_jsx(Icon, { className: "w-4 h-4" }), _jsx("span", { children: item.label })] }), _jsx("div", { className: "absolute left-0 top-full mt-1 w-56 bg-card border border-border rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all", children: item.subItems.map((subItem) => {
                                                        const SubIcon = subItem.icon;
                                                        return (_jsxs(Link, { to: subItem.path, className: `flex items-center gap-2 px-4 py-3 hover:bg-accent transition-colors first:rounded-t-lg last:rounded-b-lg ${location.pathname === subItem.path ? 'bg-primary/10 text-primary' : ''}`, children: [SubIcon && _jsx(SubIcon, { className: "w-4 h-4" }), _jsx("span", { className: "text-sm", children: subItem.label })] }, subItem.path));
                                                    }) })] }, item.path));
                                    }
                                    return (_jsxs(Link, { to: item.path, className: `flex items-center gap-2 px-3 py-2 rounded-md transition ${isActive
                                            ? 'bg-primary/10 text-primary'
                                            : 'text-foreground hover:bg-accent hover:text-primary'}`, children: [_jsx(Icon, { className: "w-4 h-4" }), _jsx("span", { children: item.label })] }, item.path));
                                }), _jsx("div", { className: "w-px h-6 bg-border mx-2" }), _jsxs("button", { onClick: handleLogout, className: "flex items-center gap-2 px-3 py-2 rounded-md hover:bg-red-500/10 hover:text-red-400 transition", title: "Sair", children: [_jsx(LogOut, { className: "w-4 h-4" }), _jsx("span", { className: "hidden lg:inline text-sm", children: "Sair" })] })] }), _jsx("button", { onClick: () => setMobileMenuOpen(!mobileMenuOpen), className: "md:hidden p-2 rounded-lg hover:bg-accent transition-colors", children: mobileMenuOpen ? _jsx(X, { className: "w-5 h-5" }) : _jsx(Menu, { className: "w-5 h-5" }) })] }), mobileMenuOpen && (_jsxs("div", { className: "md:hidden mt-4 pb-4 border-t border-border pt-4 space-y-1", children: [navItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = isActivePath(item.path);
                            if (item.subItems) {
                                return (_jsxs("div", { children: [_jsxs("button", { onClick: () => setOpenSubmenu(openSubmenu === item.path ? null : item.path), className: `w-full flex items-center justify-between px-3 py-2 rounded-md transition ${isActive ? 'bg-primary/10 text-primary' : 'hover:bg-accent'}`, children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx(Icon, { className: "w-4 h-4" }), _jsx("span", { children: item.label })] }), _jsx("span", { className: "text-xs", children: openSubmenu === item.path ? '▼' : '▶' })] }), openSubmenu === item.path && (_jsx("div", { className: "ml-6 mt-1 space-y-1", children: item.subItems.map((subItem) => {
                                                const SubIcon = subItem.icon;
                                                return (_jsxs(Link, { to: subItem.path, onClick: () => setMobileMenuOpen(false), className: `flex items-center gap-2 px-3 py-2 rounded-md text-sm transition ${location.pathname === subItem.path
                                                        ? 'bg-primary/10 text-primary'
                                                        : 'hover:bg-accent'}`, children: [SubIcon && _jsx(SubIcon, { className: "w-4 h-4" }), _jsx("span", { children: subItem.label })] }, subItem.path));
                                            }) }))] }, item.path));
                            }
                            return (_jsxs(Link, { to: item.path, onClick: () => setMobileMenuOpen(false), className: `flex items-center gap-2 px-3 py-2 rounded-md transition ${isActive ? 'bg-primary/10 text-primary' : 'hover:bg-accent'}`, children: [_jsx(Icon, { className: "w-4 h-4" }), _jsx("span", { children: item.label })] }, item.path));
                        }), _jsxs("button", { onClick: handleLogout, className: "w-full flex items-center gap-2 px-3 py-2 rounded-md hover:bg-red-500/10 hover:text-red-400 transition mt-4", children: [_jsx(LogOut, { className: "w-4 h-4" }), _jsx("span", { children: "Sair" })] })] }))] }) }));
}
