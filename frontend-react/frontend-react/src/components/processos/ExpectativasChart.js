import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../../lib/api';
import { Loader2 } from 'lucide-react';
export default function ExpectativasChart({ indicador, titulo }) {
    const [dados, setDados] = useState([]);
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
            geral.forEach((item) => {
                const data = item.Data;
                if (!mapa.has(data))
                    mapa.set(data, { data });
                mapa.get(data).mercado = item.Mediana;
            });
            top5.forEach((item) => {
                const data = item.Data;
                if (!mapa.has(data))
                    mapa.set(data, { data });
                mapa.get(data).top5 = item.Mediana;
            });
            const dadosFormatados = Array.from(mapa.values())
                .sort((a, b) => new Date(a.data).getTime() - new Date(b.data).getTime())
                .map((d) => ({
                ...d,
                dataDisplay: new Date(d.data).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
            }));
            setDados(dadosFormatados);
        }
        catch (err) {
            console.error(err);
        }
        finally {
            setLoading(false);
        }
    };
    if (loading)
        return _jsx("div", { className: "h-64 flex items-center justify-center", children: _jsx(Loader2, { className: "animate-spin text-primary" }) });
    if (dados.length === 0)
        return _jsx("div", { className: "h-64 flex items-center justify-center text-muted-foreground", children: "Sem dados hist\u00F3ricos recentes" });
    return (_jsxs("div", { className: "bg-card border border-border rounded-xl p-4 mt-4", children: [_jsxs("h3", { className: "font-semibold mb-4 text-sm", children: ["Hist\u00F3rico de Expectativas (90 dias) - ", titulo] }), _jsx("div", { className: "h-[300px] w-full items-center justify-center", children: _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(LineChart, { data: dados, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", stroke: "#333" }), _jsx(XAxis, { dataKey: "dataDisplay", stroke: "#888", style: { fontSize: '11px' } }), _jsx(YAxis, { stroke: "#888", style: { fontSize: '11px' }, domain: ['auto', 'auto'] }), _jsx(Tooltip, { contentStyle: { backgroundColor: '#1f1f1f', border: '1px solid #333' } }), _jsx(Legend, {}), _jsx(Line, { type: "monotone", dataKey: "mercado", name: "Mercado (Mediana)", stroke: "#8884d8", dot: false, strokeWidth: 2 }), _jsx(Line, { type: "monotone", dataKey: "top5", name: "Top 5 (Mediana)", stroke: "#82ca9d", dot: false, strokeWidth: 2 })] }) }) }), _jsx("p", { className: "text-xs text-muted-foreground mt-2 text-center", children: "Comparativo entre a mediana de todo o mercado vs Top 5 institui\u00E7\u00F5es" })] }));
}
