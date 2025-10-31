/**
 * API service for connecting Vue frontend to Django backend.
 * 
 * This service provides:
 * - HTTP client configuration with interceptors
 * - Authentication token management
 * - Centralized API endpoint definitions
 * - Error handling and response transformation
 */

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios'
import { useUserStore } from '@/stores/user'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for token refresh and error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error: AxiosError) => {
    const original = error.config

    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/accounts/auth/refresh/`, {
            refresh: refreshToken
          })

          const { access } = response.data
          localStorage.setItem('access_token', access)

          // Retry original request with new token
          original.headers.Authorization = `Bearer ${access}`
          return apiClient(original)
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        const userStore = useUserStore()
        userStore.logout()
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// API Service Classes
export class AuthAPI {
  static async login(email: string, password: string) {
    const response = await apiClient.post('/accounts/auth/login/', {
      email,
      password
    })
    
    // Store tokens
    const { access, refresh, user } = response.data
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    
    return { success: true, user }
  }

  static async logout() {
    const refreshToken = localStorage.getItem('refresh_token')
    
    try {
      await apiClient.post('/accounts/auth/logout/', {
        refresh_token: refreshToken
      })
    } catch (error) {
      console.warn('Logout request failed, but continuing with local logout')
    }
    
    // Clear tokens regardless of API response
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    
    return { success: true }
  }

  static async register(userData: {
    email: string
    username: string
    password: string
    password_confirm: string
    full_name?: string
    organization?: string
    department?: string
    phone_number?: string
  }) {
    const response = await apiClient.post('/accounts/auth/register/', userData)
    return response.data
  }

  static async getProfile() {
    const response = await apiClient.get('/accounts/profile/')
    return response.data
  }

  static async updateProfile(userData: {
    full_name?: string
    organization?: string
    department?: string
    phone_number?: string
  }) {
    const response = await apiClient.patch('/accounts/profile/', userData)
    return response.data
  }

  static async changePassword(passwordData: {
    old_password: string
    new_password: string
    new_password_confirm: string
  }) {
    const response = await apiClient.post('/accounts/password/change/', passwordData)
    return response.data
  }
}

export class SystemAPI {
  static async getStatus() {
    const response = await apiClient.get('/accounts/system/status/')
    return response.data
  }

  static async getHealth() {
    // Mock implementation - will be replaced with actual health check
    return {
      database: { status: 'Connected', message: 'Database connection successful' },
      vectorSearch: { status: 'Available', message: 'Vector search index accessible' },
      aiModel: { status: 'Ready', message: 'AI model endpoint responding' },
      configuration: { status: 'Valid', message: 'All configuration parameters set' }
    }
  }
}

export class UserPreferencesAPI {
  static async getPreferences() {
    const response = await apiClient.get('/accounts/preferences/')
    return response.data
  }

  static async updatePreferences(preferences: any) {
    const response = await apiClient.patch('/accounts/preferences/', preferences)
    return response.data
  }
}

// Admin APIs
export class AdminAPI {
  static async getUsers(params?: {
    page?: number
    search?: string
    role?: string
    is_active?: boolean
  }) {
    const response = await apiClient.get('/accounts/admin/users/', { params })
    return response.data
  }

  static async getUser(userId: number) {
    const response = await apiClient.get(`/accounts/admin/users/${userId}/`)
    return response.data
  }

  static async updateUser(userId: number, userData: any) {
    const response = await apiClient.patch(`/accounts/admin/users/${userId}/`, userData)
    return response.data
  }

  static async activateUser(userId: number) {
    const response = await apiClient.post(`/accounts/admin/users/${userId}/activate/`)
    return response.data
  }

  static async deactivateUser(userId: number) {
    const response = await apiClient.post(`/accounts/admin/users/${userId}/deactivate/`)
    return response.data
  }

  static async getUserSessions(userId: number) {
    const response = await apiClient.get(`/accounts/admin/users/${userId}/sessions/`)
    return response.data
  }
}

// Mapping APIs (placeholder for future implementation)
export class MappingAPI {
  static async getTables() {
    // TODO: Implement when mapping endpoints are ready
    throw new Error('Mapping API endpoints not yet implemented')
  }

  static async getColumns(tableName: string) {
    // TODO: Implement when mapping endpoints are ready
    throw new Error('Mapping API endpoints not yet implemented')
  }

  static async getMappings() {
    // TODO: Implement when mapping endpoints are ready
    throw new Error('Mapping API endpoints not yet implemented')
  }

  static async createMapping(mappingData: any) {
    // TODO: Implement when mapping endpoints are ready
    throw new Error('Mapping API endpoints not yet implemented')
  }
}

// Configuration APIs (placeholder for future implementation)
export class ConfigAPI {
  static async getConfiguration() {
    // TODO: Implement when config endpoints are ready
    throw new Error('Configuration API endpoints not yet implemented')
  }

  static async updateConfiguration(configData: any) {
    // TODO: Implement when config endpoints are ready
    throw new Error('Configuration API endpoints not yet implemented')
  }
}

// Error handling utility
export const handleApiError = (error: any) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response
    
    switch (status) {
      case 400:
        return { error: data.detail || 'Invalid request data' }
      case 401:
        return { error: 'Authentication required' }
      case 403:
        return { error: 'Permission denied' }
      case 404:
        return { error: 'Resource not found' }
      case 500:
        return { error: 'Server error occurred' }
      default:
        return { error: data.detail || 'An error occurred' }
    }
  } else if (error.request) {
    // Network error
    return { error: 'Network error - please check your connection' }
  } else {
    // Other error
    return { error: error.message || 'An unexpected error occurred' }
  }
}

export default apiClient
