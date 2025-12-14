import { Link } from 'react-router-dom'
import {
    Zap,
    Shield,
    Users,
    TrendingUp,
    Check,
    ArrowRight,
    Brain,
    FileText,
    BarChart3
} from 'lucide-react'

export default function LandingPage() {
    const features = [
        {
            icon: Brain,
            title: 'IA Jurídica Avançada',
            description: '368 agentes especializados em diferentes áreas do direito'
        },
        {
            icon: FileText,
            title: 'Análise Multi-Agente',
            description: 'Análises complexas com múltiplos agentes trabalhando em conjunto'
        },
        {
            icon: BarChart3,
            title: 'Analytics Preditivo',
            description: 'Previsões baseadas em machine learning e dados históricos'
        },
        {
            icon: Shield,
            title: 'Segurança Enterprise',
            description: 'Criptografia end-to-end e conformidade com LGPD'
        },
        {
            icon: Users,
            title: 'Colaboração em Equipe',
            description: 'Trabalhe com sua equipe jurídica em tempo real'
        },
        {
            icon: TrendingUp,
            title: 'ROI Comprovado',
            description: 'Reduza em até 70% o tempo gasto em análises jurídicas'
        }
    ]

    const testimonials = [
        {
            quote: 'O Legal Pro revolucionou nossa operação jurídica. Aumentamos nossa produtividade em 300%.',
            author: 'Dr. Carlos Silva',
            position: 'Sócio, Silva & Associados'
        },
        {
            quote: 'A análise multi-agente é simplesmente incrível. Nunca vi nada igual no mercado.',
            author: 'Dra. Ana Paula',
            position: 'Head Legal, TechCorp Brasil'
        }
    ]

    return (
        <div className="min-h-screen bg-white">
            {/* Navigation */}
            <nav className="border-b border-gray-200">
                <div className="container mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="text-2xl font-bold text-gray-900">
                            Legal<span className="text-blue-600">Pro</span>
                        </div>
                        <div className="hidden md:flex items-center gap-8">
                            <a href="#features" className="text-gray-600 hover:text-gray-900">Recursos</a>
                            <a href="#pricing" className="text-gray-600 hover:text-gray-900">Preços</a>
                            <Link to="/login" className="text-gray-600 hover:text-gray-900">Login</Link>
                            <Link
                                to="/signup"
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                            >
                                Começar Grátis
                            </Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="container mx-auto px-6 py-20">
                <div className="max-w-4xl mx-auto text-center">
                    <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
                        Inteligência Artificial para
                        <span className="text-blue-600"> Operações Jurídicas</span>
                    </h1>
                    <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
                        Automatize análises jurídicas complexas com 368 agentes de IA especializados.
                        Aumente a produtividade do seu time em até 10x.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <Link
                            to="/signup"
                            className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-lg font-semibold"
                        >
                            Começar Trial Gratuito
                            <ArrowRight className="w-5 h-5" />
                        </Link>
                        <Link
                            to="/demo"
                            className="inline-flex items-center justify-center gap-2 px-8 py-4 border-2 border-gray-300 text-gray-900 rounded-lg hover:border-gray-400 text-lg font-semibold"
                        >
                            Ver Demonstração
                        </Link>
                    </div>
                    <p className="text-sm text-gray-500 mt-4">
                        ✓ Teste grátis por 14 dias ✓ Sem cartão de crédito ✓ Cancele quando quiser
                    </p>
                </div>
            </section>

            {/* Features Grid */}
            <section id="features" className="bg-gray-50 py-20">
                <div className="container mx-auto px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold text-gray-900 mb-4">
                            Recursos Poderosos
                        </h2>
                        <p className="text-xl text-gray-600">
                            Tudo que você precisa para revolucionar sua operação jurídica
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {features.map((feature, index) => (
                            <div key={index} className="bg-white p-8 rounded-xl shadow-sm hover:shadow-md transition-shadow">
                                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                                    <feature.icon className="w-6 h-6 text-blue-600" />
                                </div>
                                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                    {feature.title}
                                </h3>
                                <p className="text-gray-600">
                                    {feature.description}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="py-20">
                <div className="container mx-auto px-6">
                    <div className="grid md:grid-cols-4 gap-8 text-center">
                        <div>
                            <div className="text-4xl font-bold text-blue-600 mb-2">368</div>
                            <div className="text-gray-600">Agentes de IA</div>
                        </div>
                        <div>
                            <div className="text-4xl font-bold text-blue-600 mb-2">1,200+</div>
                            <div className="text-gray-600">Escritórios Ativos</div>
                        </div>
                        <div>
                            <div className="text-4xl font-bold text-blue-600 mb-2">50M+</div>
                            <div className="text-gray-600">Análises Realizadas</div>
                        </div>
                        <div>
                            <div className="text-4xl font-bold text-blue-600 mb-2">98%</div>
                            <div className="text-gray-600">Satisfação</div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Testimonials */}
            <section className="bg-blue-600 py-20">
                <div className="container mx-auto px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold text-white mb-4">
                            Confiado por Líderes do Mercado
                        </h2>
                    </div>

                    <div className="grid md:grid-cols-2 gap-8">
                        {testimonials.map((testimonial, index) => (
                            <div key={index} className="bg-white p-8 rounded-xl">
                                <p className="text-lg text-gray-700 mb-6 italic">
                                    "{testimonial.quote}"
                                </p>
                                <div>
                                    <div className="font-semibold text-gray-900">{testimonial.author}</div>
                                    <div className="text-sm text-gray-600">{testimonial.position}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20">
                <div className="container mx-auto px-6">
                    <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl p-12 text-center">
                        <h2 className="text-4xl font-bold text-white mb-4">
                            Pronto para Transformar sua Operação Jurídica?
                        </h2>
                        <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
                            Junte-se a milhares de advogados que já estão usando IA para trabalhar de forma mais inteligente
                        </p>
                        <Link
                            to="/signup"
                            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-gray-100 text-lg font-semibold"
                        >
                            Começar Agora - É Grátis
                            <ArrowRight className="w-5 h-5" />
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 text-gray-400 py-12">
                <div className="container mx-auto px-6">
                    <div className="grid md:grid-cols-4 gap-8">
                        <div>
                            <div className="text-2xl font-bold text-white mb-4">
                                Legal<span className="text-blue-600">Pro</span>
                            </div>
                            <p className="text-sm">
                                IA Jurídica para advogados modernos
                            </p>
                        </div>
                        <div>
                            <h4 className="text-white font-semibold mb-4">Produto</h4>
                            <ul className="space-y-2 text-sm">
                                <li><a href="#" className="hover:text-white">Recursos</a></li>
                                <li><a href="#" className="hover:text-white">Preços</a></li>
                                <li><a href="#" className="hover:text-white">API</a></li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="text-white font-semibold mb-4">Empresa</h4>
                            <ul className="space-y-2 text-sm">
                                <li><a href="#" className="hover:text-white">Sobre</a></li>
                                <li><a href="#" className="hover:text-white">Blog</a></li>
                                <li><a href="#" className="hover:text-white">Carreiras</a></li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="text-white font-semibold mb-4">Legal</h4>
                            <ul className="space-y-2 text-sm">
                                <li><a href="#" className="hover:text-white">Privacidade</a></li>
                                <li><a href="#" className="hover:text-white">Termos</a></li>
                                <li><a href="#" className="hover:text-white">LGPD</a></li>
                            </ul>
                        </div>
                    </div>
                    <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm">
                        © 2025 LegalPro. Todos os direitos reservados.
                    </div>
                </div>
            </footer>
        </div>
    )
}
