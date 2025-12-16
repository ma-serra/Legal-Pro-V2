import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * IndicesPage - Importação de Índices Monetários
 * Interface para importar índices do BACEN
 */
import ImportadorIndices from '../../components/processos/ImportadorIndices';
import IndicesChart from '../../components/processos/IndicesChart';
import { useState } from 'react';
export default function IndicesPage() {
    const [indiceSelecionado, setIndiceSelecionado] = useState(1); // SELIC padrão
    return (_jsxs("div", { className: "p-6 max-w-7xl mx-auto space-y-6", children: [_jsx(ImportadorIndices, {}), _jsxs("div", { className: "bg-card border border-border rounded-xl p-6", children: [_jsx("h3", { className: "text-xl font-bold mb-4", children: "Hist\u00F3rico de \u00CDndices" }), _jsx("div", { className: "flex gap-2 mb-6", children: [
                            { id: 1, nome: 'SELIC' },
                            { id: 2, nome: 'IPCA' },
                            { id: 3, nome: 'CDI' }
                        ].map(indice => (_jsx("button", { onClick: () => setIndiceSelecionado(indice.id), className: `px-4 py-2 rounded-lg transition-colors ${indiceSelecionado === indice.id
                                ? 'bg-primary text-white'
                                : 'bg-accent hover:bg-accent/80'}`, children: indice.nome }, indice.id))) }), _jsx(IndicesChart, { indiceId: indiceSelecionado, indiceName: indiceSelecionado === 1 ? 'SELIC' : indiceSelecionado === 2 ? 'IPCA' : 'CDI' })] })] }));
}
