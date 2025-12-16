import axios from 'axios';
const API_BASE = import.meta.env.VITE_API_URL || 'https://legal-pro-saas.up.railway.app';
export const api = axios.create({
    baseURL: API_BASE, // Removido /api - será adicionado nas rotas específicas
    headers: {
        'Content-Type': 'application/json'
    }
});
// Interceptor para incluir token de autenticação
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
export default api;
