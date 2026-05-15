import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import LearnerDashboard from './pages/LearnerDashboard'
import PathDetailPage from './pages/PathDetailPage'
import CoursePlayerPage from './pages/CoursePlayerPage'
import InstructorDashboard from './pages/InstructorDashboard'
import InstructorPathEditor from './pages/InstructorPathEditor'
import InstructorAnalytics from './pages/InstructorAnalytics'
import AdminDashboard from './pages/AdminDashboard'
import BrowsePathsPage from './pages/BrowsePathsPage'

function ProtectedRoute({ children, allowedRoles }: { children: React.ReactNode; allowedRoles?: string[] }) {
  const { user } = useAuthStore()
  if (!user) return <Navigate to="/login" replace />
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/browse" replace />
  return <>{children}</>
}

export default function App() {
  const { user, loadFromStorage } = useAuthStore()

  useEffect(() => { loadFromStorage() }, [])

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/browse" replace /> : <LoginPage />} />
      <Route path="/register" element={user ? <Navigate to="/browse" replace /> : <RegisterPage />} />

      <Route path="/" element={<ProtectedRoute><LearnerDashboard /></ProtectedRoute>} />
      <Route path="/browse" element={<ProtectedRoute><BrowsePathsPage /></ProtectedRoute>} />
      <Route path="/paths/:id" element={<ProtectedRoute><PathDetailPage /></ProtectedRoute>} />
      <Route path="/paths/:pathId/lessons/:lessonId" element={<ProtectedRoute><CoursePlayerPage /></ProtectedRoute>} />

      <Route path="/instructor" element={<ProtectedRoute allowedRoles={['INSTRUCTOR', 'ADMIN']}><InstructorDashboard /></ProtectedRoute>} />
      <Route path="/instructor/paths/:id?" element={<ProtectedRoute allowedRoles={['INSTRUCTOR', 'ADMIN']}><InstructorPathEditor /></ProtectedRoute>} />
      <Route path="/instructor/analytics" element={<ProtectedRoute allowedRoles={['INSTRUCTOR', 'ADMIN']}><InstructorAnalytics /></ProtectedRoute>} />

      <Route path="/admin" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminDashboard /></ProtectedRoute>} />

      <Route path="*" element={<Navigate to="/browse" replace />} />
    </Routes>
  )
}
