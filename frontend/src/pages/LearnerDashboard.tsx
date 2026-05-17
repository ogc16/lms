import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, Compass, BarChart3, CheckCircle } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { usePathStore } from '../stores/pathStore'
import Footer from '../components/Footer'

export default function LearnerDashboard() {
  const { user, logout } = useAuthStore()
  const { paths, isLoading, fetchPaths } = usePathStore()

  useEffect(() => { fetchPaths() }, [])

  const inProgress = paths.filter((p) => p.is_enrolled && p.progress_percent < 100)
  const completed = paths.filter((p) => p.is_enrolled && p.progress_percent >= 100)
  const hasEnrollments = inProgress.length > 0 || completed.length > 0

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <h1 className="text-xl font-bold text-primary-600">LMS</h1>
          <div className="flex items-center gap-4">
            <Link to="/browse" className="text-sm text-gray-600 hover:text-primary-600 flex items-center gap-1">
              <Compass className="w-4 h-4" /> Browse Paths
            </Link>
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

      <main className="max-w-4xl mx-auto px-4 py-8">
        {!hasEnrollments && !isLoading && (
          <div className="text-center py-20">
            <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-600 mb-2">You haven't picked a path yet</h2>
            <p className="text-gray-400 mb-6">Choose a learning path to get started on your journey.</p>
            <Link
              to="/browse"
              className="inline-flex items-center gap-2 bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700"
            >
              <Compass className="w-5 h-5" /> Browse Learning Paths
            </Link>
          </div>
        )}

        {inProgress.length > 0 && (
          <section className="mb-8">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><BarChart3 className="w-5 h-5" /> In Progress</h2>
            <div className="grid gap-4">
              {inProgress.map((p) => (
                <Link key={p.id} to={`/paths/${p.id}`} className="bg-white rounded-xl border p-5 hover:shadow-md transition">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold">{p.title}</h3>
                      <p className="text-sm text-gray-500">{p.instructor_name}</p>
                    </div>
                    <span className="text-sm font-medium text-primary-600">{p.progress_percent}%</span>
                  </div>
                  <div className="mt-3 bg-gray-100 rounded-full h-2">
                    <div className="bg-primary-600 h-2 rounded-full transition-all" style={{ width: `${p.progress_percent}%` }} />
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {completed.length > 0 && (
          <section>
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><CheckCircle className="w-5 h-5 text-green-600" /> Completed</h2>
            <div className="grid gap-4">
              {completed.map((p) => (
                <Link key={p.id} to={`/paths/${p.id}`} className="bg-white rounded-xl border p-5 hover:shadow-md transition border-green-200">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold">{p.title}</h3>
                      <p className="text-sm text-gray-500">{p.instructor_name}</p>
                    </div>
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Completed</span>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}
      </main>
      <Footer />
    </div>
  )
}
