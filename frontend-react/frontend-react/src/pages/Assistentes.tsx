/**
 * Assistentes Jurídicos - Interface Completa
 * Features: Drag & Drop, Histórico, Salvar, Excluir
 */
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MessageSquare, Upload, History, Save, Trash2, Download,
  Send, Paperclip, X, FileText, Clock, ChevronLeft
} from 'lucide-react';
import api from '../lib/api';

interface Mensagem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  arquivos?: string[];
}

interface Conversa {
  id: string;
  titulo: string;
  assistente_id: number;
  mensagens: Mensagem[];
  criado_em: Date;
  atualizado_em: Date;
}

const assistentes = [
  { id: 1, nome: 'Assistente Cível', descricao: 'Direito Cível', cor: 'blue' },
  { id: 2, nome: 'Assistente Trabalhista', descricao: 'Direito Trabalhista', cor: 'green' },
  { id: 3, nome: 'Assistente Empresarial', descricao: 'Direito Empresarial', cor: 'purple' },
  { id: 4, nome: 'Assistente Tributário', descricao: 'Direito Tributário', cor: 'orange' },
  { id: 5, nome: 'Assistente Previdenciário', descricao: 'Direito Previdenciário', cor: 'red' },
  { id: 6, nome: 'Assistente Penal', descricao: 'Direito Penal', cor: 'red' },
  { id: 7, nome: 'Assistente Imobiliário', descricao: 'Direito Imobiliário', cor: 'cyan' },
  { id: 8, nome: 'Assistente Consumidor', descricao: 'Direito do Consumidor', cor: 'pink' }
];

export default function Assistentes() {
  const navigate = useNavigate();
  const [assistenteSelecionado, setAssistenteSelecionado] = useState<number | null>(null);
  const [conversaAtual, setConversaAtual] = useState<Conversa | null>(null);
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [inputMensagem, setInputMensagem] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [historico, setHistorico] = useState<Conversa[]>([]);
  const [mostrarHistorico, setMostrarHistorico] = useState(false);
  const [arquivosSelecionados, setArquivosSelecionados] = useState<File[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    carregarHistorico();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [mensagens]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const carregarHistorico = async () => {
    try {
      const conversasSalvas = localStorage.getItem('conversas_assistentes');
      if (conversasSalvas) {
        setHistorico(JSON.parse(conversasSalvas));
      }
    } catch (error) {
      console.error('Erro ao carregar histórico:', error);
    }
  };

  const selecionarAssistente = (id: number) => {
    setAssistenteSelecionado(id);
    setConversaAtual({
      id: Date.now().toString(),
      titulo: `Nova conversa - ${assistentes.find(a => a.id === id)?.nome}`,
      assistente_id: id,
      mensagens: [],
      criado_em: new Date(),
      atualizado_em: new Date()
    });
    setMensagens([]);
    setArquivosSelecionados([]);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    setArquivosSelecionados(prev => [...prev, ...files]);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setArquivosSelecionados(prev => [...prev, ...files]);
    }
  };

  const removerArquivo = (index: number) => {
    setArquivosSelecionados(prev => prev.filter((_, i) => i !== index));
  };

  const enviarMensagem = async () => {
    if (!inputMensagem.trim() && arquivosSelecionados.length === 0) return;
    if (!assistenteSelecionado) return;

    setEnviando(true);

    const novaMensagem: Mensagem = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMensagem,
      timestamp: new Date(),
      arquivos: arquivosSelecionados.map(f => f.name)
    };

    setMensagens(prev => [...prev, novaMensagem]);
    setInputMensagem('');
    const arquivosTemp = [...arquivosSelecionados];
    setArquivosSelecionados([]);

    try {
      // Simular resposta do assistente (substituir por API real)
      await new Promise(resolve => setTimeout(resolve, 1500));

      const respostaAssistente: Mensagem = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Entendi sua solicitação sobre "${inputMensagem.substring(0, 50)}...". ${arquivosTemp.length > 0 ? `Analisei ${arquivosTemp.length} arquivo(s). ` : ''}Como assistente jurídico, posso ajudá-lo com análise detalhada e orientações específicas.`,
        timestamp: new Date()
      };

      setMensagens(prev => [...prev, respostaAssistente]);

      // Atualizar conversa atual
      if (conversaAtual) {
        const conversaAtualizada = {
          ...conversaAtual,
          mensagens: [...mensagens, novaMensagem, respostaAssistente],
          atualizado_em: new Date()
        };
        setConversaAtual(conversaAtualizada);
      }

    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
    } finally {
      setEnviando(false);
    }
  };

  const salvarConversa = () => {
    if (!conversaAtual || mensagens.length === 0) return;

    const conversaParaSalvar = {
      ...conversaAtual,
      mensagens,
      atualizado_em: new Date()
    };

    const historicoAtualizado = [conversaParaSalvar, ...historico.filter(c => c.id !== conversaAtual.id)];
    setHistorico(historicoAtualizado);
    localStorage.setItem('conversas_assistentes', JSON.stringify(historicoAtualizado));

    alert('Conversa salva com sucesso!');
  };

  const carregarConversa = (conversa: Conversa) => {
    setConversaAtual(conversa);
    setMensagens(conversa.mensagens);
    setAssistenteSelecionado(conversa.assistente_id);
    setMostrarHistorico(false);
  };

  const excluirConversa = (id: string) => {
    if (!confirm('Deseja realmente excluir esta conversa?')) return;

    const historicoAtualizado = historico.filter(c => c.id !== id);
    setHistorico(historicoAtualizado);
    localStorage.setItem('conversas_assistentes', JSON.stringify(historicoAtualizado));

    if (conversaAtual?.id === id) {
      setConversaAtual(null);
      setMensagens([]);
      setAssistenteSelecionado(null);
    }
  };

  const exportarConversa = () => {
    if (!conversaAtual || mensagens.length === 0) return;

    const conteudo = mensagens.map(m =>
      `[${m.timestamp.toLocaleString('pt-BR')}] ${m.role === 'user' ? 'Você' : 'Assistente'}:\n${m.content}\n${m.arquivos ? `Arquivos: ${m.arquivos.join(', ')}\n` : ''}\n`
    ).join('\n');

    const blob = new Blob([conteudo], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conversa_${conversaAtual.id}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // View: Seleção de Assistente
  if (!assistenteSelecionado) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Assistentes Jurídicos</h1>
            <p className="text-muted-foreground">Escolha um assistente especializado</p>
          </div>

          <button
            onClick={() => setMostrarHistorico(!mostrarHistorico)}
            className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors"
          >
            <History className="w-5 h-5" />
            Histórico ({historico.length})
          </button>
        </div>

        {mostrarHistorico ? (
          <div className="space-y-4">
            <button
              onClick={() => setMostrarHistorico(false)}
              className="flex items-center gap-2 text-primary hover:underline mb-4"
            >
              <ChevronLeft className="w-4 h-4" />
              Voltar para assistentes
            </button>

            {historico.length === 0 ? (
              <div className="text-center py-12 bg-card border border-border rounded-xl">
                <History className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">Nenhuma conversa salva</p>
              </div>
            ) : (
              <div className="grid gap-4">
                {historico.map(conversa => (
                  <div
                    key={conversa.id}
                    className="bg-card border border-border rounded-xl p-6 hover:shadow-lg transition-all"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold mb-2">{conversa.titulo}</h3>
                        <p className="text-sm text-muted-foreground mb-2">
                          {conversa.mensagens.length} mensagens
                        </p>
                        <p className="text-xs text-muted-foreground">
                          <Clock className="w-3 h-3 inline mr-1" />
                          {new Date(conversa.atualizado_em).toLocaleString('pt-BR')}
                        </p>
                      </div>

                      <div className="flex gap-2">
                        <button
                          onClick={() => carregarConversa(conversa)}
                          className="px-3 py-2 bg-primary hover:bg-primary/90 rounded-lg text-sm"
                        >
                          Abrir
                        </button>
                        <button
                          onClick={() => excluirConversa(conversa.id)}
                          className="px-3 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {assistentes.map(assistente => (
              <button
                key={assistente.id}
                onClick={() => selecionarAssistente(assistente.id)}
                className="bg-card border border-border rounded-xl p-6 hover:shadow-xl hover:scale-105 transition-all text-left group"
              >
                <div className={`w-12 h-12 rounded-full bg-${assistente.cor}-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <MessageSquare className={`w-6 h-6 text-${assistente.cor}-400`} />
                </div>
                <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">
                  {assistente.nome}
                </h3>
                <p className="text-sm text-muted-foreground">{assistente.descricao}</p>
              </button>
            ))}
          </div>
        )}
      </div>
    );
  }

  // View: Chat
  return (
    <div className="flex flex-col h-[calc(100vh-80px)]">
      {/* Header */}
      <div className="border-b border-border bg-card p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setAssistenteSelecionado(null)}
            className="p-2 hover:bg-accent rounded-lg transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>

          <div>
            <h2 className="font-semibold">
              {assistentes.find(a => a.id === assistenteSelecionado)?.nome}
            </h2>
            <p className="text-xs text-muted-foreground">
              {mensagens.length} mensagens
            </p>
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setMostrarHistorico(true)}
            className="p-2 hover:bg-accent rounded-lg transition-colors"
            title="Histórico"
          >
            <History className="w-5 h-5" />
          </button>

          <button
            onClick={salvarConversa}
            disabled={mensagens.length === 0}
            className="p-2 hover:bg-accent rounded-lg transition-colors disabled:opacity-50"
            title="Salvar conversa"
          >
            <Save className="w-5 h-5" />
          </button>

          <button
            onClick={exportarConversa}
            disabled={mensagens.length === 0}
            className="p-2 hover:bg-accent rounded-lg transition-colors disabled:opacity-50"
            title="Exportar"
          >
            <Download className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Mensagens */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-background">
        {mensagens.length === 0 ? (
          <div className="text-center py-12">
            <MessageSquare className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
            <p className="text-lg font-medium mb-2">Inicie uma conversa</p>
            <p className="text-sm text-muted-foreground">
              Envie uma mensagem ou anexe arquivos para análise
            </p>
          </div>
        ) : (
          mensagens.map(mensagem => (
            <div
              key={mensagem.id}
              className={`flex ${mensagem.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[70%] rounded-xl p-4 ${mensagem.role === 'user'
                  ? 'bg-primary text-white'
                  : 'bg-card border border-border'
                  }`}
              >
                <p className="whitespace-pre-wrap">{mensagem.content}</p>

                {mensagem.arquivos && mensagem.arquivos.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-white/20 space-y-1">
                    {mensagem.arquivos.map((arquivo, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-xs">
                        <Paperclip className="w-3 h-3" />
                        <span>{arquivo}</span>
                      </div>
                    ))}
                  </div>
                )}

                <p className={`text-xs mt-2 ${mensagem.role === 'user' ? 'text-white/70' : 'text-muted-foreground'}`}>
                  {new Date(mensagem.timestamp).toLocaleTimeString('pt-BR')}
                </p>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div
        className={`border-t border-border bg-card p-4 ${dragOver ? 'bg-primary/10' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {/* Arquivos selecionados */}
        {arquivosSelecionados.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-2">
            {arquivosSelecionados.map((arquivo, index) => (
              <div
                key={index}
                className="flex items-center gap-2 bg-accent px-3 py-2 rounded-lg text-sm"
              >
                <FileText className="w-4 h-4" />
                <span>{arquivo.name}</span>
                <button
                  onClick={() => removerArquivo(index)}
                  className="hover:text-red-400"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="flex gap-2">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            multiple
            className="hidden"
          />

          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-3 hover:bg-accent rounded-lg transition-colors"
            title="Anexar arquivos"
          >
            <Paperclip className="w-5 h-5" />
          </button>

          <input
            type="text"
            value={inputMensagem}
            onChange={(e) => setInputMensagem(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && enviarMensagem()}
            placeholder="Digite sua mensagem..."
            disabled={enviando}
            className="flex-1 bg-background border border-border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
          />

          <button
            onClick={enviarMensagem}
            disabled={enviando || (!inputMensagem.trim() && arquivosSelecionados.length === 0)}
            className="px-6 py-3 bg-primary hover:bg-primary/90 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send className="w-5 h-5" />
            <span className="hidden sm:inline">Enviar</span>
          </button>
        </div>

        {dragOver && (
          <div className="absolute inset-0 bg-primary/20 border-2 border-dashed border-primary rounded-lg flex items-center justify-center pointer-events-none">
            <div className="text-center">
              <Upload className="w-12 h-12 mx-auto mb-2 text-primary" />
              <p className="text-lg font-semibold text-primary">Solte os arquivos aqui</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
