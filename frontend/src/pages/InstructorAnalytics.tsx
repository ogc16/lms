import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ChevronLeft, BarChart3, Users, TrendingUp } from 'lucide-react'
import api from '../api/client'
import Footer from '../components/Footer'

interface PathAnalytics {
  path_id: number
  path_title: string
  enrolled_count: number
  completed_count: number
  published: boolean
}

export default function InstructorAnalytics() {
  const [paths, setPaths] = useState<PathAnalytics[]>([])

  useEffect(() => {
    api.get('/instructor/paths/analytics/').then(({ data }) => setPaths(data)).catch(() => {})
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 h-14 flex items-center">
          <Link to="/instructor" className="text-sm text-gray-500 hover:text-primary-600 flex items-center gap-1">
            <ChevronLeft className="w-4 h-4" /> Back
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        <h1 className="text-lg font-semibold flex items-center gap-2"><BarChart3 className="w-5 h-5" /> Analytics</h1>

        <div className="grid md:grid-cols-3 gap-4">
          {paths.map((p) => (
            <div key={p.path_id} className="bg-white rounded-xl border p-5">
              <h3 className="font-semibold text-sm mb-3">{p.path_title}</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500 flex items-center gap-1"><Users className="w-3.5 h-3.5" /> Enrolled</span>
                  <span className="font-medium">{p.enrolled_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 flex items-center gap-1"><TrendingUp className="w-3.5 h-3.5" /> Completed</span>
                  <span className="font-medium">{p.completed_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Rate</span>
                  <span className="font-medium">
                    {p.enrolled_count ? Math.round((p.completed_count / p.enrolled_count) * 100) : 0}%
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>
      <Footer />
    </div>
  )
}
