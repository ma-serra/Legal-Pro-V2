import { useState, useEffect } from 'react'
import { Gavel, Plus, BarChart2, Eye, Trash2 } from 'lucide-react'
import StatsCard from '../components/ui/StatsCard'
import PageHeader from '../components/ui/PageHeader'
import FilterBar from '../components/ui/FilterBar'
import DataTable from '../components/ui/DataTable'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import api from '../lib/api'

interface Processo {
  id: number
  numero_cnj: string
  cliente: string
  area_juridica: string
  valor_causa: number
  nivel_risco: string
  status: string
  data_cadastro: string
}

interface Estatisticas {
  total_processos: number
  areas_diferentes: number
  valor_total_causas: number
  processos_alto_risco: number
}

const areasJuridicas = [
  { value: '', label: 'Todas as Áreas' },
  { value: 'Direito Civil', label: 'Direito Civil' },
  { value: 'Direito Trabalhista', label: 'Direito Trabalhista' },
  { value: 'Direito Empresarial', label: 'Direito Empresarial' },
  { value: 'Direito Tributário', label: 'Direito Tributário' },
  { value: 'Direito Previdenciário', label: 'Direito Previdenciário' },
  { value: 'Direito Penal', label: 'Direito Penal' },
  { value: 'Direito Imobiliário', label: 'Direito Imobiliário' },
  { value: 'Direito Bancário', label: 'Direito Bancário' },
  { value: 'Direito do Consumidor', label: 'Direito do Consumidor' },
  { value: 'Direito de Família', label: 'Direito de Família' },
  { value: 'Direito Administrativo', label: 'Direito Administrativo' },
  { value: 'Direito Digital', label: 'Direito Digital' }
]

const niveisRisco = [
  { value: '', label: 'Todos os Riscos' },
  { value: 'Baixo', label: 'Baixo' },
  { value: 'Médio', label: 'Médio' },
  { value: 'Alto', label: 'Alto' }
]

export default function Processos() {
  const [processos, setProcessos] = useState<Processo[]>([])
  const [estatisticas, setEstatisticas] = useState<Estatisticas | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [filtroArea, setFiltroArea] = useState('')
  const [filtroRisco, setFiltroRisco] = useState('')
  const [busca, setBusca] = useState('')

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    setIsLoading(true)
    try {
      const [processosRes, statsRes] = await Promise.all([
        api.get('/processos-juridicos/processos').catch(() => ({ data: { processos: [] } })),
        api.get('/processos-juridicos/estatisticas').catch(() => ({ data: null }))
      ])

      if (processosRes.data?.processos) {
        setProcessos(processosRes.data.processos)
      } else {
        setProcessos([])
      }

      if (statsRes.data) {
        setEstatisticas(statsRes.data)
      } else {
        setEstatisticas({
          total_processos: 0,
          areas_diferentes: 0,
          valor_total_causas: 0,
          processos_alto_risco: 0
        })
      }
    } catch (error) {
      console.error('Error fetching processos:', error)
      setProcessos([])
      setEstatisticas(null)
    } finally {
      setIsLoading(false)
    }
  }

  const filteredProcessos = processos.filter((p) => {
    if (filtroArea && p.area_juridica !== filtroArea) return false
    if (filtroRisco && p.nivel_risco !== filtroRisco) return false
    if (busca) {
      const searchLower = busca.toLowerCase()
      return (
        p.numero_cnj.toLowerCase().includes(searchLower) ||
        p.cliente.toLowerCase().includes(searchLower)
      )
    }
    return true
  })

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const getRiskBadge = (risco: string) => {
    const variant = risco === 'Alto' ? 'danger' : risco === 'Médio' ? 'warning' : 'success'
    return <Badge variant={variant}>{risco}</Badge>
  }

  const columns = [
    { key: 'numero_cnj', header: 'Número CNJ' },
    { key: 'cliente', header: 'Cliente' },
    { key: 'area_juridica', header: 'Área Jurídica' },
    {
      key: 'valor_causa',
      header: 'Valor da Causa',
      render: (item: Processo) => formatCurrency(item.valor_causa)
    },
    {
      key: 'nivel_risco',
      header: 'Risco',
      render: (item: Processo) => getRiskBadge(item.nivel_risco)
    },
    { key: 'status', header: 'Status' },
    {
      key: 'actions',
      header: 'Ações',
      render: () => (
        <div className="flex gap-2">
          <button className="p-1 hover:bg-accent rounded" title="Ver detalhes">
            <Eye className="w-4 h-4" />
          </button>
          <button className="p-1 hover:bg-red-500/20 rounded text-red-400" title="Excluir">
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      )
    }
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" text="Carregando processos..." />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Processos Jurídicos" icon={Gavel}>
        <Button variant="success" icon={Plus}>
          Novo Processo
        </Button>
        <Button variant="secondary" icon={BarChart2}>
          Estatísticas
        </Button>
      </PageHeader>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total de Processos"
          value={estatisticas?.total_processos || 0}
          icon={Gavel}
          variant="primary"
        />
        <StatsCard
          title="Áreas Jurídicas"
          value={estatisticas?.areas_diferentes || 0}
          icon={BarChart2}
          variant="success"
        />
        <StatsCard
          title="Valor Total"
          value={formatCurrency(estatisticas?.valor_total_causas || 0)}
          icon={Gavel}
          variant="warning"
        />
        <StatsCard
          title="Alto Risco"
          value={estatisticas?.processos_alto_risco || 0}
          icon={Gavel}
          variant="danger"
        />
      </div>

      <FilterBar
        filters={[
          {
            label: 'Área Jurídica',
            options: areasJuridicas,
            value: filtroArea,
            onChange: setFiltroArea
          },
          {
            label: 'Nível de Risco',
            options: niveisRisco,
            value: filtroRisco,
            onChange: setFiltroRisco
          }
        ]}
        searchValue={busca}
        onSearchChange={setBusca}
        searchPlaceholder="Buscar por CNJ, cliente..."
      />

      <div className="bg-card rounded-xl border border-border">
        <DataTable
          data={filteredProcessos}
          columns={columns}
          emptyMessage="Nenhum processo encontrado"
          onRowClick={(item) => console.log('Clicked:', item)}
        />
      </div>
    </div>
  )
}


