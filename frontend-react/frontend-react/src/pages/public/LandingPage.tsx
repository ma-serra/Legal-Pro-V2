/**
 * LandingPage - Rosenthal Sarfatis Metta Advogados
 * Design clean, elegante e profissional
 * Estilo minimalista corporativo
 */
import { Link } from 'react-router-dom';
import { Scale, Mail, Phone, MapPin, ChevronRight } from 'lucide-react';

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-white dark:bg-slate-950">
            {/* Header/Navigation */}
            <header className="fixed top-0 w-full bg-slate-900 text-white z-50 shadow-lg">
                <div className="container mx-auto px-6">
                    <div className="flex items-center justify-between h-20">
                        {/* Logo */}
                        <div className="flex items-center">
                            <img
                                src="/rosenthal-logo.png"
                                alt="Rosenthal Sarfatis Metta Advogados"
                                className="h-12"
                            />
                        </div>

                        {/* Navigation */}
                        <nav className="hidden md:flex items-center gap-8">
                            <a href="#sobre" className="hover:text-slate-300 transition-colors text-sm uppercase tracking-wide">
                                Sobre
                            </a>
                            <a href="#especialidades" className="hover:text-slate-300 transition-colors text-sm uppercase tracking-wide">
                                Especialidades
                            </a>
                            <a href="#contato" className="hover:text-slate-300 transition-colors text-sm uppercase tracking-wide">
                                Contato
                            </a>
                            <Link
                                to="/login"
                                className="px-6 py-2 bg-white text-slate-900 rounded hover:bg-slate-100 transition-colors text-sm font-semibold"
                            >
                                Acessar Sistema
                            </Link>
                        </nav>
                    </div>
                </div>
            </header>

            {/* Hero Section */}
            <section className="pt-32 pb-20 bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-950">
                <div className="container mx-auto px-6">
                    <div className="max-w-4xl mx-auto text-center">
                        <div className="mb-8">
                            <div className="inline-block p-3 bg-slate-900 dark:bg-slate-800 rounded-lg mb-6">
                                <Scale className="w-12 h-12 text-white" />
                            </div>
                        </div>

                        <h1 className="text-5xl md:text-6xl font-light mb-6 text-slate-900 dark:text-white leading-tight">
                            "A Rosenthal se diferencia de muitos escritórios de advocacia com os quais trabalhamos porque une a visão jurídica à visão 'de negócio'..."
                        </h1>

                        <p className="text-xl text-slate-600 dark:text-slate-400 mb-4">
                            Rafael Campos, Bosch
                        </p>
                    </div>
                </div>
            </section>

            {/* Nosso Trabalho */}
            <section id="sobre" className="py-20 bg-white dark:bg-slate-950">
                <div className="container mx-auto px-6">
                    <div className="max-w-5xl mx-auto">
                        <h2 className="text-4xl font-light text-center mb-12 text-slate-900 dark:text-white">
                            Nosso Trabalho
                        </h2>

                        <div className="prose prose-lg mx-auto text-center max-w-3xl">
                            <p className="text-lg text-slate-700 dark:text-slate-300 leading-relaxed mb-6">
                                O foco da Rosenthal Sarfatis Metta Advogados é atuar preventivamente,
                                proporcionando segurança jurídica aos nossos clientes, seja auxiliando-os
                                em suas decisões, analisando riscos ou elaborando estratégias.
                            </p>

                            <p className="text-lg text-slate-700 dark:text-slate-300 leading-relaxed">
                                Atuando tanto na área consultiva quanto na contenciosa, nossos clientes
                                estão sempre bem informados. Sabemos que nosso futuro está intimamente
                                ligado ao sucesso daqueles para os quais prestamos serviços.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Especialidades */}
            <section id="especialidades" className="py-20 bg-slate-50 dark:bg-slate-900/50">
                <div className="container mx-auto px-6">
                    <div className="max-w-6xl mx-auto">
                        <h2 className="text-4xl font-light text-center mb-16 text-slate-900 dark:text-white">
                            Especialidades
                        </h2>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                            {/* Tributário */}
                            <div className="text-center">
                                <div className="mb-6">
                                    <div className="w-1 h-16 bg-slate-900 dark:bg-slate-700 mx-auto"></div>
                                </div>
                                <h3 className="text-2xl font-light mb-6 text-slate-900 dark:text-white">
                                    Tributário
                                </h3>
                                <ul className="space-y-3 text-slate-600 dark:text-slate-400">
                                    <li>Planejamento e consultoria tributária</li>
                                    <li>Otimização da carga tributária</li>
                                    <li>Atuação judicial e administrativa</li>
                                    <li>Defesa dos interesses dos contribuintes</li>
                                    <li>Gestão e reestruturação de passivo</li>
                                </ul>
                            </div>

                            {/* Trabalhista */}
                            <div className="text-center">
                                <div className="mb-6">
                                    <div className="w-1 h-16 bg-slate-900 dark:bg-slate-700 mx-auto"></div>
                                </div>
                                <h3 className="text-2xl font-light mb-6 text-slate-900 dark:text-white">
                                    Trabalhista
                                </h3>
                                <ul className="space-y-3 text-slate-600 dark:text-slate-400">
                                    <li>Defesa em reclamações trabalhistas</li>
                                    <li>Consultoria para redução de passivo</li>
                                    <li>Cursos e treinamentos in company</li>
                                    <li>Assessoria em relações trabalhistas</li>
                                    <li>Compliance trabalhista</li>
                                </ul>
                            </div>

                            {/* Cível */}
                            <div className="text-center">
                                <div className="mb-6">
                                    <div className="w-1 h-16 bg-slate-900 dark:bg-slate-700 mx-auto"></div>
                                </div>
                                <h3 className="text-2xl font-light mb-6 text-slate-900 dark:text-white">
                                    Cível
                                </h3>
                                <ul className="space-y-3 text-slate-600 dark:text-slate-400">
                                    <li>Negociações e disputas societárias</li>
                                    <li>Fusões, aquisições e incorporações</li>
                                    <li>Defesas em ações de consumidores</li>
                                    <li>Contratos e ações indenizatórias</li>
                                    <li>Auditoria legal (due diligence)</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Nossos Valores */}
            <section className="py-20 bg-slate-900 text-white">
                <div className="container mx-auto px-6">
                    <div className="max-w-5xl mx-auto">
                        <h2 className="text-4xl font-light text-center mb-16">
                            Nossos Valores
                        </h2>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                            <div className="text-center">
                                <h3 className="text-2xl font-light mb-4">Conhecimento</h3>
                                <p className="text-slate-300">
                                    Do direito e da realidade empresarial de cada cliente.
                                    Não existem soluções padronizadas.
                                </p>
                            </div>

                            <div className="text-center">
                                <h3 className="text-2xl font-light mb-4">Eficiência</h3>
                                <p className="text-slate-300">
                                    Comunicação clara e objetiva com o cliente e com as autoridades.
                                </p>
                            </div>

                            <div className="text-center">
                                <h3 className="text-2xl font-light mb-4">Liderança</h3>
                                <p className="text-slate-300">
                                    Antecipar as necessidades dos clientes. Tomar a iniciativa.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Reconhecimentos */}
            <section className="py-20 bg-white dark:bg-slate-950">
                <div className="container mx-auto px-6">
                    <div className="max-w-4xl mx-auto text-center">
                        <h2 className="text-4xl font-light mb-12 text-slate-900 dark:text-white">
                            Reconhecimentos
                        </h2>

                        <blockquote className="text-2xl font-light text-slate-700 dark:text-slate-300 mb-6 italic">
                            "O escritório se destaca pelo atendimento ágil, qualificado e sempre muito próximo,
                            nos ajudando nas resoluções para nosso negócio."
                        </blockquote>

                        <p className="text-lg text-slate-600 dark:text-slate-400">
                            João Campanha
                        </p>
                    </div>
                </div>
            </section>

            {/* Contato */}
            <section id="contato" className="py-20 bg-slate-50 dark:bg-slate-900/50">
                <div className="container mx-auto px-6">
                    <div className="max-w-4xl mx-auto">
                        <h2 className="text-4xl font-light text-center mb-16 text-slate-900 dark:text-white">
                            Contato
                        </h2>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center mb-12">
                            <div className="space-y-3">
                                <MapPin className="w-8 h-8 mx-auto text-slate-700 dark:text-slate-400" />
                                <div className="text-slate-700 dark:text-slate-300">
                                    <p>Rua Lisboa, nº 500</p>
                                    <p>Cerqueira Cesar | 05413-000</p>
                                    <p>São Paulo - SP | Brasil</p>
                                </div>
                            </div>

                            <div className="space-y-3">
                                <Phone className="w-8 h-8 mx-auto text-slate-700 dark:text-slate-400" />
                                <a
                                    href="tel:+551132594866"
                                    className="block text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
                                >
                                    +55 (11) 3259-4866
                                </a>
                            </div>

                            <div className="space-y-3">
                                <Mail className="w-8 h-8 mx-auto text-slate-700 dark:text-slate-400" />
                                <a
                                    href="mailto:rosenthal@rosenthal.com.br"
                                    className="block text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
                                >
                                    rosenthal@rosenthal.com.br
                                </a>
                            </div>
                        </div>

                        {/* Newsletter */}
                        <div className="bg-white dark:bg-slate-800 rounded-lg p-8 text-center">
                            <h3 className="text-2xl font-light mb-4 text-slate-900 dark:text-white">
                                Cadastre seu e-mail para receber nossos informativos
                            </h3>
                            <p className="text-slate-600 dark:text-slate-400 mb-6">
                                Fique por dentro das novidades jurídicas importantes para sua empresa sem perder muito tempo.
                            </p>

                            <div className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
                                <input
                                    type="email"
                                    placeholder="Seu e-mail"
                                    className="flex-1 px-4 py-3 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded focus:outline-none focus:ring-2 focus:ring-slate-900 dark:focus:ring-slate-600"
                                />
                                <button className="px-6 py-3 bg-slate-900 dark:bg-slate-700 text-white rounded hover:bg-slate-800 dark:hover:bg-slate-600 transition-colors font-semibold">
                                    Cadastrar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-slate-900 text-slate-400 py-12">
                <div className="container mx-auto px-6">
                    <div className="max-w-6xl mx-auto">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
                            <div>
                                <h4 className="text-white font-semibold mb-4 text-sm uppercase tracking-wide">
                                    Escritório
                                </h4>
                                <ul className="space-y-2 text-sm">
                                    <li><a href="#sobre" className="hover:text-white transition-colors">Sobre</a></li>
                                    <li><a href="#especialidades" className="hover:text-white transition-colors">Especialidades</a></li>
                                    <li><a href="#contato" className="hover:text-white transition-colors">Contato</a></li>
                                </ul>
                            </div>

                            <div>
                                <h4 className="text-white font-semibold mb-4 text-sm uppercase tracking-wide">
                                    Sistema
                                </h4>
                                <ul className="space-y-2 text-sm">
                                    <li><Link to="/login" className="hover:text-white transition-colors">Acessar Sistema</Link></li>
                                    <li><Link to="/signup" className="hover:text-white transition-colors">Cadastrar</Link></li>
                                </ul>
                            </div>

                            <div>
                                <h4 className="text-white font-semibold mb-4 text-sm uppercase tracking-wide">
                                    LGPD
                                </h4>
                                <ul className="space-y-2 text-sm">
                                    <li><a href="#" className="hover:text-white transition-colors">Política de Privacidade</a></li>
                                    <li><a href="#" className="hover:text-white transition-colors">Termos e Condições</a></li>
                                </ul>
                            </div>
                        </div>

                        <div className="border-t border-slate-800 pt-8 text-center text-sm">
                            <p>
                                Atuando há mais de duas décadas, Rosenthal Sarfatis Metta Advogados consolidou
                                sua atuação assessorando empresas no âmbito do Direito Empresarial,
                                com destaque no Direito Tributário.
                            </p>
                            <p className="mt-4">
                                Copyright © {new Date().getFullYear()} Rosenthal Sarfatis Metta Sociedade de Advogados | OAB-SP 6738
                            </p>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}
