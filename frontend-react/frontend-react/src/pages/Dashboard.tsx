/**
 * Dashboard - Moderna e Corporativa
 * Stats reais, gráficos e métricas
 */
import ProcessoStats from '../components/processos/ProcessoStats';
import { TrendingUp, Users, FileText, DollarSign } from 'lucide-react';

export default function Dashboard() {
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header Moderno */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
          <p className="text-muted-foreground">Visão geral do sistema Legal Pro</p>
        </div>

        <div className="text-right">
          <p className="text-sm text-muted-foreground">Última atualização</p>
          <p className="font-semibold">{new Date().toLocaleDateString('pt-BR')}</p>
        </div>
      </div>

      {/* Stats de Processos */}
      <ProcessoStats />

      {/* Métricas Adicionais */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-primary/20 rounded-lg">
              <TrendingUp className="w-5 h-5 text-primary" />
            </div>
            <h3 className="font-semibold">Tendências</h3>
          </div>

          <p className="text-sm text-muted-foreground">
            Visualização de tendências será implementada em breve
          </p>
        </div>

        <div className="bg-card border border-border rounded-xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <FileText className="w-5 h-5 text-green-400" />
            </div>
            <h3 className="font-semibold">Atividade Recente</h3>
          </div>

          <p className="text-sm text-muted-foreground">
            Atividades recentes serão exibidas aqui
          </p>
        </div>
      </div>
    </div>
  );
}
