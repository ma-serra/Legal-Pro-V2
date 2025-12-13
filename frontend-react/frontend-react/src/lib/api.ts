import axios from 'axios'

const API_BASE = (import.meta.env.VITE_API_URL as string) || 'http://localhost:5000'

export const api = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para incluir token de autenticação
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
