import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader, StatCard } from '../../components/ui/AdminComponents'
import { FileText, Calendar, DollarSign, User, Download, Brain, Paperclip, ArrowLeft } from 'lucide-react'
import api from '../../lib/api'

interface Processo {
    id: number
    numero_processo: string
    client_id?: number
    client_name?: string
    area_direito: string
    status: string
    valor_causa?: number
    data_distribuicao: string
    data_ultima_movimentacao?: string
    vara: string
    comarca: string
    descricao?: string
    autor?: string
    reu?: string
    advogado_responsavel?: string
}

interface Anexo {
    id: number
    nome: string
    tipo: string
    tamanho: number
    data_upload: string
}

export default function ProcessoDetails() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [processo, setProcesso] = useState<Processo | null>(null)
    const [anexos, setAnexos] = useState<Anexo[]>([])
    const [loading, setLoading] = useState(true)
    const [generatingAnalysis, setGeneratingAnalysis] = useState(false)

    useEffect(() => {
        fetchProcesso()
        fetchAnexos()
    }, [id])

    // Endpoint: GET /processos/:processo_id
    const fetchProcesso = async () => {
        try {
            const response = await api.get(`/processos/${id}`)
            setProcesso(response.data)
        } catch (error) {
            console.error('Error fetching processo:', error)
        } finally {
            setLoading(false)
        }
    }

    // Endpoint: GET /api/processos/:processo_id/anexos
    const fetchAnexos = async () => {
        try {
            const response = await api.get(`/api/processos/${id}/anexos`)
            setAnexos(response.data)
        } catch (error) {
            console.error('Error fetching anexos:', error)
        }
    }

    // Endpoint: POST /api/processos/:processo_id/gerar-analise-ia
    const handleGenerateAnalysis = async () => {
        setGeneratingAnalysis(true)
        try {
            const response = await api.post(`/api/processos/${id}/gerar-analise-ia`)
            alert('Análise gerada com sucesso!')
            // Optionally download or display the analysis
        } catch (error) {
            console.error('Error generating analysis:', error)
            alert('Erro ao gerar análise')
        } finally {
            setGeneratingAnalysis(false)
        }
    }

    // Endpoint: POST /api/processos/:processo_id/exportar-analise-docx
    const handleExportAnalysis = async () => {
        try {
            const response = await api.post(`/api/processos/${id}/exportar-analise-docx`, {}, {
                responseType: 'blob'
            })

            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `analise-processo-${processo?.numero_processo}.docx`)
            document.body.appendChild(link)
            link.click()
            link.remove()
        } catch (error) {
            console.error('Error exporting analysis:', error)
            alert('Erro ao exportar análise')
        }
    }

    if (loading) {
        return (
            <AdminLayout>
                <div className="flex items-center justify-center h-96">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
            </AdminLayout>
        )
    }

    if (!processo) {
        return (
            <AdminLayout>
                <div className="text-center py-12">
                    <p className="text-gray-600">Processo não encontrado</p>
                    <Link to="/processos/lista" className="text-blue-600 hover:text-blue-700 mt-4 inline-block">
                        Voltar para lista
                    </Link>
                </div>
            </AdminLayout>
        )
    }

    return (
        <AdminLayout>
            {/* Header */}
            <div className="mb-6">
                <button
                    onClick={() => navigate('/processos/lista')}
                    className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Voltar para lista
                </button>

                <PageHeader
                    title={`Processo ${processo.numero_processo}`}
                    description={processo.area_direito}
                    action={
                        <div className="flex gap-2">
                            <button
                                onClick={handleGenerateAnalysis}
                                disabled={generatingAnalysis}
                                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                            >
                                <Brain className="w-4 h-4" />
                                {generatingAnalysis ? 'Gerando...' : 'Gerar Análise IA'}
                            </button>
                            <button
                                onClick={handleExportAnalysis}
                                className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                            >
                                <Download className="w-4 h-4" />
                                Exportar DOCX
                            </button>
                        </div>
                    }
                />
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <StatCard
                    title="Status"
                    value={processo.status || 'Ativo'}
                    icon={FileText}
                />
                <StatCard
                    title="Valor da Causa"
                    value={processo.valor_causa ? `R$ ${processo.valor_causa.toLocaleString('pt-BR')}` : 'Não informado'}
                    icon={DollarSign}
                />
                <StatCard
                    title="Data Distribuição"
                    value={new Date(processo.data_distribuicao).toLocaleDateString('pt-BR')}
                    icon={Calendar}
                />
                <StatCard
                    title="Cliente"
                    value={processo.client_name || 'Não atribuído'}
                    icon={User}
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Info */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Basic Info */}
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Informações Básicas</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="text-sm text-gray-600">Número do Processo</label>
                                <p className="font-mono font-medium">{processo.numero_processo}</p>
                            </div>
                            <div>
                                <label className="text-sm text-gray-600">Área do Direito</label>
                                <p className="font-medium">{processo.area_direito}</p>
                            </div>
                            <div>
                                <label className="text-sm text-gray-600">Vara</label>
                                <p className="font-medium">{processo.vara || '-'}</p>
                            </div>
                            <div>
                                <label className="text-sm text-gray-600">Comarca</label>
                                <p className="font-medium">{processo.comarca || '-'}</p>
                            </div>
                            {processo.autor && (
                                <div>
                                    <label className="text-sm text-gray-600">Autor</label>
                                    <p className="font-medium">{processo.autor}</p>
                                </div>
                            )}
                            {processo.reu && (
                                <div>
                                    <label className="text-sm text-gray-600">Réu</label>
                                    <p className="font-medium">{processo.reu}</p>
                                </div>
                            )}
                        </div>

                        {processo.descricao && (
                            <div className="mt-4 pt-4 border-t border-gray-200">
                                <label className="text-sm text-gray-600">Descrição</label>
                                <p className="mt-2 text-gray-700">{processo.descricao}</p>
                            </div>
                        )}
                    </div>

                    {/* Anexos */}
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                            <Paperclip className="w-5 h-5" />
                            Anexos ({anexos.length})
                        </h3>

                        {anexos.length > 0 ? (
                            <div className="space-y-2">
                                {anexos.map(anexo => (
                                    <div key={anexo.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                                        <div className="flex items-center gap-3">
                                            <FileText className="w-5 h-5 text-gray-400" />
                                            <div>
                                                <p className="font-medium text-gray-900">{anexo.nome}</p>
                                                <p className="text-sm text-gray-500">
                                                    {anexo.tipo} • {(anexo.tamanho / 1024).toFixed(2)} KB
                                                </p>
                                            </div>
                                        </div>
                                        <button className="text-blue-600 hover:text-blue-700">
                                            <Download className="w-4 h-4" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500 text-center py-4">Nenhum anexo encontrado</p>
                        )}
                    </div>
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                    {/* Timeline */}
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Timeline</h3>
                        <div className="space-y-4">
                            <div className="flex gap-3">
                                <div className="flex-shrink-0 w-2 h-2 mt-2 bg-blue-600 rounded-full"></div>
                                <div>
                                    <p className="font-medium text-gray-900">Distribuição</p>
                                    <p className="text-sm text-gray-500">
                                        {new Date(processo.data_distribuicao).toLocaleDateString('pt-BR')}
                                    </p>
                                </div>
                            </div>
                            {processo.data_ultima_movimentacao && (
                                <div className="flex gap-3">
                                    <div className="flex-shrink-0 w-2 h-2 mt-2 bg-gray-400 rounded-full"></div>
                                    <div>
                                        <p className="font-medium text-gray-900">Última Movimentação</p>
                                        <p className="text-sm text-gray-500">
                                            {new Date(processo.data_ultima_movimentacao).toLocaleDateString('pt-BR')}
                                        </p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Ações Rápidas</h3>
                        <div className="space-y-2">
                            <Link
                                to={`/processos/${id}/edit`}
                                className="block w-full px-4 py-2 text-center border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                            >
                                Editar Processo
                            </Link>
                            <button className="w-full px-4 py-2 text-center border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                                Adicionar Movimentação
                            </button>
                            <button className="w-full px-4 py-2 text-center border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                                Upload Documento
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </AdminLayout>
    )
}
