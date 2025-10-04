import axios from 'axios'
import { useAuthStore } from '@/store/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API endpoints
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/auth/login', credentials, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  
  register: (userData: {
    email: string
    username: string
    full_name: string
    password: string
  }) => api.post('/auth/register', userData),
}

export const dubbingAPI = {
  createJob: (formData: FormData) =>
    api.post('/dubbing/process', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  getJob: (jobId: string) => api.get(`/dubbing/jobs/${jobId}`),
  
  getProgress: (jobId: string) => api.get(`/dubbing/jobs/${jobId}/progress`),
  
  cancelJob: (jobId: string) => api.post(`/dubbing/jobs/${jobId}/cancel`),
  
  retryJob: (jobId: string) => api.post(`/dubbing/jobs/${jobId}/retry`),
  
  listJobs: (params?: { skip?: number; limit?: number; status?: string }) =>
    api.get('/dubbing/jobs', { params }),
  
  getPreview: (jobId: string, language: string, segmentId?: string) =>
    api.get(`/dubbing/preview/${jobId}`, {
      params: { language, segment_id: segmentId },
    }),
  
  runQualityCheck: (jobId: string, checkRequest: any) =>
    api.post(`/dubbing/quality-check/${jobId}`, checkRequest),
  
  getSupportedLanguages: () => api.get('/dubbing/supported-languages'),
  
  getModelInfo: () => api.get('/dubbing/models/info'),
}

export const projectsAPI = {
  list: (params?: { skip?: number; limit?: number }) =>
    api.get('/projects', { params }),
  
  get: (projectId: string) => api.get(`/projects/${projectId}`),
  
  create: (projectData: any) => api.post('/projects', projectData),
  
  update: (projectId: string, projectData: any) =>
    api.put(`/projects/${projectId}`, projectData),
  
  delete: (projectId: string) => api.delete(`/projects/${projectId}`),
}

export const healthAPI = {
  check: () => api.get('/health'),
  detailed: () => api.get('/health/detailed'),
}