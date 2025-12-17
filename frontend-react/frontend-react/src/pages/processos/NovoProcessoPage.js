import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ProcessoForm from '../../components/processos/ProcessoForm';
import api from '../../lib/api';
import { useState } from 'react';
export default function NovoProcessoPage() {
    const navigate = useNavigate();
    const [salvando, setSalvando] = useState(false);
    const handleSave = async (data) => {
        setSalvando(true);
        try {
            await api.post('/api/processos', data);
            alert('Processo cadastrado com sucesso!');
            navigate('/processos');
        }
        catch (error) {
            console.error('Erro ao salvar processo:', error);
            alert('Erro ao salvar processo. Verifique os dados e tente novamente.');
        }
        finally {
            setSalvando(false);
        }
    };
    const handleCancel = () => {
        if (confirm('Deseja cancelar o cadastro? Dados não salvos serão perdidos.')) {
            navigate('/processos');
        }
    };
    return (_jsxs("div", { className: "p-6 max-w-5xl mx-auto", children: [_jsxs("div", { className: "mb-6", children: [_jsxs("button", { onClick: () => navigate('/processos'), className: "flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors mb-4", children: [_jsx(ArrowLeft, { className: "w-4 h-4" }), "Voltar para lista"] }), _jsx("h1", { className: "text-3xl font-bold", children: "Novo Processo" }), _jsx("p", { className: "text-muted-foreground mt-2", children: "Preencha os dados do processo jur\u00EDdico" })] }), _jsx("div", { className: "bg-card border border-border rounded-xl p-6", children: _jsx(ProcessoForm, { onSave: handleSave, onCancel: handleCancel, saving: salvando }) })] }));
}
