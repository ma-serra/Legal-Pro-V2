import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Gavel, Plus, BarChart2, Eye, Trash2 } from 'lucide-react';
import StatsCard from '../components/ui/StatsCard';
import PageHeader from '../components/ui/PageHeader';
import FilterBar from '../components/ui/FilterBar';
import DataTable from '../components/ui/DataTable';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import api from '../lib/api';
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
];
const niveisRisco = [
    { value: '', label: 'Todos os Riscos' },
    { value: 'Baixo', label: 'Baixo' },
    { value: 'Médio', label: 'Médio' },
    { value: 'Alto', label: 'Alto' }
];
export default function Processos() {
    const [processos, setProcessos] = useState([]);
    const [estatisticas, setEstatisticas] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [filtroArea, setFiltroArea] = useState('');
    const [filtroRisco, setFiltroRisco] = useState('');
    const [busca, setBusca] = useState('');
    useEffect(() => {
        fetchData();
    }, []);
    async function fetchData() {
        setIsLoading(true);
        try {
            const [processosRes, statsRes] = await Promise.all([
                api.get('/processos-juridicos/processos').catch(() => ({ data: { processos: [] } })),
                api.get('/processos-juridicos/estatisticas').catch(() => ({ data: null }))
            ]);
            if (processosRes.data?.processos) {
                setProcessos(processosRes.data.processos);
            }
            else {
                setProcessos(mockProcessos);
            }
            if (statsRes.data) {
                setEstatisticas(statsRes.data);
            }
            else {
                setEstatisticas({
                    total_processos: mockProcessos.length,
                    areas_diferentes: 12,
                    valor_total_causas: 15750000,
                    processos_alto_risco: 5
                });
            }
        }
        catch (error) {
            console.error('Error fetching processos:', error);
            setProcessos(mockProcessos);
            setEstatisticas({
                total_processos: mockProcessos.length,
                areas_diferentes: 12,
                valor_total_causas: 15750000,
                processos_alto_risco: 5
            });
        }
        finally {
            setIsLoading(false);
        }
    }
    const filteredProcessos = processos.filter((p) => {
        if (filtroArea && p.area_juridica !== filtroArea)
            return false;
        if (filtroRisco && p.nivel_risco !== filtroRisco)
            return false;
        if (busca) {
            const searchLower = busca.toLowerCase();
            return (p.numero_cnj.toLowerCase().includes(searchLower) ||
                p.cliente.toLowerCase().includes(searchLower));
        }
        return true;
    });
    const formatCurrency = (value) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    };
    const getRiskBadge = (risco) => {
        const variant = risco === 'Alto' ? 'danger' : risco === 'Médio' ? 'warning' : 'success';
        return _jsx(Badge, { variant: variant, children: risco });
    };
    const columns = [
        { key: 'numero_cnj', header: 'Número CNJ' },
        { key: 'cliente', header: 'Cliente' },
        { key: 'area_juridica', header: 'Área Jurídica' },
        {
            key: 'valor_causa',
            header: 'Valor da Causa',
            render: (item) => formatCurrency(item.valor_causa)
        },
        {
            key: 'nivel_risco',
            header: 'Risco',
            render: (item) => getRiskBadge(item.nivel_risco)
        },
        { key: 'status', header: 'Status' },
        {
            key: 'actions',
            header: 'Ações',
            render: () => (_jsxs("div", { className: "flex gap-2", children: [_jsx("button", { className: "p-1 hover:bg-accent rounded", title: "Ver detalhes", children: _jsx(Eye, { className: "w-4 h-4" }) }), _jsx("button", { className: "p-1 hover:bg-red-500/20 rounded text-red-400", title: "Excluir", children: _jsx(Trash2, { className: "w-4 h-4" }) })] }))
        }
    ];
    if (isLoading) {
        return (_jsx("div", { className: "flex items-center justify-center min-h-96", children: _jsx(LoadingSpinner, { size: "lg", text: "Carregando processos..." }) }));
    }
    return (_jsxs("div", { className: "space-y-6", children: [_jsxs(PageHeader, { title: "Processos Jur\u00EDdicos", icon: Gavel, children: [_jsx(Button, { variant: "success", icon: Plus, children: "Novo Processo" }), _jsx(Button, { variant: "secondary", icon: BarChart2, children: "Estat\u00EDsticas" })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4", children: [_jsx(StatsCard, { title: "Total de Processos", value: estatisticas?.total_processos || 0, icon: Gavel, variant: "primary" }), _jsx(StatsCard, { title: "\u00C1reas Jur\u00EDdicas", value: estatisticas?.areas_diferentes || 0, icon: BarChart2, variant: "success" }), _jsx(StatsCard, { title: "Valor Total", value: formatCurrency(estatisticas?.valor_total_causas || 0), icon: Gavel, variant: "warning" }), _jsx(StatsCard, { title: "Alto Risco", value: estatisticas?.processos_alto_risco || 0, icon: Gavel, variant: "danger" })] }), _jsx(FilterBar, { filters: [
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
                ], searchValue: busca, onSearchChange: setBusca, searchPlaceholder: "Buscar por CNJ, cliente..." }), _jsx("div", { className: "bg-card rounded-xl border border-border", children: _jsx(DataTable, { data: filteredProcessos, columns: columns, emptyMessage: "Nenhum processo encontrado", onRowClick: (item) => console.log('Clicked:', item) }) })] }));
}
const mockProcessos = [
    { id: 1, numero_cnj: '0001234-56.2024.8.26.0100', cliente: 'Empresa ABC Ltda', area_juridica: 'Direito Empresarial', valor_causa: 250000, nivel_risco: 'Médio', status: 'Ativo', data_cadastro: '2024-01-15' },
    { id: 2, numero_cnj: '0002345-67.2024.8.26.0100', cliente: 'João Silva', area_juridica: 'Direito Trabalhista', valor_causa: 75000, nivel_risco: 'Baixo', status: 'Ativo', data_cadastro: '2024-02-10' },
    { id: 3, numero_cnj: '0003456-78.2024.8.26.0100', cliente: 'Maria Santos', area_juridica: 'Direito de Família', valor_causa: 150000, nivel_risco: 'Alto', status: 'Em análise', data_cadastro: '2024-03-05' },
    { id: 4, numero_cnj: '0004567-89.2024.8.26.0100', cliente: 'Tech Solutions SA', area_juridica: 'Direito Digital', valor_causa: 500000, nivel_risco: 'Alto', status: 'Ativo', data_cadastro: '2024-03-20' },
    { id: 5, numero_cnj: '0005678-90.2024.8.26.0100', cliente: 'Construtora XYZ', area_juridica: 'Direito Imobiliário', valor_causa: 1200000, nivel_risco: 'Médio', status: 'Ativo', data_cadastro: '2024-04-01' },
    { id: 6, numero_cnj: '0006789-01.2024.8.26.0100', cliente: 'Pedro Oliveira', area_juridica: 'Direito do Consumidor', valor_causa: 25000, nivel_risco: 'Baixo', status: 'Arquivado', data_cadastro: '2024-04-15' },
    { id: 7, numero_cnj: '0007890-12.2024.8.26.0100', cliente: 'Banco Nacional', area_juridica: 'Direito Bancário', valor_causa: 800000, nivel_risco: 'Alto', status: 'Ativo', data_cadastro: '2024-05-01' },
    { id: 8, numero_cnj: '0008901-23.2024.8.26.0100', cliente: 'Ana Costa', area_juridica: 'Direito Previdenciário', valor_causa: 180000, nivel_risco: 'Baixo', status: 'Ativo', data_cadastro: '2024-05-10' }
];
