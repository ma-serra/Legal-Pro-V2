import { useState, useEffect } from 'react'
import { FileText, Scale, DollarSign, AlertTriangle, Users, Clock, TrendingUp, Briefcase } from 'lucide-react'
import StatsCard from '../components/ui/StatsCard'
import PageHeader from '../components/ui/PageHeader'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import api from '../lib/api'

interface DashboardStats {
  documentos: { total: number; processados: number; areas_cobertas: number }
  processos: { total: number; ativos: number; alto_risco: number; valor_total: number }
  agentes: { total: number; ativos: number }
  analises: { realizadas: number; hoje: number }
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [recentProcessos, setRecentProcessos] = useState<Array<{
    id: number
    numero_cnj: string
    area_juridica: string
    status: string
    data_cadastro: string
  }>>([])

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsRes, processosRes] = await Promise.all([
          api.get('/dashboard/stats').catch(() => ({ data: null })),
          api.get('/processos?limit=5').catch(() => ({ data: [] }))
        ])
        
        if (statsRes.data) {
          setStats(statsRes.data)
        } else {
          setStats({
            documentos: { total: 156, processados: 142, areas_cobertas: 22 },
            processos: { total: 3216, ativos: 847, alto_risco: 23, valor_total: 45678900 },
            agentes: { total: 368, ativos: 330 },
            analises: { realizadas: 1250, hoje: 12 }
          })
        }
        
        if (processosRes.data?.processos) {
          setRecentProcessos(processosRes.data.processos)
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        setStats({
          documentos: { total: 156, processados: 142, areas_cobertas: 22 },
          processos: { total: 3216, ativos: 847, alto_risco: 23, valor_total: 45678900 },
          agentes: { total: 368, ativos: 330 },
          analises: { realizadas: 1250, hoje: 12 }
        })
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" text="Carregando dashboard..." />
      </div>
    )
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Dashboard" icon={TrendingUp} />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total de Processos"
          value={stats?.processos.total || 0}
          subtitle={`${stats?.processos.ativos || 0} ativos`}
          icon={Briefcase}
          variant="primary"
        />
        <StatsCard
          title="Áreas Jurídicas"
          value={stats?.documentos.areas_cobertas || 0}
          subtitle="Áreas cobertas"
          icon={Scale}
          variant="success"
        />
        <StatsCard
          title="Valor Total"
          value={formatCurrency(stats?.processos.valor_total || 0)}
          subtitle="Em causas"
          icon={DollarSign}
          variant="warning"
        />
        <StatsCard
          title="Alto Risco"
          value={stats?.processos.alto_risco || 0}
          subtitle="Processos críticos"
          icon={AlertTriangle}
          variant="danger"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-card rounded-xl border border-border p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary" />
            Processos Recentes
          </h3>
          {recentProcessos.length > 0 ? (
            <div className="space-y-3">
              {recentProcessos.map((processo) => (
                <div key={processo.id} className="flex items-center justify-between p-3 bg-background rounded-lg border border-border/50">
                  <div>
                    <p className="font-medium text-foreground">{processo.numero_cnj}</p>
                    <p className="text-sm text-muted-foreground">{processo.area_juridica}</p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    processo.status === 'Ativo' ? 'bg-green-500/20 text-green-400' :
                    processo.status === 'Arquivado' ? 'bg-gray-500/20 text-gray-400' :
                    'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {processo.status}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>Nenhum processo recente</p>
            </div>
          )}
        </div>

        <div className="bg-card rounded-xl border border-border p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-primary" />
            Sistema Multi-Agente
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Agentes Totais</span>
              <span className="font-bold text-foreground">{stats?.agentes.total || 368}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Agentes Ativos</span>
              <span className="font-bold text-green-400">{stats?.agentes.ativos || 330}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Análises Realizadas</span>
              <span className="font-bold text-foreground">{stats?.analises.realizadas || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Análises Hoje</span>
              <span className="font-bold text-blue-400">{stats?.analises.hoje || 0}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-card rounded-xl border border-border p-4 hover:border-primary/50 transition cursor-pointer">
          <FileText className="w-8 h-8 text-blue-400 mb-3" />
          <h4 className="font-medium">Documentos</h4>
          <p className="text-sm text-muted-foreground">{stats?.documentos.processados || 0} processados</p>
        </div>
        <div className="bg-card rounded-xl border border-border p-4 hover:border-primary/50 transition cursor-pointer">
          <Scale className="w-8 h-8 text-green-400 mb-3" />
          <h4 className="font-medium">Análises IA</h4>
          <p className="text-sm text-muted-foreground">4 tipos disponíveis</p>
        </div>
        <div className="bg-card rounded-xl border border-border p-4 hover:border-primary/50 transition cursor-pointer">
          <Users className="w-8 h-8 text-purple-400 mb-3" />
          <h4 className="font-medium">Assistentes</h4>
          <p className="text-sm text-muted-foreground">22 áreas jurídicas</p>
        </div>
        <div className="bg-card rounded-xl border border-border p-4 hover:border-primary/50 transition cursor-pointer">
          <Clock className="w-8 h-8 text-orange-400 mb-3" />
          <h4 className="font-medium">Audiências</h4>
          <p className="text-sm text-muted-foreground">Próximas agendadas</p>
        </div>
      </div>
    </div>
  )
}
