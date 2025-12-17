/**
 * Dashboard - Moderna e Corporativa
 * Stats reais, gráficos e métricas
 */
import DashboardEstatisticas from '../components/processos/DashboardEstatisticas';

export default function Dashboard() {
  return (
    <div className="p-6 max-w-[1600px] mx-auto space-y-6">
      {/* Header Moderno */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2 text-primary">Dashboard Executivo</h1>
          <p className="text-muted-foreground">Visão holística e indicadores de performance jurídica</p>
        </div>

        <div className="text-right hidden sm:block">
          <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Atualização em Tempo Real</p>
          <div className="flex items-center gap-2 justify-end">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </span>
            <p className="font-medium">{new Date().toLocaleDateString('pt-BR')} • {new Date().toLocaleTimeString('pt-BR')}</p>
          </div>
        </div>
      </div>

      {/* Analytics Completo */}
      <DashboardEstatisticas />
    </div>
  );
}
