import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { Calculator, TrendingUp, Scale, BookOpen, AlertTriangle, BarChart3, FileText, ArrowRight, Percent, Clock } from 'lucide-react';
import api from '../../lib/api';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
export default function CalculosTributariosPage() {
    const [activeTab, setActiveTab] = useState('dashboard');
    return (_jsxs("div", { className: "p-6 max-w-[1600px] mx-auto space-y-6", children: [_jsx("div", { className: "flex items-center justify-between mb-6", children: _jsxs("div", { children: [_jsxs("h1", { className: "text-3xl font-bold flex items-center gap-3", children: [_jsx(Calculator, { className: "w-8 h-8 text-primary" }), "C\u00E1lculos e Intelig\u00EAncia Tribut\u00E1ria"] }), _jsx("p", { className: "text-muted-foreground mt-1", children: "Simuladores, Recupera\u00E7\u00E3o de Cr\u00E9ditos e Dados Estrat\u00E9gicos" })] }) }), _jsx("div", { className: "flex border-b border-border mb-6 overflow-x-auto", children: [
                    { id: 'dashboard', label: 'Panorama Geral', icon: BarChart3 },
                    { id: 'simulador', label: 'Simulador de Regime', icon: Scale },
                    { id: 'recuperacao', label: 'Recuperação de Créditos', icon: TrendingUp },
                    { id: 'legislacao', label: 'Dados Legislativos', icon: BookOpen },
                ].map((tab) => (_jsxs("button", { onClick: () => setActiveTab(tab.id), className: `flex items-center gap-2 px-6 py-3 border-b-2 transition-colors whitespace-nowrap ${activeTab === tab.id
                        ? 'border-primary text-primary font-medium'
                        : 'border-transparent text-muted-foreground hover:text-foreground'}`, children: [_jsx(tab.icon, { className: "w-4 h-4" }), tab.label] }, tab.id))) }), _jsxs("div", { className: "min-h-[600px]", children: [activeTab === 'dashboard' && _jsx(DashboardTributario, {}), activeTab === 'simulador' && _jsx(SimuladorRegime, {}), activeTab === 'recuperacao' && _jsx(RecuperacaoCredito, {}), activeTab === 'legislacao' && _jsx(LegislacaoDados, {})] })] }));
}
// === SUB-COMPONENTS ===
function DashboardTributario() {
    return (_jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "grid grid-cols-1 md:grid-cols-4 gap-4", children: [_jsx(CardResumo, { title: "Carga Tribut\u00E1ria M\u00E9dia", value: "33.8%", desc: "PIB Brasil (Fonte: Tesouro)", icon: PercentIcon, color: "blue" }), _jsx(CardResumo, { title: "Normas Ativas", value: "38.540+", desc: "Federais (Fonte: IBPT)", icon: FileText, color: "amber" }), _jsx(CardResumo, { title: "SELIC Atual", value: "11.25%", desc: "Definida pelo COPOM", icon: TrendingUp, color: "green" }), _jsx(CardResumo, { title: "Contencioso", value: "R$ 5.4 mi", desc: "Valor em Discuss\u00E3o (CNJ)", icon: Scale, color: "red" })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-6", children: [_jsxs("div", { className: "bg-card border border-border rounded-xl p-6", children: [_jsxs("h3", { className: "font-bold mb-4 flex items-center gap-2", children: [_jsx(AlertTriangle, { className: "w-5 h-5 text-yellow-500" }), "Alertas de Compliance"] }), _jsxs("ul", { className: "space-y-3", children: [_jsxs("li", { className: "flex items-start gap-3 p-3 bg-red-900/10 rounded-lg border border-red-900/20", children: [_jsx(AlertTriangle, { className: "w-5 h-5 text-red-500 mt-0.5" }), _jsxs("div", { children: [_jsx("h4", { className: "font-semibold text-red-400", children: "Reforma Tribut\u00E1ria (PEC 45/2019)" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Per\u00EDodo de transi\u00E7\u00E3o iniciando em 2026. Necess\u00E1rio revisar cadastros de produtos (NCM)." })] })] }), _jsxs("li", { className: "flex items-start gap-3 p-3 bg-yellow-900/10 rounded-lg border border-yellow-900/20", children: [_jsx(ClockIcon, { className: "w-5 h-5 text-yellow-500 mt-0.5" }), _jsxs("div", { children: [_jsx("h4", { className: "font-semibold text-yellow-400", children: "Exclus\u00E3o ICMS Base PIS/COFINS" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Prazo prescricional de 5 anos para recupera\u00E7\u00E3o administrativa." })] })] })] })] }), _jsxs("div", { className: "bg-card border border-border rounded-xl p-6", children: [_jsxs("h3", { className: "font-bold mb-4 flex items-center gap-2", children: [_jsx(TrendingUp, { className: "w-5 h-5 text-primary" }), "Oportunidades"] }), _jsxs("ul", { className: "space-y-3", children: [_jsxs("li", { className: "flex items-center justify-between p-3 bg-card border border-border rounded-lg hover:border-primary transition-colors cursor-pointer", children: [_jsx("span", { className: "font-medium", children: "Simulador Lucro Real vs Presumido" }), _jsx(ArrowRight, { className: "w-4 h-4 text-primary" })] }), _jsxs("li", { className: "flex items-center justify-between p-3 bg-card border border-border rounded-lg hover:border-primary transition-colors cursor-pointer", children: [_jsx("span", { className: "font-medium", children: "C\u00E1lculo Tese do S\u00E9culo (ICMS na Base PIS/COFINS)" }), _jsx(ArrowRight, { className: "w-4 h-4 text-primary" })] })] })] })] })] }));
}
function SimuladorRegime() {
    const [receita, setReceita] = useState(300000); // 100k/mês
    const [folha, setFolha] = useState(84000); // 28k/mês (28%)
    const [atividade, setAtividade] = useState('servicos');
    const [resultado, setResultado] = useState(null);
    const [loading, setLoading] = useState(false);
    const calcular = async () => {
        setLoading(true);
        try {
            // Paralelo: Simples e Presumido
            const [resSimples, resPresumido] = await Promise.all([
                api.post('/api/calculos-tributarios/simular/simples', {
                    receita_mensal: receita / 3, // Estima mensal
                    receita_bruta_12_meses: receita * 4, // Estima anual (4 tri)
                    folha_12_meses: folha * 4,
                    anexo: 'ANEXO_III' // Simplificado
                }),
                api.post('/api/calculos-tributarios/simular/presumido', {
                    receita_trimestral: receita,
                    atividade,
                    folha_pagamento: folha
                })
            ]);
            setResultado({
                simples: resSimples.data,
                presumido: resPresumido.data
            });
        }
        catch (err) {
            console.error(err);
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-3 gap-6", children: [_jsxs("div", { className: "lg:col-span-1 bg-card border border-border rounded-xl p-6 space-y-4", children: [_jsx("h3", { className: "font-bold mb-4", children: "Par\u00E2metros de Simula\u00E7\u00E3o (Trimestral)" }), _jsxs("div", { className: "space-y-2", children: [_jsx("label", { className: "text-sm font-medium", children: "Receita Trimestral (R$)" }), _jsx("input", { type: "number", value: receita, onChange: (e) => setReceita(Number(e.target.value)), className: "w-full p-2 bg-background border border-border rounded-md" })] }), _jsxs("div", { className: "space-y-2", children: [_jsx("label", { className: "text-sm font-medium", children: "Folha de Pagamento Trimestral (R$)" }), _jsx("input", { type: "number", value: folha, onChange: (e) => setFolha(Number(e.target.value)), className: "w-full p-2 bg-background border border-border rounded-md" })] }), _jsxs("div", { className: "space-y-2", children: [_jsx("label", { className: "text-sm font-medium", children: "Atividade Principal" }), _jsxs("select", { value: atividade, onChange: (e) => setAtividade(e.target.value), className: "w-full p-2 bg-background border border-border rounded-md", children: [_jsx("option", { value: "servicos", children: "Servi\u00E7os em Geral (32%)" }), _jsx("option", { value: "comercio", children: "Com\u00E9rcio (8%)" }), _jsx("option", { value: "industria", children: "Ind\u00FAstria (8%)" })] })] }), _jsx("button", { onClick: calcular, disabled: loading, className: "w-full py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 mt-4", children: loading ? 'Calculando...' : 'Simular Comparativo' })] }), _jsxs("div", { className: "lg:col-span-2 bg-card border border-border rounded-xl p-6", children: [_jsx("h3", { className: "font-bold mb-4", children: "Resultados Comparativos" }), resultado ? (_jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { className: `p-4 rounded-lg border-2 ${resultado.simples.total < resultado.presumido.total ? 'border-green-500 bg-green-500/10' : 'border-border'}`, children: [_jsx("h4", { className: "font-bold", children: "Simples Nacional" }), _jsxs("p", { className: "text-2xl font-bold mt-2", children: ["R$ ", resultado.simples.total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })] }), _jsxs("p", { className: "text-sm text-muted-foreground mt-1", children: ["Al\u00EDquota Efetiva: ", resultado.simples.aliquota_efetiva.toFixed(2), "%"] }), _jsx("p", { className: "text-xs text-muted-foreground", children: resultado.simples.fator_r_status !== 'N/A' ? `Fator R: ${resultado.simples.fator_r_status}` : '' })] }), _jsxs("div", { className: `p-4 rounded-lg border-2 ${resultado.presumido.total < resultado.simples.total ? 'border-green-500 bg-green-500/10' : 'border-border'}`, children: [_jsx("h4", { className: "font-bold", children: "Lucro Presumido" }), _jsxs("p", { className: "text-2xl font-bold mt-2", children: ["R$ ", resultado.presumido.total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })] }), _jsxs("p", { className: "text-sm text-muted-foreground mt-1", children: ["Al\u00EDquota Efetiva: ", resultado.presumido.aliquota_efetiva.toFixed(2), "%"] })] })] }), _jsx("div", { className: "h-64", children: _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(BarChart, { data: [
                                            { name: 'Simples', valor: resultado.simples.total },
                                            { name: 'L. Presumido', valor: resultado.presumido.total },
                                        ], layout: "vertical", children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", stroke: "#333" }), _jsx(XAxis, { type: "number", stroke: "#888" }), _jsx(YAxis, { dataKey: "name", type: "category", stroke: "#888", width: 100 }), _jsx(Tooltip, { contentStyle: { backgroundColor: '#1f1f1f' }, cursor: { fill: 'transparent' } }), _jsx(Bar, { dataKey: "valor", fill: "#8884d8", barSize: 40 })] }) }) })] })) : (_jsx("div", { className: "h-full flex items-center justify-center text-muted-foreground", children: "Preencha os dados e clique em Simular" }))] })] }));
}
function RecuperacaoCredito() {
    const [faturamento, setFaturamento] = useState(1000000);
    const [icms, setIcms] = useState(18);
    const [resultado, setResultado] = useState(null);
    const calcular = async () => {
        try {
            const res = await api.post('/api/calculos-tributarios/simular/tese-icms', {
                faturamento_mensal: faturamento,
                aliquota_icms: icms,
                meses: 60
            });
            setResultado(res.data);
        }
        catch (err) {
            console.error(err);
        }
    };
    return (_jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [_jsx("div", { className: "space-y-6", children: _jsxs("div", { className: "bg-card border border-border rounded-xl p-6", children: [_jsx("h3", { className: "font-bold mb-4", children: "Calculadora \"Tese do S\u00E9culo\"" }), _jsx("p", { className: "text-sm text-muted-foreground mb-4", children: "Estimativa de recupera\u00E7\u00E3o da exclus\u00E3o do ICMS da base de c\u00E1lculo do PIS/COFINS (Tema 69 STF)." }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsx("label", { className: "text-sm font-medium", children: "Faturamento M\u00E9dio Mensal (R$)" }), _jsx("input", { type: "number", value: faturamento, onChange: e => setFaturamento(Number(e.target.value)), className: "w-full p-2 bg-background border border-border rounded-md" })] }), _jsxs("div", { children: [_jsx("label", { className: "text-sm font-medium", children: "Al\u00EDquota M\u00E9dia ICMS (%)" }), _jsx("input", { type: "number", value: icms, onChange: e => setIcms(Number(e.target.value)), className: "w-full p-2 bg-background border border-border rounded-md" })] }), _jsx("button", { onClick: calcular, className: "w-full py-2 bg-primary text-white rounded-md mt-2", children: "Calcular Potencial" })] })] }) }), _jsx("div", { className: "bg-card border border-border rounded-xl p-6 flex flex-col justify-center", children: resultado ? (_jsxs("div", { className: "text-center space-y-6", children: [_jsxs("div", { children: [_jsx("h4", { className: "text-muted-foreground font-medium uppercase tracking-wider text-xs", children: "Potencial Total Recuper\u00E1vel (5 Anos)" }), _jsxs("p", { className: "text-4xl font-bold text-green-400 mt-2", children: ["R$ ", resultado.total_final_estimado.toLocaleString('pt-BR', { minimumFractionDigits: 2 })] }), _jsx("p", { className: "text-sm text-muted-foreground mt-1", children: "Inclui Principal + Atualiza\u00E7\u00E3o SELIC Estimada (~40%)" })] }), _jsxs("div", { className: "grid grid-cols-2 gap-4 text-left border-t border-border pt-4", children: [_jsxs("div", { children: [_jsx("p", { className: "text-xs text-muted-foreground", children: "Economia Mensal" }), _jsxs("p", { className: "font-bold", children: ["R$ ", resultado.economia_mensal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })] })] }), _jsxs("div", { children: [_jsx("p", { className: "text-xs text-muted-foreground", children: "Valor Principal (5 Anos)" }), _jsxs("p", { className: "font-bold", children: ["R$ ", resultado.total_periodo_principal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })] })] })] })] })) : (_jsxs("div", { className: "text-center text-muted-foreground", children: [_jsx(Calculator, { className: "w-12 h-12 mx-auto mb-2 opacity-20" }), _jsx("p", { children: "Simule o potencial de recupera\u00E7\u00E3o tribut\u00E1ria" })] })) })] }));
}
function LegislacaoDados() {
    return (_jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6", children: [_jsx(CardLink, { title: "Constitui\u00E7\u00E3o Federal", desc: "Arts. 145 a 162 - Sistema Tribut\u00E1rio Nacional", href: "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm" }), _jsx(CardLink, { title: "C\u00F3digo Tribut\u00E1rio Nacional", desc: "Lei 5.172/1966", href: "https://www.planalto.gov.br/ccivil_03/leis/l5172compilado.htm" }), _jsx(CardLink, { title: "Regulamento do Imposto de Renda", desc: "Decreto 9.580/2018", href: "http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/decreto/d9580.htm" }), _jsx(CardLink, { title: "Simples Nacional", desc: "Lei Complementar 123/2006", href: "http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp123.htm" }), _jsx(CardLink, { title: "Reforma Tribut\u00E1ria", desc: "PEC 45/2019 e regulamenta\u00E7\u00F5es", href: "https://www.camara.leg.br/propostas-legislativas/2196833" })] }));
}
function CardLink({ title, desc, href }) {
    return (_jsxs("a", { href: href, target: "_blank", rel: "noopener noreferrer", className: "block p-4 border border-border rounded-xl hover:border-primary transition-colors bg-card", children: [_jsxs("div", { className: "flex items-center justify-between mb-2", children: [_jsx(BookOpen, { className: "w-5 h-5 text-primary" }), _jsx(ArrowRight, { className: "w-4 h-4 text-muted-foreground" })] }), _jsx("h3", { className: "font-bold text-lg", children: title }), _jsx("p", { className: "text-sm text-muted-foreground mt-1", children: desc })] }));
}
function CardResumo({ title, value, desc, icon: Icon, color }) {
    const colors = {
        blue: 'text-blue-400 bg-blue-400/10 border-blue-400/20',
        green: 'text-green-400 bg-green-400/10 border-green-400/20',
        red: 'text-red-400 bg-red-400/10 border-red-400/20',
        amber: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
    };
    return (_jsxs("div", { className: `p-4 rounded-xl border ${colors[color] || colors.blue}`, children: [_jsx("div", { className: "flex items-center justify-between mb-2", children: _jsx(Icon, { className: "w-5 h-5 opacity-80" }) }), _jsx("p", { className: "text-2xl font-bold", children: value }), _jsx("p", { className: "text-xs opacity-70 mt-1", children: title }), _jsx("p", { className: "text-[10px] opacity-50", children: desc })] }));
}
const PercentIcon = (props) => _jsx(Percent, { ...props });
const ClockIcon = (props) => _jsx(Clock, { ...props });
