import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { AdminLayout } from '../../components/layouts/AdminLayout';
import { PageHeader } from '../../components/ui/AdminComponents';
import { MapPin, Navigation, Filter, Layers } from 'lucide-react';
import api from '../../lib/api';
export default function Geolocation() {
    const [locations, setLocations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [selectedLocation, setSelectedLocation] = useState(null);
    useEffect(() => {
        fetchLocations();
    }, []);
    const fetchLocations = async () => {
        try {
            const response = await api.get('/setorenergia/geolocalizacao');
            setLocations(response.data);
        }
        catch (error) {
            console.error('Error fetching locations:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const filteredLocations = filter === 'all'
        ? locations
        : locations.filter(l => l.nivel_prioridade === filter);
    const getPriorityColor = (nivel) => {
        switch (nivel) {
            case 'alto': return 'bg-red-500';
            case 'medio': return 'bg-yellow-500';
            case 'baixo': return 'bg-green-500';
            default: return 'bg-gray-500';
        }
    };
    if (loading) {
        return (_jsx(AdminLayout, { children: _jsx("div", { className: "flex items-center justify-center h-96", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) }) }));
    }
    return (_jsxs(AdminLayout, { children: [_jsx(PageHeader, { title: "Geolocaliza\u00E7\u00E3o de Processos", description: "Visualiza\u00E7\u00E3o geogr\u00E1fica dos processos por localiza\u00E7\u00E3o" }), _jsx("div", { className: "bg-white rounded-lg border border-gray-200 p-4 mb-6", children: _jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { className: "flex items-center gap-4", children: [_jsx(Filter, { className: "w-5 h-5 text-gray-600" }), _jsxs("select", { value: filter, onChange: (e) => setFilter(e.target.value), className: "px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { value: "all", children: "Todas as Prioridades" }), _jsx("option", { value: "alto", children: "Alta" }), _jsx("option", { value: "medio", children: "M\u00E9dia" }), _jsx("option", { value: "baixo", children: "Baixa" })] })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx(Layers, { className: "w-5 h-5 text-gray-600" }), _jsxs("span", { className: "text-sm text-gray-600", children: [filteredLocations.length, " localiza\u00E7\u00F5es"] })] })] }) }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-3 gap-6", children: [_jsx("div", { className: "lg:col-span-2", children: _jsx("div", { className: "bg-white rounded-lg border border-gray-200 p-6", children: _jsx("div", { className: "bg-gray-100 rounded-lg h-[600px] flex items-center justify-center", children: _jsxs("div", { className: "text-center", children: [_jsx(MapPin, { className: "w-20 h-20 text-gray-400 mx-auto mb-4" }), _jsx("h3", { className: "text-xl font-medium text-gray-900 mb-3", children: "Mapa Interativo" }), _jsx("p", { className: "text-gray-600 mb-6 max-w-md mx-auto", children: "Integra\u00E7\u00E3o com Google Maps ou Leaflet ser\u00E1 adicionada para visualiza\u00E7\u00E3o interativa dos processos por localiza\u00E7\u00E3o geogr\u00E1fica" }), _jsxs("div", { className: "flex justify-center gap-4", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("div", { className: "w-3 h-3 rounded-full bg-red-500" }), _jsx("span", { className: "text-sm text-gray-700", children: "Alta Prioridade" })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("div", { className: "w-3 h-3 rounded-full bg-yellow-500" }), _jsx("span", { className: "text-sm text-gray-700", children: "M\u00E9dia Prioridade" })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("div", { className: "w-3 h-3 rounded-full bg-green-500" }), _jsx("span", { className: "text-sm text-gray-700", children: "Baixa Prioridade" })] })] })] }) }) }) }), _jsxs("div", { className: "lg:col-span-1", children: [_jsxs("div", { className: "bg-white rounded-lg border border-gray-200", children: [_jsx("div", { className: "p-4 border-b border-gray-200", children: _jsx("h3", { className: "font-semibold text-gray-900", children: "Processos" }) }), _jsx("div", { className: "max-h-[600px] overflow-y-auto", children: filteredLocations.map((location) => (_jsx("div", { className: `p-4 border-b border-gray-100 cursor-pointer transition-colors ${selectedLocation?.id === location.id ? 'bg-blue-50' : 'hover:bg-gray-50'}`, onClick: () => setSelectedLocation(location), children: _jsxs("div", { className: "flex items-start gap-3", children: [_jsx("div", { className: `w-3 h-3 rounded-full mt-1.5 flex-shrink-0 ${getPriorityColor(location.nivel_prioridade)}` }), _jsxs("div", { className: "flex-1 min-w-0", children: [_jsx("p", { className: "font-medium text-gray-900 text-sm truncate", children: location.titulo }), _jsxs("p", { className: "text-xs text-gray-600 mb-1", children: ["N\u00BA ", location.numero] }), _jsxs("div", { className: "flex items-center gap-1 text-xs text-gray-500", children: [_jsx(MapPin, { className: "w-3 h-3" }), _jsx("span", { className: "truncate", children: location.comarca })] }), _jsx("p", { className: "text-xs text-gray-900 mt-1 font-medium", children: new Intl.NumberFormat('pt-BR', {
                                                                    style: 'currency',
                                                                    currency: 'BRL',
                                                                    notation: 'compact'
                                                                }).format(location.valor_causa) })] })] }) }, location.id))) })] }), selectedLocation && (_jsxs("div", { className: "mt-4 bg-white rounded-lg border border-gray-200 p-4", children: [_jsx("h4", { className: "font-semibold text-gray-900 mb-3", children: "Detalhes" }), _jsxs("div", { className: "space-y-3 text-sm", children: [_jsxs("div", { children: [_jsx("span", { className: "text-gray-600", children: "N\u00FAmero:" }), _jsx("p", { className: "font-medium text-gray-900", children: selectedLocation.numero })] }), _jsxs("div", { children: [_jsx("span", { className: "text-gray-600", children: "Comarca:" }), _jsx("p", { className: "font-medium text-gray-900", children: selectedLocation.comarca })] }), _jsxs("div", { children: [_jsx("span", { className: "text-gray-600", children: "Endere\u00E7o:" }), _jsx("p", { className: "font-medium text-gray-900", children: selectedLocation.endereco })] }), _jsxs("div", { children: [_jsx("span", { className: "text-gray-600", children: "Status:" }), _jsx("span", { className: "ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded", children: selectedLocation.status })] }), _jsxs("div", { children: [_jsx("span", { className: "text-gray-600", children: "Coordenadas:" }), _jsxs("p", { className: "font-mono text-xs text-gray-700", children: [selectedLocation.latitude, ", ", selectedLocation.longitude] })] }), _jsxs("button", { className: "w-full mt-2 px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2", children: [_jsx(Navigation, { className: "w-4 h-4" }), "Abrir no Maps"] })] })] }))] })] }), _jsxs("div", { className: "mt-6 bg-white rounded-lg border border-gray-200 p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-gray-900 mb-4", children: "Estat\u00EDsticas por Regi\u00E3o" }), _jsx("div", { className: "grid grid-cols-1 md:grid-cols-4 gap-4", children: ['Porto Alegre', 'Caxias do Sul', 'Pelotas', 'Santa Maria'].map((cidade) => {
                            const count = locations.filter(l => l.comarca.includes(cidade)).length;
                            const total = locations.filter(l => l.comarca.includes(cidade))
                                .reduce((sum, l) => sum + l.valor_causa, 0);
                            return (_jsxs("div", { className: "bg-gray-50 rounded-lg p-4", children: [_jsx("h4", { className: "font-medium text-gray-900 mb-2", children: cidade }), _jsx("p", { className: "text-2xl font-bold text-blue-600 mb-1", children: count }), _jsx("p", { className: "text-xs text-gray-600", children: new Intl.NumberFormat('pt-BR', {
                                            style: 'currency',
                                            currency: 'BRL',
                                            notation: 'compact'
                                        }).format(total) })] }, cidade));
                        }) })] })] }));
}
