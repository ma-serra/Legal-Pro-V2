import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader, StatCard } from '../../components/ui/AdminComponents';
import { Settings, Users, FileText, Bot, Zap, DollarSign, Mic, Video, GitBranch, Brain, FileCode, BarChart3, GitMerge, Calendar, Building2, Scale } from 'lucide-react';
import api from '../../lib/api';
export default function AdminModulesOverview() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchStats();
    }, []);
    const fetchStats = async () => {
        try {
            // Aggregate stats from various endpoints
            const [usuarios, processos, templates, multiagente] = await Promise.all([
                api.get('/admin/usuarios'),
                api.get('/api/processos'),
                api.get('/api/templates'),
                api.get('/api/multi-agente-real/estatisticas')
            ]);
            setStats({
                usuarios: usuarios.data.length || 0,
                processos: processos.data.length || 0,
                agentes: 368, // Total de agentes do sistema
                templates: templates.data.length || 0,
                multiagente_execucoes: multiagente.data.total_execucoes || 0
            });
        }
        catch (error) {
            console.error('Error fetching stats:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const modules = [
        {
            name: 'Usuários & Permissões',
            icon: Users,
            path: '/admin/usuarios',
            color: 'blue',
            endpoints: 9,
            description: 'Gerenciar usuários, roles e permissões'
        },
        {
            name: 'Processos Jurídicos',
            icon: FileText,
            path: '/admin/processos',
            color: 'green',
            endpoints: 20,
            description: 'Administrar processos e áreas jurídicas'
        },
        {
            name: 'Agentes IA',
            icon: Bot,
            path: '/admin/agents',
            color: 'purple',
            endpoints: 132,
            description: 'Configurar e otimizar agentes IA'
        },
        {
            name: 'Multi-Agente',
            icon: GitMerge,
            path: '/admin/multiagente',
            color: 'indigo',
            endpoints: 44,
            description: 'Orquestração de múltiplos agentes'
        },
        {
            name: 'Templates',
            icon: FileCode,
            path: '/admin/templates',
            color: 'pink',
            endpoints: 25,
            description: 'Gerenciar templates de documentos'
        },
        {
            name: 'CPFL/RGE Energia',
            icon: Zap,
            path: '/admin/cpfl',
            color: 'yellow',
            endpoints: 50,
            description: 'Setor de energia elétrica'
        },
        {
            name: 'Fintechs',
            icon: DollarSign,
            path: '/admin/fintechs',
            color: 'emerald',
            endpoints: 30,
            description: 'Análise financeira e compliance'
        },
        {
            name: 'Transcrição Áudio/Vídeo',
            icon: Mic,
            path: '/admin/transcricao',
            color: 'red',
            endpoints: 15,
            description: 'Transcrição automática'
        },
        {
            name: 'Zoom Integration',
            icon: Video,
            path: '/admin/zoom',
            color: 'cyan',
            endpoints: 16,
            description: 'Integração com Zoom'
        },
        {
            name: 'Mapas Mentais',
            icon: GitBranch,
            path: '/admin/mapas-mentais',
            color: 'orange',
            endpoints: 10,
            description: 'Editor de mapas mentais'
        },
        {
            name: 'Análise NLP',
            icon: Brain,
            path: '/admin/nlp',
            color: 'teal',
            endpoints: 10,
            description: 'Processamento de linguagem natural'
        },
        {
            name: 'Relatórios',
            icon: BarChart3,
            path: '/admin/relatorios',
            color: 'violet',
            endpoints: 20,
            description: 'Geração de relatórios'
        },
        {
            name: 'Fluxos & Workflows',
            icon: GitMerge,
            path: '/admin/fluxos',
            color: 'lime',
            endpoints: 15,
            description: 'Automação de processos'
        },
        {
            name: 'Audiências',
            icon: Calendar,
            path: '/admin/audiencias',
            color: 'amber',
            endpoints: 5,
            description: 'Gestão de audiências'
        },
        {
            name: 'Clientes',
            icon: Building2,
            path: '/admin/clientes',
            color: 'rose',
            endpoints: 5,
            description: 'Gerenciar clientes'
        },
        {
            name: 'Jurimetria',
            icon: Scale,
            path: '/admin/jurimetria',
            color: 'sky',
            endpoints: 12,
            description: 'Analytics e predições'
        },
        {
            name: 'APIs & Integrações',
            icon: Settings,
            path: '/admin/apis',
            color: 'gray',
            endpoints: 398,
            description: 'Configurar APIs externas'
        },
        {
            name: 'Database',
            icon: Settings,
            path: '/admin/database',
            color: 'slate',
            endpoints: 10,
            description: 'Gerenciar banco de dados'
        }
    ];
    const getColorClasses = (color) => {
        const colors = {
            blue: 'bg-blue-100 text-blue-600',
            green: 'bg-green-100 text-green-600',
            purple: 'bg-purple-100 text-purple-600',
            indigo: 'bg-indigo-100 text-indigo-600',
            pink: 'bg-pink-100 text-pink-600',
            yellow: 'bg-yellow-100 text-yellow-600',
            emerald: 'bg-emerald-100 text-emerald-600',
            red: 'bg-red-100 text-red-600',
            cyan: 'bg-cyan-100 text-cyan-600',
            orange: 'bg-orange-100 text-orange-600',
            teal: 'bg-teal-100 text-teal-600',
            violet: 'bg-violet-100 text-violet-600',
            lime: 'bg-lime-100 text-lime-600',
            amber: 'bg-amber-100 text-amber-600',
            rose: 'bg-rose-100 text-rose-600',
            sky: 'bg-sky-100 text-sky-600',
            gray: 'bg-gray-100 text-gray-600',
            slate: 'bg-slate-100 text-slate-600'
        };
        return colors[color] || colors.gray;
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Administra\u00E7\u00E3o de M\u00F3dulos", description: "Gerenciamento completo de todos os m\u00F3dulos do sistema" }), stats && (_jsxs("div", { className: "grid grid-cols-1 md:grid-cols-5 gap-6 mb-8", children: [_jsx(StatCard, { title: "Usu\u00E1rios", value: stats.usuarios.toString(), icon: Users }), _jsx(StatCard, { title: "Processos", value: stats.processos.toString(), icon: FileText }), _jsx(StatCard, { title: "Agentes IA", value: stats.agentes.toString(), icon: Bot }), _jsx(StatCard, { title: "Templates", value: stats.templates.toString(), icon: FileCode }), _jsx(StatCard, { title: "Multi-Agente", value: stats.multiagente_execucoes.toString(), icon: GitMerge })] })), _jsxs("div", { className: "mb-6", children: [_jsx("h2", { className: "text-xl font-semibold text-gray-900 mb-4", children: "M\u00F3dulos do Sistema" }), _jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4", children: modules.map((module) => {
                            const Icon = module.icon;
                            return (_jsxs(Link, { to: module.path, className: "bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow", children: [_jsxs("div", { className: "flex items-start justify-between mb-3", children: [_jsx("div", { className: `p-3 rounded-lg ${getColorClasses(module.color)}`, children: _jsx(Icon, { className: "w-6 h-6" }) }), _jsxs("span", { className: "text-xs font-medium text-gray-500", children: [module.endpoints, " endpoints"] })] }), _jsx("h3", { className: "font-semibold text-gray-900 mb-2", children: module.name }), _jsx("p", { className: "text-sm text-gray-600", children: module.description })] }, module.path));
                        }) })] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Estat\u00EDsticas R\u00E1pidas" }), _jsxs("div", { className: "grid grid-cols-3 gap-6 text-center", children: [_jsxs("div", { children: [_jsx("p", { className: "text-3xl font-bold text-blue-600", children: "1,164" }), _jsx("p", { className: "text-sm text-gray-600", children: "Total Endpoints" })] }), _jsxs("div", { children: [_jsx("p", { className: "text-3xl font-bold text-green-600", children: "18" }), _jsx("p", { className: "text-sm text-gray-600", children: "M\u00F3dulos Ativos" })] }), _jsxs("div", { children: [_jsx("p", { className: "text-3xl font-bold text-purple-600", children: "100%" }), _jsx("p", { className: "text-sm text-gray-600", children: "Funcionalidade" })] })] })] })] }));
}
