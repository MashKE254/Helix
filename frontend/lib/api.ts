/**
 * API client for Helix backend
 */

import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export interface User {
  id: number
  email: string
  full_name: string
  role: 'student' | 'parent' | 'teacher' | 'admin'
  subscription_tier: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  full_name: string
  role: 'student' | 'parent' | 'teacher'
}

export const auth = {
  login: async (credentials: LoginCredentials) => {
    const response = await api.post('/auth/login', credentials)
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
    }
    return response.data
  },

  register: async (data: RegisterData) => {
    const response = await api.post('/auth/register', data)
    return response.data
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me')
    return response.data
  },

  logout: () => {
    localStorage.removeItem('access_token')
  },
}

export const students = {
  completeIntake: async (intake: any) => {
    const response = await api.post('/students/intake', intake)
    return response.data
  },

  getState: async () => {
    const response = await api.get('/students/state')
    return response.data
  },

  getWeakConcepts: async (threshold: number = 0.6) => {
    const response = await api.get(`/students/weak-concepts?threshold=${threshold}`)
    return response.data
  },

  getLearningPath: async (subject: string) => {
    const response = await api.get(`/students/learning-path?subject=${subject}`)
    return response.data
  },
}

export const tutoring = {
  ask: async (query: string, subject: string, topic?: string, sessionId?: number) => {
    const response = await api.post('/tutoring/ask', {
      query,
      subject,
      topic,
      session_id: sessionId,
    })
    return response.data
  },

  createSession: async (subject: string, topic?: string) => {
    const response = await api.post('/tutoring/sessions', null, {
      params: { subject, topic },
    })
    return response.data
  },

  getSession: async (sessionId: number) => {
    const response = await api.get(`/tutoring/sessions/${sessionId}`)
    return response.data
  },
}

export const practice = {
  generate: async (subject: string, topic: string, difficulty?: number, problemType?: string) => {
    const response = await api.post('/practice/generate', {
      subject,
      topic,
      difficulty: difficulty || 0.5,
      problem_type: problemType || 'free_response',
    })
    return response.data
  },

  submit: async (problemId: number, answer: string) => {
    const response = await api.post('/practice/submit', {
      problem_id: problemId,
      answer,
    })
    return response.data
  },
}

export const parents = {
  getDashboard: async () => {
    const response = await api.get('/parents/dashboard')
    return response.data
  },

  linkChild: async (childEmail: string) => {
    const response = await api.post('/parents/link-child', null, {
      params: { child_email: childEmail },
    })
    return response.data
  },
}

export const teachers = {
  getBriefing: async (classId: string) => {
    const response = await api.get('/teachers/briefing', {
      params: { class_id: classId },
    })
    return response.data
  },

  getStudentState: async (studentId: number) => {
    const response = await api.get(`/teachers/students/${studentId}/state`)
    return response.data
  },
}

export default api
