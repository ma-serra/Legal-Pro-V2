import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ProcessoForm from '../../components/processos/ProcessoForm';
import type { ProcessoFormData } from '../../types/processos';
import api from '../../lib/api';
import { useState } from 'react';

export default function NovoProcessoPage() {
    const navigate = useNavigate();
    const [salvando, setSalvando] = useState(false);

    const handleSave = async (data: ProcessoFormData) => {
        setSalvando(true);
        try {
            await api.post('/api/processos', data);
            alert('Processo cadastrado com sucesso!');
            navigate('/processos');
        } catch (error) {
            console.error('Erro ao salvar processo:', error);
            alert('Erro ao salvar processo. Verifique os dados e tente novamente.');
        } finally {
            setSalvando(false);
        }
    };

    const handleCancel = () => {
        if (confirm('Deseja cancelar o cadastro? Dados não salvos serão perdidos.')) {
            navigate('/processos');
        }
    };

    return (
        <div className="p-6 max-w-5xl mx-auto">
            <div className="mb-6">
                <button
                    onClick={() => navigate('/processos')}
                    className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors mb-4"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Voltar para lista
                </button>

                <h1 className="text-3xl font-bold">Novo Processo</h1>
                <p className="text-muted-foreground mt-2">
                    Preencha os dados do processo jurídico
                </p>
            </div>

            <div className="bg-card border border-border rounded-xl p-6">
                <ProcessoForm
                    onSave={handleSave}
                    onCancel={handleCancel}
                    saving={salvando}
                />
            </div>
        </div>
    );
}
