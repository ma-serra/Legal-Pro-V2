import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Processos from './pages/Processos'
import Analises from './pages/Analises'
import Assistentes from './pages/Assistentes'
import NotFound from './pages/NotFound'

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard'
import AgentsList from './pages/admin/AgentsList'
import SystemMonitoring from './pages/admin/SystemMonitoring'

// Public SaaS Pages
import LandingPage from './pages/public/LandingPage'
import PricingPage from './pages/public/PricingPage'
import SignupPage from './pages/public/SignupPage'

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
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/processos" element={<Processos />} />
            <Route path="/analises" element={<Analises />} />
            <Route path="/assistentes" element={<Assistentes />} />

            {/* Admin Routes */}
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/monitoring" element={<SystemMonitoring />} />
            <Route path="/admin/agents" element={<AgentsList />} />

            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
