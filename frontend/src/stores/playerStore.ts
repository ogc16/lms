import { create } from 'zustand'
import api from '../api/client'
import type {
  LessonContentResponse,
  CompleteLessonResponse,
  QuestionResponse,
} from '../types'

interface PlayerState {
  currentLesson: LessonContentResponse | null
  questions: QuestionResponse[]
  progressPercent: number
  isLoading: boolean
  fetchLesson: (lessonId: number) => Promise<void>
  fetchQuestions: (lessonId: number) => Promise<void>
  completeLesson: (lessonId: number) => Promise<CompleteLessonResponse>
}

export const usePlayerStore = create<PlayerState>((set) => ({
  currentLesson: null,
  questions: [],
  progressPercent: 0,
  isLoading: false,

  fetchLesson: async (lessonId) => {
    set({ isLoading: true })
    const { data } = await api.get<LessonContentResponse>(`/lessons/${lessonId}/`)
    set({ currentLesson: data, isLoading: false })
  },

  fetchQuestions: async (lessonId) => {
    const { data } = await api.get<{ results: QuestionResponse[] }>(`/lessons/${lessonId}/questions/`)
    set({ questions: data.results ?? data })
  },

  completeLesson: async (lessonId) => {
    const { data } = await api.post<CompleteLessonResponse>(`/lessons/${lessonId}/complete/`)
    set({ progressPercent: data.progress_percent })
    return data
  },
}))
