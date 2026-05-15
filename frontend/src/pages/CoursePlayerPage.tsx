import { useEffect, useState, useMemo, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Menu, X, CheckCircle, Circle, Lock, FileText, Video, HelpCircle } from 'lucide-react'
import { usePathStore } from '../stores/pathStore'
import { usePlayerStore } from '../stores/playerStore'

export default function CoursePlayerPage() {
  const { pathId, lessonId } = useParams()
  const navigate = useNavigate()
  const { activePath, fetchPathDetail } = usePathStore()
  const { currentLesson, questions, isLoading, fetchLesson, fetchQuestions } = usePlayerStore()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const { completeLesson } = usePlayerStore()
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({})
  const [submittedQuestions, setSubmittedQuestions] = useState<Record<number, boolean>>({})

  useEffect(() => {
    if (pathId) fetchPathDetail(Number(pathId))
    if (lessonId) {
      fetchLesson(Number(lessonId))
      fetchQuestions(Number(lessonId))
    }
    setSelectedAnswers({})
    setSubmittedQuestions({})
  }, [pathId, lessonId])

  const allLessons = useMemo(
    () => activePath?.modules.flatMap((m) => m.lessons) ?? [],
    [activePath],
  )

  const firstIncompleteIdx = useMemo(
    () => allLessons.findIndex((l) => !l.is_completed),
    [allLessons],
  )

  const isLocked = (idx: number) =>
    firstIncompleteIdx >= 0 && idx > firstIncompleteIdx

  const currentIdx = allLessons.findIndex((l) => l.id === Number(lessonId))
  const currentLocked = isLocked(currentIdx)
  const firstAvailable = firstIncompleteIdx >= 0 ? firstIncompleteIdx : 0

  // Redirect if current lesson is locked
  useEffect(() => {
    if (!isLoading && currentLocked && allLessons.length > 0) {
      const target = allLessons[firstAvailable]
      if (target) {
        navigate(`/paths/${pathId}/lessons/${target.id}`, { replace: true })
      }
    }
  }, [currentLocked, isLoading])

  // find previous available (completed or first incomplete)
  const prevLesson = (() => {
    if (currentIdx <= 0) return null
    for (let i = currentIdx - 1; i >= 0; i--) {
      if (!isLocked(i)) return allLessons[i]
    }
    return null
  })()

  // find next available (the first one after current that is not locked)
  const nextLesson = (() => {
    for (let i = currentIdx + 1; i < allLessons.length; i++) {
      if (!isLocked(i)) return allLessons[i]
    }
    return null
  })()

  const handleComplete = async () => {
    if (!lessonId) return
    await completeLesson(Number(lessonId))
    if (nextLesson) {
      navigate(`/paths/${pathId}/lessons/${nextLesson.id}`)
    }
  }

  const iconMap: Record<string, React.ReactNode> = {
    VIDEO: <Video className="w-4 h-4" />,
    MARKDOWN: <FileText className="w-4 h-4" />,
    QUIZ: <HelpCircle className="w-4 h-4" />,
  }

  return (
    <div className="h-screen flex bg-white">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-80' : 'w-0'} border-r bg-gray-50 flex-shrink-0 overflow-hidden transition-all duration-300`}>
        <div className="w-80 h-full flex flex-col">
          <div className="p-4 border-b bg-white flex items-center justify-between">
            <h2 className="font-semibold text-sm truncate">Course Content</h2>
            <button onClick={() => setSidebarOpen(false)} className="text-gray-400 hover:text-gray-600">
              <X className="w-4 h-4" />
            </button>
          </div>

          {activePath && (
            <div className="p-4 border-b bg-white">
              <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>Progress</span><span>{activePath.progress_percent}%</span>
              </div>
              <div className="bg-gray-200 rounded-full h-1.5">
                <div className="bg-primary-600 h-1.5 rounded-full" style={{ width: `${activePath.progress_percent}%` }} />
              </div>
            </div>
          )}

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {activePath?.modules.map((mod) => {
              let globalIdx = -1
              return (
                <div key={mod.id}>
                  <p className="text-xs font-medium text-gray-500 px-2 pt-3 pb-1">{mod.title}</p>
                  {mod.lessons.map((lesson) => {
                    globalIdx++
                    const idx = globalIdx
                    const isActive = lesson.id === Number(lessonId)
                    const locked = isLocked(idx)
                    return (
                      <button
                        key={lesson.id}
                        disabled={locked}
                        onClick={() => navigate(`/paths/${pathId}/lessons/${lesson.id}`)}
                        className={`w-full flex items-center gap-2 px-2 py-2 rounded-lg text-left text-sm transition ${
                          isActive ? 'bg-primary-100 text-primary-700' : locked ? 'opacity-40 cursor-not-allowed' : 'hover:bg-gray-100'
                        }`}
                      >
                        {locked ? (
                          <Lock className="w-4 h-4 text-gray-300 shrink-0" />
                        ) : lesson.is_completed ? (
                          <CheckCircle className="w-4 h-4 text-green-500 shrink-0" />
                        ) : (
                          <Circle className={`w-4 h-4 shrink-0 ${isActive ? 'text-primary-500' : 'text-gray-300'}`} />
                        )}
                        <span className="truncate flex-1">{lesson.title}</span>
                        {iconMap[lesson.content_type]}
                      </button>
                    )
                  })}
                </div>
              )
            })}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="h-14 border-b flex items-center px-4 gap-3 bg-white shrink-0">
          {!sidebarOpen && (
            <button onClick={() => setSidebarOpen(true)} className="text-gray-500 hover:text-gray-700">
              <Menu className="w-5 h-5" />
            </button>
          )}
          <button onClick={() => navigate(`/paths/${pathId}`)} className="text-sm text-gray-500 hover:text-primary-600 flex items-center gap-1">
            <ChevronLeft className="w-4 h-4" /> Back
          </button>
          <span className="text-xs text-gray-400 ml-auto">
            {currentIdx + 1} of {allLessons.length}
          </span>
        </header>

        {/* Content area */}
        <main className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center h-full text-gray-400">Loading...</div>
          ) : currentLesson ? (
            <div className="max-w-3xl mx-auto px-6 py-8">
              {/* Content type display */}
              {currentLesson.content_type === 'VIDEO' && (
                <div className="aspect-video bg-gray-900 rounded-xl flex items-center justify-center mb-6">
                  <Video className="w-16 h-16 text-gray-500" />
                </div>
              )}
              {currentLesson.content_type === 'MARKDOWN' && currentLesson.content_body && (
                <div className="prose prose-sm max-w-none mb-6 bg-gray-50 rounded-xl p-6 border">
                  {currentLesson.content_body.split('\n').map((line, i) => (
                    <p key={i} className="mb-2">{line}</p>
                  ))}
                </div>
              )}
              {currentLesson.content_type === 'QUIZ' && (
                questions.length > 0 ? (
                  <div className="mb-6 space-y-6">
                    {questions.map((q) => {
                      const opts = [
                        { key: 'a', text: q.option_a },
                        { key: 'b', text: q.option_b },
                        { key: 'c', text: q.option_c },
                        { key: 'd', text: q.option_d },
                      ]
                      const answered = submittedQuestions[q.id] ?? false
                      const selected = selectedAnswers[q.id]
                      return (
                        <div key={q.id} className="bg-white rounded-xl border p-5">
                          <p className="font-semibold mb-3">{q.question_text}</p>
                          <div className="space-y-2">
                            {opts.map((opt) => {
                              const isCorrect = opt.key === q.correct_option
                              const isSelected = selected === opt.key
                              let bg = 'bg-gray-50'
                              let border = ''
                              let circleBg = 'bg-gray-200 text-gray-500'
                              let textColor = 'text-gray-700'
                              if (answered) {
                                if (isCorrect) {
                                  bg = 'bg-green-50'
                                  border = 'border border-green-200'
                                  circleBg = 'bg-green-500 text-white'
                                  textColor = 'text-green-800 font-medium'
                                } else if (isSelected) {
                                  bg = 'bg-red-50'
                                  border = 'border border-red-200'
                                  circleBg = 'bg-red-500 text-white'
                                  textColor = 'text-red-800 font-medium'
                                }
                              } else if (isSelected) {
                                bg = 'bg-blue-50'
                                border = 'border border-blue-200'
                                circleBg = 'bg-blue-500 text-white'
                              }
                              return (
                                <button
                                  key={opt.key}
                                  disabled={answered}
                                  onClick={() => {
                                    setSelectedAnswers(prev => ({ ...prev, [q.id]: opt.key }))
                                    setSubmittedQuestions(prev => ({ ...prev, [q.id]: true }))
                                  }}
                                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-left transition ${bg} ${border} ${answered ? '' : 'cursor-pointer hover:bg-gray-100'}`}
                                >
                                  <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${circleBg}`}>
                                    {opt.key}
                                  </span>
                                  <span className={textColor}>{opt.text}</span>
                                  {answered && isCorrect && <span className="ml-auto text-green-600 text-xs font-medium">Correct</span>}
                                  {answered && isSelected && !isCorrect && <span className="ml-auto text-red-600 text-xs font-medium">Incorrect</span>}
                                </button>
                              )
                            })}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div className="mb-6 bg-amber-50 border border-amber-200 rounded-xl p-6 text-center">
                    <p className="text-amber-800 font-medium">Complete all lessons in this module to unlock the quiz.</p>
                  </div>
                )
              )}

              <h1 className="text-2xl font-bold mb-2">{currentLesson.title}</h1>
              {currentLesson.description && (
                <p className="text-gray-500 mb-6">{currentLesson.description}</p>
              )}

              {/* Navigation */}
              <div className="flex items-center justify-between pt-6 border-t">
                {prevLesson ? (
                  <button
                    onClick={() => navigate(`/paths/${pathId}/lessons/${prevLesson.id}`)}
                    className="flex items-center gap-1 text-sm text-gray-600 hover:text-primary-600"
                  >
                    <ChevronLeft className="w-4 h-4" /> {prevLesson.title}
                  </button>
                ) : <div />}
                <button
                  onClick={handleComplete}
                  className="bg-primary-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 flex items-center gap-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  {nextLesson ? 'Complete & Continue' : 'Complete'}
                </button>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">Lesson not found</div>
          )}
        </main>

        {/* Bottom progress */}
        <div className="h-1 bg-gray-100 shrink-0">
          <div className="h-1 bg-primary-600 transition-all" style={{ width: `${activePath?.progress_percent ?? 0}%` }} />
        </div>
      </div>
    </div>
  )
}
