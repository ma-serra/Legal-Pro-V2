export default function Home() {
  return (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-primary to-primary/80 text-white rounded-lg p-8">
        <h1 className="text-4xl font-bold mb-4">Legal Pro Frontend</h1>
        <p className="text-lg opacity-90">
          Nova interface refatorada em React - Sistema jurídico multi-agente
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-card p-6 rounded-lg border border-border">
          <h3 className="text-xl font-semibold mb-2">🚀 Rápido</h3>
          <p className="text-secondary">Interface otimizada para máxima performance</p>
        </div>
        <div className="bg-card p-6 rounded-lg border border-border">
          <h3 className="text-xl font-semibold mb-2">🔒 Seguro</h3>
          <p className="text-secondary">Autenticação e dados protegidos</p>
        </div>
        <div className="bg-card p-6 rounded-lg border border-border">
          <h3 className="text-xl font-semibold mb-2">⚖️ Jurídico</h3>
          <p className="text-secondary">368 agentes especializados em direito</p>
        </div>
      </div>

      <div className="bg-accent/10 border border-accent rounded-lg p-6">
        <h2 className="text-2xl font-semibold mb-4">Status do Frontend</h2>
        <ul className="space-y-2 text-foreground">
          <li>✅ Estrutura React criada</li>
          <li>✅ Roteamento configurado</li>
          <li>✅ Componentes base implementados</li>
          <li>⏳ Integração com backend em progresso</li>
        </ul>
      </div>
    </div>
  )
}
