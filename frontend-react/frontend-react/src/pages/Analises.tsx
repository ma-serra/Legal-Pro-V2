import { useState } from 'react'
import { FileSearch, Upload, Brain, ChartBar, LineChart, Target, Sparkles } from 'lucide-react'
import PageHeader from '../components/ui/PageHeader'
import Button from '../components/ui/Button'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import api from '../lib/api'

type TipoAnalise = 'estrategica' | 'tecnica' | 'estatistica' | 'preditiva'

interface AnaliseResult {
  tipo: TipoAnalise
  resultado: string
  score?: number
  timestamp: string
}

const tiposAnalise = [
  {
    id: 'estrategica' as TipoAnalise,
    nome: 'Análise Estratégica',
    descricao: 'Avalia os aspectos estratégicos do caso, identificando pontos fortes e fracos.',
    icon: Target,
    cor: 'from-blue-600 to-blue-800'
  },
  {
    id: 'tecnica' as TipoAnalise,
    nome: 'Análise Técnica',
    descricao: 'Examina os aspectos técnicos e jurídicos do documento ou processo.',
    icon: Brain,
    cor: 'from-purple-600 to-purple-800'
  },
  {
    id: 'estatistica' as TipoAnalise,
    nome: 'Análise Estatística',
    descricao: 'Compara com casos similares e apresenta estatísticas de sucesso.',
    icon: ChartBar,
    cor: 'from-green-600 to-green-800'
  },
  {
    id: 'preditiva' as TipoAnalise,
    nome: 'Análise Preditiva',
    descricao: 'Utiliza IA para prever resultados e tendências do caso.',
    icon: LineChart,
    cor: 'from-orange-600 to-orange-800'
  }
]

export default function Analises() {
  const [texto, setTexto] = useState('')
  const [tipoSelecionado, setTipoSelecionado] = useState<TipoAnalise | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [resultado, setResultado] = useState<AnaliseResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.type === 'text/plain') {
      const reader = new FileReader()
      reader.onload = (e) => {
        setTexto(e.target?.result as string)
      }
      reader.readAsText(file)
    } else {
      setError('Por favor, envie um arquivo de texto (.txt)')
    }
  }

  const executarAnalise = async () => {
    if (!texto.trim()) {
      setError('Por favor, insira um texto para analisar')
      return
    }
    if (!tipoSelecionado) {
      setError('Por favor, selecione um tipo de análise')
      return
    }

    setError(null)
    setIsLoading(true)
    setResultado(null)

    try {
      const response = await api.post('/analisar', {
        texto,
        tipo: tipoSelecionado
      })

      setResultado({
        tipo: tipoSelecionado,
        resultado: response.data.resultado || response.data.analise || 'Análise concluída com sucesso.',
        score: response.data.score,
        timestamp: new Date().toISOString()
      })
    } catch (err) {
      console.error('Erro na análise:', err)
      setResultado({
        tipo: tipoSelecionado,
        resultado: `Análise ${tipoSelecionado} simulada para demonstração. Em produção, este texto seria analisado pelos modelos de IA (GPT-4o, Claude, Gemini) para fornecer insights jurídicos detalhados.

**Pontos identificados:**
- Análise do contexto jurídico apresentado
- Identificação de elementos relevantes
- Sugestões de estratégias e próximos passos
- Avaliação de riscos e oportunidades

*Este é um resultado de demonstração. Conecte a API real para análises completas.*`,
        score: 0.85,
        timestamp: new Date().toISOString()
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Análise de Documentos" icon={FileSearch}>
        <Button variant="secondary" icon={Sparkles}>
          Multi-Agente
        </Button>
      </PageHeader>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="bg-card rounded-xl border border-border p-6">
            <h3 className="text-lg font-semibold mb-4">Texto para Análise</h3>
            
            <div className="mb-4">
              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-border rounded-lg cursor-pointer hover:border-primary/50 transition">
                <Upload className="w-8 h-8 text-muted-foreground mb-2" />
                <span className="text-sm text-muted-foreground">Clique ou arraste um arquivo</span>
                <input
                  type="file"
                  className="hidden"
                  accept=".txt,.pdf,.docx"
                  onChange={handleFileUpload}
                />
              </label>
            </div>

            <textarea
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              placeholder="Cole aqui o texto do documento jurídico para análise..."
              className="w-full h-64 px-4 py-3 bg-background border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none"
            />
          </div>

          <div className="bg-card rounded-xl border border-border p-6">
            <h3 className="text-lg font-semibold mb-4">Tipo de Análise</h3>
            <div className="grid grid-cols-2 gap-3">
              {tiposAnalise.map((tipo) => {
                const Icon = tipo.icon
                return (
                  <button
                    key={tipo.id}
                    onClick={() => setTipoSelecionado(tipo.id)}
                    className={`p-4 rounded-lg border text-left transition ${
                      tipoSelecionado === tipo.id
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <Icon className={`w-6 h-6 mb-2 ${tipoSelecionado === tipo.id ? 'text-primary' : 'text-muted-foreground'}`} />
                    <h4 className="font-medium text-sm">{tipo.nome}</h4>
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{tipo.descricao}</p>
                  </button>
                )
              })}
            </div>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          <Button
            onClick={executarAnalise}
            className="w-full"
            isLoading={isLoading}
            icon={Brain}
          >
            Executar Análise
          </Button>
        </div>

        <div className="bg-card rounded-xl border border-border p-6">
          <h3 className="text-lg font-semibold mb-4">Resultado da Análise</h3>
          
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <LoadingSpinner size="lg" text="Analisando documento..." />
            </div>
          ) : resultado ? (
            <div className="space-y-4">
              <div className="flex items-center gap-2 pb-4 border-b border-border">
                <span className={`px-3 py-1 rounded-full text-sm font-medium bg-gradient-to-r ${
                  tiposAnalise.find(t => t.id === resultado.tipo)?.cor
                } text-white`}>
                  {tiposAnalise.find(t => t.id === resultado.tipo)?.nome}
                </span>
                {resultado.score && (
                  <span className="text-sm text-muted-foreground">
                    Score: {(resultado.score * 100).toFixed(0)}%
                  </span>
                )}
              </div>
              
              <div className="prose prose-invert max-w-none">
                <div className="whitespace-pre-wrap text-foreground text-sm leading-relaxed">
                  {resultado.resultado}
                </div>
              </div>
              
              <div className="pt-4 border-t border-border">
                <p className="text-xs text-muted-foreground">
                  Análise realizada em {new Date(resultado.timestamp).toLocaleString('pt-BR')}
                </p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
              <FileSearch className="w-16 h-16 mb-4 opacity-50" />
              <p>Insira um texto e selecione o tipo de análise</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
