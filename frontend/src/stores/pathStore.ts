import { create } from 'zustand'
import api from '../api/client'
import type { PathListResponse, PathDetailResponse } from '../types'

interface PathState {
  paths: PathListResponse[]
  activePath: PathDetailResponse | null
  isLoading: boolean
  fetchPaths: () => Promise<void>
  fetchPathDetail: (id: number) => Promise<void>
  enroll: (pathId: number) => Promise<void>
}

export const usePathStore = create<PathState>((set) => ({
  paths: [],
  activePath: null,
  isLoading: false,

  fetchPaths: async () => {
    set({ isLoading: true })
    const { data } = await api.get<{ results: PathListResponse[] }>('/paths/')
    set({ paths: data.results ?? [], isLoading: false })
  },

  fetchPathDetail: async (id) => {
    set({ isLoading: true })
    const { data } = await api.get<PathDetailResponse>(`/paths/${id}/`)
    set({ activePath: data, isLoading: false })
  },

  enroll: async (pathId) => {
    await api.post(`/paths/${pathId}/enroll/`)
    set((state) => ({
      activePath: state.activePath
        ? { ...state.activePath, is_enrolled: true }
        : null,
    }))
  },
}))
