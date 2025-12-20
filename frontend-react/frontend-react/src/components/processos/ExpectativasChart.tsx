
import { useState, useEffect } from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import api from '../../lib/api';
import { Loader2 } from 'lucide-react';

interface ExpectativasChartProps {
    indicador: string; // 'Selic', 'IPCA', etc.
    titulo: string;
}

export default function ExpectativasChart({ indicador, titulo }: ExpectativasChartProps) {
    const [dados, setDados] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (indicador) {
            fetchData();
        }
    }, [indicador]);

    const fetchData = async () => {
        setLoading(true);
        try {
            const res = await api.get(`/api/bcb/expectativas/historico/${indicador}?dias=90`);
            const { geral, top5 } = res.data;

            // Merge dos dados por data
            const mapa = new Map();

            geral.forEach((item: any) => {
                const data = item.Data;
                if (!mapa.has(data)) mapa.set(data, { data });
                mapa.get(data).mercado = item.Mediana;
            });

            top5.forEach((item: any) => {
                const data = item.Data;
                if (!mapa.has(data)) mapa.set(data, { data });
                mapa.get(data).top5 = item.Mediana;
            });

            const dadosFormatados = Array.from(mapa.values())
                .sort((a: any, b: any) => new Date(a.data).getTime() - new Date(b.data).getTime())
                .map((d: any) => ({
                    ...d,
                    dataDisplay: new Date(d.data).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
                }));

            setDados(dadosFormatados);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="h-64 flex items-center justify-center"><Loader2 className="animate-spin text-primary" /></div>;
    if (dados.length === 0) return <div className="h-64 flex items-center justify-center text-muted-foreground">Sem dados históricos recentes</div>;

    return (
        <div className="bg-card border border-border rounded-xl p-4 mt-4">
            <h3 className="font-semibold mb-4 text-sm">Histórico de Expectativas (90 dias) - {titulo}</h3>
            <div className="h-[300px] w-full items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={dados}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                        <XAxis dataKey="dataDisplay" stroke="#888" style={{ fontSize: '11px' }} />
                        <YAxis stroke="#888" style={{ fontSize: '11px' }} domain={['auto', 'auto']} />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#1f1f1f', border: '1px solid #333' }}
                        />
                        <Legend />
                        <Line type="monotone" dataKey="mercado" name="Mercado (Mediana)" stroke="#8884d8" dot={false} strokeWidth={2} />
                        <Line type="monotone" dataKey="top5" name="Top 5 (Mediana)" stroke="#82ca9d" dot={false} strokeWidth={2} />
                    </LineChart>
                </ResponsiveContainer>
            </div>
            <p className="text-xs text-muted-foreground mt-2 text-center">
                Comparativo entre a mediana de todo o mercado vs Top 5 instituições
            </p>
        </div>
    );
}
