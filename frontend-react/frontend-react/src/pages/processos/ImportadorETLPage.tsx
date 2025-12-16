/**
 * ImportadorProcessosETL - Upload com ETL Completo
 * XLSX, CSV, JSON com normalização avançada
 */
import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
    Upload, FileSpreadsheet, FileJson, CheckCircle, XCircle,
    AlertTriangle, Download, RefreshCw, Database
} from 'lucide-react';
import * as XLSX from 'xlsx';
import api from '../../lib/api';

interface ProcessoNormalizado {
    linha: number;
    dados: any;
    status: 'valido' | 'invalido' | 'warning';
    erros: string[];
    warnings: string[];
}

interface ResultadoNormalizacao {
    total: number;
    validos: number;
    invalidos: number;
    warnings: number;
    processos: ProcessoNormalizado[];
}

export default function ImportadorProcessosETL() {
    const [arquivo, setArquivo] = useState<File | null>(null);
    const [processando, setProcessando] = useState(false);
    const [resultado, setResultado] = useState<ResultadoNormalizacao | null>(null);
    const [etapa, setEtapa] = useState<'upload' | 'normalizacao' | 'preview' | 'importando'>('upload');

    // ========================================================================
    // ETL - NORMALIZAÇÃO DE DADOS
    // ========================================================================

    /**
     * 🔤 Strings: Trim + remove caracteres invisíveis
     */
    const normalizarString = (valor: any): string => {
        if (valor === null || valor === undefined) return '';
        return String(valor)
            .trim()
            .replace(/[\u200B-\u200D\uFEFF\u00A0]/g, '') // Remove zero-width, NBSP
            .replace(/\s+/g, ' '); // Normaliza espaços múltiplos
    };

    /**
     * 🔢 Números: Limpa texto, converte int/float
     */
    const normalizarNumero = (valor: any): number | null => {
        if (valor === null || valor === undefined || valor === '') return null;

        // Se já é número, retornar
        if (typeof valor === 'number') return valor;

        // Limpar string
        const limpo = String(valor)
            .trim()
            .replace(/[^\d.,\-]/g, '')  // Manter apenas dígitos, vírgula, ponto, hífen
            .replace(/\./g, '')         // Remove pontos de milhar
            .replace(',', '.');          // Troca vírgula decimal por ponto

        const numero = parseFloat(limpo);
        return isNaN(numero) ? null : numero;
    };

    /**
     * ✅ Boolean: true/false/sim/não/1/0
     */
    const normalizarBoolean = (valor: any): boolean | null => {
        if (valor === null || valor === undefined) return null;

        // Se já é boolean
        if (typeof valor === 'boolean') return valor;

        const str = String(valor).toLowerCase().trim();

        // TRUE
        const verdadeiro = ['true', 't', 'sim', 's', 'yes', 'y', '1', 'verdadeiro', 'v'];
        if (verdadeiro.includes(str)) return true;

        // FALSE
        const falso = ['false', 'f', 'não', 'nao', 'no', 'n', '0', 'falso'];
        if (falso.includes(str)) return false;

        return null;
    };

    /**
     * 📅 Datas: DD/MM/YYYY → ISO (YYYY-MM-DD)
     */
    const normalizarData = (valor: any): string | null => {
        if (!valor) return null;

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
            } catch {
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
            } catch { }
        }

        return null;
    };

    /**
     * 📋 JSON: Parse automático de arrays/objects
     */
    const normalizarJSON = (valor: any): any => {
        if (!valor) return null;

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
                } catch {
                    return null;
                }
            }
        }

        return null;
    };

    /**
     * 🆔 UUID: Validação de formato
     */
    const validarUUID = (valor: any): string | null => {
        if (!valor) return null;

        const str = String(valor).trim();
        const regexUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

        return regexUUID.test(str) ? str : null;
    };

    // ========================================================================
    // NORMALIZAÇÃO DE PROCESSO COMPLETO
    // ========================================================================

    const normalizarProcesso = (linha: any, numeroLinha: number): ProcessoNormalizado => {
        const erros: string[] = [];
        const warnings: string[] = [];

        // Dados básicos
        const dados: any = {
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

        const status: 'valido' | 'invalido' | 'warning' =
            erros.length > 0 ? 'invalido' :
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

    const processarArquivo = async (file: File) => {
        setProcessando(true);
        setEtapa('normalizacao');

        try {
            let dadosRaw: any[] = [];

            // Ler arquivo conforme tipo
            if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
                const buffer = await file.arrayBuffer();
                const workbook = XLSX.read(buffer);
                const sheetName = workbook.SheetNames[0];
                const worksheet = workbook.Sheets[sheetName];
                dadosRaw = XLSX.utils.sheet_to_json(worksheet);

            } else if (file.name.endsWith('.csv')) {
                const texto = await file.text();
                const workbook = XLSX.read(texto, { type: 'string' });
                const sheetName = workbook.SheetNames[0];
                const worksheet = workbook.Sheets[sheetName];
                dadosRaw = XLSX.utils.sheet_to_json(worksheet);

            } else if (file.name.endsWith('.json')) {
                const texto = await file.text();
                dadosRaw = JSON.parse(texto);

                if (!Array.isArray(dadosRaw)) {
                    throw new Error('JSON deve ser um array de objetos');
                }
            } else {
                throw new Error('Formato não suportado. Use XLSX, CSV ou JSON.');
            }

            if (dadosRaw.length === 0) {
                throw new Error('Arquivo vazio');
            }

            // Normalizar com ETL
            const processosNormalizados = dadosRaw.map((linha, index) =>
                normalizarProcesso(linha, index + 2) // Linha 2+ (header = 1)
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

        } catch (error: any) {
            alert(`Erro ao processar arquivo: ${error.message}`);
            setEtapa('upload');
        } finally {
            setProcessando(false);
        }
    };

    const importarParaBackend = async () => {
        if (!resultado) return;

        const processosValidos = resultado.processos.filter(
            p => p.status === 'valido' || p.status === 'warning'
        );

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

        } catch (error: any) {
            alert(`❌ Erro ao importar: ${error.response?.data?.error || error.message}`);
            setEtapa('preview');
        } finally {
            setProcessando(false);
        }
    };

    // Dropzone
    const onDrop = useCallback((acceptedFiles: File[]) => {
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

    return (
        <div className="p-6 max-w-[1600px] mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <Database className="w-8 h-8 text-primary" />
                        Importação ETL de Processos
                    </h1>
                    <p className="text-muted-foreground mt-2">
                        Upload XLSX/CSV/JSON com normalização automática completa
                    </p>
                </div>

                <button
                    onClick={downloadTemplate}
                    className="px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg flex items-center gap-2 transition-colors"
                >
                    <Download className="w-4 h-4" />
                    Template Excel
                </button>
            </div>

            {/* ETL Info */}
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
                <h3 className="font-bold text-blue-300 mb-2">🔧 Normalização Automática (ETL)</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
                    <div className="bg-background/50 rounded p-2">
                        <div className="font-semibold text-blue-400 mb-1">🔤 Strings</div>
                        <div className="text-muted-foreground">Trim + caracteres invisíveis</div>
                    </div>
                    <div className="bg-background/50 rounded p-2">
                        <div className="font-semibold text-green-400 mb-1">🔢 Números</div>
                        <div className="text-muted-foreground">Limpa + int/float</div>
                    </div>
                    <div className="bg-background/50 rounded p-2">
                        <div className="font-semibold text-yellow-400 mb-1">✅ Boolean</div>
                        <div className="text-muted-foreground">sim/não/1/0</div>
                    </div>
                    <div className="bg-background/50 rounded p-2">
                        <div className="font-semibold text-purple-400 mb-1">📅 Datas</div>
                        <div className="text-muted-foreground">DD/MM/YYYY→ISO</div>
                    </div>
                    <div className="bg-background/50 rounded p-2">
                        <div className="font-semibold text-orange-400 mb-1">📋 JSON</div>
                        <div className="text-muted-foreground">Parse auto</div>
                    </div>
                    <div className="bg-background/50 rounded p-2">
                        <div className="font-semibold text-pink-400 mb-1">🆔 UUID</div>
                        <div className="text-muted-foreground">Validação</div>
                    </div>
                </div>
            </div>

            {/* Upload Zone */}
            {etapa === 'upload' && (
                <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-xl p-16 text-center cursor-pointer transition-all ${isDragActive
                            ? 'border-primary bg-primary/10 scale-105'
                            : 'border-border hover:border-primary/50 bg-card'
                        }`}
                >
                    <input {...getInputProps()} />
                    <Upload className="w-20 h-20 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-xl font-medium mb-2">
                        {isDragActive
                            ? '📥 Solte aqui...'
                            : 'Arraste arquivo ou clique'}
                    </p>
                    <p className="text-sm text-muted-foreground mb-6">
                        XLSX, XLS, CSV, JSON
                    </p>
                    <div className="flex items-center justify-center gap-6 text-xs text-muted-foreground">
                        <div className="flex flex-col items-center gap-1">
                            <FileSpreadsheet className="w-6 h-6" />
                            <span>Excel</span>
                        </div>
                        <div className="flex flex-col items-center gap-1">
                            <FileJson className="w-6 h-6" />
                            <span>JSON</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Processando */}
            {(etapa === 'normalizacao' || etapa === 'importando') && processando && (
                <div className="bg-card border border-border rounded-xl p-8 text-center">
                    <RefreshCw className="w-12 h-12 mx-auto mb-4 text-primary animate-spin" />
                    <p className="text-lg font-medium">
                        {etapa === 'normalizacao' ? '🔧 Normalizando dados (ETL)...' : '📤 Importando para banco...'}
                    </p>
                    <p className="text-sm text-muted-foreground mt-2">
                        {arquivo?.name}
                    </p>
                </div>
            )}

            {/* Preview */}
            {etapa === 'preview' && resultado && (
                <div className="space-y-6">
                    {/* Stats */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-card border border-border rounded-lg p-4">
                            <div className="text-sm text-muted-foreground mb-1">Total</div>
                            <div className="text-3xl font-bold">{resultado.total}</div>
                        </div>
                        <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
                            <div className="text-sm text-green-300 mb-1">✅ Válidos</div>
                            <div className="text-3xl font-bold text-green-400">{resultado.validos}</div>
                        </div>
                        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                            <div className="text-sm text-yellow-300 mb-1">⚠️ Warnings</div>
                            <div className="text-3xl font-bold text-yellow-400">{resultado.warnings}</div>
                        </div>
                        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                            <div className="text-sm text-red-300 mb-1">❌ Inválidos</div>
                            <div className="text-3xl font-bold text-red-400">{resultado.invalidos}</div>
                        </div>
                    </div>

                    {/* Preview Table */}
                    <div className="bg-card border border-border rounded-xl overflow-hidden">
                        <div className="p-4 border-b border-border bg-accent flex items-center justify-between">
                            <h3 className="font-bold">Preview Pós-ETL</h3>
                            <span className="text-sm text-muted-foreground">{arquivo?.name}</span>
                        </div>

                        <div className="overflow-x-auto max-h-[500px]">
                            <table className="w-full">
                                <thead className="bg-accent sticky top-0">
                                    <tr>
                                        <th className="text-left p-2 text-xs font-medium">Ln</th>
                                        <th className="text-left p-2 text-xs font-medium">Status</th>
                                        <th className="text-left p-2 text-xs font-medium">CNJ/Pasta</th>
                                        <th className="text-left p-2 text-xs font-medium">Natureza</th>
                                        <th className="text-left p-2 text-xs font-medium">Valor Causa</th>
                                        <th className="text-left p-2 text-xs font-medium">Problemas</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {resultado.processos.map((proc) => (
                                        <tr key={proc.linha} className="border-b border-border/50 hover:bg-accent/30">
                                            <td className="p-2 text-xs text-muted-foreground">{proc.linha}</td>
                                            <td className="p-2">
                                                {proc.status === 'valido' && <CheckCircle className="w-4 h-4 text-green-500" />}
                                                {proc.status === 'warning' && <AlertTriangle className="w-4 h-4 text-yellow-500" />}
                                                {proc.status === 'invalido' && <XCircle className="w-4 h-4 text-red-500" />}
                                            </td>
                                            <td className="p-2 text-xs">{proc.dados.numero_cnj || proc.dados.pasta}</td>
                                            <td className="p-2 text-xs">
                                                {proc.dados.natureza_id === 1 && 'Trib'}
                                                {proc.dados.natureza_id === 2 && 'Trab'}
                                                {proc.dados.natureza_id === 3 && 'Cível'}
                                                {!proc.dados.natureza_id && '-'}
                                            </td>
                                            <td className="p-2 text-xs">
                                                {proc.dados.valor_causa
                                                    ? `R$ ${proc.dados.valor_causa.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`
                                                    : '-'}
                                            </td>
                                            <td className="p-2 text-xs">
                                                {proc.erros.map((e, i) => (
                                                    <div key={i} className="text-red-400">{e}</div>
                                                ))}
                                                {proc.warnings.map((w, i) => (
                                                    <div key={i} className="text-yellow-400">{w}</div>
                                                ))}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center justify-between">
                        <button
                            onClick={() => {
                                setEtapa('upload');
                                setArquivo(null);
                                setResultado(null);
                            }}
                            className="px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors"
                        >
                            ← Voltar
                        </button>
                        <button
                            onClick={importarParaBackend}
                            disabled={processando || resultado.validos + resultado.warnings === 0}
                            className="px-8 py-3 bg-primary hover:bg-primary/90 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium text-lg"
                        >
                            {processando ? 'Importando...' : `Importar ${resultado.validos + resultado.warnings} Processos`}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
