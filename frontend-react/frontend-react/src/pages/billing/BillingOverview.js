import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader, StatCard } from '../../components/ui/AdminComponents';
import { CreditCard, Calendar, Download, DollarSign } from 'lucide-react';
export default function BillingOverview() {
    // const { slug } = useParams()
    // Mock data
    const billingData = {
        currentPlan: 'Professional',
        monthlyPrice: 99,
        billingCycle: 'monthly',
        nextBilling: '2025-01-14',
        mrr: 99,
        invoices: 3
    };
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Billing & Assinaturas", description: "Gerenciar pagamentos e faturas" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8", children: [_jsx(StatCard, { title: "Plano Atual", value: billingData.currentPlan, icon: CreditCard }), _jsx(StatCard, { title: "Valor Mensal", value: `R$ ${billingData.monthlyPrice}`, icon: DollarSign }), _jsx(StatCard, { title: "Pr\u00F3ximo Billing", value: new Date(billingData.nextBilling).toLocaleDateString('pt-BR'), icon: Calendar }), _jsx(StatCard, { title: "Faturas", value: billingData.invoices.toString(), icon: Download })] }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Plano Atual" }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "flex justify-between", children: [_jsx("span", { className: "text-gray-600", children: "Plano" }), _jsx("span", { className: "font-medium", children: billingData.currentPlan })] }), _jsxs("div", { className: "flex justify-between", children: [_jsx("span", { className: "text-gray-600", children: "Ciclo" }), _jsx("span", { className: "font-medium", children: "Mensal" })] }), _jsxs("div", { className: "flex justify-between", children: [_jsx("span", { className: "text-gray-600", children: "Valor" }), _jsxs("span", { className: "font-medium", children: ["R$ ", billingData.monthlyPrice, "/m\u00EAs"] })] }), _jsx("button", { className: "w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700", children: "Fazer Upgrade" })] })] }), _jsxs("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "M\u00E9todo de Pagamento" }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "flex items-center gap-3 p-4 border border-gray-200 rounded-lg", children: [_jsx(CreditCard, { className: "w-8 h-8 text-gray-400" }), _jsxs("div", { className: "flex-1", children: [_jsx("div", { className: "font-medium", children: "\u2022\u2022\u2022\u2022 \u2022\u2022\u2022\u2022 \u2022\u2022\u2022\u2022 4242" }), _jsx("div", { className: "text-sm text-gray-500", children: "Expira 12/25" })] })] }), _jsx("button", { className: "w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50", children: "Atualizar Cart\u00E3o" })] })] })] })] }));
}
