// Tipos do sistema jurídico

export interface Processo {
  id: number
  titulo: string
  descricao: string
  status: 'ativo' | 'arquivado' | 'pausado'
  data_criacao: string
}

export interface Analise {
  id: number
  processo_id: number
  tipo: 'estrategica' | 'tecnica' | 'estatistica' | 'preditiva'
  resultado: string
  data: string
}

export interface Usuario {
  id: number
  email: string
  nome: string
  nivel: 'master' | 'admin' | 'advogado'
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  message: string
}
