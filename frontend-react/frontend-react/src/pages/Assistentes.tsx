import { useState } from 'react'
import { Users, MessageCircle, Send, Sparkles } from 'lucide-react'
import PageHeader from '../components/ui/PageHeader'
import Button from '../components/ui/Button'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import api from '../lib/api'

interface Assistente {
  id: string
  nome: string
  area: string
  descricao: string
  cor: string
}

const assistentes: Assistente[] = [
  { id: 'civil', nome: 'Assistente Civil', area: 'Direito Civil', descricao: 'Especialista em contratos, responsabilidade civil e obrigações.', cor: 'bg-blue-600' },
  { id: 'trabalhista', nome: 'Assistente Trabalhista', area: 'Direito Trabalhista', descricao: 'Expert em CLT, relações de trabalho e direitos do trabalhador.', cor: 'bg-green-600' },
  { id: 'empresarial', nome: 'Assistente Empresarial', area: 'Direito Empresarial', descricao: 'Focado em sociedades, contratos comerciais e recuperação judicial.', cor: 'bg-purple-600' },
  { id: 'tributario', nome: 'Assistente Tributário', area: 'Direito Tributário', descricao: 'Especializado em tributos, planejamento fiscal e contencioso.', cor: 'bg-yellow-600' },
  { id: 'previdenciario', nome: 'Assistente Previdenciário', area: 'Direito Previdenciário', descricao: 'Expert em aposentadoria, benefícios e INSS.', cor: 'bg-orange-600' },
  { id: 'penal', nome: 'Assistente Penal', area: 'Direito Penal', descricao: 'Focado em crimes, processo penal e execução penal.', cor: 'bg-red-600' },
  { id: 'imobiliario', nome: 'Assistente Imobiliário', area: 'Direito Imobiliário', descricao: 'Especialista em compra/venda, locação e registros.', cor: 'bg-teal-600' },
  { id: 'consumidor', nome: 'Assistente do Consumidor', area: 'Direito do Consumidor', descricao: 'Expert em CDC, relações de consumo e proteção.', cor: 'bg-pink-600' },
  { id: 'familia', nome: 'Assistente de Família', area: 'Direito de Família', descricao: 'Focado em divórcio, guarda, pensão e sucessões.', cor: 'bg-indigo-600' },
  { id: 'digital', nome: 'Assistente Digital', area: 'Direito Digital', descricao: 'Especializado em LGPD, crimes cibernéticos e contratos digitais.', cor: 'bg-cyan-600' },
  { id: 'ambiental', nome: 'Assistente Ambiental', area: 'Direito Ambiental', descricao: 'Expert em licenciamento, crimes ambientais e sustentabilidade.', cor: 'bg-emerald-600' },
  { id: 'administrativo', nome: 'Assistente Administrativo', area: 'Direito Administrativo', descricao: 'Focado em licitações, servidores públicos e atos administrativos.', cor: 'bg-slate-600' }
]

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export default function Assistentes() {
  const [assistenteSelecionado, setAssistenteSelecionado] = useState<Assistente | null>(null)
  const [mensagem, setMensagem] = useState('')
  const [mensagens, setMensagens] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const enviarMensagem = async () => {
    if (!mensagem.trim() || !assistenteSelecionado) return

    const novaMensagem: Message = {
      role: 'user',
      content: mensagem,
      timestamp: new Date()
    }

    setMensagens(prev => [...prev, novaMensagem])
    setMensagem('')
    setIsLoading(true)

    try {
      const response = await api.post('/assistente/chat', {
        assistente: assistenteSelecionado.id,
        mensagem: mensagem,
        historico: mensagens
      })

      const respostaAssistente: Message = {
        role: 'assistant',
        content: response.data.resposta || response.data.message || 'Resposta recebida.',
        timestamp: new Date()
      }

      setMensagens(prev => [...prev, respostaAssistente])
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error)
      const respostaDemo: Message = {
        role: 'assistant',
        content: `Olá! Sou o ${assistenteSelecionado.nome}, especializado em ${assistenteSelecionado.area}. 

Como posso ajudá-lo hoje? Posso auxiliar com:
- Análise de casos e documentos
- Estratégias jurídicas
- Pesquisa de jurisprudência
- Elaboração de peças processuais
- Orientações sobre procedimentos

*Esta é uma resposta de demonstração. Em produção, a resposta viria dos modelos de IA integrados.*`,
        timestamp: new Date()
      }
      setMensagens(prev => [...prev, respostaDemo])
    } finally {
      setIsLoading(false)
    }
  }

  const selecionarAssistente = (assistente: Assistente) => {
    setAssistenteSelecionado(assistente)
    setMensagens([{
      role: 'assistant',
      content: `Olá! Sou o ${assistente.nome}, especializado em ${assistente.area}. ${assistente.descricao} Como posso ajudá-lo hoje?`,
      timestamp: new Date()
    }])
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Assistentes Jurídicos" icon={Users}>
        <Button variant="secondary" icon={Sparkles}>
          {assistentes.length} Assistentes
        </Button>
      </PageHeader>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <h3 className="font-semibold text-foreground">Escolha um Assistente</h3>
          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
            {assistentes.map((assistente) => (
              <button
                key={assistente.id}
                onClick={() => selecionarAssistente(assistente)}
                className={`w-full p-4 rounded-lg border text-left transition ${
                  assistenteSelecionado?.id === assistente.id
                    ? 'border-primary bg-primary/10'
                    : 'border-border hover:border-primary/50 bg-card'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-full ${assistente.cor} flex items-center justify-center`}>
                    <Users className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h4 className="font-medium text-foreground">{assistente.nome}</h4>
                    <p className="text-xs text-muted-foreground">{assistente.area}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="lg:col-span-2 bg-card rounded-xl border border-border flex flex-col h-[650px]">
          {assistenteSelecionado ? (
            <>
              <div className="p-4 border-b border-border flex items-center gap-3">
                <div className={`w-10 h-10 rounded-full ${assistenteSelecionado.cor} flex items-center justify-center`}>
                  <Users className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">{assistenteSelecionado.nome}</h3>
                  <p className="text-sm text-muted-foreground">{assistenteSelecionado.area}</p>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {mensagens.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] p-3 rounded-lg ${
                        msg.role === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-background border border-border'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      <p className="text-xs opacity-70 mt-1">
                        {msg.timestamp.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-background border border-border p-3 rounded-lg">
                      <LoadingSpinner size="sm" />
                    </div>
                  </div>
                )}
              </div>

              <div className="p-4 border-t border-border">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={mensagem}
                    onChange={(e) => setMensagem(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && enviarMensagem()}
                    placeholder="Digite sua mensagem..."
                    className="flex-1 px-4 py-2 bg-background border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <Button onClick={enviarMensagem} icon={Send} disabled={!mensagem.trim() || isLoading}>
                    Enviar
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
              <MessageCircle className="w-16 h-16 mb-4 opacity-50" />
              <p className="text-lg">Selecione um assistente</p>
              <p className="text-sm">para iniciar uma conversa</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
