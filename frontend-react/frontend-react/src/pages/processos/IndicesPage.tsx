/**
 * IndicesPage - Importação de Índices Monetários
 * Interface para importar índices do BACEN
 */
import ImportadorIndices from '../../components/processos/ImportadorIndices';
import IndicesChart from '../../components/processos/IndicesChart';
import { useState } from 'react';

export default function IndicesPage() {
    const [indiceSelecionado, setIndiceSelecionado] = useState<number>(1); // SELIC padrão

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            <ImportadorIndices />

            <div className="bg-card border border-border rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">Histórico de Índices</h3>

                <div className="flex gap-2 mb-6">
                    {[
                        { id: 1, nome: 'SELIC' },
                        { id: 2, nome: 'IPCA' },
                        { id: 3, nome: 'CDI' }
                    ].map(indice => (
                        <button
                            key={indice.id}
                            onClick={() => setIndiceSelecionado(indice.id)}
                            className={`px-4 py-2 rounded-lg transition-colors ${indiceSelecionado === indice.id
                                    ? 'bg-primary text-white'
                                    : 'bg-accent hover:bg-accent/80'
                                }`}
                        >
                            {indice.nome}
                        </button>
                    ))}
                </div>

                <IndicesChart
                    indiceId={indiceSelecionado}
                    indiceName={indiceSelecionado === 1 ? 'SELIC' : indiceSelecionado === 2 ? 'IPCA' : 'CDI'}
                />
            </div>
        </div>
    );
}
