import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Analises from './pages/Analises';
import Assistentes from './pages/Assistentes';
import NotFound from './pages/NotFound';
// Public SaaS Pages
import LandingPage from './pages/public/LandingPage';
import PricingPage from './pages/public/PricingPage';
import SignupPage from './pages/public/SignupPage';
// Processos Pages - NOVA ESTRUTURA MODERNA
import ProcessosDinamicosList from './pages/processos/ProcessosDinamicosList';
import ProcessoDetailsPage from './pages/processos/ProcessoDetailsPage';
import ImportacaoPage from './pages/processos/ImportacaoPage';
import TesesPage from './pages/processos/TesesPage';
import IndicesPage from './pages/processos/IndicesPage';
// Multi-Agente Pages
import MultiAgenteDashboard from './pages/multiagente/MultiAgenteDashboard';
import MultiAgenteOrquestrador from './pages/multiagente/MultiAgenteOrquestrador';
import MultiAgenteHistorico from './pages/multiagente/MultiAgenteHistorico';
import MultiAgentePerformance from './pages/multiagente/MultiAgentePerformance';
import SelecaoInteligente from './pages/multiagente/SelecaoInteligente';
// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import AgentsList from './pages/admin/AgentsList';
import SystemMonitoring from './pages/admin/SystemMonitoring';
import UserManagement from './pages/admin/UserManagement';
import PermissionsManagement from './pages/admin/PermissionsManagement';
import DatabaseManagement from './pages/admin/DatabaseManagement';
import DatabaseStatus from './pages/admin/DatabaseStatus';
import APIConfiguration from './pages/admin/APIConfiguration';
import AdminModulesOverview from './pages/admin/AdminModulesOverview';
// Clientes Pages
import ClientsList from './pages/clients/ClientsList';
import NewClient from './pages/clients/NewClient';
import ClientDetails from './pages/clients/ClientDetails';
import EditClient from './pages/clients/EditClient';
// Assistentes Pages
import AssistenteChat from './pages/assistentes/AssistenteChat';
import AssistentesList from './pages/assistentes/AssistentesList';
import ConfigureAssistant from './pages/assistentes/ConfigureAssistant';
import PromptsManagement from './pages/assistentes/PromptsManagement';
// Análises Pages
import AnalysisHub from './pages/analises/AnalysisHub';
// CPFL/Setor Energia Pages
import CPFLAnalytics from './pages/setorenergia/CPFLAnalytics';
import CPFLDashboard from './pages/setorenergia/CPFLDashboard';
import Sobrestados from './pages/setorenergia/Sobrestados';
import RiskMap from './pages/setorenergia/RiskMap';
import Geolocation from './pages/setorenergia/Geolocation';
import Hearings from './pages/setorenergia/Hearings';
// Templates Pages
import TemplatesList from './pages/templates/TemplatesList';
import NewTemplate from './pages/templates/NewTemplate';
import EditTemplate from './pages/templates/EditTemplate';
import TemplateCategories from './pages/templates/TemplateCategories';
// Settings Pages
import Settings from './pages/settings/Settings';
// Billing Pages
import BillingOverview from './pages/billing/BillingOverview';
export default function App() {
    return (_jsx(BrowserRouter, { children: _jsx(AuthProvider, { children: _jsxs(Routes, { children: [_jsx(Route, { path: "/", element: _jsx(LandingPage, {}) }), _jsx(Route, { path: "/pricing", element: _jsx(PricingPage, {}) }), _jsx(Route, { path: "/signup", element: _jsx(SignupPage, {}) }), _jsx(Route, { path: "/login", element: _jsx(Login, {}) }), _jsxs(Route, { element: _jsx(ProtectedRoute, { children: _jsx(Layout, {}) }), children: [_jsx(Route, { path: "/dashboard", element: _jsx(Dashboard, {}) }), _jsx(Route, { path: "/home", element: _jsx(Home, {}) }), _jsxs(Route, { path: "/processos", children: [_jsx(Route, { index: true, element: _jsx(ProcessosDinamicosList, {}) }), _jsx(Route, { path: "importar", element: _jsx(ImportacaoPage, {}) }), _jsx(Route, { path: "teses", element: _jsx(TesesPage, {}) }), _jsx(Route, { path: "indices", element: _jsx(IndicesPage, {}) }), _jsx(Route, { path: ":id", element: _jsx(ProcessoDetailsPage, {}) })] }), _jsx(Route, { path: "/multi-agente", element: _jsx(MultiAgenteDashboard, {}) }), _jsx(Route, { path: "/multi-agente/orquestrador", element: _jsx(MultiAgenteOrquestrador, {}) }), _jsx(Route, { path: "/multi-agente/historico", element: _jsx(MultiAgenteHistorico, {}) }), _jsx(Route, { path: "/multi-agente/performance", element: _jsx(MultiAgentePerformance, {}) }), _jsx(Route, { path: "/multi-agente/selecao", element: _jsx(SelecaoInteligente, {}) }), _jsx(Route, { path: "/analises", element: _jsx(Analises, {}) }), _jsx(Route, { path: "/analises/hub", element: _jsx(AnalysisHub, {}) }), _jsx(Route, { path: "/assistentes", element: _jsx(Assistentes, {}) }), _jsx(Route, { path: "/assistentes/lista", element: _jsx(AssistentesList, {}) }), _jsx(Route, { path: "/assistentes/:id/chat", element: _jsx(AssistenteChat, {}) }), _jsx(Route, { path: "/assistentes/:id/configurar", element: _jsx(ConfigureAssistant, {}) }), _jsx(Route, { path: "/assistentes/prompts", element: _jsx(PromptsManagement, {}) }), _jsx(Route, { path: "/clientes", element: _jsx(ClientsList, {}) }), _jsx(Route, { path: "/clientes/novo", element: _jsx(NewClient, {}) }), _jsx(Route, { path: "/clientes/:id", element: _jsx(ClientDetails, {}) }), _jsx(Route, { path: "/clientes/:id/editar", element: _jsx(EditClient, {}) }), _jsx(Route, { path: "/setorenergia", element: _jsx(CPFLDashboard, {}) }), _jsx(Route, { path: "/setorenergia/analytics", element: _jsx(CPFLAnalytics, {}) }), _jsx(Route, { path: "/setorenergia/sobrestados", element: _jsx(Sobrestados, {}) }), _jsx(Route, { path: "/setorenergia/mapa-risco", element: _jsx(RiskMap, {}) }), _jsx(Route, { path: "/setorenergia/geolocalizacao", element: _jsx(Geolocation, {}) }), _jsx(Route, { path: "/setorenergia/audiencias", element: _jsx(Hearings, {}) }), _jsx(Route, { path: "/templates", element: _jsx(TemplatesList, {}) }), _jsx(Route, { path: "/templates/novo", element: _jsx(NewTemplate, {}) }), _jsx(Route, { path: "/templates/:id/editar", element: _jsx(EditTemplate, {}) }), _jsx(Route, { path: "/templates/categorias", element: _jsx(TemplateCategories, {}) }), _jsx(Route, { path: "/settings", element: _jsx(Settings, {}) }), _jsx(Route, { path: "/billing", element: _jsx(BillingOverview, {}) }), _jsx(Route, { path: "/admin", element: _jsx(AdminDashboard, {}) }), _jsx(Route, { path: "/admin/monitoring", element: _jsx(SystemMonitoring, {}) }), _jsx(Route, { path: "/admin/agents", element: _jsx(AgentsList, {}) }), _jsx(Route, { path: "/admin/usuarios", element: _jsx(UserManagement, {}) }), _jsx(Route, { path: "/admin/permissoes", element: _jsx(PermissionsManagement, {}) }), _jsx(Route, { path: "/admin/database", element: _jsx(DatabaseManagement, {}) }), _jsx(Route, { path: "/admin/database/status", element: _jsx(DatabaseStatus, {}) }), _jsx(Route, { path: "/admin/apis", element: _jsx(APIConfiguration, {}) }), _jsx(Route, { path: "/admin/modulos", element: _jsx(AdminModulesOverview, {}) }), _jsx(Route, { path: "*", element: _jsx(NotFound, {}) })] })] }) }) }));
}
