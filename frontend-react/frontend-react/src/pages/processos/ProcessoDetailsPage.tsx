/**
 * ProcessoDetailsPage - Wrapper para componente de detalhes
 * Integra ProcessoDetails nos módulo de processos
 */
import { useParams, useNavigate } from 'react-router-dom';
import ProcessoDetails from '../../components/processos/ProcessoDetails';

export default function ProcessoDetailsPage() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();

    if (!id || isNaN(parseInt(id))) {
        return (
            <div className="p-6">
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-center">
                    <p className="text-red-400 font-semibold">ID de processo inválido</p>
                    <button
                        onClick={() => navigate('/processos')}
                        className="mt-4 px-6 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors"
                    >
                        Voltar para Processos
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <ProcessoDetails
                processoId={parseInt(id)}
                onClose={() => navigate('/processos')}
            />
        </div>
    );
}
