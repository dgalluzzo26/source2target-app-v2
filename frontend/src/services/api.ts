/**
 * API service for connecting Vue frontend to Django backend.
 * 
 * This service provides:
 * - HTTP client configuration with interceptors
 * - Authentication token management
 * - Centralized API endpoint definitions
 * - Error handling and response transformation
 */

import axios from 'axios'
import APP_CONFIG from '@/config/app'

// Frontend-only mode: Disable all API calls
const API_BASE_URL = APP_CONFIG.FRONTEND_ONLY ? '' : (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api')

const apiClient = axios.create({
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
  (response) => {
    return response
  },
  async (error) => {
    const original = error.config

    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/accounts/auth/token/refresh/`, {
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
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// Frontend-only mode check
const checkFrontendOnly = () => {
  if (APP_CONFIG.FRONTEND_ONLY) {
    console.warn('Frontend-only mode: API call blocked')
    throw new Error('API calls disabled in frontend-only mode')
  }
}

// API Service Classes
export class AuthAPI {
  static async login(email: string, password: string) {
    checkFrontendOnly()
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

  static async getCurrentUser() {
    checkFrontendOnly()
    // Get current user from Databricks context (like original app's AuthManager.get_current_user())
    const response = await apiClient.get('/accounts/current-user/')
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

// Mapping APIs
export class MappingAPI {
  static async getSourceTables(params?: {
    page?: number
    search?: string
    catalog_name?: string
    schema_name?: string
    table_type?: string
  }) {
    const response = await apiClient.get('/mapping/source-tables/', { params })
    return response.data
  }

  static async getSourceTable(tableId: number) {
    const response = await apiClient.get(`/mapping/source-tables/${tableId}/`)
    return response.data
  }

  static async getTableColumns(tableId: number) {
    const response = await apiClient.get(`/mapping/source-tables/${tableId}/columns/`)
    return response.data
  }

  static async getTableMappings(tableId: number) {
    const response = await apiClient.get(`/mapping/source-tables/${tableId}/mappings/`)
    return response.data
  }

  static async analyzeTable(tableId: number) {
    const response = await apiClient.post(`/mapping/source-tables/${tableId}/analyze/`)
    return response.data
  }

  static async discoverTables(params?: {
    catalogs?: string
    search?: string
  }) {
    const response = await apiClient.post('/mapping/source-tables/discover/', params)
    return response.data
  }

  static async testDatabricksConnection() {
    const response = await apiClient.get('/mapping/source-tables/test_connection/')
    return response.data
  }

  static async getTargetSchemas(params?: {
    page?: number
    search?: string
    schema_type?: string
  }) {
    const response = await apiClient.get('/mapping/target-schemas/', { params })
    return response.data
  }

  static async getTargetSchema(schemaId: number) {
    const response = await apiClient.get(`/mapping/target-schemas/${schemaId}/`)
    return response.data
  }

  static async getSchemaFields(schemaId: number) {
    const response = await apiClient.get(`/mapping/target-schemas/${schemaId}/fields/`)
    return response.data
  }

  static async getFieldMappings(params?: {
    page?: number
    search?: string
    mapping_type?: string
    status?: string
    suggested_by_ai?: boolean
    is_validated?: boolean
  }) {
    const response = await apiClient.get('/mapping/field-mappings/', { params })
    return response.data
  }

  static async createFieldMapping(mappingData: {
    source_column: number
    target_field: number
    mapping_type?: string
    transformation_logic?: string
    transformation_language?: string
    confidence_score?: number
    suggested_by_ai?: boolean
    ai_reasoning?: string
    ai_model_version?: string
  }) {
    const response = await apiClient.post('/mapping/field-mappings/', mappingData)
    return response.data
  }

  static async updateFieldMapping(mappingId: number, mappingData: any) {
    const response = await apiClient.patch(`/mapping/field-mappings/${mappingId}/`, mappingData)
    return response.data
  }

  static async deleteFieldMapping(mappingId: number) {
    const response = await apiClient.delete(`/mapping/field-mappings/${mappingId}/`)
    return response.data
  }

  static async validateMapping(mappingId: number, validationNotes?: string) {
    const response = await apiClient.post(`/mapping/field-mappings/${mappingId}/validate_mapping/`, {
      validation_notes: validationNotes
    })
    return response.data
  }

  static async bulkCreateMappings(mappingsData: {
    mappings: Array<{
      source_column_id: number
      target_field_id: number
      mapping_type?: string
      transformation_logic?: string
    }>
    template_id?: number
    auto_validate?: boolean
  }) {
    const response = await apiClient.post('/mapping/field-mappings/bulk_create/', mappingsData)
    return response.data
  }

  static async getAISuggestions(params?: {
    page?: number
    search?: string
    status?: string
    model_name?: string
  }) {
    const response = await apiClient.get('/mapping/ai-suggestions/', { params })
    return response.data
  }

  static async acceptAISuggestion(suggestionId: number) {
    const response = await apiClient.post(`/mapping/ai-suggestions/${suggestionId}/accept/`)
    return response.data
  }

  static async rejectAISuggestion(suggestionId: number, feedback?: string) {
    const response = await apiClient.post(`/mapping/ai-suggestions/${suggestionId}/reject/`, {
      feedback
    })
    return response.data
  }

  static async getMappingTemplates(params?: {
    page?: number
    search?: string
    target_schema?: number
  }) {
    const response = await apiClient.get('/mapping/templates/', { params })
    return response.data
  }

  static async applyTemplate(templateId: number) {
    const response = await apiClient.post(`/mapping/templates/${templateId}/apply/`)
    return response.data
  }

  static async getMappingSessions(params?: {
    page?: number
    search?: string
    status?: string
    target_schema?: number
  }) {
    const response = await apiClient.get('/mapping/sessions/', { params })
    return response.data
  }

  static async createMappingSession(sessionData: {
    session_name: string
    source_tables: number[]
    target_schema: number
    notes?: string
    tags?: string[]
  }) {
    const response = await apiClient.post('/mapping/sessions/', sessionData)
    return response.data
  }

  static async updateSessionProgress(sessionId: number) {
    const response = await apiClient.post(`/mapping/sessions/${sessionId}/update_progress/`)
    return response.data
  }

  static async getMappingStats() {
    const response = await apiClient.get('/mapping/stats/')
    return response.data
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
// Configuration APIs
export class ConfigurationAPI {
  static async getFullConfiguration() {
    const response = await apiClient.get('/config/settings/full/')
    return response.data
  }

  static async getConfigurationBySection(section: string) {
    const response = await apiClient.get('/config/settings/by_section/', {
      params: { section }
    })
    return response.data
  }

  static async updateSetting(section: string, key: string, value: any, reason?: string) {
    const response = await apiClient.post('/config/settings/update_setting/', {
      section,
      key,
      value,
      reason
    })
    return response.data
  }

  static async bulkUpdateConfiguration(configuration: any, reason?: string) {
    const response = await apiClient.post('/config/settings/bulk_update/', {
      configuration,
      reason
    })
    return response.data
  }

  static async testConfiguration(testType: string, configuration?: any) {
    const response = await apiClient.post('/config/settings/test/', {
      test_type: testType,
      configuration
    })
    return response.data
  }

  static async exportConfiguration(includeSections?: string[], format = 'json') {
    const response = await apiClient.post('/config/settings/export/', {
      include_sections: includeSections,
      format
    }, {
      responseType: 'blob'
    })
    return response.data
  }

  static async importConfiguration(configurationData: any, mergeStrategy = 'merge', reason?: string) {
    const response = await apiClient.post('/config/settings/import_config/', {
      configuration_data: configurationData,
      merge_strategy: mergeStrategy,
      reason
    })
    return response.data
  }

  static async resetToDefaults() {
    const response = await apiClient.post('/config/settings/reset_defaults/')
    return response.data
  }

  static async getConfigurationTemplates() {
    const response = await apiClient.get('/config/templates/')
    return response.data
  }

  static async createConfigurationTemplate(name: string, description: string, configurationData: any) {
    const response = await apiClient.post('/config/templates/', {
      name,
      description,
      configuration_data: configurationData
    })
    return response.data
  }

  static async applyConfigurationTemplate(templateId: number) {
    const response = await apiClient.post(`/config/templates/${templateId}/apply/`)
    return response.data
  }

  static async getConfigurationHistory(params?: any) {
    const response = await apiClient.get('/config/history/', { params })
    return response.data
  }
}

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
