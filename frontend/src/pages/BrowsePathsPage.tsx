import { useEffect, useState, useMemo } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { BookOpen, Clock, Users, CheckCircle, ChevronRight, GraduationCap, Layers, Search } from 'lucide-react'
import api from '../api/client'
import { useAuthStore } from '../stores/authStore'
import type { PathListResponse, ProgramResponse, SemesterResponse } from '../types'

export default function BrowsePathsPage() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [paths, setPaths] = useState<PathListResponse[]>([])
  const [programs, setPrograms] = useState<ProgramResponse[]>([])
  const [semesters, setSemesters] = useState<SemesterResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [enrolling, setEnrolling] = useState<number | null>(null)
  const [view, setView] = useState<'program' | 'all'>('program')
  const [search, setSearch] = useState('')
  const [selectedProgram, setSelectedProgram] = useState<number | null>(null)

  const filteredPaths = useMemo(() => {
    if (!search.trim()) return paths
    const q = search.toLowerCase()
    return paths.filter(p =>
      p.title.toLowerCase().includes(q) ||
      (p.description && p.description.toLowerCase().includes(q))
    )
  }, [paths, search])

  useEffect(() => {
    let cancelled = false
    Promise.all([
      api.get<ProgramResponse[]>('/programs/').then(r => {
        if (cancelled) return
        setPrograms(r.data)
        if (r.data.length > 0) setSelectedProgram(r.data[0].id)
      }).catch(() => {}),
      api.get<{ results: PathListResponse[] }>('/paths/').then(r => {
        if (!cancelled) setPaths(r.data.results ?? [])
      }).catch(() => {}),
      api.get<SemesterResponse[]>('/semesters/').then(r => {
        if (!cancelled) setSemesters(r.data)
      }).catch(() => {}),
    ]).finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  const handleEnroll = async (pathId: number) => {
    setEnrolling(pathId)
    try {
      await api.post(`/paths/${pathId}/enroll/`)
      setPaths(prev => prev.map(p => p.id === pathId ? { ...p, is_enrolled: true } : p))
    } catch { /* ignore */ }
    setEnrolling(null)
  }

  const pathCard = (p: PathListResponse) => (
    <div key={p.id} className="bg-white rounded-xl border hover:shadow-lg transition-shadow">
      <div className="p-6">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-lg font-semibold">{p.title}</h3>
          {p.is_enrolled && (
            <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full flex items-center gap-1 shrink-0">
              <CheckCircle className="w-3 h-3" /> Enrolled
            </span>
          )}
        </div>
        <p className="text-sm text-gray-500 line-clamp-2 mb-4">{p.description || 'No description'}</p>
        <div className="flex items-center gap-4 text-xs text-gray-400 mb-4">
          <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" />{p.estimated_hours}h</span>
          <span className="flex items-center gap-1"><BookOpen className="w-3.5 h-3.5" />{p.lesson_count} lessons</span>
          <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5" />{p.enrolled_count}</span>
          <span className="bg-gray-100 px-2 py-0.5 rounded">{p.difficulty}</span>
        </div>
        {p.is_enrolled ? (
          <button onClick={() => navigate(`/paths/${p.id}`)}
            className="w-full bg-primary-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-primary-700 flex items-center justify-center gap-1">
            Continue Learning <ChevronRight className="w-4 h-4" />
          </button>
        ) : (
          <button onClick={() => handleEnroll(p.id)} disabled={enrolling === p.id}
            className="w-full bg-white text-primary-600 border border-primary-600 rounded-lg py-2.5 text-sm font-medium hover:bg-primary-50 disabled:opacity-50">
            {enrolling === p.id ? 'Enrolling...' : 'Enroll Now'}
          </button>
        )}
      </div>
      {p.is_enrolled && p.progress_percent > 0 && (
        <div className="border-t">
          <div className="px-6 py-3 flex items-center justify-between text-xs text-gray-500">
            <span>Progress</span> <span className="font-medium">{p.progress_percent}%</span>
          </div>
          <div className="px-6 pb-4">
            <div className="bg-gray-100 rounded-full h-1.5">
              <div className="bg-primary-600 h-1.5 rounded-full transition-all" style={{ width: `${p.progress_percent}%` }} />
            </div>
          </div>
        </div>
      )}
    </div>
  )

  const semesterView = () => {
    const prog = programs.find(p => p.id === selectedProgram)
    if (!prog) return (
      <p className="text-center text-gray-400 py-20">
        {programs.length === 0 ? 'No programs available.' : 'Select a program to view.'}
      </p>
    )
    const grouped: { sem: SemesterResponse; courses: PathListResponse[] }[] = semesters
      .filter(s => s.program === selectedProgram)
      .sort((a, b) => a.year_number * 2 + a.semester_number - (b.year_number * 2 + b.semester_number))
      .map(sem => ({
        sem,
        courses: filteredPaths.filter(p => p.semester_id === sem.id),
      }))

    return (
      <div className="space-y-12">
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 text-primary-600 mb-2">
            <GraduationCap className="w-6 h-6" />
            <h2 className="text-2xl font-bold text-gray-900">{prog.title}</h2>
          </div>
          <p className="text-gray-500">{prog.description}</p>
          {programs.length > 1 && (
            <div className="mt-4 flex items-center justify-center gap-2">
              <span className="text-sm text-gray-500">Switch program:</span>
              <select
                value={selectedProgram ?? ''}
                onChange={e => setSelectedProgram(Number(e.target.value))}
                className="text-sm border rounded-lg px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {programs.map(p => (
                  <option key={p.id} value={p.id}>{p.title}</option>
                ))}
              </select>
            </div>
          )}
        </div>
        {grouped.map(({ sem, courses }) => (
          <section key={sem.id}>
            <div className="flex items-center gap-3 mb-6">
              <Layers className="w-5 h-5 text-primary-500" />
              <div>
                <h3 className="text-xl font-semibold text-gray-900">
                  Year {sem.year_number}, Semester {sem.semester_number}
                </h3>
                {sem.name && <p className="text-sm text-gray-500">{sem.name}</p>}
              </div>
            </div>
            {courses.length === 0 ? (
              <p className="text-gray-400 text-sm ml-8">No courses in this semester yet.</p>
            ) : (
              <div className="grid md:grid-cols-2 gap-6 ml-8">
                {courses.map(pathCard)}
              </div>
            )}
          </section>
        ))}
        {grouped.length === 0 && (
          <p className="text-center text-gray-400 py-10">No semesters configured yet.</p>
        )}
      </div>
    )
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

      <main className="max-w-5xl mx-auto px-4 py-8">
        {/* Search bar */}
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search courses by title or description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        {/* View toggle */}
        <div className="flex items-center gap-4 mb-8 border-b pb-4">
          <button onClick={() => setView('program')}
            className={`text-sm font-medium px-3 py-1.5 rounded-lg transition ${view === 'program' ? 'bg-primary-100 text-primary-700' : 'text-gray-500 hover:text-gray-700'}`}>
            <GraduationCap className="w-4 h-4 inline mr-1" /> Program View
          </button>
          <button onClick={() => setView('all')}
            className={`text-sm font-medium px-3 py-1.5 rounded-lg transition ${view === 'all' ? 'bg-primary-100 text-primary-700' : 'text-gray-500 hover:text-gray-700'}`}>
            <Layers className="w-4 h-4 inline mr-1" /> All Courses
          </button>
        </div>

        {loading ? (
          <p className="text-center text-gray-400 py-20">Loading...</p>
        ) : view === 'program' ? (
          semesterView()
        ) : (
          <>
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900">All Courses</h2>
              <p className="text-gray-500 mt-1">{search ? `Found ${filteredPaths.length} courses matching "${search}"` : 'Browse every available course.'}</p>
            </div>
            {filteredPaths.length === 0 ? (
              <p className="text-center text-gray-400 py-20">{search ? 'No courses match your search.' : 'No paths available yet.'}</p>
            ) : (
              <div className="grid md:grid-cols-2 gap-6">{filteredPaths.map(pathCard)}</div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
