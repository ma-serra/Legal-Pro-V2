import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Analises from './pages/Analises'
import Assistentes from './pages/Assistentes'
import NotFound from './pages/NotFound'

// Public SaaS Pages
import LandingPage from './pages/public/LandingPage'
import PricingPage from './pages/public/PricingPage'
import SignupPage from './pages/public/SignupPage'

// Processos Pages - NOVA ESTRUTURA MODERNA
import ProcessosDinamicosList from './pages/processos/ProcessosDinamicosList'
import ProcessoDetailsPage from './pages/processos/ProcessoDetailsPage'
import NovoProcessoPage from './pages/processos/NovoProcessoPage'
import ImportacaoPage from './pages/processos/ImportacaoPage'
import TesesPage from './pages/processos/TesesPage'
import IndicesPage from './pages/processos/IndicesPage'

// Multi-Agente Pages
import MultiAgenteDashboard from './pages/multiagente/MultiAgenteDashboard'
import MultiAgenteOrquestrador from './pages/multiagente/MultiAgenteOrquestrador'
import MultiAgenteHistorico from './pages/multiagente/MultiAgenteHistorico'
import MultiAgentePerformance from './pages/multiagente/MultiAgentePerformance'
import SelecaoInteligente from './pages/multiagente/SelecaoInteligente'

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard'
import AgentsList from './pages/admin/AgentsList'
import SystemMonitoring from './pages/admin/SystemMonitoring'
import UserManagement from './pages/admin/UserManagement'
import PermissionsManagement from './pages/admin/PermissionsManagement'
import DatabaseManagement from './pages/admin/DatabaseManagement'
import DatabaseStatus from './pages/admin/DatabaseStatus'
import APIConfiguration from './pages/admin/APIConfiguration'
import AdminModulesOverview from './pages/admin/AdminModulesOverview'

// Clientes Pages
import ClientsList from './pages/clients/ClientsList'
import NewClient from './pages/clients/NewClient'
import ClientDetails from './pages/clients/ClientDetails'
import EditClient from './pages/clients/EditClient'

// Assistentes Pages
import AssistenteChat from './pages/assistentes/AssistenteChat'
import AssistentesList from './pages/assistentes/AssistentesList'
import ConfigureAssistant from './pages/assistentes/ConfigureAssistant'
import PromptsManagement from './pages/assistentes/PromptsManagement'

// Análises Pages
import AnalysisHub from './pages/analises/AnalysisHub'

// CPFL/Setor Energia Pages
import CPFLAnalytics from './pages/setorenergia/CPFLAnalytics'
import CPFLDashboard from './pages/setorenergia/CPFLDashboard'
import Sobrestados from './pages/setorenergia/Sobrestados'
import RiskMap from './pages/setorenergia/RiskMap'
import Geolocation from './pages/setorenergia/Geolocation'
import Hearings from './pages/setorenergia/Hearings'

// Templates Pages
import TemplatesList from './pages/templates/TemplatesList'
import NewTemplate from './pages/templates/NewTemplate'
import EditTemplate from './pages/templates/EditTemplate'
import TemplateCategories from './pages/templates/TemplateCategories'

// Settings Pages
import Settings from './pages/settings/Settings'

// Billing Pages
import BillingOverview from './pages/billing/BillingOverview'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/login" element={<Login />} />

          {/* Protected Routes */}
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            {/* Dashboard */}
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/home" element={<Home />} />

            {/* Processos - NOVA ESTRUTURA */}
            <Route path="/processos">
              <Route index element={<ProcessosDinamicosList />} />
              <Route path="novo" element={<NovoProcessoPage />} />
              <Route path="importar" element={<ImportacaoPage />} />
              <Route path="teses" element={<TesesPage />} />
              <Route path="indices" element={<IndicesPage />} />
              <Route path=":id" element={<ProcessoDetailsPage />} />
            </Route>

            {/* Multi-Agente - Módulo Completo */}
            <Route path="/multi-agente" element={<MultiAgenteDashboard />} />
            <Route path="/multi-agente/orquestrador" element={<MultiAgenteOrquestrador />} />
            <Route path="/multi-agente/historico" element={<MultiAgenteHistorico />} />
            <Route path="/multi-agente/performance" element={<MultiAgentePerformance />} />
            <Route path="/multi-agente/selecao" element={<SelecaoInteligente />} />

            {/* Análises */}
            <Route path="/analises" element={<Analises />} />
            <Route path="/analises/hub" element={<AnalysisHub />} />

            {/* Assistentes - Módulo Completo */}
            <Route path="/assistentes" element={<Assistentes />} />
            <Route path="/assistentes/lista" element={<AssistentesList />} />
            <Route path="/assistentes/:id/chat" element={<AssistenteChat />} />
            <Route path="/assistentes/:id/configurar" element={<ConfigureAssistant />} />
            <Route path="/assistentes/prompts" element={<PromptsManagement />} />

            {/* Clientes */}
            <Route path="/clientes" element={<ClientsList />} />
            <Route path="/clientes/novo" element={<NewClient />} />
            <Route path="/clientes/:id" element={<ClientDetails />} />
            <Route path="/clientes/:id/editar" element={<EditClient />} />

            {/* CPFL/Setor Energia - Módulo Completo */}
            <Route path="/setorenergia" element={<CPFLDashboard />} />
            <Route path="/setorenergia/analytics" element={<CPFLAnalytics />} />
            <Route path="/setorenergia/sobrestados" element={<Sobrestados />} />
            <Route path="/setorenergia/mapa-risco" element={<RiskMap />} />
            <Route path="/setorenergia/geolocalizacao" element={<Geolocation />} />
            <Route path="/setorenergia/audiencias" element={<Hearings />} />

            {/* Templates - Módulo Completo */}
            <Route path="/templates" element={<TemplatesList />} />
            <Route path="/templates/novo" element={<NewTemplate />} />
            <Route path="/templates/:id/editar" element={<EditTemplate />} />
            <Route path="/templates/categorias" element={<TemplateCategories />} />

            {/* Settings */}
            <Route path="/settings" element={<Settings />} />

            {/* Billing */}
            <Route path="/billing" element={<BillingOverview />} />

            {/* Admin - Módulo Completo */}
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/monitoring" element={<SystemMonitoring />} />
            <Route path="/admin/agents" element={<AgentsList />} />
            <Route path="/admin/usuarios" element={<UserManagement />} />
            <Route path="/admin/permissoes" element={<PermissionsManagement />} />
            <Route path="/admin/database" element={<DatabaseManagement />} />
            <Route path="/admin/database/status" element={<DatabaseStatus />} />
            <Route path="/admin/apis" element={<APIConfiguration />} />
            <Route path="/admin/modulos" element={<AdminModulesOverview />} />

            {/* 404 */}
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
