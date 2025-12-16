import { useState, useEffect } from 'react';
import api from '../lib/api';
export function useApi(endpoint, options = { immediate: true }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await api.get(endpoint);
            setData(response.data);
        }
        catch (err) {
            setError(err instanceof Error ? err : new Error('Erro ao buscar dados'));
        }
        finally {
            setLoading(false);
        }
    };
    useEffect(() => {
        if (options.immediate) {
            fetchData();
        }
    }, [endpoint]);
    return { data, loading, error, refetch: fetchData };
}
