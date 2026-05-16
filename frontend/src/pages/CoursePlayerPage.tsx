import { useEffect, useState, useMemo, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ChevronLeft, Menu, X, CheckCircle, Circle, Lock, FileText, Video, HelpCircle, Award, Star, Send } from 'lucide-react'
import { usePathStore } from '../stores/pathStore'
import { usePlayerStore } from '../stores/playerStore'
import api from '../api/client'
import type { CompleteLessonResponse, ReviewResponse, CertificateResponse } from '../types'

function embedUrl(url: string): string {
  if (url.includes('youtube.com/watch') || url.includes('youtu.be')) {
    const m = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)/)
    if (m) return `https://www.youtube.com/embed/${m[1]}`
  }
  if (url.includes('youtube.com/embed')) return url
  return url
}

function renderMarkdown(text: string) {
  const inline = (s: string) =>
    s
      .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" class="max-w-full rounded-lg my-3" loading="lazy" />')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-primary-600 underline" target="_blank" rel="noopener">$1</a>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/__([^_]+)__/g, '<strong>$1</strong>')
      .replace(/\*([^*]+)\*/g, '<em>$1</em>')
      .replace(/_([^_]+)_/g, '<em>$1</em>')

  const blocks: string[] = []
  let inUl = false
  let inOl = false
  for (const line of text.split('\n')) {
    const trimmed = line.trim()
    if (!trimmed) {
      if (inUl) { blocks.push('</ul>'); inUl = false }
      if (inOl) { blocks.push('</ol>'); inOl = false }
      continue
    }
    const h3 = trimmed.match(/^### (.+)/)
    if (h3) { blocks.push(`<h3 class="text-lg font-semibold mt-4 mb-2">${inline(h3[1])}</h3>`); continue }
    const h2 = trimmed.match(/^## (.+)/)
    if (h2) { blocks.push(`<h2 class="text-xl font-semibold mt-5 mb-2">${inline(h2[1])}</h2>`); continue }
    const h1 = trimmed.match(/^# (.+)/)
    if (h1) { blocks.push(`<h1 class="text-2xl font-bold mt-5 mb-3">${inline(h1[1])}</h1>`); continue }
    const ul = trimmed.match(/^- (.+)/)
    if (ul) {
      if (inOl) { blocks.push('</ol>'); inOl = false }
      if (!inUl) { blocks.push('<ul class="space-y-1 my-2 list-disc pl-5">'); inUl = true }
      blocks.push(`<li>${inline(ul[1])}</li>`)
      continue
    }
    const ol = trimmed.match(/^\d+\. (.+)/)
    if (ol) {
      if (inUl) { blocks.push('</ul>'); inUl = false }
      if (!inOl) { blocks.push('<ol class="space-y-1 my-2 list-decimal pl-5">'); inOl = true }
      blocks.push(`<li>${inline(ol[1])}</li>`)
      continue
    }
    if (trimmed.startsWith('<img')) {
      blocks.push(trimmed)
      continue
    }
    if (inUl) { blocks.push('</ul>'); inUl = false }
    if (inOl) { blocks.push('</ol>'); inOl = false }
    blocks.push(`<p class="mb-2">${inline(trimmed)}</p>`)
  }
  if (inUl) blocks.push('</ul>')
  if (inOl) blocks.push('</ol>')
  return <div dangerouslySetInnerHTML={{ __html: blocks.join('\n') }} />
}

export default function CoursePlayerPage() {
  const { pathId, lessonId } = useParams()
  const navigate = useNavigate()
  const { activePath, fetchPathDetail } = usePathStore()
  const { currentLesson, questions, isLoading, fetchLesson, fetchQuestions } = usePlayerStore()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const { completeLesson } = usePlayerStore()
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({})
  const [submittedQuestions, setSubmittedQuestions] = useState<Record<number, boolean>>({})
  const [showCompletion, setShowCompletion] = useState(false)
  const [certificateId, setCertificateId] = useState<string | null>(null)
  const [reviewRating, setReviewRating] = useState(0)
  const [reviewComment, setReviewComment] = useState('')
  const [reviewSubmitted, setReviewSubmitted] = useState(false)
  const [submittingReview, setSubmittingReview] = useState(false)

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
  const nextInOrder = allLessons[currentIdx + 1]

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

  const handleComplete = async () => {
    if (!lessonId) return
    const data = await completeLesson(Number(lessonId))
    if (data.is_path_completed) {
      setCertificateId(data.certificate_id)
      setShowCompletion(true)
      return
    }
    const nextInOrder = allLessons[currentIdx + 1]
    if (nextInOrder) {
      navigate(`/paths/${pathId}/lessons/${nextInOrder.id}`)
    }
  }

  const handleSubmitReview = async () => {
    if (reviewRating === 0) return
    setSubmittingReview(true)
    try {
      await api.post(`/enrollments/paths/${pathId}/review/`, { rating: reviewRating, comment: reviewComment })
      setReviewSubmitted(true)
    } catch { /* ignore */ }
    setSubmittingReview(false)
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
              {/* Video embed from content_url */}
              {currentLesson.content_url && (
                <div className="aspect-video bg-gray-900 rounded-xl overflow-hidden mb-6">
                  <iframe
                    src={embedUrl(currentLesson.content_url)}
                    className="w-full h-full"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    title={currentLesson.title}
                  />
                </div>
              )}
              {/* Content body (shown for all non-quiz types) */}
              {currentLesson.content_type !== 'QUIZ' && currentLesson.content_body && (
                <div className="mb-6 bg-gray-50 rounded-xl p-6 border">
                  {renderMarkdown(currentLesson.content_body)}
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
                  {nextInOrder ? 'Complete & Continue' : 'Complete'}
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

      {/* Completion Modal */}
      {showCompletion && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 p-8 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Award className="w-8 h-8 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold mb-2">Congratulations!</h2>
            <p className="text-gray-500 mb-6">You completed the course successfully!</p>

            {certificateId && (
              <a
                href={`/api/enrollments/paths/${pathId}/certificate/`}
                target="_blank"
                className="inline-flex items-center gap-2 bg-primary-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-primary-700 mb-6"
                onClick={(e) => {
                  e.preventDefault()
                  api.get<CertificateResponse>(`/enrollments/paths/${pathId}/certificate/`).then(({ data }) => {
                    if (!data) return
                    const win = window.open('', '_blank')
                    if (!win) return
                    win.document.write(`
                      <!DOCTYPE html><html><head><title>Certificate</title>
                      <style>
                        body { font-family: Georgia, serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: #f3f4f6; }
                        .cert { width: 700px; padding: 50px; background: white; border: 8px double #1e40af; text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.1); }
                        h1 { font-size: 32px; color: #1e40af; margin-bottom: 5px; }
                        .subtitle { font-size: 14px; color: #6b7280; letter-spacing: 3px; text-transform: uppercase; }
                        .name { font-size: 28px; font-weight: bold; margin: 20px 0; }
                        .course { font-size: 20px; color: #374151; margin: 10px 0; }
                        .details { font-size: 14px; color: #6b7280; margin: 20px 0; }
                        .id { font-size: 12px; color: #9ca3af; margin-top: 30px; }
                        hr { border: none; border-top: 1px solid #e5e7eb; margin: 20px 0; }
                      </style></head><body>
                      <div class="cert">
                        <h1>Certificate of Completion</h1>
                        <p class="subtitle">This certifies that</p>
                        <p class="name">${document.title.split(' ')[0] || 'Student'}</p>
                        <p class="subtitle">has successfully completed the course</p>
                        <p class="course">${data.path_title}</p>
                        <hr>
                        <p class="details">Certificate ID: ${data.certificate_id}</p>
                        <p class="details">Issued: ${new Date(data.issued_at).toLocaleDateString()}</p>
                      </div></body></html>
                    `)
                    win.document.close()
                  })
                }}
              >
                <Award className="w-5 h-5" /> Download Certificate
              </a>
            )}

            <div className="border-t pt-6">
              <h3 className="font-semibold mb-3">Rate this course</h3>
              {reviewSubmitted ? (
                <p className="text-green-600 text-sm flex items-center justify-center gap-1">
                  <CheckCircle className="w-4 h-4" /> Thank you for your feedback!
                </p>
              ) : (
                <>
                  <div className="flex justify-center gap-1 mb-4">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button key={star} onClick={() => setReviewRating(star)}>
                        <Star className={`w-8 h-8 ${star <= reviewRating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`} />
                      </button>
                    ))}
                  </div>
                  <textarea
                    placeholder="Share your thoughts about this course..."
                    value={reviewComment}
                    onChange={(e) => setReviewComment(e.target.value)}
                    className="w-full border rounded-lg p-3 text-sm mb-3 resize-none"
                    rows={3}
                  />
                  <button
                    onClick={handleSubmitReview}
                    disabled={reviewRating === 0 || submittingReview}
                    className="bg-primary-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50 flex items-center gap-2 mx-auto"
                  >
                    <Send className="w-4 h-4" /> {submittingReview ? 'Submitting...' : 'Submit Review'}
                  </button>
                </>
              )}
            </div>

            <button
              onClick={() => navigate(`/paths/${pathId}`)}
              className="mt-6 text-sm text-gray-500 hover:text-primary-600"
            >
              Back to Course Overview
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
