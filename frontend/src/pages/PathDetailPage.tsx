import { useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { Clock, BookOpen, ChevronLeft, CheckCircle, Circle } from 'lucide-react'
import { usePathStore } from '../stores/pathStore'
import Footer from '../components/Footer'

export default function PathDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { activePath, isLoading, fetchPathDetail, enroll } = usePathStore()

  useEffect(() => { if (id) fetchPathDetail(Number(id)) }, [id])

  if (isLoading || !activePath) return <div className="p-8 text-gray-400">Loading...</div>

  const firstLessonId = activePath.modules[0]?.lessons[0]?.id
  const allLessons = activePath.modules.flatMap((m) => m.lessons)

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 h-14 flex items-center">
          <Link to="/" className="text-sm text-gray-500 hover:text-primary-600 flex items-center gap-1">
            <ChevronLeft className="w-4 h-4" /> Back to Dashboard
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        <div className="bg-white rounded-xl border p-6">
          <h1 className="text-2xl font-bold">{activePath.title}</h1>
          <p className="text-gray-500 mt-1">{activePath.description}</p>
          <div className="flex items-center gap-4 mt-3 text-sm text-gray-400">
            <span className="flex items-center gap-1"><Clock className="w-4 h-4" />{activePath.estimated_hours}h</span>
            <span className="flex items-center gap-1"><BookOpen className="w-4 h-4" />{allLessons.length} lessons</span>
            <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">{activePath.difficulty}</span>
          </div>

          {activePath.is_enrolled ? (
            <div className="mt-4">
              <div className="flex justify-between text-sm mb-1">
                <span>Progress</span><span className="font-medium">{activePath.progress_percent}%</span>
              </div>
              <div className="bg-gray-100 rounded-full h-2.5">
                <div className="bg-primary-600 h-2.5 rounded-full" style={{ width: `${activePath.progress_percent}%` }} />
              </div>
              {firstLessonId && (
                <button onClick={() => navigate(`/paths/${id}/lessons/${firstLessonId}`)}
                  className="mt-4 bg-primary-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-primary-700">
                  Continue Learning
                </button>
              )}
            </div>
          ) : (
            <button onClick={() => enroll(Number(id))}
              className="mt-4 bg-primary-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-primary-700">
              Enroll Now
            </button>
          )}
        </div>

        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Course Content</h2>
          {activePath.modules.map((mod, i) => (
            <div key={mod.id} className="bg-white rounded-xl border">
              <div className="p-4 border-b bg-gray-50 rounded-t-xl">
                <span className="text-sm text-gray-500">Module {i + 1}</span>
                <h3 className="font-semibold">{mod.title}</h3>
              </div>
              <div className="divide-y">
                {mod.lessons.map((lesson) => (
                  <div key={lesson.id} className="p-4 flex items-center gap-3 hover:bg-gray-50">
                    {lesson.is_completed ? (
                      <CheckCircle className="w-5 h-5 text-green-500 shrink-0" />
                    ) : (
                      <Circle className="w-5 h-5 text-gray-300 shrink-0" />
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{lesson.title}</p>
                      <p className="text-xs text-gray-400">{lesson.duration_minutes} min</p>
                    </div>
                    <Link
                      to={`/paths/${id}/lessons/${lesson.id}`}
                      className="text-sm text-primary-600 hover:underline shrink-0"
                    >
                      {lesson.is_completed ? 'Review' : 'Start'}
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </main>
      <Footer />
    </div>
  )
}
