/**
 * ImportadorProcessos - Upload e ETL de Planilhas
 * Interface para importação em massa de processos
 */
import { useState } from 'react';
import { Upload, FileSpreadsheet, CheckCircle, XCircle, AlertCircle, Download } from 'lucide-react';
import api from '../../lib/api';

export default function ImportadorProcessos() {
    const [arquivo, setArquivo] = useState<File | null>(null);
    const [processando, setProcessando] = useState(false);
    const [resultado, setResultado] = useState<any>(null);
    const [progresso, setProgresso] = useState(0);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setArquivo(e.target.files[0]);
            setResultado(null);
        }
    };

    const handleImportar = async () => {
        if (!arquivo) return;

        setProcessando(true);
        setProgresso(10);

        const formData = new FormData();
        formData.append('arquivo', arquivo);

        try {
            setProgresso(30);

            const response = await api.post('/api/processos/importar', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                },
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round(
                        (progressEvent.loaded * 50) / (progressEvent.total || 1)
                    );
                    setProgresso(30 + percentCompleted);
                }
            });

            setProgresso(100);
            setResultado(response.data);
        } catch (error: any) {
            setResultado({
                sucesso: false,
                erro: error.response?.data?.error || 'Erro ao processar arquivo'
            });
        } finally {
            setProcessando(false);
        }
    };

    const baixarRelatorio = () => {
        if (!resultado) return;

        const relatorio = `
RELATÓRIO DE IMPORTAÇÃO DE PROCESSOS
=====================================

Arquivo: ${arquivo?.name}
Data: ${new Date().toLocaleString('pt-BR')}

RESUMO:
-------
Total de registros: ${resultado.total_registros}
Importados com sucesso: ${resultado.importados} (${resultado.taxa_sucesso}%)
Registros com erro: ${resultado.erros}
Avisos: ${resultado.avisos}
Tempo total: ${resultado.tempo_segundos}s

${resultado.registros_com_erro?.length > 0 ? `
REGISTROS COM ERRO:
-------------------
${resultado.registros_com_erro.map((r: any, i: number) =>
            `${i + 1}. Pasta: ${r.pasta} - Erro: ${r._erros}`
        ).join('\n')}
` : ''}

${resultado.avisos?.length > 0 ? `
AVISOS:
-------
${resultado.avisos.map((a: any, i: number) =>
            `${i + 1}. ${a}`
        ).join('\n')}
` : ''}
    `.trim();

        const blob = new Blob([relatorio], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `relatorio_importacao_${new Date().getTime()}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-primary/20 rounded-lg">
                        <FileSpreadsheet className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold">Importar Processos</h2>
                        <p className="text-sm text-muted-foreground">
                            Upload de planilha Excel/CSV com validação e ETL automático
                        </p>
                    </div>
                </div>
            </div>

            {/* Upload Area */}
            <div className="bg-card border border-border rounded-xl p-8">
                <div className="text-center">
                    <input
                        type="file"
                        id="file-upload"
                        accept=".xlsx,.xls,.csv"
                        onChange={handleFileChange}
                        className="hidden"
                    />

                    <label
                        htmlFor="file-upload"
                        className="cursor-pointer flex flex-col items-center gap-4"
                    >
                        <div className="p-6 bg-primary/10 rounded-full">
                            <Upload className="w-12 h-12 text-primary" />
                        </div>

                        <div>
                            <p className="text-lg font-semibold mb-1">
                                Clique para selecionar arquivo
                            </p>
                            <p className="text-sm text-muted-foreground">
                                Formatos aceitos: Excel (.xlsx, .xls) ou CSV (.csv)
                            </p>
                        </div>
                    </label>

                    {arquivo && (
                        <div className="mt-6 bg-accent rounded-lg p-4 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <FileSpreadsheet className="w-5 h-5 text-primary" />
                                <div className="text-left">
                                    <p className="font-medium">{arquivo.name}</p>
                                    <p className="text-xs text-muted-foreground">
                                        {(arquivo.size / 1024).toFixed(2)} KB
                                    </p>
                                </div>
                            </div>

                            <button
                                onClick={handleImportar}
                                disabled={processando}
                                className="px-6 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                            >
                                {processando ? 'Processando...' : 'Importar'}
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Progress Bar */}
            {processando && (
                <div className="bg-card border border-border rounded-xl p-6">
                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <p className="font-semibold">Processando ETL...</p>
                            <p className="text-sm text-muted-foreground">{progresso}%</p>
                        </div>

                        <div className="w-full bg-accent rounded-full h-3">
                            <div
                                className="bg-primary rounded-full h-3 transition-all duration-300"
                                style={{ width: `${progresso}%` }}
                            />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                            <div className={progresso >= 10 ? 'text-primary' : 'text-muted-foreground'}>
                                ✓ Validando arquivo
                            </div>
                            <div className={progresso >= 50 ? 'text-primary' : 'text-muted-foreground'}>
                                {progresso >= 50 ? '✓' : '⏳'} Processando dados
                            </div>
                            <div className={progresso >= 100 ? 'text-primary' : 'text-muted-foreground'}>
                                {progresso >= 100 ? '✓' : '⏳'} Finalizando
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Resultado */}
            {resultado && (
                <div className={`bg-card border rounded-xl p-6 ${resultado.sucesso
                        ? 'border-green-500/50 bg-green-500/10'
                        : 'border-red-500/50 bg-red-500/10'
                    }`}>
                    <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                            {resultado.sucesso ? (
                                <CheckCircle className="w-8 h-8 text-green-400" />
                            ) : (
                                <XCircle className="w-8 h-8 text-red-400" />
                            )}

                            <div>
                                <h3 className="text-xl font-bold">
                                    {resultado.sucesso ? 'Importação Concluída!' : 'Erro na Importação'}
                                </h3>
                                <p className="text-sm text-muted-foreground">
                                    {resultado.sucesso
                                        ? `${resultado.importados} de ${resultado.total_registros} registros importados`
                                        : resultado.erro}
                                </p>
                            </div>
                        </div>

                        {resultado.sucesso && (
                            <button
                                onClick={baixarRelatorio}
                                className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors text-sm"
                            >
                                <Download className="w-4 h-4" />
                                Baixar Relatório
                            </button>
                        )}
                    </div>

                    {resultado.sucesso && (
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div className="bg-background rounded-lg p-4">
                                <p className="text-sm text-muted-foreground mb-1">Total</p>
                                <p className="text-2xl font-bold">{resultado.total_registros}</p>
                            </div>

                            <div className="bg-green-500/20 rounded-lg p-4">
                                <p className="text-sm text-green-400 mb-1">Importados</p>
                                <p className="text-2xl font-bold text-green-400">{resultado.importados}</p>
                            </div>

                            <div className="bg-red-500/20 rounded-lg p-4">
                                <p className="text-sm text-red-400 mb-1">Erros</p>
                                <p className="text-2xl font-bold text-red-400">{resultado.erros}</p>
                            </div>

                            <div className="bg-yellow-500/20 rounded-lg p-4">
                                <p className="text-sm text-yellow-400 mb-1">Avisos</p>
                                <p className="text-2xl font-bold text-yellow-400">{resultado.avisos}</p>
                            </div>
                        </div>
                    )}

                    {resultado.registros_com_erro?.length > 0 && (
                        <div className="mt-6">
                            <div className="flex items-center gap-2 mb-3">
                                <AlertCircle className="w-5 h-5 text-red-400" />
                                <h4 className="font-semibold">Registros com Erro</h4>
                            </div>

                            <div className="bg-background rounded-lg p-4 max-h-64 overflow-y-auto space-y-2">
                                {resultado.registros_com_erro.slice(0, 10).map((registro: any, idx: number) => (
                                    <div key={idx} className="border-b border-border pb-2 last:border-0">
                                        <p className="font-medium">Pasta: {registro.pasta}</p>
                                        <p className="text-sm text-red-400">{registro._erros}</p>
                                    </div>
                                ))}

                                {resultado.registros_com_erro.length > 10 && (
                                    <p className="text-sm text-muted-foreground text-center pt-2">
                                        + {resultado.registros_com_erro.length - 10} registros com erro
                                    </p>
                                )}
                            </div>
                        </div>
                    )}

                    {resultado.sucesso && (
                        <div className="mt-6 pt-6 border-t border-border flex items-center justify-between text-sm">
                            <div className="flex items-center gap-4">
                                <span className="text-muted-foreground">
                                    Taxa de sucesso: <span className="text-green-400 font-bold">{resultado.taxa_sucesso}%</span>
                                </span>
                                <span className="text-muted-foreground">
                                    Tempo: <span className="font-semibold">{resultado.tempo_segundos}s</span>
                                </span>
                            </div>

                            <button
                                onClick={() => {
                                    setArquivo(null);
                                    setResultado(null);
                                    setProgresso(0);
                                }}
                                className="px-4 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors"
                            >
                                Nova Importação
                            </button>
                        </div>
                    )}
                </div>
            )}

            {/* Instruções */}
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-6">
                <h4 className="font-semibold text-blue-400 mb-3">💡 Instruções de Importação</h4>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                        <p className="font-medium mb-2">Campos Obrigatórios:</p>
                        <ul className="space-y-1 text-muted-foreground">
                            <li>• <code className="bg-accent px-1 rounded">pasta</code> - Número da pasta</li>
                            <li>• <code className="bg-accent px-1 rounded">natureza</code> - Tributário/Trabalhista/Cível</li>
                        </ul>
                    </div>

                    <div>
                        <p className="font-medium mb-2">Campos Opcionais:</p>
                        <ul className="space-y-1 text-muted-foreground">
                            <li>• <code className="bg-accent px-1 rounded">numero_cnj</code> - Número CNJ</li>
                            <li>• <code className="bg-accent px-1 rounded">valor_causa</code> - Valor da causa</li>
                            <li>• <code className="bg-accent px-1 rounded">data_distribuicao</code> - Data</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
