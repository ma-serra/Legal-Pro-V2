import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const { login } = useAuth();
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        try {
            await login(email, password);
            navigate('/dashboard');
        }
        catch (err) {
            setError('Email ou senha inválidos');
        }
        finally {
            setIsLoading(false);
        }
    };
    return (_jsx("div", { className: "min-h-screen bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center px-4", children: _jsx("div", { className: "w-full max-w-md", children: _jsxs("div", { className: "bg-card rounded-lg shadow-lg p-8 border border-border", children: [_jsx("h1", { className: "text-3xl font-bold text-center mb-2 text-foreground", children: "Legal Pro" }), _jsx("p", { className: "text-center text-muted-foreground mb-8", children: "Sistema Jur\u00EDdico Multi-Agente" }), _jsxs("form", { onSubmit: handleSubmit, className: "space-y-4", children: [error && (_jsx("div", { className: "bg-red-500/10 border border-red-500/30 rounded-md p-3", children: _jsx("p", { className: "text-red-700 dark:text-red-400 text-sm", children: error }) })), _jsxs("div", { children: [_jsx("label", { htmlFor: "email", className: "block text-sm font-medium text-foreground mb-2", children: "Email" }), _jsx("input", { id: "email", type: "email", value: email, onChange: (e) => setEmail(e.target.value), placeholder: "seu@email.com", className: "w-full px-4 py-2 border border-border rounded-md bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary", required: true })] }), _jsxs("div", { children: [_jsx("label", { htmlFor: "password", className: "block text-sm font-medium text-foreground mb-2", children: "Senha" }), _jsx("input", { id: "password", type: "password", value: password, onChange: (e) => setPassword(e.target.value), placeholder: "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022", className: "w-full px-4 py-2 border border-border rounded-md bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary", required: true })] }), _jsx("button", { type: "submit", disabled: isLoading, className: "w-full bg-primary text-primary-foreground py-2 rounded-md font-medium hover:bg-primary/90 transition disabled:opacity-50 disabled:cursor-not-allowed", children: isLoading ? 'Carregando...' : 'Entrar' })] }), _jsxs("p", { className: "text-center text-sm text-muted-foreground mt-6", children: ["Credenciais de teste:", _jsx("br", {}), "Email: ", _jsx("code", { className: "bg-muted px-2 py-1 rounded", children: "demo@legal.pro" }), _jsx("br", {}), "Senha: ", _jsx("code", { className: "bg-muted px-2 py-1 rounded", children: "demo123" })] })] }) }) }));
}
