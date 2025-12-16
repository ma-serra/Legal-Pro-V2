import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Check, Zap, Building2, Rocket } from 'lucide-react';
import api from '../../lib/api';
export default function PricingPage() {
    const [plans, setPlans] = useState([]);
    const [billing, setBilling] = useState('monthly');
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchPlans();
    }, []);
    const fetchPlans = async () => {
        try {
            const response = await api.get('/api/saas/api/saas/plans');
            setPlans(response.data);
        }
        catch (error) {
            console.error('Error fetching plans:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const getPlanIcon = (slug) => {
        switch (slug) {
            case 'starter':
                return Zap;
            case 'professional':
                return Building2;
            case 'enterprise':
                return Rocket;
            default:
                return Zap;
        }
    };
    const getPlanColor = (slug) => {
        switch (slug) {
            case 'starter':
                return 'blue';
            case 'professional':
                return 'purple';
            case 'enterprise':
                return 'orange';
            default:
                return 'blue';
        }
    };
    if (loading) {
        return (_jsx("div", { className: "min-h-screen flex items-center justify-center", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }));
    }
    return (_jsxs("div", { className: "min-h-screen bg-gray-50", children: [_jsx("div", { className: "bg-white border-b border-gray-200", children: _jsx("div", { className: "container mx-auto px-6 py-4", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs(Link, { to: "/", className: "text-2xl font-bold text-gray-900", children: ["Legal", _jsx("span", { className: "text-blue-600", children: "Pro" })] }), _jsx(Link, { to: "/login", className: "text-gray-600 hover:text-gray-900", children: "Voltar ao Login" })] }) }) }), _jsxs("div", { className: "container mx-auto px-6 py-16 text-center", children: [_jsx("h1", { className: "text-5xl font-bold text-gray-900 mb-4", children: "Escolha o Plano Perfeito" }), _jsx("p", { className: "text-xl text-gray-600 mb-8", children: "Comece gr\u00E1tis. Escale conforme cresce. Cancele quando quiser." }), _jsxs("div", { className: "inline-flex items-center gap-4 bg-white rounded-lg p-2 shadow-sm", children: [_jsx("button", { onClick: () => setBilling('monthly'), className: `px-6 py-2 rounded-lg font-medium transition-colors ${billing === 'monthly'
                                    ? 'bg-blue-600 text-white'
                                    : 'text-gray-600 hover:text-gray-900'}`, children: "Mensal" }), _jsxs("button", { onClick: () => setBilling('yearly'), className: `px-6 py-2 rounded-lg font-medium transition-colors ${billing === 'yearly'
                                    ? 'bg-blue-600 text-white'
                                    : 'text-gray-600 hover:text-gray-900'}`, children: ["Anual", _jsx("span", { className: "ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full", children: "-17%" })] })] })] }), _jsx("div", { className: "container mx-auto px-6 pb-20", children: _jsx("div", { className: "grid md:grid-cols-3 gap-8 max-w-6xl mx-auto", children: plans.map((plan) => {
                        const Icon = getPlanIcon(plan.slug);
                        const color = getPlanColor(plan.slug);
                        const price = billing === 'monthly' ? plan.price_monthly : plan.price_yearly;
                        const isProfessional = plan.slug === 'professional';
                        return (_jsxs("div", { className: `bg-white rounded-2xl shadow-lg overflow-hidden ${isProfessional ? 'ring-2 ring-blue-600 relative' : ''}`, children: [isProfessional && (_jsx("div", { className: "absolute top-0 right-0 bg-blue-600 text-white text-xs font-bold px-4 py-1 rounded-bl-lg", children: "POPULAR" })), _jsxs("div", { className: "p-8", children: [_jsx("div", { className: `w-12 h-12 bg-${color}-100 rounded-lg flex items-center justify-center mb-4`, children: _jsx(Icon, { className: `w-6 h-6 text-${color}-600` }) }), _jsx("h3", { className: "text-2xl font-bold text-gray-900 mb-2", children: plan.name }), _jsx("p", { className: "text-gray-600 mb-6", children: plan.description }), _jsxs("div", { className: "mb-6", children: [_jsxs("div", { className: "flex items-baseline gap-2", children: [_jsxs("span", { className: "text-4xl font-bold text-gray-900", children: ["R$ ", price.toFixed(0)] }), _jsxs("span", { className: "text-gray-600", children: ["/", billing === 'monthly' ? 'mês' : 'ano'] })] }), billing === 'yearly' && price > 0 && (_jsxs("p", { className: "text-sm text-gray-500 mt-1", children: ["ou R$ ", (price / 12).toFixed(2), "/m\u00EAs"] }))] }), _jsx(Link, { to: `/signup?plan=${plan.slug}`, className: `block w-full text-center px-6 py-3 rounded-lg font-semibold mb-8 transition-colors ${isProfessional
                                                ? 'bg-blue-600 text-white hover:bg-blue-700'
                                                : 'bg-gray-100 text-gray-900 hover:bg-gray-200'}`, children: plan.slug === 'starter' ? 'Começar Trial Gratuito' : 'Começar Agora' }), _jsxs("div", { className: "space-y-4", children: [_jsx("div", { className: "text-sm font-semibold text-gray-900 mb-3", children: "Tudo incluso:" }), _jsx("ul", { className: "space-y-3", children: plan.features.map((feature, index) => (_jsxs("li", { className: "flex items-start gap-3", children: [_jsx(Check, { className: "w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" }), _jsx("span", { className: "text-sm text-gray-600", children: feature })] }, index))) }), _jsxs("div", { className: "pt-6 mt-6 border-t border-gray-200", children: [_jsx("div", { className: "text-xs font-semibold text-gray-500 uppercase mb-3", children: "Limites do Plano" }), _jsxs("div", { className: "space-y-2 text-sm text-gray-600", children: [_jsxs("div", { className: "flex justify-between", children: [_jsx("span", { children: "Usu\u00E1rios:" }), _jsx("span", { className: "font-medium", children: plan.limits.max_users === -1 ? 'Ilimitado' : plan.limits.max_users })] }), _jsxs("div", { className: "flex justify-between", children: [_jsx("span", { children: "Processos:" }), _jsx("span", { className: "font-medium", children: plan.limits.max_processes === -1 ? 'Ilimitado' : plan.limits.max_processes })] }), _jsxs("div", { className: "flex justify-between", children: [_jsx("span", { children: "An\u00E1lises/m\u00EAs:" }), _jsx("span", { className: "font-medium", children: plan.limits.max_analyses_month === -1 ? 'Ilimitado' : plan.limits.max_analyses_month })] }), _jsxs("div", { className: "flex justify-between", children: [_jsx("span", { children: "Agentes IA:" }), _jsx("span", { className: "font-medium", children: plan.limits.max_agents })] })] })] })] })] })] }, plan.id));
                    }) }) }), _jsx("div", { className: "bg-white py-20", children: _jsxs("div", { className: "container mx-auto px-6", children: [_jsx("h2", { className: "text-3xl font-bold text-center text-gray-900 mb-12", children: "Perguntas Frequentes" }), _jsxs("div", { className: "max-w-3xl mx-auto space-y-6", children: [_jsxs("div", { className: "border-b border-gray-200 pb-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-2", children: "Posso mudar de plano depois?" }), _jsx("p", { className: "text-gray-600", children: "Sim! Voc\u00EA pode fazer upgrade ou downgrade a qualquer momento. As mudan\u00E7as ser\u00E3o aplicadas imediatamente e ajustaremos o valor proporcional." })] }), _jsxs("div", { className: "border-b border-gray-200 pb-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-2", children: "Quais formas de pagamento voc\u00EAs aceitam?" }), _jsx("p", { className: "text-gray-600", children: "Aceitamos cart\u00E3o de cr\u00E9dito (Visa, Mastercard, Amex, Elo) e boleto banc\u00E1rio. Planos anuais tamb\u00E9m podem ser pagos via transfer\u00EAncia banc\u00E1ria." })] }), _jsxs("div", { className: "border-b border-gray-200 pb-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-2", children: "Como funciona o trial gratuito?" }), _jsx("p", { className: "text-gray-600", children: "O trial de 14 dias \u00E9 completamente gratuito e n\u00E3o requer cart\u00E3o de cr\u00E9dito. Voc\u00EA tem acesso total ao plano Starter durante esse per\u00EDodo." })] }), _jsxs("div", { children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-2", children: "H\u00E1 garantia de reembolso?" }), _jsx("p", { className: "text-gray-600", children: "Sim! Oferecemos garantia de reembolso de 30 dias. Se n\u00E3o ficar satisfeito, devolvemos 100% do seu investimento." })] })] })] }) }), _jsx("div", { className: "bg-blue-600 py-16", children: _jsxs("div", { className: "container mx-auto px-6 text-center", children: [_jsx("h2", { className: "text-3xl font-bold text-white mb-4", children: "Ainda tem d\u00FAvidas?" }), _jsx("p", { className: "text-xl text-blue-100 mb-8", children: "Nossa equipe est\u00E1 pronta para ajudar voc\u00EA a escolher o melhor plano" }), _jsx("a", { href: "mailto:contato@legalpro.com", className: "inline-block px-8 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-gray-100", children: "Falar com Vendas" })] }) })] }));
}
