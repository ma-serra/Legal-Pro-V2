import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Check, X, Zap, Building2, Rocket } from 'lucide-react'
import api from '../../lib/api'

interface Plan {
    id: number
    name: string
    slug: string
    description: string
    price_monthly: number
    price_yearly: number
    features: string[]
    limits: {
        max_users: number
        max_processes: number
        max_analyses_month: number
        max_agents: number
        max_storage_gb: number
    }
}

export default function PricingPage() {
    const [plans, setPlans] = useState<Plan[]>([])
    const [billing, setBilling] = useState<'monthly' | 'yearly'>('monthly')
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchPlans()
    }, [])

    const fetchPlans = async () => {
        try {
            const response = await api.get('/api/saas/api/saas/plans')
            setPlans(response.data)
        } catch (error) {
            console.error('Error fetching plans:', error)
        } finally {
            setLoading(false)
        }
    }

    const getPlanIcon = (slug: string) => {
        switch (slug) {
            case 'starter':
                return Zap
            case 'professional':
                return Building2
            case 'enterprise':
                return Rocket
            default:
                return Zap
        }
    }

    const getPlanColor = (slug: string) => {
        switch (slug) {
            case 'starter':
                return 'blue'
            case 'professional':
                return 'purple'
            case 'enterprise':
                return 'orange'
            default:
                return 'blue'
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white border-b border-gray-200">
                <div className="container mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <Link to="/" className="text-2xl font-bold text-gray-900">
                            Legal<span className="text-blue-600">Pro</span>
                        </Link>
                        <Link to="/login" className="text-gray-600 hover:text-gray-900">
                            Voltar ao Login
                        </Link>
                    </div>
                </div>
            </div>

            {/* Hero */}
            <div className="container mx-auto px-6 py-16 text-center">
                <h1 className="text-5xl font-bold text-gray-900 mb-4">
                    Escolha o Plano Perfeito
                </h1>
                <p className="text-xl text-gray-600 mb-8">
                    Comece grátis. Escale conforme cresce. Cancele quando quiser.
                </p>

                {/* Billing Toggle */}
                <div className="inline-flex items-center gap-4 bg-white rounded-lg p-2 shadow-sm">
                    <button
                        onClick={() => setBilling('monthly')}
                        className={`px-6 py-2 rounded-lg font-medium transition-colors ${billing === 'monthly'
                                ? 'bg-blue-600 text-white'
                                : 'text-gray-600 hover:text-gray-900'
                            }`}
                    >
                        Mensal
                    </button>
                    <button
                        onClick={() => setBilling('yearly')}
                        className={`px-6 py-2 rounded-lg font-medium transition-colors ${billing === 'yearly'
                                ? 'bg-blue-600 text-white'
                                : 'text-gray-600 hover:text-gray-900'
                            }`}
                    >
                        Anual
                        <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                            -17%
                        </span>
                    </button>
                </div>
            </div>

            {/* Pricing Cards */}
            <div className="container mx-auto px-6 pb-20">
                <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                    {plans.map((plan) => {
                        const Icon = getPlanIcon(plan.slug)
                        const color = getPlanColor(plan.slug)
                        const price = billing === 'monthly' ? plan.price_monthly : plan.price_yearly
                        const isProfessional = plan.slug === 'professional'

                        return (
                            <div
                                key={plan.id}
                                className={`bg-white rounded-2xl shadow-lg overflow-hidden ${isProfessional ? 'ring-2 ring-blue-600 relative' : ''
                                    }`}
                            >
                                {isProfessional && (
                                    <div className="absolute top-0 right-0 bg-blue-600 text-white text-xs font-bold px-4 py-1 rounded-bl-lg">
                                        POPULAR
                                    </div>
                                )}

                                <div className="p-8">
                                    {/* Icon */}
                                    <div className={`w-12 h-12 bg-${color}-100 rounded-lg flex items-center justify-center mb-4`}>
                                        <Icon className={`w-6 h-6 text-${color}-600`} />
                                    </div>

                                    {/* Plan Name */}
                                    <h3 className="text-2xl font-bold text-gray-900 mb-2">
                                        {plan.name}
                                    </h3>
                                    <p className="text-gray-600 mb-6">
                                        {plan.description}
                                    </p>

                                    {/* Price */}
                                    <div className="mb-6">
                                        <div className="flex items-baseline gap-2">
                                            <span className="text-4xl font-bold text-gray-900">
                                                R$ {price.toFixed(0)}
                                            </span>
                                            <span className="text-gray-600">
                                                /{billing === 'monthly' ? 'mês' : 'ano'}
                                            </span>
                                        </div>
                                        {billing === 'yearly' && price > 0 && (
                                            <p className="text-sm text-gray-500 mt-1">
                                                ou R$ {(price / 12).toFixed(2)}/mês
                                            </p>
                                        )}
                                    </div>

                                    {/* CTA Button */}
                                    <Link
                                        to={`/signup?plan=${plan.slug}`}
                                        className={`block w-full text-center px-6 py-3 rounded-lg font-semibold mb-8 transition-colors ${isProfessional
                                                ? 'bg-blue-600 text-white hover:bg-blue-700'
                                                : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                                            }`}
                                    >
                                        {plan.slug === 'starter' ? 'Começar Trial Gratuito' : 'Começar Agora'}
                                    </Link>

                                    {/* Features */}
                                    <div className="space-y-4">
                                        <div className="text-sm font-semibold text-gray-900 mb-3">
                                            Tudo incluso:
                                        </div>
                                        <ul className="space-y-3">
                                            {plan.features.map((feature, index) => (
                                                <li key={index} className="flex items-start gap-3">
                                                    <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                                                    <span className="text-sm text-gray-600">{feature}</span>
                                                </li>
                                            ))}
                                        </ul>

                                        {/* Limits */}
                                        <div className="pt-6 mt-6 border-t border-gray-200">
                                            <div className="text-xs font-semibold text-gray-500 uppercase mb-3">
                                                Limites do Plano
                                            </div>
                                            <div className="space-y-2 text-sm text-gray-600">
                                                <div className="flex justify-between">
                                                    <span>Usuários:</span>
                                                    <span className="font-medium">
                                                        {plan.limits.max_users === -1 ? 'Ilimitado' : plan.limits.max_users}
                                                    </span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>Processos:</span>
                                                    <span className="font-medium">
                                                        {plan.limits.max_processes === -1 ? 'Ilimitado' : plan.limits.max_processes}
                                                    </span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>Análises/mês:</span>
                                                    <span className="font-medium">
                                                        {plan.limits.max_analyses_month === -1 ? 'Ilimitado' : plan.limits.max_analyses_month}
                                                    </span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>Agentes IA:</span>
                                                    <span className="font-medium">{plan.limits.max_agents}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )
                    })}
                </div>
            </div>

            {/* FAQ Section */}
            <div className="bg-white py-20">
                <div className="container mx-auto px-6">
                    <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
                        Perguntas Frequentes
                    </h2>
                    <div className="max-w-3xl mx-auto space-y-6">
                        <div className="border-b border-gray-200 pb-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                Posso mudar de plano depois?
                            </h3>
                            <p className="text-gray-600">
                                Sim! Você pode fazer upgrade ou downgrade a qualquer momento. As mudanças serão aplicadas imediatamente e ajustaremos o valor proporcional.
                            </p>
                        </div>
                        <div className="border-b border-gray-200 pb-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                Quais formas de pagamento vocês aceitam?
                            </h3>
                            <p className="text-gray-600">
                                Aceitamos cartão de crédito (Visa, Mastercard, Amex, Elo) e boleto bancário. Planos anuais também podem ser pagos via transferência bancária.
                            </p>
                        </div>
                        <div className="border-b border-gray-200 pb-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                Como funciona o trial gratuito?
                            </h3>
                            <p className="text-gray-600">
                                O trial de 14 dias é completamente gratuito e não requer cartão de crédito. Você tem acesso total ao plano Starter durante esse período.
                            </p>
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                Há garantia de reembolso?
                            </h3>
                            <p className="text-gray-600">
                                Sim! Oferecemos garantia de reembolso de 30 dias. Se não ficar satisfeito, devolvemos 100% do seu investimento.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* CTA */}
            <div className="bg-blue-600 py-16">
                <div className="container mx-auto px-6 text-center">
                    <h2 className="text-3xl font-bold text-white mb-4">
                        Ainda tem dúvidas?
                    </h2>
                    <p className="text-xl text-blue-100 mb-8">
                        Nossa equipe está pronta para ajudar você a escolher o melhor plano
                    </p>
                    <a
                        href="mailto:contato@legalpro.com"
                        className="inline-block px-8 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-gray-100"
                    >
                        Falar com Vendas
                    </a>
                </div>
            </div>
        </div>
    )
}
