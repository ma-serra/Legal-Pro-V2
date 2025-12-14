import { useState } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { Building2, Mail, Lock, User, Check, AlertCircle } from 'lucide-react'
import api from '../../lib/api'

export default function SignupPage() {
    const navigate = useNavigate()
    const [searchParams] = useSearchParams()
    const selectedPlan = searchParams.get('plan') || 'starter'

    const [step, setStep] = useState(1)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const [formData, setFormData] = useState({
        orgName: '',
        ownerName: '',
        ownerEmail: '',
        ownerPassword: '',
        ownerPasswordConfirm: '',
        acceptTerms: false
    })

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, type, checked } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }))
        setError('')
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        // Validation
        if (!formData.orgName || !formData.ownerEmail || !formData.ownerPassword) {
            setError('Por favor, preencha todos os campos obrigatórios')
            return
        }

        if (formData.ownerPassword !== formData.ownerPasswordConfirm) {
            setError('As senhas não conferem')
            return
        }

        if (formData.ownerPassword.length < 8) {
            setError('A senha deve ter no mínimo 8 caracteres')
            return
        }

        if (!formData.acceptTerms) {
            setError('Você deve aceitar os termos de uso')
            return
        }

        setLoading(true)

        try {
            const response = await api.post('/api/saas/api/saas/tenants', {
                name: formData.orgName,
                owner_email: formData.ownerEmail,
                owner_password: formData.ownerPassword,
                plan_slug: selectedPlan
            })

            if (response.data.success) {
                // Success! Show confirmation and redirect
                setStep(3)

                // Auto-redirect to dashboard after 3 seconds
                setTimeout(() => {
                    const slug = response.data.tenant.slug
                    navigate(`/org/${slug}/dashboard`)
                }, 3000)
            }
        } catch (err: any) {
            const errorMessage = err.response?.data?.error || 'Erro ao criar conta. Tente novamente.'
            setError(errorMessage)
        } finally {
            setLoading(false)
        }
    }

    // Step 1: Organization Info
    if (step === 1) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
                <div className="max-w-md w-full">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <Link to="/" className="text-3xl font-bold text-gray-900 inline-block mb-4">
                            Legal<span className="text-blue-600">Pro</span>
                        </Link>
                        <h1 className="text-2xl font-bold text-gray-900 mb-2">
                            Crie sua Conta
                        </h1>
                        <p className="text-gray-600">
                            Trial gratuito de 14 dias • Sem cartão de crédito
                        </p>
                    </div>

                    {/* Progress */}
                    <div className="flex items-center justify-center gap-2 mb-8">
                        <div className="w-12 h-1 bg-blue-600 rounded"></div>
                        <div className="w-12 h-1 bg-gray-300 rounded"></div>
                        <div className="w-12 h-1 bg-gray-300 rounded"></div>
                    </div>

                    {/* Form Card */}
                    <div className="bg-white rounded-lg shadow-sm p-8">
                        <form onSubmit={(e) => { e.preventDefault(); setStep(2); }}>
                            {/* Organization Name */}
                            <div className="mb-6">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Nome da Organização *
                                </label>
                                <div className="relative">
                                    <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                    <input
                                        type="text"
                                        name="orgName"
                                        value={formData.orgName}
                                        onChange={handleInputChange}
                                        placeholder="Silva & Associados Advocacia"
                                        className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        required
                                    />
                                </div>
                                <p className="text-xs text-gray-500 mt-1">
                                    Nome do seu escritório ou departamento jurídico
                                </p>
                            </div>

                            <button
                                type="submit"
                                className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                            >
                                Continuar
                            </button>
                        </form>

                        <div className="mt-6 text-center text-sm text-gray-600">
                            Já tem uma conta?{' '}
                            <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium">
                                Fazer Login
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    // Step 2: User Info & Password
    if (step === 2) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
                <div className="max-w-md w-full">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <Link to="/" className="text-3xl font-bold text-gray-900 inline-block mb-4">
                            Legal<span className="text-blue-600">Pro</span>
                        </Link>
                        <h1 className="text-2xl font-bold text-gray-900 mb-2">
                            Dados do Administrador
                        </h1>
                        <p className="text-gray-600">
                            Organização: <strong>{formData.orgName}</strong>
                        </p>
                    </div>

                    {/* Progress */}
                    <div className="flex items-center justify-center gap-2 mb-8">
                        <div className="w-12 h-1 bg-blue-600 rounded"></div>
                        <div className="w-12 h-1 bg-blue-600 rounded"></div>
                        <div className="w-12 h-1 bg-gray-300 rounded"></div>
                    </div>

                    {/* Form Card */}
                    <div className="bg-white rounded-lg shadow-sm p-8">
                        {error && (
                            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                                <p className="text-sm text-red-800">{error}</p>
                            </div>
                        )}

                        <form onSubmit={handleSubmit}>
                            {/* Full Name */}
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Nome Completo
                                </label>
                                <div className="relative">
                                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                    <input
                                        type="text"
                                        name="ownerName"
                                        value={formData.ownerName}
                                        onChange={handleInputChange}
                                        placeholder="João Silva"
                                        className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    />
                                </div>
                            </div>

                            {/* Email */}
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Email Profissional *
                                </label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                    <input
                                        type="email"
                                        name="ownerEmail"
                                        value={formData.ownerEmail}
                                        onChange={handleInputChange}
                                        placeholder="joao@silva-associados.com.br"
                                        className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        required
                                    />
                                </div>
                            </div>

                            {/* Password */}
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Senha *
                                </label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                    <input
                                        type="password"
                                        name="ownerPassword"
                                        value={formData.ownerPassword}
                                        onChange={handleInputChange}
                                        placeholder="Mínimo 8 caracteres"
                                        className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        required
                                        minLength={8}
                                    />
                                </div>
                            </div>

                            {/* Confirm Password */}
                            <div className="mb-6">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Confirmar Senha *
                                </label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                    <input
                                        type="password"
                                        name="ownerPasswordConfirm"
                                        value={formData.ownerPasswordConfirm}
                                        onChange={handleInputChange}
                                        placeholder="Digite a senha novamente"
                                        className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        required
                                    />
                                </div>
                            </div>

                            {/* Terms */}
                            <div className="mb-6">
                                <label className="flex items-start gap-3">
                                    <input
                                        type="checkbox"
                                        name="acceptTerms"
                                        checked={formData.acceptTerms}
                                        onChange={handleInputChange}
                                        className="mt-1"
                                        required
                                    />
                                    <span className="text-sm text-gray-600">
                                        Concordo com os{' '}
                                        <a href="#" className="text-blue-600 hover:text-blue-700">
                                            Termos de Uso
                                        </a>{' '}
                                        e{' '}
                                        <a href="#" className="text-blue-600 hover:text-blue-700">
                                            Política de Privacidade
                                        </a>
                                    </span>
                                </label>
                            </div>

                            <div className="flex gap-3">
                                <button
                                    type="button"
                                    onClick={() => setStep(1)}
                                    className="flex-1 border border-gray-300 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
                                >
                                    Voltar
                                </button>
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50"
                                >
                                    {loading ? 'Criando conta...' : 'Criar Conta'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        )
    }

    // Step 3: Success
    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
            <div className="max-w-md w-full text-center">
                <div className="bg-white rounded-lg shadow-sm p-12">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                        <Check className="w-8 h-8 text-green-600" />
                    </div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-4">
                        Conta Criada com Sucesso!
                    </h1>
                    <p className="text-gray-600 mb-8">
                        Bem-vindo ao LegalPro, <strong>{formData.orgName}</strong>!
                        <br />
                        Seu trial gratuito de 14 dias já começou.
                    </p>
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="text-sm text-gray-500 mt-4">
                        Redirecionando para o dashboard...
                    </p>
                </div>
            </div>
        </div>
    )
}
