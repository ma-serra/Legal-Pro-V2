
import { useState, useEffect } from 'react';
import {
    Calculator, TrendingUp, Scale, BookOpen, AlertTriangle, Check,
    PieChart, BarChart3, Building2, Landmark, RefreshCw, FileText,
    DollarSign, ArrowRight, Percent, Clock, History, Download, Printer, Save
} from 'lucide-react';
import api from '../../lib/api';
import {
    ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid
} from 'recharts';

export default function CalculosTributariosPage() {
    const [activeTab, setActiveTab] = useState<'dashboard' | 'simulador' | 'recuperacao' | 'legislacao' | 'historico'>('dashboard');

    return (
        <div className="p-6 max-w-[1600px] mx-auto space-y-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <Calculator className="w-8 h-8 text-primary" />
                        Cálculos e Inteligência Tributária
                    </h1>
                    <p className="text-muted-foreground mt-1">
                        Simuladores, Recuperação de Créditos e Dados Estratégicos
                    </p>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex border-b border-border mb-6 overflow-x-auto">
                {[
                    { id: 'dashboard', label: 'Panorama Geral', icon: BarChart3 },
                    { id: 'simulador', label: 'Simulador de Regime', icon: Scale },
                    { id: 'recuperacao', label: 'Recuperação de Créditos', icon: TrendingUp },
                    { id: 'historico', label: 'Histórico & Relatórios', icon: History },
                    { id: 'legislacao', label: 'Dados Legislativos', icon: BookOpen },
                ].map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as any)}
                        className={`flex items-center gap-2 px-6 py-3 border-b-2 transition-colors whitespace-nowrap ${activeTab === tab.id
                                ? 'border-primary text-primary font-medium'
                                : 'border-transparent text-muted-foreground hover:text-foreground'
                            }`}
                    >
                        <tab.icon className="w-4 h-4" />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Content Area */}
            <div className="min-h-[600px]">
                {activeTab === 'dashboard' && <DashboardTributario />}
                {activeTab === 'simulador' && <SimuladorRegime />}
                {activeTab === 'recuperacao' && <RecuperacaoCredito />}
                {activeTab === 'historico' && <HistoricoSimulacoes />}
                {activeTab === 'legislacao' && <LegislacaoDados />}
            </div>
        </div>
    );
}

// === SUB-COMPONENTS ===

function DashboardTributario() {
    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <CardResumo title="Carga Tributária Média" value="33.8%" desc="PIB Brasil (Fonte: Tesouro)" icon={PercentIcon} color="blue" />
                <CardResumo title="Normas Ativas" value="38.540+" desc="Federais (Fonte: IBPT)" icon={FileText} color="amber" />
                <CardResumo title="SELIC Atual" value="11.25%" desc="Definida pelo COPOM" icon={TrendingUp} color="green" />
                <CardResumo title="Contencioso" value="R$ 5.4 mi" desc="Valor em Discussão (CNJ)" icon={Scale} color="red" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-card border border-border rounded-xl p-6">
                    <h3 className="font-bold mb-4 flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-yellow-500" />
                        Alertas de Compliance
                    </h3>
                    <ul className="space-y-3">
                        <li className="flex items-start gap-3 p-3 bg-red-900/10 rounded-lg border border-red-900/20">
                            <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5" />
                            <div>
                                <h4 className="font-semibold text-red-400">Reforma Tributária (PEC 45/2019)</h4>
                                <p className="text-sm text-muted-foreground">Período de transição iniciando em 2026. Necessário revisar cadastros de produtos (NCM).</p>
                            </div>
                        </li>
                    </ul>
                </div>

                <div className="bg-card border border-border rounded-xl p-6">
                    <h3 className="font-bold mb-4 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-primary" />
                        Oportunidades
                    </h3>
                    <ul className="space-y-3">
                        <li className="flex items-center justify-between p-3 bg-card border border-border rounded-lg hover:border-primary transition-colors cursor-pointer">
                            <span className="font-medium">Simulador Lucro Real vs Presumido</span>
                            <ArrowRight className="w-4 h-4 text-primary" />
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    );
}

function SimuladorRegime() {
    const [receita, setReceita] = useState(300000); // 100k/mês
    const [folha, setFolha] = useState(84000);    // 28k/mês (28%)
    const [atividade, setAtividade] = useState('servicos');
    const [clienteNome, setClienteNome] = useState('');
    const [resultado, setResultado] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [salvando, setSalvando] = useState(false);

    const calcular = async () => {
        setLoading(true);
        try {
            const [resSimples, resPresumido] = await Promise.all([
                api.post('/api/calculos-tributarios/simular/simples', {
                    receita_mensal: receita / 3,
                    receita_bruta_12_meses: receita * 4,
                    folha_12_meses: folha * 4,
                    anexo: 'ANEXO_III'
                }),
                api.post('/api/calculos-tributarios/simular/presumido', {
                    receita_trimestral: receita,
                    atividade,
                    folha_pagamento: folha
                })
            ]);

            setResultado({
                simples: resSimples.data,
                presumido: resPresumido.data
            });
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const salvarSimulacao = async () => {
        if (!resultado) return;
        setSalvando(true);
        try {
            await api.post('/api/calculos-tributarios/simulacoes', {
                cliente_nome: clienteNome || 'Cliente Não Identificado',
                tipo_simulacao: 'COMPARATIVO_REGIME',
                parametros_input: { receita, folha, atividade },
                resultado_output: resultado
            });
            alert('Simulação salva com sucesso! Consulte na aba Histórico.');
        } catch (err) {
            console.error(err);
            alert('Erro ao salvar simulação.');
        } finally {
            setSalvando(false);
        }
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 bg-card border border-border rounded-xl p-6 space-y-4">
                <h3 className="font-bold mb-4">Parâmetros de Simulação (Trimestral)</h3>

                <div className="space-y-2">
                    <label className="text-sm font-medium">Nome do Cliente (Opcional)</label>
                    <input
                        type="text"
                        value={clienteNome}
                        onChange={(e) => setClienteNome(e.target.value)}
                        placeholder="Ex: Empresa ABC Ltda"
                        className="w-full p-2 bg-background border border-border rounded-md"
                    />
                </div>

                <div className="space-y-2">
                    <label className="text-sm font-medium">Receita Trimestral (R$)</label>
                    <input
                        type="number"
                        value={receita}
                        onChange={(e) => setReceita(Number(e.target.value))}
                        className="w-full p-2 bg-background border border-border rounded-md"
                    />
                </div>

                <div className="space-y-2">
                    <label className="text-sm font-medium">Folha de Pagamento Trimestral (R$)</label>
                    <input
                        type="number"
                        value={folha}
                        onChange={(e) => setFolha(Number(e.target.value))}
                        className="w-full p-2 bg-background border border-border rounded-md"
                    />
                </div>

                <div className="space-y-2">
                    <label className="text-sm font-medium">Atividade Principal</label>
                    <select
                        value={atividade}
                        onChange={(e) => setAtividade(e.target.value)}
                        className="w-full p-2 bg-background border border-border rounded-md"
                    >
                        <option value="servicos">Serviços em Geral (32%)</option>
                        <option value="comercio">Comércio (8%)</option>
                        <option value="industria">Indústria (8%)</option>
                    </select>
                </div>

                <button
                    onClick={calcular}
                    disabled={loading}
                    className="w-full py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 mt-4"
                >
                    {loading ? 'Calculando...' : 'Simular Comparativo'}
                </button>
            </div>

            <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="font-bold">Resultados Comparativos</h3>
                    {resultado && (
                        <button
                            onClick={salvarSimulacao}
                            disabled={salvando}
                            className="flex items-center gap-2 px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded-md text-sm"
                        >
                            <Save className="w-4 h-4" />
                            {salvando ? 'Salvando...' : 'Salvar Simulação'}
                        </button>
                    )}
                </div>

                {resultado ? (
                    <div className="space-y-6">
                        <div className="grid grid-cols-2 gap-4">
                            <div className={`p-4 rounded-lg border-2 ${resultado.simples.total < resultado.presumido.total ? 'border-green-500 bg-green-500/10' : 'border-border'}`}>
                                <h4 className="font-bold">Simples Nacional</h4>
                                <p className="text-2xl font-bold mt-2">R$ {resultado.simples.total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</p>
                                <p className="text-sm text-muted-foreground mt-1">Alíquota Efetiva: {resultado.simples.aliquota_efetiva.toFixed(2)}%</p>
                                <p className="text-xs text-muted-foreground">{resultado.simples.fator_r_status !== 'N/A' ? `Fator R: ${resultado.simples.fator_r_status}` : ''}</p>
                            </div>

                            <div className={`p-4 rounded-lg border-2 ${resultado.presumido.total < resultado.simples.total ? 'border-green-500 bg-green-500/10' : 'border-border'}`}>
                                <h4 className="font-bold">Lucro Presumido</h4>
                                <p className="text-2xl font-bold mt-2">R$ {resultado.presumido.total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</p>
                                <p className="text-sm text-muted-foreground mt-1">Alíquota Efetiva: {resultado.presumido.aliquota_efetiva.toFixed(2)}%</p>
                            </div>
                        </div>

                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart
                                    data={[
                                        { name: 'Simples', valor: resultado.simples.total },
                                        { name: 'L. Presumido', valor: resultado.presumido.total },
                                    ]}
                                    layout="vertical"
                                >
                                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                    <XAxis type="number" stroke="#888" />
                                    <YAxis dataKey="name" type="category" stroke="#888" width={100} />
                                    <Tooltip contentStyle={{ backgroundColor: '#1f1f1f' }} cursor={{ fill: 'transparent' }} />
                                    <Bar dataKey="valor" fill="#8884d8" barSize={40} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                ) : (
                    <div className="h-full flex items-center justify-center text-muted-foreground">
                        Preencha os dados e clique em Simular
                    </div>
                )}
            </div>
        </div>
    );
}

function RecuperacaoCredito() {
    const [faturamento, setFaturamento] = useState(1000000);
    const [icms, setIcms] = useState(18);
    const [clienteNome, setClienteNome] = useState('');
    const [resultado, setResultado] = useState<any>(null);
    const [salvando, setSalvando] = useState(false);

    const calcular = async () => {
        try {
            const res = await api.post('/api/calculos-tributarios/simular/tese-icms', {
                faturamento_mensal: faturamento,
                aliquota_icms: icms,
                meses: 60
            });
            setResultado(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const salvarSimulacao = async () => {
        if (!resultado) return;
        setSalvando(true);
        try {
            await api.post('/api/calculos-tributarios/simulacoes', {
                cliente_nome: clienteNome || 'Cliente Não Identificado',
                tipo_simulacao: 'RECUPERACAO_ICMS',
                parametros_input: { faturamento, icms },
                resultado_output: resultado
            });
            alert('Simulação salva com sucesso! Consulte na aba Histórico.');
        } catch (err) {
            console.error(err);
            alert('Erro ao salvar simulação.');
        } finally {
            setSalvando(false);
        }
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
                <div className="bg-card border border-border rounded-xl p-6">
                    <h3 className="font-bold mb-4">Calculadora "Tese do Século"</h3>

                    <div className="space-y-4">
                        <div>
                            <label className="text-sm font-medium">Nome do Cliente (Opcional)</label>
                            <input
                                type="text"
                                value={clienteNome}
                                onChange={(e) => setClienteNome(e.target.value)}
                                className="w-full p-2 bg-background border border-border rounded-md"
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium">Faturamento Médio Mensal (R$)</label>
                            <input
                                type="number"
                                value={faturamento}
                                onChange={e => setFaturamento(Number(e.target.value))}
                                className="w-full p-2 bg-background border border-border rounded-md"
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium">Alíquota Média ICMS (%)</label>
                            <input
                                type="number"
                                value={icms}
                                onChange={e => setIcms(Number(e.target.value))}
                                className="w-full p-2 bg-background border border-border rounded-md"
                            />
                        </div>
                        <button onClick={calcular} className="w-full py-2 bg-primary text-white rounded-md mt-2">
                            Calcular Potencial
                        </button>
                    </div>
                </div>
            </div>

            <div className="bg-card border border-border rounded-xl p-6 flex flex-col justify-center">
                {resultado ? (
                    <div className="text-center space-y-6">
                        <div>
                            <h4 className="text-muted-foreground font-medium uppercase tracking-wider text-xs">Potencial Total Recuperável (5 Anos)</h4>
                            <p className="text-4xl font-bold text-green-400 mt-2">
                                R$ {resultado.total_final_estimado.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</p>
                            <p className="text-sm text-muted-foreground mt-1">Inclui Principal + Atualização SELIC Estimada (~40%)</p>
                        </div>

                        <div className="flex justify-center pt-4">
                            <button
                                onClick={salvarSimulacao}
                                disabled={salvando}
                                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg"
                            >
                                <Save className="w-4 h-4" />
                                {salvando ? 'Salvando...' : 'Salvar Estimativa e Gerar PDF'}
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="text-center text-muted-foreground">
                        <Calculator className="w-12 h-12 mx-auto mb-2 opacity-20" />
                        <p>Simule o potencial de recuperação tributária</p>
                    </div>
                )}
            </div>
        </div>
    );
}

function HistoricoSimulacoes() {
    const [simulacoes, setSimulacoes] = useState<any[]>([]);

    useEffect(() => {
        carregarHistorico();
    }, []);

    const carregarHistorico = async () => {
        try {
            const res = await api.get('/api/calculos-tributarios/simulacoes');
            setSimulacoes(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const downloadPDF = async (id: string) => {
        try {
            const response = await api.get(`/api/calculos-tributarios/simulacoes/${id}/pdf`, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `simulacao_${id.substring(0, 8)}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error('Erro ao baixar PDF:', error);
            alert('Erro ao gerar PDF');
        }
    };

    return (
        <div className="bg-card border border-border rounded-xl p-6">
            <div className="flex justify-between items-center mb-6">
                <h3 className="font-bold text-xl">Histórico de Simulações</h3>
                <button onClick={carregarHistorico} className="p-2 bg-background border border-border rounded-lg hover:border-primary">
                    <RefreshCw className="w-4 h-4" />
                </button>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-border text-left">
                            <th className="py-3 px-4 font-medium text-muted-foreground">Data</th>
                            <th className="py-3 px-4 font-medium text-muted-foreground">Cliente</th>
                            <th className="py-3 px-4 font-medium text-muted-foreground">Tipo</th>
                            <th className="py-3 px-4 font-medium text-muted-foreground">Parâmetros Principais</th>
                            <th className="py-3 px-4 font-medium text-muted-foreground text-right">Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        {simulacoes.map((sim: any) => (
                            <tr key={sim.id} className="border-b border-border/50 hover:bg-accent/50">
                                <td className="py-3 px-4 text-sm">{new Date(sim.data_criacao).toLocaleString('pt-BR')}</td>
                                <td className="py-3 px-4 text-sm font-medium">{sim.cliente_nome || '-'}</td>
                                <td className="py-3 px-4 text-sm">
                                    <span className={`px-2 py-1 rounded text-xs ${sim.tipo_simulacao === 'COMPARATIVO_REGIME'
                                            ? 'bg-blue-500/10 text-blue-400'
                                            : 'bg-green-500/10 text-green-400'
                                        }`}>
                                        {sim.tipo_simulacao.replace('_', ' ')}
                                    </span>
                                </td>
                                <td className="py-3 px-4 text-sm text-muted-foreground">
                                    {Object.entries(sim.parametros_input).slice(0, 2).map(([k, v]) => `${k}: ${v}`).join(', ')}...
                                </td>
                                <td className="py-3 px-4 text-sm text-right">
                                    <button
                                        onClick={() => downloadPDF(sim.id)}
                                        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 hover:bg-primary/20 text-primary rounded-md text-xs font-medium transition-colors"
                                    >
                                        <Download className="w-3 h-3" />
                                        PDF
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {simulacoes.length === 0 && (
                            <tr>
                                <td colSpan={5} className="py-8 text-center text-muted-foreground">
                                    Nenhuma simulação salva.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function LegislacaoDados() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <CardLink title="Constituição Federal" desc="Arts. 145 a 162 - Sistema Tributário Nacional" href="https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm" />
            <CardLink title="Código Tributário Nacional" desc="Lei 5.172/1966" href="https://www.planalto.gov.br/ccivil_03/leis/l5172compilado.htm" />
            <CardLink title="Regulamento do Imposto de Renda" desc="Decreto 9.580/2018" href="http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/decreto/d9580.htm" />
            <CardLink title="Simples Nacional" desc="Lei Complementar 123/2006" href="http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp123.htm" />
            <CardLink title="Reforma Tributária" desc="PEC 45/2019 e regulamentações" href="https://www.camara.leg.br/propostas-legislativas/2196833" />
        </div>
    );
}

function CardLink({ title, desc, href }: { title: string, desc: string, href: string }) {
    return (
        <a href={href} target="_blank" rel="noopener noreferrer" className="block p-4 border border-border rounded-xl hover:border-primary transition-colors bg-card">
            <div className="flex items-center justify-between mb-2">
                <BookOpen className="w-5 h-5 text-primary" />
                <ArrowRight className="w-4 h-4 text-muted-foreground" />
            </div>
            <h3 className="font-bold text-lg">{title}</h3>
            <p className="text-sm text-muted-foreground mt-1">{desc}</p>
        </a>
    );
}

function CardResumo({ title, value, desc, icon: Icon, color }: any) {
    const colors: any = {
        blue: 'text-blue-400 bg-blue-400/10 border-blue-400/20',
        green: 'text-green-400 bg-green-400/10 border-green-400/20',
        red: 'text-red-400 bg-red-400/10 border-red-400/20',
        amber: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
    };

    return (
        <div className={`p-4 rounded-xl border ${colors[color] || colors.blue}`}>
            <div className="flex items-center justify-between mb-2">
                <Icon className="w-5 h-5 opacity-80" />
            </div>
            <p className="text-2xl font-bold">{value}</p>
            <p className="text-xs opacity-70 mt-1">{title}</p>
            <p className="text-[10px] opacity-50">{desc}</p>
        </div>
    );
}

const PercentIcon = (props: any) => <Percent {...props} />;
const ClockIcon = (props: any) => <Clock {...props} />;
