import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * ProcessoDetailsPage - Wrapper para componente de detalhes
 * Integra ProcessoDetails nos módulo de processos
 */
import { useParams, useNavigate } from 'react-router-dom';
import ProcessoDetails from '../../components/processos/ProcessoDetails';
export default function ProcessoDetailsPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    if (!id || isNaN(parseInt(id))) {
        return (_jsx("div", { className: "p-6", children: _jsxs("div", { className: "bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-center", children: [_jsx("p", { className: "text-red-400 font-semibold", children: "ID de processo inv\u00E1lido" }), _jsx("button", { onClick: () => navigate('/processos'), className: "mt-4 px-6 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors", children: "Voltar para Processos" })] }) }));
    }
    return (_jsx("div", { className: "p-6", children: _jsx(ProcessoDetails, { processoId: parseInt(id), onClose: () => navigate('/processos') }) }));
}
