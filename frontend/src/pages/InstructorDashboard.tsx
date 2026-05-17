import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, BookOpen, Users, BarChart3, Edit3 } from 'lucide-react'
import api from '../api/client'
import { useAuthStore } from '../stores/authStore'
import Footer from '../components/Footer'

interface PathAnalytics {
  path_id: number
  path_title: string
  enrolled_count: number
  completed_count: number
  published: boolean
}

export default function InstructorDashboard() {
  const { user, logout } = useAuthStore()
  const [paths, setPaths] = useState<PathAnalytics[]>([])

  useEffect(() => {
    api.get('/instructor/paths/analytics/').then(({ data }) => setPaths(data)).catch(() => {})
  }, [])

  const totalEnrollments = paths.reduce((s, p) => s + p.enrolled_count, 0)
  const avgCompletion = paths.length
    ? Math.round(paths.reduce((s, p) => s + (p.enrolled_count ? (p.completed_count / p.enrolled_count) * 100 : 0), 0) / paths.length)
    : 0

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <h1 className="text-xl font-bold text-primary-600">LMS</h1>
            <nav className="flex gap-4 text-sm">
              <Link to="/instructor" className="text-primary-600 font-medium">Dashboard</Link>
              <Link to="/instructor/analytics" className="text-gray-500 hover:text-primary-600">Analytics</Link>
              <Link to="/" className="text-gray-500 hover:text-primary-600">Learner View</Link>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">{user?.full_name}</span>
            <button onClick={logout} className="text-sm text-red-500 hover:text-red-700">Logout</button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Instructor Dashboard</h2>
          <Link to="/instructor/paths/new" className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 flex items-center gap-2">
            <Plus className="w-4 h-4" /> New Path
          </Link>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white rounded-xl border p-5">
            <p className="text-2xl font-bold">{paths.length}</p>
            <p className="text-sm text-gray-500 flex items-center gap-1 mt-1"><BookOpen className="w-4 h-4" /> Total Paths</p>
          </div>
          <div className="bg-white rounded-xl border p-5">
            <p className="text-2xl font-bold">{totalEnrollments}</p>
            <p className="text-sm text-gray-500 flex items-center gap-1 mt-1"><Users className="w-4 h-4" /> Total Enrollments</p>
          </div>
          <div className="bg-white rounded-xl border p-5">
            <p className="text-2xl font-bold">{avgCompletion}%</p>
            <p className="text-sm text-gray-500 flex items-center gap-1 mt-1"><BarChart3 className="w-4 h-4" /> Avg Completion</p>
          </div>
        </div>

        <div className="bg-white rounded-xl border">
          <div className="p-4 border-b">
            <h3 className="font-semibold">Your Paths</h3>
          </div>
          <div className="divide-y">
            {paths.map((p) => (
              <div key={p.path_id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                <div>
                  <p className="font-medium">{p.path_title}</p>
                  <p className="text-sm text-gray-500">{p.enrolled_count} enrolled · {p.completed_count} completed</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs px-2 py-0.5 rounded ${p.published ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                    {p.published ? 'Published' : 'Draft'}
                  </span>
                  <Link to={`/instructor/paths/${p.path_id}`} className="text-primary-600 hover:underline text-sm flex items-center gap-1">
                    <Edit3 className="w-3.5 h-3.5" /> Edit
                  </Link>
                </div>
              </div>
            ))}
            {paths.length === 0 && (
              <div className="p-8 text-center text-gray-400">No paths yet. Create your first one!</div>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
