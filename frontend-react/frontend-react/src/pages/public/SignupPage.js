import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { Building2, Mail, Lock, User, Check, AlertCircle } from 'lucide-react';
import api from '../../lib/api';
export default function SignupPage() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const selectedPlan = searchParams.get('plan') || 'starter';
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [formData, setFormData] = useState({
        orgName: '',
        ownerName: '',
        ownerEmail: '',
        ownerPassword: '',
        ownerPasswordConfirm: '',
        acceptTerms: false
    });
    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
        setError('');
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        // Validation
        if (!formData.orgName || !formData.ownerEmail || !formData.ownerPassword) {
            setError('Por favor, preencha todos os campos obrigatórios');
            return;
        }
        if (formData.ownerPassword !== formData.ownerPasswordConfirm) {
            setError('As senhas não conferem');
            return;
        }
        if (formData.ownerPassword.length < 8) {
            setError('A senha deve ter no mínimo 8 caracteres');
            return;
        }
        if (!formData.acceptTerms) {
            setError('Você deve aceitar os termos de uso');
            return;
        }
        setLoading(true);
        try {
            const response = await api.post('/api/saas/api/saas/tenants', {
                name: formData.orgName,
                owner_email: formData.ownerEmail,
                owner_password: formData.ownerPassword,
                plan_slug: selectedPlan
            });
            if (response.data.success) {
                // Success! Show confirmation and redirect
                setStep(3);
                // Auto-redirect to dashboard after 3 seconds
                setTimeout(() => {
                    const slug = response.data.tenant.slug;
                    navigate(`/org/${slug}/dashboard`);
                }, 3000);
            }
        }
        catch (err) {
            const errorMessage = err.response?.data?.error || 'Erro ao criar conta. Tente novamente.';
            setError(errorMessage);
        }
        finally {
            setLoading(false);
        }
    };
    // Step 1: Organization Info
    if (step === 1) {
        return (_jsx("div", { className: "min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4", children: _jsxs("div", { className: "max-w-md w-full", children: [_jsxs("div", { className: "text-center mb-8", children: [_jsxs(Link, { to: "/", className: "text-3xl font-bold text-gray-900 inline-block mb-4", children: ["Legal", _jsx("span", { className: "text-blue-600", children: "Pro" })] }), _jsx("h1", { className: "text-2xl font-bold text-gray-900 mb-2", children: "Crie sua Conta" }), _jsx("p", { className: "text-gray-600", children: "Trial gratuito de 14 dias \u2022 Sem cart\u00E3o de cr\u00E9dito" })] }), _jsxs("div", { className: "flex items-center justify-center gap-2 mb-8", children: [_jsx("div", { className: "w-12 h-1 bg-blue-600 rounded" }), _jsx("div", { className: "w-12 h-1 bg-gray-300 rounded" }), _jsx("div", { className: "w-12 h-1 bg-gray-300 rounded" })] }), _jsxs("div", { className: "bg-white rounded-lg shadow-sm p-8", children: [_jsxs("form", { onSubmit: (e) => { e.preventDefault(); setStep(2); }, children: [_jsxs("div", { className: "mb-6", children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Nome da Organiza\u00E7\u00E3o *" }), _jsxs("div", { className: "relative", children: [_jsx(Building2, { className: "absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" }), _jsx("input", { type: "text", name: "orgName", value: formData.orgName, onChange: handleInputChange, placeholder: "Silva & Associados Advocacia", className: "w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent", required: true })] }), _jsx("p", { className: "text-xs text-gray-500 mt-1", children: "Nome do seu escrit\u00F3rio ou departamento jur\u00EDdico" })] }), _jsx("button", { type: "submit", className: "w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors", children: "Continuar" })] }), _jsxs("div", { className: "mt-6 text-center text-sm text-gray-600", children: ["J\u00E1 tem uma conta?", ' ', _jsx(Link, { to: "/login", className: "text-blue-600 hover:text-blue-700 font-medium", children: "Fazer Login" })] })] })] }) }));
    }
    // Step 2: User Info & Password
    if (step === 2) {
        return (_jsx("div", { className: "min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4", children: _jsxs("div", { className: "max-w-md w-full", children: [_jsxs("div", { className: "text-center mb-8", children: [_jsxs(Link, { to: "/", className: "text-3xl font-bold text-gray-900 inline-block mb-4", children: ["Legal", _jsx("span", { className: "text-blue-600", children: "Pro" })] }), _jsx("h1", { className: "text-2xl font-bold text-gray-900 mb-2", children: "Dados do Administrador" }), _jsxs("p", { className: "text-gray-600", children: ["Organiza\u00E7\u00E3o: ", _jsx("strong", { children: formData.orgName })] })] }), _jsxs("div", { className: "flex items-center justify-center gap-2 mb-8", children: [_jsx("div", { className: "w-12 h-1 bg-blue-600 rounded" }), _jsx("div", { className: "w-12 h-1 bg-blue-600 rounded" }), _jsx("div", { className: "w-12 h-1 bg-gray-300 rounded" })] }), _jsxs("div", { className: "bg-white rounded-lg shadow-sm p-8", children: [error && (_jsxs("div", { className: "mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3", children: [_jsx(AlertCircle, { className: "w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" }), _jsx("p", { className: "text-sm text-red-800", children: error })] })), _jsxs("form", { onSubmit: handleSubmit, children: [_jsxs("div", { className: "mb-4", children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Nome Completo" }), _jsxs("div", { className: "relative", children: [_jsx(User, { className: "absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" }), _jsx("input", { type: "text", name: "ownerName", value: formData.ownerName, onChange: handleInputChange, placeholder: "Jo\u00E3o Silva", className: "w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" })] })] }), _jsxs("div", { className: "mb-4", children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Email Profissional *" }), _jsxs("div", { className: "relative", children: [_jsx(Mail, { className: "absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" }), _jsx("input", { type: "email", name: "ownerEmail", value: formData.ownerEmail, onChange: handleInputChange, placeholder: "joao@silva-associados.com.br", className: "w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent", required: true })] })] }), _jsxs("div", { className: "mb-4", children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Senha *" }), _jsxs("div", { className: "relative", children: [_jsx(Lock, { className: "absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" }), _jsx("input", { type: "password", name: "ownerPassword", value: formData.ownerPassword, onChange: handleInputChange, placeholder: "M\u00EDnimo 8 caracteres", className: "w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent", required: true, minLength: 8 })] })] }), _jsxs("div", { className: "mb-6", children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-2", children: "Confirmar Senha *" }), _jsxs("div", { className: "relative", children: [_jsx(Lock, { className: "absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" }), _jsx("input", { type: "password", name: "ownerPasswordConfirm", value: formData.ownerPasswordConfirm, onChange: handleInputChange, placeholder: "Digite a senha novamente", className: "w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent", required: true })] })] }), _jsx("div", { className: "mb-6", children: _jsxs("label", { className: "flex items-start gap-3", children: [_jsx("input", { type: "checkbox", name: "acceptTerms", checked: formData.acceptTerms, onChange: handleInputChange, className: "mt-1", required: true }), _jsxs("span", { className: "text-sm text-gray-600", children: ["Concordo com os", ' ', _jsx("a", { href: "#", className: "text-blue-600 hover:text-blue-700", children: "Termos de Uso" }), ' ', "e", ' ', _jsx("a", { href: "#", className: "text-blue-600 hover:text-blue-700", children: "Pol\u00EDtica de Privacidade" })] })] }) }), _jsxs("div", { className: "flex gap-3", children: [_jsx("button", { type: "button", onClick: () => setStep(1), className: "flex-1 border border-gray-300 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors", children: "Voltar" }), _jsx("button", { type: "submit", disabled: loading, className: "flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50", children: loading ? 'Criando conta...' : 'Criar Conta' })] })] })] })] }) }));
    }
    // Step 3: Success
    return (_jsx("div", { className: "min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4", children: _jsx("div", { className: "max-w-md w-full text-center", children: _jsxs("div", { className: "bg-white rounded-lg shadow-sm p-12", children: [_jsx("div", { className: "w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6", children: _jsx(Check, { className: "w-8 h-8 text-green-600" }) }), _jsx("h1", { className: "text-2xl font-bold text-gray-900 mb-4", children: "Conta Criada com Sucesso!" }), _jsxs("p", { className: "text-gray-600 mb-8", children: ["Bem-vindo ao LegalPro, ", _jsx("strong", { children: formData.orgName }), "!", _jsx("br", {}), "Seu trial gratuito de 14 dias j\u00E1 come\u00E7ou."] }), _jsx("div", { className: "animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto" }), _jsx("p", { className: "text-sm text-gray-500 mt-4", children: "Redirecionando para o dashboard..." })] }) }) }));
}
