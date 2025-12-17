import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * ImportadorProcessosETL - Upload com ETL Completo
 * XLSX, CSV, JSON com normalização avançada
 */
import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileSpreadsheet, FileJson, CheckCircle, XCircle, AlertTriangle, Download, RefreshCw, Database } from 'lucide-react';
import * as XLSX from 'xlsx';
import api from '../../lib/api';
export default function ImportadorProcessosETL() {
    const [arquivo, setArquivo] = useState(null);
    const [processando, setProcessando] = useState(false);
    const [resultado, setResultado] = useState(null);
    const [etapa, setEtapa] = useState('upload');
    // ========================================================================
    // ETL - NORMALIZAÇÃO DE DADOS
    // ========================================================================
    /**
     * 🔤 Strings: Trim + remove caracteres invisíveis
     */
    const normalizarString = (valor) => {
        if (valor === null || valor === undefined)
            return '';
        return String(valor)
            .trim()
            .replace(/[\u200B-\u200D\uFEFF\u00A0]/g, '') // Remove zero-width, NBSP
            .replace(/\s+/g, ' '); // Normaliza espaços múltiplos
    };
    /**
     * 🔢 Números: Limpa texto, converte int/float
     */
    const normalizarNumero = (valor) => {
        if (valor === null || valor === undefined || valor === '')
            return null;
        // Se já é número, retornar
        if (typeof valor === 'number')
            return valor;
        // Limpar string
        const limpo = String(valor)
            .trim()
            .replace(/[^\d.,\-]/g, '') // Manter apenas dígitos, vírgula, ponto, hífen
            .replace(/\./g, '') // Remove pontos de milhar
            .replace(',', '.'); // Troca vírgula decimal por ponto
        const numero = parseFloat(limpo);
        return isNaN(numero) ? null : numero;
    };
    /**
     * ✅ Boolean: true/false/sim/não/1/0
     */
    const normalizarBoolean = (valor) => {
        if (valor === null || valor === undefined)
            return null;
        // Se já é boolean
        if (typeof valor === 'boolean')
            return valor;
        const str = String(valor).toLowerCase().trim();
        // TRUE
        const verdadeiro = ['true', 't', 'sim', 's', 'yes', 'y', '1', 'verdadeiro', 'v'];
        if (verdadeiro.includes(str))
            return true;
        // FALSE
        const falso = ['false', 'f', 'não', 'nao', 'no', 'n', '0', 'falso'];
        if (falso.includes(str))
            return false;
        return null;
    };
    /**
     * 📅 Datas: DD/MM/YYYY → ISO (YYYY-MM-DD)
     */
    const normalizarData = (valor) => {
        if (!valor)
            return null;
        const str = String(valor).trim();
        // 1. DD/MM/YYYY ou D/M/YYYY
        const regexDDMMYYYY = /^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})$/;
        const matchDDMMYYYY = str.match(regexDDMMYYYY);
        if (matchDDMMYYYY) {
            const [, dia, mes, ano] = matchDDMMYYYY;
            return `${ano}-${mes.padStart(2, '0')}-${dia.padStart(2, '0')}`;
        }
        // 2. ISO: YYYY-MM-DD
        const regexISO = /^(\d{4})-(\d{1,2})-(\d{1,2})$/;
        const matchISO = str.match(regexISO);
        if (matchISO) {
            const [, ano, mes, dia] = matchISO;
            return `${ano}-${mes.padStart(2, '0')}-${dia.padStart(2, '0')}`;
        }
        // 3. Data Excel (número serial: 40000-60000)
        const numero = parseFloat(str);
        if (!isNaN(numero) && numero > 40000 && numero < 60000) {
            try {
                const dataExcel = XLSX.SSF.parse_date_code(numero);
                const ano = dataExcel.y;
                const mes = String(dataExcel.m).padStart(2, '0');
                const dia = String(dataExcel.d).padStart(2, '0');
                return `${ano}-${mes}-${dia}`;
            }
            catch {
                return null;
            }
        }
        // 4. Timestamp ISO com hora
        if (str.includes('T') || str.includes(' ')) {
            try {
                const date = new Date(str);
                if (!isNaN(date.getTime())) {
                    const ano = date.getFullYear();
                    const mes = String(date.getMonth() + 1).padStart(2, '0');
                    const dia = String(date.getDate()).padStart(2, '0');
                    return `${ano}-${mes}-${dia}`;
                }
            }
            catch { }
        }
        return null;
    };
    /**
     * 📋 JSON: Parse automático de arrays/objects
     */
    const normalizarJSON = (valor) => {
        if (!valor)
            return null;
        // Já é objeto/array
        if (typeof valor === 'object') {
            return valor;
        }
        // Tentar parse string JSON
        if (typeof valor === 'string') {
            const str = valor.trim();
            if ((str.startsWith('{') && str.endsWith('}')) ||
                (str.startsWith('[') && str.endsWith(']'))) {
                try {
                    return JSON.parse(str);
                }
                catch {
                    return null;
                }
            }
        }
        return null;
    };
    /**
     * 🆔 UUID: Validação de formato
     */
    const validarUUID = (valor) => {
        if (!valor)
            return null;
        const str = String(valor).trim();
        const regexUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
        return regexUUID.test(str) ? str : null;
    };
    // ========================================================================
    // NORMALIZAÇÃO DE PROCESSO COMPLETO
    // ========================================================================
    const normalizarProcesso = (linha, numeroLinha) => {
        const erros = [];
        const warnings = [];
        // Dados básicos
        const dados = {
            // Strings
            numero_cnj: normalizarString(linha['Número CNJ'] || linha['numero_cnj'] || linha['numero']),
            pasta: normalizarString(linha['Pasta'] || linha['pasta'] || linha['numero_pasta']),
            titulo: normalizarString(linha['Título'] || linha['titulo'] || linha['assunto']),
            autor: normalizarString(linha['Autor'] || linha['autor'] || linha['nome_autor']),
            reu: normalizarString(linha['Réu'] || linha['reu'] || linha['nome_reu']),
            // IDs (números)
            natureza_id: normalizarNumero(linha['Natureza ID'] || linha['natureza_id'] || linha['natureza']),
            status_id: normalizarNumero(linha['Status ID'] || linha['status_id'] || linha['status']),
            cliente_id: normalizarNumero(linha['Cliente ID'] || linha['cliente_id'] || linha['cliente']),
            fase_id: normalizarNumero(linha['Fase ID'] || linha['fase_id'] || linha['fase']),
            risco_id: normalizarNumero(linha['Risco ID'] || linha['risco_id'] || linha['risco']),
            // Datas
            data_distribuicao: normalizarData(linha['Data Distribuição'] || linha['data_distribuicao'] || linha['data']),
            // Valores (decimais)
            valor_causa: normalizarNumero(linha['Valor Causa'] || linha['valor_causa']),
            valor_envolvido: normalizarNumero(linha['Valor Envolvido'] || linha['valor_envolvido']),
            contingencia: normalizarNumero(linha['Contingência'] || linha['contingencia']),
            // UUID (se fornecido)
            uuid: validarUUID(linha['UUID'] || linha['uuid'])
        };
        // Validações obrigatórias
        if (!dados.numero_cnj && !dados.pasta) {
            erros.push('Número CNJ ou Pasta obrigatório');
        }
        if (!dados.natureza_id) {
            erros.push('Natureza ID obrigatório (1=Tributário, 2=Trabalhista, 3=Cível)');
        }
        // Warnings
        if (!dados.cliente_id) {
            warnings.push('Cliente ID não informado');
        }
        if (!dados.valor_causa && !dados.contingencia) {
            warnings.push('Valores financeiros não informados');
        }
        if (dados.data_distribuicao === null && linha['Data Distribuição']) {
            warnings.push('Data distribuição em formato inválido');
        }
        // Dados específicos TRIBUTÁRIO
        if (dados.natureza_id === 1) {
            dados.dados_tributario = {
                tributo_id: normalizarNumero(linha['Tributo ID'] || linha['tributo_id']),
                numero_aiim: normalizarString(linha['Número AIIM'] || linha['numero_aiim']),
                numero_cda: normalizarString(linha['Número CDA'] || linha['numero_cda']),
                valor_inscrito_cda: normalizarNumero(linha['Valor CDA'] || linha['valor_inscrito_cda'] || linha['valor_cda']),
                valor_principal: normalizarNumero(linha['Valor Principal'] || linha['valor_principal']),
                valor_multa: normalizarNumero(linha['Valor Multa'] || linha['valor_multa']),
                percentual_multa: normalizarNumero(linha['Percentual Multa'] || linha['percentual_multa']),
                valor_juros: normalizarNumero(linha['Valor Juros'] || linha['valor_juros']),
                indice_juros: normalizarString(linha['Índice Juros'] || linha['indice_juros'] || 'SELIC')
            };
            if (!dados.dados_tributario.tributo_id) {
                warnings.push('Tributo ID não informado (processo tributário)');
            }
        }
        // Dados específicos TRABALHISTA
        if (dados.natureza_id === 2) {
            dados.dados_trabalhista = {
                tolerancia_acordo: normalizarNumero(linha['Tolerância Acordo'] || linha['tolerancia_acordo']),
                acordo_realizado: normalizarBoolean(linha['Acordo Realizado'] || linha['acordo_realizado']),
                data_acordo: normalizarData(linha['Data Acordo'] || linha['data_acordo'])
            };
        }
        // Dados específicos CÍVEL
        if (dados.natureza_id === 3) {
            dados.dados_civel = {
                tolerancia_acordo: normalizarNumero(linha['Tolerância Acordo'] || linha['tolerancia_acordo']),
                acordo_realizado: normalizarBoolean(linha['Acordo Realizado'] || linha['acordo_realizado']),
                data_acordo: normalizarData(linha['Data Acordo'] || linha['data_acordo'])
            };
        }
        const status = erros.length > 0 ? 'invalido' :
            warnings.length > 0 ? 'warning' :
                'valido';
        return {
            linha: numeroLinha,
            dados,
            status,
            erros,
            warnings
        };
    };
    // ========================================================================
    // PROCESSAMENTO DE ARQUIVO
    // ========================================================================
    const processarArquivo = async (file) => {
        setProcessando(true);
        setEtapa('normalizacao');
        try {
            let dadosRaw = [];
            // Ler arquivo conforme tipo
            if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
                const buffer = await file.arrayBuffer();
                const workbook = XLSX.read(buffer);
                const sheetName = workbook.SheetNames[0];
                const worksheet = workbook.Sheets[sheetName];
                dadosRaw = XLSX.utils.sheet_to_json(worksheet);
            }
            else if (file.name.endsWith('.csv')) {
                const texto = await file.text();
                const workbook = XLSX.read(texto, { type: 'string' });
                const sheetName = workbook.SheetNames[0];
                const worksheet = workbook.Sheets[sheetName];
                dadosRaw = XLSX.utils.sheet_to_json(worksheet);
            }
            else if (file.name.endsWith('.json')) {
                const texto = await file.text();
                dadosRaw = JSON.parse(texto);
                if (!Array.isArray(dadosRaw)) {
                    throw new Error('JSON deve ser um array de objetos');
                }
            }
            else {
                throw new Error('Formato não suportado. Use XLSX, CSV ou JSON.');
            }
            if (dadosRaw.length === 0) {
                throw new Error('Arquivo vazio');
            }
            // Normalizar com ETL
            const processosNormalizados = dadosRaw.map((linha, index) => normalizarProcesso(linha, index + 2) // Linha 2+ (header = 1)
            );
            const validos = processosNormalizados.filter(p => p.status === 'valido').length;
            const invalidos = processosNormalizados.filter(p => p.status === 'invalido').length;
            const warningsCount = processosNormalizados.filter(p => p.status === 'warning').length;
            setResultado({
                total: processosNormalizados.length,
                validos,
                invalidos,
                warnings: warningsCount,
                processos: processosNormalizados
            });
            setEtapa('preview');
        }
        catch (error) {
            alert(`Erro ao processar arquivo: ${error.message}`);
            setEtapa('upload');
        }
        finally {
            setProcessando(false);
        }
    };
    const importarParaBackend = async () => {
        if (!resultado)
            return;
        const processosValidos = resultado.processos.filter(p => p.status === 'valido' || p.status === 'warning');
        if (processosValidos.length === 0) {
            alert('Nenhum processo válido para importar');
            return;
        }
        setProcessando(true);
        setEtapa('importando');
        try {
            const response = await api.post('/api/processos/importar-lote', {
                processos: processosValidos.map(p => p.dados)
            });
            alert(`✅ ${response.data.importados || processosValidos.length} processos importados com sucesso!`);
            // Reset
            setEtapa('upload');
            setArquivo(null);
            setResultado(null);
        }
        catch (error) {
            alert(`❌ Erro ao importar: ${error.response?.data?.error || error.message}`);
            setEtapa('preview');
        }
        finally {
            setProcessando(false);
        }
    };
    // Dropzone
    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles.length > 0) {
            const file = acceptedFiles[0];
            setArquivo(file);
            processarArquivo(file);
        }
    }, []);
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
            'application/vnd.ms-excel': ['.xls'],
            'text/csv': ['.csv'],
            'application/json': ['.json']
        },
        maxFiles: 1,
        disabled: processando
    });
    // Download template
    const downloadTemplate = () => {
        const template = [{
                'Número CNJ': '0000000-00.0000.0.00.0000',
                'Pasta': 'PROC-2024-001',
                'Título': 'Processo Exemplo',
                'Autor': 'João da Silva',
                'Réu': 'Fazenda Nacional',
                'Natureza ID': 1,
                'Status ID': 1,
                'Cliente ID': 1,
                'Fase ID': 1,
                'Risco ID': 2,
                'Data Distribuição': '15/01/2024',
                'Valor Causa': '50.000,00',
                'Contingência': '25.000,00',
                'Tributo ID': 1,
                'Valor CDA': '40.000,00',
                'Valor Principal': '30.000,00',
                'Valor Multa': '8.000,00',
                'Percentual Multa': '40',
                'Índice Juros': 'SELIC'
            }];
        const ws = XLSX.utils.json_to_sheet(template);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'Template');
        XLSX.writeFile(wb, 'template_processos_etl.xlsx');
    };
    return (_jsxs("div", { className: "p-6 max-w-[1600px] mx-auto space-y-6", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsxs("h1", { className: "text-3xl font-bold flex items-center gap-3", children: [_jsx(Database, { className: "w-8 h-8 text-primary" }), "Importa\u00E7\u00E3o ETL de Processos"] }), _jsx("p", { className: "text-muted-foreground mt-2", children: "Upload XLSX/CSV/JSON com normaliza\u00E7\u00E3o autom\u00E1tica completa" })] }), _jsxs("button", { onClick: downloadTemplate, className: "px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg flex items-center gap-2 transition-colors", children: [_jsx(Download, { className: "w-4 h-4" }), "Template Excel"] })] }), _jsxs("div", { className: "bg-blue-500/10 border border-blue-500/30 rounded-xl p-4", children: [_jsx("h3", { className: "font-bold text-blue-300 mb-2", children: "\uD83D\uDD27 Normaliza\u00E7\u00E3o Autom\u00E1tica (ETL)" }), _jsxs("div", { className: "grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 text-xs", children: [_jsxs("div", { className: "bg-background/50 rounded p-2", children: [_jsx("div", { className: "font-semibold text-blue-400 mb-1", children: "\uD83D\uDD24 Strings" }), _jsx("div", { className: "text-muted-foreground", children: "Trim + caracteres invis\u00EDveis" })] }), _jsxs("div", { className: "bg-background/50 rounded p-2", children: [_jsx("div", { className: "font-semibold text-green-400 mb-1", children: "\uD83D\uDD22 N\u00FAmeros" }), _jsx("div", { className: "text-muted-foreground", children: "Limpa + int/float" })] }), _jsxs("div", { className: "bg-background/50 rounded p-2", children: [_jsx("div", { className: "font-semibold text-yellow-400 mb-1", children: "\u2705 Boolean" }), _jsx("div", { className: "text-muted-foreground", children: "sim/n\u00E3o/1/0" })] }), _jsxs("div", { className: "bg-background/50 rounded p-2", children: [_jsx("div", { className: "font-semibold text-purple-400 mb-1", children: "\uD83D\uDCC5 Datas" }), _jsx("div", { className: "text-muted-foreground", children: "DD/MM/YYYY\u2192ISO" })] }), _jsxs("div", { className: "bg-background/50 rounded p-2", children: [_jsx("div", { className: "font-semibold text-orange-400 mb-1", children: "\uD83D\uDCCB JSON" }), _jsx("div", { className: "text-muted-foreground", children: "Parse auto" })] }), _jsxs("div", { className: "bg-background/50 rounded p-2", children: [_jsx("div", { className: "font-semibold text-pink-400 mb-1", children: "\uD83C\uDD94 UUID" }), _jsx("div", { className: "text-muted-foreground", children: "Valida\u00E7\u00E3o" })] })] })] }), etapa === 'upload' && (_jsxs("div", { ...getRootProps(), className: `border-2 border-dashed rounded-xl p-16 text-center cursor-pointer transition-all ${isDragActive
                    ? 'border-primary bg-primary/10 scale-105'
                    : 'border-border hover:border-primary/50 bg-card'}`, children: [_jsx("input", { ...getInputProps() }), _jsx(Upload, { className: "w-20 h-20 mx-auto mb-4 text-muted-foreground" }), _jsx("p", { className: "text-xl font-medium mb-2", children: isDragActive
                            ? '📥 Solte aqui...'
                            : 'Arraste arquivo ou clique' }), _jsx("p", { className: "text-sm text-muted-foreground mb-6", children: "XLSX, XLS, CSV, JSON" }), _jsxs("div", { className: "flex items-center justify-center gap-6 text-xs text-muted-foreground", children: [_jsxs("div", { className: "flex flex-col items-center gap-1", children: [_jsx(FileSpreadsheet, { className: "w-6 h-6" }), _jsx("span", { children: "Excel" })] }), _jsxs("div", { className: "flex flex-col items-center gap-1", children: [_jsx(FileJson, { className: "w-6 h-6" }), _jsx("span", { children: "JSON" })] })] })] })), (etapa === 'normalizacao' || etapa === 'importando') && processando && (_jsxs("div", { className: "bg-card border border-border rounded-xl p-8 text-center", children: [_jsx(RefreshCw, { className: "w-12 h-12 mx-auto mb-4 text-primary animate-spin" }), _jsx("p", { className: "text-lg font-medium", children: etapa === 'normalizacao' ? '🔧 Normalizando dados (ETL)...' : '📤 Importando para banco...' }), _jsx("p", { className: "text-sm text-muted-foreground mt-2", children: arquivo?.name })] })), etapa === 'preview' && resultado && (_jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "grid grid-cols-2 md:grid-cols-4 gap-4", children: [_jsxs("div", { className: "bg-card border border-border rounded-lg p-4", children: [_jsx("div", { className: "text-sm text-muted-foreground mb-1", children: "Total" }), _jsx("div", { className: "text-3xl font-bold", children: resultado.total })] }), _jsxs("div", { className: "bg-green-500/10 border border-green-500/30 rounded-lg p-4", children: [_jsx("div", { className: "text-sm text-green-300 mb-1", children: "\u2705 V\u00E1lidos" }), _jsx("div", { className: "text-3xl font-bold text-green-400", children: resultado.validos })] }), _jsxs("div", { className: "bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4", children: [_jsx("div", { className: "text-sm text-yellow-300 mb-1", children: "\u26A0\uFE0F Warnings" }), _jsx("div", { className: "text-3xl font-bold text-yellow-400", children: resultado.warnings })] }), _jsxs("div", { className: "bg-red-500/10 border border-red-500/30 rounded-lg p-4", children: [_jsx("div", { className: "text-sm text-red-300 mb-1", children: "\u274C Inv\u00E1lidos" }), _jsx("div", { className: "text-3xl font-bold text-red-400", children: resultado.invalidos })] })] }), _jsxs("div", { className: "bg-card border border-border rounded-xl overflow-hidden", children: [_jsxs("div", { className: "p-4 border-b border-border bg-accent flex items-center justify-between", children: [_jsx("h3", { className: "font-bold", children: "Preview P\u00F3s-ETL" }), _jsx("span", { className: "text-sm text-muted-foreground", children: arquivo?.name })] }), _jsx("div", { className: "overflow-x-auto max-h-[500px]", children: _jsxs("table", { className: "w-full", children: [_jsx("thead", { className: "bg-accent sticky top-0", children: _jsxs("tr", { children: [_jsx("th", { className: "text-left p-2 text-xs font-medium", children: "Ln" }), _jsx("th", { className: "text-left p-2 text-xs font-medium", children: "Status" }), _jsx("th", { className: "text-left p-2 text-xs font-medium", children: "CNJ/Pasta" }), _jsx("th", { className: "text-left p-2 text-xs font-medium", children: "Natureza" }), _jsx("th", { className: "text-left p-2 text-xs font-medium", children: "Valor Causa" }), _jsx("th", { className: "text-left p-2 text-xs font-medium", children: "Problemas" })] }) }), _jsx("tbody", { children: resultado.processos.map((proc) => (_jsxs("tr", { className: "border-b border-border/50 hover:bg-accent/30", children: [_jsx("td", { className: "p-2 text-xs text-muted-foreground", children: proc.linha }), _jsxs("td", { className: "p-2", children: [proc.status === 'valido' && _jsx(CheckCircle, { className: "w-4 h-4 text-green-500" }), proc.status === 'warning' && _jsx(AlertTriangle, { className: "w-4 h-4 text-yellow-500" }), proc.status === 'invalido' && _jsx(XCircle, { className: "w-4 h-4 text-red-500" })] }), _jsx("td", { className: "p-2 text-xs", children: proc.dados.numero_cnj || proc.dados.pasta }), _jsxs("td", { className: "p-2 text-xs", children: [proc.dados.natureza_id === 1 && 'Trib', proc.dados.natureza_id === 2 && 'Trab', proc.dados.natureza_id === 3 && 'Cível', !proc.dados.natureza_id && '-'] }), _jsx("td", { className: "p-2 text-xs", children: proc.dados.valor_causa
                                                            ? `R$ ${proc.dados.valor_causa.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`
                                                            : '-' }), _jsxs("td", { className: "p-2 text-xs", children: [proc.erros.map((e, i) => (_jsx("div", { className: "text-red-400", children: e }, i))), proc.warnings.map((w, i) => (_jsx("div", { className: "text-yellow-400", children: w }, i)))] })] }, proc.linha))) })] }) })] }), _jsxs("div", { className: "flex items-center justify-between", children: [_jsx("button", { onClick: () => {
                                    setEtapa('upload');
                                    setArquivo(null);
                                    setResultado(null);
                                }, className: "px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors", children: "\u2190 Voltar" }), _jsx("button", { onClick: importarParaBackend, disabled: processando || resultado.validos + resultado.warnings === 0, className: "px-8 py-3 bg-primary hover:bg-primary/90 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium text-lg", children: processando ? 'Importando...' : `Importar ${resultado.validos + resultado.warnings} Processos` })] })] }))] }));
}
