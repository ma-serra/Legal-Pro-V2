import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Dashboard - Moderna e Corporativa
 * Stats reais, gráficos e métricas
 */
import DashboardEstatisticas from '../components/processos/DashboardEstatisticas';
export default function Dashboard() {
    return (_jsxs("div", { className: "p-6 max-w-[1600px] mx-auto space-y-6", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold mb-2 text-primary", children: "Dashboard Executivo" }), _jsx("p", { className: "text-muted-foreground", children: "Vis\u00E3o hol\u00EDstica e indicadores de performance jur\u00EDdica" })] }), _jsxs("div", { className: "text-right hidden sm:block", children: [_jsx("p", { className: "text-xs text-muted-foreground uppercase tracking-wider font-semibold", children: "Atualiza\u00E7\u00E3o em Tempo Real" }), _jsxs("div", { className: "flex items-center gap-2 justify-end", children: [_jsxs("span", { className: "relative flex h-3 w-3", children: [_jsx("span", { className: "animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" }), _jsx("span", { className: "relative inline-flex rounded-full h-3 w-3 bg-green-500" })] }), _jsxs("p", { className: "font-medium", children: [new Date().toLocaleDateString('pt-BR'), " \u2022 ", new Date().toLocaleTimeString('pt-BR')] })] })] })] }), _jsx(DashboardEstatisticas, {})] }));
}
