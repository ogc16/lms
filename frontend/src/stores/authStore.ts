import { create } from 'zustand'
import api from '../api/client'
import type { User, AuthResponse } from '../types'

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string) => Promise<void>
  logout: () => void
  loadFromStorage: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: false,

  login: async (email, password) => {
    set({ isLoading: true })
    const { data } = await api.post<AuthResponse>('/auth/login/', { email, password })
    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify(data.user))
    set({ user: data.user, token: data.token, isLoading: false })
  },

  register: async (email, password, fullName) => {
    set({ isLoading: true })
    const [firstName, ...lastParts] = fullName.split(' ')
    const { data } = await api.post<AuthResponse>('/auth/register/', {
      email, password, first_name: firstName, last_name: lastParts.join(' '),
    })
    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify(data.user))
    set({ user: data.user, token: data.token, isLoading: false })
  },

  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    set({ user: null, token: null })
  },

  loadFromStorage: () => {
    const token = localStorage.getItem('token')
    const raw = localStorage.getItem('user')
    if (token && raw) {
      set({ user: JSON.parse(raw), token })
    }
  },
}))
