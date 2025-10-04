import { Routes, Route } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import Layout from '@/components/Layout'
import HomePage from '@/pages/HomePage'
import DashboardPage from '@/pages/DashboardPage'
import DubbingPage from '@/pages/DubbingPage'
import ProjectsPage from '@/pages/ProjectsPage'
import ProjectDetailPage from '@/pages/ProjectDetailPage'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'
import SettingsPage from '@/pages/SettingsPage'
import ProtectedRoute from '@/components/ProtectedRoute'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* Protected routes */}
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/dubbing" element={<DubbingPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/projects/:id" element={<ProjectDetailPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Route>
      </Routes>
    </div>
  )
}

export default App