/**
 * LandingPage - Premium Corporativa
 * Inspirada em Rosenthal Advogados
 * Design clean, profissional e institucional
 */
import { Link } from 'react-router-dom';
import {
    Scale, CheckCircle, Users, Award, TrendingUp,
    FileText, Shield, Briefcase, ArrowRight, Star
} from 'lucide-react';

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-background">
            {/* Hero Section */}
            <section className="relative bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white overflow-hidden">
                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDE0YzMuNTQgMCA2LTIuNDYgNi02cy0yLjQ2LTYtNi02LTYgMi40Ni02IDYgMi40NiA2IDYgNnptMCAxMmMzLjU0IDAgNi0yLjQ2IDYtNnMtMi40Ni02LTYtNi02IDIuNDYtNiA2IDIuNDYgNiA2IDZ6bS0yNCAwYzMuNTQgMCA2LTIuNDYgNi02cy0yLjQ2LTYtNi02LTYgMi40Ni02IDYgMi40NiA2IDYgNnoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-30"></div>

                <div className="container mx-auto px-6 py-24 relative z-10">
                    <div className="max-w-4xl mx-auto text-center">
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full mb-6">
                            <Scale className="w-4 h-4" />
                            <span className="text-sm font-medium">Excelência Jurídica</span>
                        </div>

                        <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
                            Gestão Inteligente de
                            <span className="block bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                                Processos Jurídicos
                            </span>
                        </h1>

                        <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto leading-relaxed">
                            Plataforma completa para escritórios de advocacia que buscam eficiência,
                            organização e resultados excepcionais
                        </p>

                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <Link
                                to="/signup"
                                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-all hover:scale-105 shadow-lg shadow-blue-600/50"
                            >
                                Começar Gratuitamente
                                <ArrowRight className="w-5 h-5" />
                            </Link>

                            <Link
                                to="/pricing"
                                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white/10 hover:bg-white/20 text-white border border-white/20 rounded-lg font-semibold backdrop-blur-sm transition-all"
                            >
                                Conhecer Planos
                            </Link>
                        </div>

                        <div className="mt-12 flex items-center justify-center gap-8 text-sm">
                            <div className="flex items-center gap-2">
                                <CheckCircle className="w-5 h-5 text-green-400" />
                                <span>Teste grátis 30 dias</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Shield className="w-5 h-5 text-blue-400" />
                                <span>Segurança garantida</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="py-20 bg-slate-50 dark:bg-slate-900/50">
                <div className="container mx-auto px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold mb-4">Ferramentas Completas</h2>
                        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                            Tudo que seu escritório precisa em uma única plataforma moderna e intuitiva
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {[
                            {
                                icon: FileText,
                                title: 'Gestão de Processos',
                                description: 'Controle completo de processos tributários, trabalhistas e cíveis com dashboards inteligentes'
                            },
                            {
                                icon: TrendingUp,
                                title: 'Atualização Monetária',
                                description: 'Integração automática com BACEN para cálculos precisos de SELIC, IPCA e demais índices'
                            },
                            {
                                icon: Users,
                                title: 'Assistentes Jurídicos IA',
                                description: 'Inteligência artificial para pesquisa jurídica, análise de documentos e elaboração de peças'
                            },
                            {
                                icon: Briefcase,
                                title: 'Teses Jurídicas',
                                description: 'Biblioteca organizada de teses tributárias com probabilidades de sucesso e jurisprudência'
                            },
                            {
                                icon: Award,
                                title: 'Análises Avançadas',
                                description: 'Relatórios detalhados, estatísticas em tempo real e insights estratégicos'
                            },
                            {
                                icon: Shield,
                                title: 'Segurança Total',
                                description: 'Criptografia de ponta a ponta, backup automático e conformidade com LGPD'
                            }
                        ].map((feature, idx) => (
                            <div
                                key={idx}
                                className="bg-white dark:bg-card border border-border rounded-2xl p-8 hover:shadow-xl transition-all hover:-translate-y-1"
                            >
                                <div className="p-3 bg-blue-500/10 rounded-xl w-fit mb-4">
                                    <feature.icon className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                                </div>
                                <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                                <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="py-20 bg-gradient-to-br from-blue-600 to-cyan-600 text-white">
                <div className="container mx-auto px-6">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                        {[
                            { value: '15+', label: 'Anos de Experiência' },
                            { value: '500+', label: 'Escritórios Atendidos' },
                            { value: '50k+', label: 'Processos Gerenciados' },
                            { value: '98%', label: 'Satisfação Cliente' }
                        ].map((stat, idx) => (
                            <div key={idx} className="text-center">
                                <div className="text-4xl md:text-5xl font-bold mb-2">{stat.value}</div>
                                <div className="text-blue-100">{stat.label}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* About Section - Inspirado em Rosenthal */}
            <section className="py-20">
                <div className="container mx-auto px-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                        <div>
                            <h2 className="text-4xl font-bold mb-6">
                                Excelência e Compromisso com Resultados
                            </h2>
                            <p className="text-lg text-muted-foreground mb-6 leading-relaxed">
                                O Legal Pro nasceu da necessidade de modernizar a advocacia brasileira,
                                combinando expertise jurídica com tecnologia de ponta.
                            </p>
                            <p className="text-lg text-muted-foreground mb-6 leading-relaxed">
                                Nossa plataforma é desenvolvida por advogados, para advogados,
                                garantindo que cada funcionalidade atenda às reais demandas do dia a dia jurídico.
                            </p>

                            <div className="space-y-4">
                                {[
                                    'Ferramenta criada por profissionais do Direito',
                                    'Suporte especializado 24/7',
                                    'Atualizações constantes com novas funcionalidades',
                                    'Treinamento completo para toda equipe'
                                ].map((item, idx) => (
                                    <div key={idx} className="flex items-center gap-3">
                                        <div className="p-1 bg-green-500/20 rounded-full">
                                            <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                                        </div>
                                        <span className="text-muted-foreground">{item}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="relative">
                            <div className="aspect-square bg-gradient-to-br from-blue-600 to-cyan-600 rounded-3xl overflow-hidden shadow-2xl">
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <Scale className="w-32 h-32 text-white/20" />
                                </div>
                                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-8">
                                    <div className="flex items-center gap-3">
                                        <Star className="w-6 h-6 text-yellow-400 fill-yellow-400" />
                                        <Star className="w-6 h-6 text-yellow-400 fill-yellow-400" />
                                        <Star className="w-6 h-6 text-yellow-400 fill-yellow-400" />
                                        <Star className="w-6 h-6 text-yellow-400 fill-yellow-400" />
                                        <Star className="w-6 h-6 text-yellow-400 fill-yellow-400" />
                                    </div>
                                    <p className="text-white mt-2 font-semibold">
                                        Avaliação 5.0 - Escritórios Parceiros
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20 bg-slate-900 text-white">
                <div className="container mx-auto px-6 text-center">
                    <h2 className="text-4xl font-bold mb-6">
                        Pronto para Transformar seu Escritório?
                    </h2>
                    <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
                        Junte-se a centenas de escritórios que já modernizaram sua gestão jurídica
                    </p>

                    <Link
                        to="/signup"
                        className="inline-flex items-center gap-2 px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-all hover:scale-105 shadow-lg shadow-blue-600/50 text-lg"
                    >
                        Iniciar Teste Gratuito
                        <ArrowRight className="w-5 h-5" />
                    </Link>

                    <p className="text-sm text-slate-400 mt-6">
                        Não precisa cartão de crédito • Cancele quando quiser
                    </p>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-slate-950 text-slate-400 py-12">
                <div className="container mx-auto px-6">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                        <div>
                            <div className="flex items-center gap-2 mb-4">
                                <Scale className="w-6 h-6 text-blue-400" />
                                <span className="text-white font-bold text-lg">Legal Pro</span>
                            </div>
                            <p className="text-sm">
                                Plataforma completa de gestão jurídica para escritórios modernos
                            </p>
                        </div>

                        <div>
                            <h4 className="text-white font-semibold mb-4">Produto</h4>
                            <ul className="space-y-2 text-sm">
                                <li><Link to="/pricing" className="hover:text-white transition-colors">Planos</Link></li>
                                <li><Link to="/signup" className="hover:text-white transition-colors">Teste Grátis</Link></li>
                            </ul>
                        </div>

                        <div>
                            <h4 className="text-white font-semibold mb-4">Empresa</h4>
                            <ul className="space-y-2 text-sm">
                                <li><a href="#" className="hover:text-white transition-colors">Sobre</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">Contato</a></li>
                            </ul>
                        </div>

                        <div>
                            <h4 className="text-white font-semibold mb-4">Legal</h4>
                            <ul className="space-y-2 text-sm">
                                <li><a href="#" className="hover:text-white transition-colors">Privacidade</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">Termos de Uso</a></li>
                            </ul>
                        </div>
                    </div>

                    <div className="border-t border-slate-800 mt-12 pt-8 text-center text-sm">
                        <p>© 2025 Legal Pro. Todos os direitos reservados.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}
