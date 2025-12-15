import { useParams } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader, StatCard } from '../../components/ui/AdminComponents'
import { CreditCard, Calendar, Download, DollarSign } from 'lucide-react'

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
    }

    return (
        <AdminLayout>
            <PageHeader
                title="Billing & Assinaturas"
                description="Gerenciar pagamentos e faturas"
            />

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard
                    title="Plano Atual"
                    value={billingData.currentPlan}
                    icon={CreditCard}
                />
                <StatCard
                    title="Valor Mensal"
                    value={`R$ ${billingData.monthlyPrice}`}
                    icon={DollarSign}
                />
                <StatCard
                    title="Próximo Billing"
                    value={new Date(billingData.nextBilling).toLocaleDateString('pt-BR')}
                    icon={Calendar}
                />
                <StatCard
                    title="Faturas"
                    value={billingData.invoices.toString()}
                    icon={Download}
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Current Plan */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Plano Atual</h3>
                    <div className="space-y-4">
                        <div className="flex justify-between">
                            <span className="text-gray-600">Plano</span>
                            <span className="font-medium">{billingData.currentPlan}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-600">Ciclo</span>
                            <span className="font-medium">Mensal</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-600">Valor</span>
                            <span className="font-medium">R$ {billingData.monthlyPrice}/mês</span>
                        </div>
                        <button className="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                            Fazer Upgrade
                        </button>
                    </div>
                </div>

                {/* Payment Method */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Método de Pagamento</h3>
                    <div className="space-y-4">
                        <div className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg">
                            <CreditCard className="w-8 h-8 text-gray-400" />
                            <div className="flex-1">
                                <div className="font-medium">•••• •••• •••• 4242</div>
                                <div className="text-sm text-gray-500">Expira 12/25</div>
                            </div>
                        </div>
                        <button className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                            Atualizar Cartão
                        </button>
                    </div>
                </div>
            </div>
        </AdminLayout>
    )
}
