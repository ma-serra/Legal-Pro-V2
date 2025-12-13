import { useState, useEffect } from 'react'
import api from '../lib/api'

interface UseApiOptions {
  immediate?: boolean
}

export function useApi<T>(
  endpoint: string,
  options: UseApiOptions = { immediate: true }
) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get<T>(endpoint)
      setData(response.data)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Erro ao buscar dados'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (options.immediate) {
      fetchData()
    }
  }, [endpoint])

  return { data, loading, error, refetch: fetchData }
}
