import { jsx as _jsx } from "react/jsx-runtime";
import { createContext, useState, useEffect } from 'react';
import api from '../lib/api';
export const AuthContext = createContext(undefined);
export function AuthProvider({ children }) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [token, setToken] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            setToken(storedToken);
            setIsAuthenticated(true);
        }
        setIsLoading(false);
    }, []);
    const login = async (email, password) => {
        try {
            const response = await api.post('/api/auth/login', { email, password });
            const { token: newToken } = response.data;
            localStorage.setItem('token', newToken);
            setToken(newToken);
            setIsAuthenticated(true);
        }
        catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    };
    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setIsAuthenticated(false);
    };
    return (_jsx(AuthContext.Provider, { value: { isAuthenticated, token, isLoading, login, logout }, children: children }));
}
