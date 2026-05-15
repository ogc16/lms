import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { BookOpen, Clock, Users, CheckCircle, ChevronRight } from 'lucide-react'
import api from '../api/client'
import { useAuthStore } from '../stores/authStore'
import type { PathListResponse } from '../types'

export default function BrowsePathsPage() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [paths, setPaths] = useState<PathListResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [enrolling, setEnrolling] = useState<number | null>(null)

  useEffect(() => {
    api.get<{ results: typeof paths }>('/paths/').then(({ data }) => setPaths(data.results ?? [])).catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const handleEnroll = async (pathId: number) => {
    setEnrolling(pathId)
    try {
      await api.post(`/paths/${pathId}/enroll/`)
      setPaths((prev) =>
        prev.map((p) => (p.id === pathId ? { ...p, is_enrolled: true } : p))
      )
    } catch {
      // ignore
    }
    setEnrolling(null)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <h1 className="text-xl font-bold text-primary-600">LMS</h1>
          <div className="flex items-center gap-4">
            <Link to="/" className="text-sm text-gray-600 hover:text-primary-600">My Learning</Link>
            {(user?.role === 'INSTRUCTOR' || user?.role === 'ADMIN') && (
              <Link to="/instructor" className="text-sm text-gray-600 hover:text-primary-600">Instructor</Link>
            )}
            {user?.role === 'ADMIN' && (
              <Link to="/admin" className="text-sm text-gray-600 hover:text-primary-600">Admin</Link>
            )}
            <span className="text-sm text-gray-500">{user?.full_name}</span>
            <button onClick={logout} className="text-sm text-red-500 hover:text-red-700">Logout</button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-12">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold text-gray-900">Choose Your Learning Path</h2>
          <p className="text-gray-500 mt-2 max-w-xl mx-auto">
            Pick a path that matches your goals and start learning at your own pace.
          </p>
        </div>

        {loading ? (
          <p className="text-center text-gray-400 py-20">Loading paths...</p>
        ) : paths.length === 0 ? (
          <p className="text-center text-gray-400 py-20">No paths available yet.</p>
        ) : (
          <div className="grid md:grid-cols-2 gap-6">
            {paths.map((p) => (
              <div
                key={p.id}
                className="bg-white rounded-xl border hover:shadow-lg transition-shadow"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-semibold">{p.title}</h3>
                    {p.is_enrolled && (
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full flex items-center gap-1 shrink-0">
                        <CheckCircle className="w-3 h-3" /> Enrolled
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 line-clamp-2 mb-4">
                    {p.description || 'No description'}
                  </p>
                  <div className="flex items-center gap-4 text-xs text-gray-400 mb-4">
                    <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" />{p.estimated_hours}h</span>
                    <span className="flex items-center gap-1"><BookOpen className="w-3.5 h-3.5" />{p.lesson_count} lessons</span>
                    <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5" />{p.enrolled_count}</span>
                    <span className="bg-gray-100 px-2 py-0.5 rounded">{p.difficulty}</span>
                  </div>

                  {p.is_enrolled ? (
                    <button
                      onClick={() => navigate(`/paths/${p.id}`)}
                      className="w-full bg-primary-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-primary-700 flex items-center justify-center gap-1"
                    >
                      Continue Learning <ChevronRight className="w-4 h-4" />
                    </button>
                  ) : (
                    <button
                      onClick={() => handleEnroll(p.id)}
                      disabled={enrolling === p.id}
                      className="w-full bg-white text-primary-600 border border-primary-600 rounded-lg py-2.5 text-sm font-medium hover:bg-primary-50 disabled:opacity-50"
                    >
                      {enrolling === p.id ? 'Enrolling...' : 'Enroll Now'}
                    </button>
                  )}
                </div>

                {p.is_enrolled && p.progress_percent > 0 && (
                  <div className="border-t">
                    <div className="px-6 py-3 flex items-center justify-between text-xs text-gray-500">
                      <span>Progress</span>
                      <span className="font-medium">{p.progress_percent}%</span>
                    </div>
                    <div className="px-6 pb-4">
                      <div className="bg-gray-100 rounded-full h-1.5">
                        <div
                          className="bg-primary-600 h-1.5 rounded-full transition-all"
                          style={{ width: `${p.progress_percent}%` }}
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
