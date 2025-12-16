import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * ImportadorProcessos - Upload e ETL de Planilhas
 * Interface para importação em massa de processos
 */
import { useState } from 'react';
import { Upload, FileSpreadsheet, CheckCircle, XCircle, AlertCircle, Download } from 'lucide-react';
import api from '../../lib/api';
export default function ImportadorProcessos() {
    const [arquivo, setArquivo] = useState(null);
    const [processando, setProcessando] = useState(false);
    const [resultado, setResultado] = useState(null);
    const [progresso, setProgresso] = useState(0);
    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setArquivo(e.target.files[0]);
            setResultado(null);
        }
    };
    const handleImportar = async () => {
        if (!arquivo)
            return;
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
                    const percentCompleted = Math.round((progressEvent.loaded * 50) / (progressEvent.total || 1));
                    setProgresso(30 + percentCompleted);
                }
            });
            setProgresso(100);
            setResultado(response.data);
        }
        catch (error) {
            setResultado({
                sucesso: false,
                erro: error.response?.data?.error || 'Erro ao processar arquivo'
            });
        }
        finally {
            setProcessando(false);
        }
    };
    const baixarRelatorio = () => {
        if (!resultado)
            return;
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
${resultado.registros_com_erro.map((r, i) => `${i + 1}. Pasta: ${r.pasta} - Erro: ${r._erros}`).join('\n')}
` : ''}

${resultado.avisos?.length > 0 ? `
AVISOS:
-------
${resultado.avisos.map((a, i) => `${i + 1}. ${a}`).join('\n')}
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
    return (_jsxs("div", { className: "space-y-6", children: [_jsx("div", { className: "flex items-center justify-between", children: _jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "p-3 bg-primary/20 rounded-lg", children: _jsx(FileSpreadsheet, { className: "w-6 h-6 text-primary" }) }), _jsxs("div", { children: [_jsx("h2", { className: "text-2xl font-bold", children: "Importar Processos" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Upload de planilha Excel/CSV com valida\u00E7\u00E3o e ETL autom\u00E1tico" })] })] }) }), _jsx("div", { className: "bg-card border border-border rounded-xl p-8", children: _jsxs("div", { className: "text-center", children: [_jsx("input", { type: "file", id: "file-upload", accept: ".xlsx,.xls,.csv", onChange: handleFileChange, className: "hidden" }), _jsxs("label", { htmlFor: "file-upload", className: "cursor-pointer flex flex-col items-center gap-4", children: [_jsx("div", { className: "p-6 bg-primary/10 rounded-full", children: _jsx(Upload, { className: "w-12 h-12 text-primary" }) }), _jsxs("div", { children: [_jsx("p", { className: "text-lg font-semibold mb-1", children: "Clique para selecionar arquivo" }), _jsx("p", { className: "text-sm text-muted-foreground", children: "Formatos aceitos: Excel (.xlsx, .xls) ou CSV (.csv)" })] })] }), arquivo && (_jsxs("div", { className: "mt-6 bg-accent rounded-lg p-4 flex items-center justify-between", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx(FileSpreadsheet, { className: "w-5 h-5 text-primary" }), _jsxs("div", { className: "text-left", children: [_jsx("p", { className: "font-medium", children: arquivo.name }), _jsxs("p", { className: "text-xs text-muted-foreground", children: [(arquivo.size / 1024).toFixed(2), " KB"] })] })] }), _jsx("button", { onClick: handleImportar, disabled: processando, className: "px-6 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium", children: processando ? 'Processando...' : 'Importar' })] }))] }) }), processando && (_jsx("div", { className: "bg-card border border-border rounded-xl p-6", children: _jsxs("div", { className: "space-y-3", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsx("p", { className: "font-semibold", children: "Processando ETL..." }), _jsxs("p", { className: "text-sm text-muted-foreground", children: [progresso, "%"] })] }), _jsx("div", { className: "w-full bg-accent rounded-full h-3", children: _jsx("div", { className: "bg-primary rounded-full h-3 transition-all duration-300", style: { width: `${progresso}%` } }) }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-3 text-sm", children: [_jsx("div", { className: progresso >= 10 ? 'text-primary' : 'text-muted-foreground', children: "\u2713 Validando arquivo" }), _jsxs("div", { className: progresso >= 50 ? 'text-primary' : 'text-muted-foreground', children: [progresso >= 50 ? '✓' : '⏳', " Processando dados"] }), _jsxs("div", { className: progresso >= 100 ? 'text-primary' : 'text-muted-foreground', children: [progresso >= 100 ? '✓' : '⏳', " Finalizando"] })] })] }) })), resultado && (_jsxs("div", { className: `bg-card border rounded-xl p-6 ${resultado.sucesso
                    ? 'border-green-500/50 bg-green-500/10'
                    : 'border-red-500/50 bg-red-500/10'}`, children: [_jsxs("div", { className: "flex items-start justify-between mb-4", children: [_jsxs("div", { className: "flex items-center gap-3", children: [resultado.sucesso ? (_jsx(CheckCircle, { className: "w-8 h-8 text-green-400" })) : (_jsx(XCircle, { className: "w-8 h-8 text-red-400" })), _jsxs("div", { children: [_jsx("h3", { className: "text-xl font-bold", children: resultado.sucesso ? 'Importação Concluída!' : 'Erro na Importação' }), _jsx("p", { className: "text-sm text-muted-foreground", children: resultado.sucesso
                                                    ? `${resultado.importados} de ${resultado.total_registros} registros importados`
                                                    : resultado.erro })] })] }), resultado.sucesso && (_jsxs("button", { onClick: baixarRelatorio, className: "flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors text-sm", children: [_jsx(Download, { className: "w-4 h-4" }), "Baixar Relat\u00F3rio"] }))] }), resultado.sucesso && (_jsxs("div", { className: "grid grid-cols-1 md:grid-cols-4 gap-4", children: [_jsxs("div", { className: "bg-background rounded-lg p-4", children: [_jsx("p", { className: "text-sm text-muted-foreground mb-1", children: "Total" }), _jsx("p", { className: "text-2xl font-bold", children: resultado.total_registros })] }), _jsxs("div", { className: "bg-green-500/20 rounded-lg p-4", children: [_jsx("p", { className: "text-sm text-green-400 mb-1", children: "Importados" }), _jsx("p", { className: "text-2xl font-bold text-green-400", children: resultado.importados })] }), _jsxs("div", { className: "bg-red-500/20 rounded-lg p-4", children: [_jsx("p", { className: "text-sm text-red-400 mb-1", children: "Erros" }), _jsx("p", { className: "text-2xl font-bold text-red-400", children: resultado.erros })] }), _jsxs("div", { className: "bg-yellow-500/20 rounded-lg p-4", children: [_jsx("p", { className: "text-sm text-yellow-400 mb-1", children: "Avisos" }), _jsx("p", { className: "text-2xl font-bold text-yellow-400", children: resultado.avisos })] })] })), resultado.registros_com_erro?.length > 0 && (_jsxs("div", { className: "mt-6", children: [_jsxs("div", { className: "flex items-center gap-2 mb-3", children: [_jsx(AlertCircle, { className: "w-5 h-5 text-red-400" }), _jsx("h4", { className: "font-semibold", children: "Registros com Erro" })] }), _jsxs("div", { className: "bg-background rounded-lg p-4 max-h-64 overflow-y-auto space-y-2", children: [resultado.registros_com_erro.slice(0, 10).map((registro, idx) => (_jsxs("div", { className: "border-b border-border pb-2 last:border-0", children: [_jsxs("p", { className: "font-medium", children: ["Pasta: ", registro.pasta] }), _jsx("p", { className: "text-sm text-red-400", children: registro._erros })] }, idx))), resultado.registros_com_erro.length > 10 && (_jsxs("p", { className: "text-sm text-muted-foreground text-center pt-2", children: ["+ ", resultado.registros_com_erro.length - 10, " registros com erro"] }))] })] })), resultado.sucesso && (_jsxs("div", { className: "mt-6 pt-6 border-t border-border flex items-center justify-between text-sm", children: [_jsxs("div", { className: "flex items-center gap-4", children: [_jsxs("span", { className: "text-muted-foreground", children: ["Taxa de sucesso: ", _jsxs("span", { className: "text-green-400 font-bold", children: [resultado.taxa_sucesso, "%"] })] }), _jsxs("span", { className: "text-muted-foreground", children: ["Tempo: ", _jsxs("span", { className: "font-semibold", children: [resultado.tempo_segundos, "s"] })] })] }), _jsx("button", { onClick: () => {
                                    setArquivo(null);
                                    setResultado(null);
                                    setProgresso(0);
                                }, className: "px-4 py-2 bg-primary hover:bg-primary/90 rounded-lg transition-colors", children: "Nova Importa\u00E7\u00E3o" })] }))] })), _jsxs("div", { className: "bg-blue-500/10 border border-blue-500/20 rounded-xl p-6", children: [_jsx("h4", { className: "font-semibold text-blue-400 mb-3", children: "\uD83D\uDCA1 Instru\u00E7\u00F5es de Importa\u00E7\u00E3o" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4 text-sm", children: [_jsxs("div", { children: [_jsx("p", { className: "font-medium mb-2", children: "Campos Obrigat\u00F3rios:" }), _jsxs("ul", { className: "space-y-1 text-muted-foreground", children: [_jsxs("li", { children: ["\u2022 ", _jsx("code", { className: "bg-accent px-1 rounded", children: "pasta" }), " - N\u00FAmero da pasta"] }), _jsxs("li", { children: ["\u2022 ", _jsx("code", { className: "bg-accent px-1 rounded", children: "natureza" }), " - Tribut\u00E1rio/Trabalhista/C\u00EDvel"] })] })] }), _jsxs("div", { children: [_jsx("p", { className: "font-medium mb-2", children: "Campos Opcionais:" }), _jsxs("ul", { className: "space-y-1 text-muted-foreground", children: [_jsxs("li", { children: ["\u2022 ", _jsx("code", { className: "bg-accent px-1 rounded", children: "numero_cnj" }), " - N\u00FAmero CNJ"] }), _jsxs("li", { children: ["\u2022 ", _jsx("code", { className: "bg-accent px-1 rounded", children: "valor_causa" }), " - Valor da causa"] }), _jsxs("li", { children: ["\u2022 ", _jsx("code", { className: "bg-accent px-1 rounded", children: "data_distribuicao" }), " - Data"] })] })] })] })] })] }));
}
