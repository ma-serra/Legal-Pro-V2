import { useState } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { FileText, Download, Eye, Calendar, Filter } from 'lucide-react'
import api from '../../lib/api'

interface ReportFilters {
    data_inicio: string
    data_fim: string
    area_direito: string
    status: string
    tipo_relatorio: string
}

export default function ProcessReports() {
    const [filters, setFilters] = useState<ReportFilters>({
        data_inicio: '',
        data_fim: '',
        area_direito: '',
        status: '',
        tipo_relatorio: 'completo'
    })
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)
    const [generating, setGenerating] = useState(false)

    const handleFilterChange = (field: keyof ReportFilters, value: string) => {
        setFilters(prev => ({ ...prev, [field]: value }))
    }

    // Endpoint: POST /processos/relatorios/gerar-previa
    const handleGeneratePreview = async () => {
        setGenerating(true)
        try {
            const response = await api.post('/processos/relatorios/gerar-previa', filters)
            setPreviewUrl(response.data.preview_url)
        } catch (error) {
            console.error('Error generating preview:', error)
            alert('Erro ao gerar prévia')
        } finally {
            setGenerating(false)
        }
    }

    // Endpoint: POST /processos/relatorios/exportar
    const handleExportReport = async (formato: 'pdf' | 'excel' | 'word') => {
        try {
            const response = await api.post('/processos/relatorios/exportar', {
                ...filters,
                formato
            }, {
                responseType: 'blob'
            })

            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            const extension = formato === 'excel' ? 'xlsx' : formato === 'word' ? 'docx' : formato
            link.setAttribute('download', `relatorio-processos.${extension}`)
            document.body.appendChild(link)
            link.click()
            link.remove()
        } catch (error) {
            console.error('Error exporting report:', error)
            alert('Erro ao exportar relatório')
        }
    }

    return (
        <AdminLayout>
            <PageHeader
                title="Relatórios de Processos"
                description="Gere relatórios personalizados dos seus processos"
            />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Filters Panel */}
                <div className="lg:col-span-1">
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                            <Filter className="w-5 h-5" />
                            Filtros
                        </h3>

                        <div className="space-y-4">
                            {/* Date Range */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    <Calendar className="w-4 h-4 inline mr-1" />
                                    Período
                                </label>
                                <div className="space-y-2">
                                    <input
                                        type="date"
                                        value={filters.data_inicio}
                                        onChange={(e) => handleFilterChange('data_inicio', e.target.value)}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                                        placeholder="Data início"
                                    />
                                    <input
                                        type="date"
                                        value={filters.data_fim}
                                        onChange={(e) => handleFilterChange('data_fim', e.target.value)}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                                        placeholder="Data fim"
                                    />
                                </div>
                            </div>

                            {/* Area */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Área do Direito
                                </label>
                                <select
                                    value={filters.area_direito}
                                    onChange={(e) => handleFilterChange('area_direito', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                                >
                                    <option value="">Todas</option>
                                    <option value="civel">Cível</option>
                                    <option value="trabalhista">Trabalhista</option>
                                    <option value="criminal">Criminal</option>
                                    <option value="tributario">Tributário</option>
                                    <option value="familia">Família</option>
                                </select>
                            </div>

                            {/* Status */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Status
                                </label>
                                <select
                                    value={filters.status}
                                    onChange={(e) => handleFilterChange('status', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                                >
                                    <option value="">Todos</option>
                                    <option value="ativo">Ativo</option>
                                    <option value="suspenso">Suspenso</option>
                                    <option value="arquivado">Arquivado</option>
                                    <option value="finalizado">Finalizado</option>
                                </select>
                            </div>

                            {/* Report Type */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Tipo de Relatório
                                </label>
                                <select
                                    value={filters.tipo_relatorio}
                                    onChange={(e) => handleFilterChange('tipo_relatorio', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                                >
                                    <option value="completo">Completo</option>
                                    <option value="resumido">Resumido</option>
                                    <option value="estatistico">Estatístico</option>
                                    <option value="financeiro">Financeiro</option>
                                </select>
                            </div>

                            {/* Actions */}
                            <div className="pt-4 space-y-2">
                                <button
                                    onClick={handleGeneratePreview}
                                    disabled={generating}
                                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                                >
                                    <Eye className="w-4 h-4" />
                                    {generating ? 'Gerando...' : 'Gerar Prévia'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Preview/Export Panel */}
                <div className="lg:col-span-2">
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">
                            Prévia e Exportação
                        </h3>

                        {previewUrl ? (
                            <div className="space-y-4">
                                {/* Preview */}
                                <div className="border border-gray-300 rounded-lg p-4 bg-gray-50 min-h-[400px]">
                                    <p className="text-sm text-gray-600 mb-2">Prévia do relatório:</p>
                                    <div className="bg-white p-6 rounded">
                                        {/* Mock preview content */}
                                        <h4 className="font-bold mb-4">Relatório de Processos Jurídicos</h4>
                                        <div className="space-y-2 text-sm">
                                            <p><strong>Período:</strong> {filters.data_inicio || 'Não especificado'} a {filters.data_fim || 'Não especificado'}</p>
                                            <p><strong>Área:</strong> {filters.area_direito || 'Todas'}</p>
                                            <p><strong>Status:</strong> {filters.status || 'Todos'}</p>
                                            <p><strong>Tipo:</strong> {filters.tipo_relatorio}</p>
                                        </div>
                                        <div className="mt-6 p-4 bg-gray-50 rounded">
                                            <p className="text-sm text-gray-500">
                                                [Conteúdo do relatório será exibido aqui]
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                {/* Export Options */}
                                <div>
                                    <p className="text-sm font-medium text-gray-700 mb-3">Exportar como:</p>
                                    <div className="flex gap-3">
                                        <button
                                            onClick={() => handleExportReport('pdf')}
                                            className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                        >
                                            <Download className="w-4 h-4" />
                                            PDF
                                        </button>
                                        <button
                                            onClick={() => handleExportReport('excel')}
                                            className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                        >
                                            <Download className="w-4 h-4" />
                                            Excel
                                        </button>
                                        <button
                                            onClick={() => handleExportReport('word')}
                                            className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                        >
                                            <Download className="w-4 h-4" />
                                            Word
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="flex items-center justify-center h-[400px] text-center">
                                <div>
                                    <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                                    <h4 className="text-lg font-medium text-gray-900 mb-2">
                                        Nenhuma prévia gerada
                                    </h4>
                                    <p className="text-gray-600">
                                        Configure os filtros e clique em "Gerar Prévia"
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </AdminLayout>
    )
}
