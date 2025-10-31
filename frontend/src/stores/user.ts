import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { AuthAPI, handleApiError } from '@/services/api'

export interface User {
  id: number
  email: string
  username: string
  full_name: string
  display_name: string
  organization?: string
  department?: string
  phone_number?: string
  role: 'admin' | 'user' | 'viewer'
  is_admin: boolean
  is_platform_user: boolean
  is_active: boolean
  last_login?: string
  date_joined: string
  created_at: string
  updated_at: string
}

export const useUserStore = defineStore('user', () => {
  const currentUser = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  const isAuthenticated = computed(() => currentUser.value !== null)
  const isAdmin = computed(() => currentUser.value?.is_admin || false)
  const isPlatformUser = computed(() => currentUser.value?.is_platform_user || false)

  const login = async (email: string, password: string) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await AuthAPI.login(email, password)
      
      if (response.success && response.user) {
        currentUser.value = response.user
        
        // Store user data for persistence (tokens are handled by API service)
        localStorage.setItem('user', JSON.stringify(response.user))
        
        return { success: true }
      }
      
      return { success: false, error: 'Login failed' }
    } catch (apiError: any) {
      const errorInfo = handleApiError(apiError)
      error.value = errorInfo.error
      return { success: false, error: errorInfo.error }
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    loading.value = true
    
    try {
      await AuthAPI.logout()
    } catch (error) {
      console.warn('Logout API call failed:', error)
    }
    
    // Clear user data regardless of API response
    currentUser.value = null
    error.value = null
    localStorage.removeItem('user')
    
    loading.value = false
  }

  const register = async (userData: {
    email: string
    username: string
    password: string
    password_confirm: string
    full_name?: string
    organization?: string
    department?: string
    phone_number?: string
  }) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await AuthAPI.register(userData)
      
      if (response.user) {
        // Auto-login after successful registration
        return await login(userData.email, userData.password)
      }
      
      return { success: true, message: 'Registration successful' }
    } catch (apiError: any) {
      const errorInfo = handleApiError(apiError)
      error.value = errorInfo.error
      return { success: false, error: errorInfo.error }
    } finally {
      loading.value = false
    }
  }

  const updateProfile = async (userData: {
    full_name?: string
    organization?: string
    department?: string
    phone_number?: string
  }) => {
    loading.value = true
    error.value = null
    
    try {
      const updatedUser = await AuthAPI.updateProfile(userData)
      
      if (updatedUser) {
        currentUser.value = updatedUser
        localStorage.setItem('user', JSON.stringify(updatedUser))
      }
      
      return { success: true }
    } catch (apiError: any) {
      const errorInfo = handleApiError(apiError)
      error.value = errorInfo.error
      return { success: false, error: errorInfo.error }
    } finally {
      loading.value = false
    }
  }

  const changePassword = async (passwordData: {
    old_password: string
    new_password: string
    new_password_confirm: string
  }) => {
    loading.value = true
    error.value = null
    
    try {
      await AuthAPI.changePassword(passwordData)
      return { success: true, message: 'Password changed successfully' }
    } catch (apiError: any) {
      const errorInfo = handleApiError(apiError)
      error.value = errorInfo.error
      return { success: false, error: errorInfo.error }
    } finally {
      loading.value = false
    }
  }

  const refreshProfile = async () => {
    if (!isAuthenticated.value) return
    
    try {
      const updatedUser = await AuthAPI.getProfile()
      
      if (updatedUser) {
        currentUser.value = updatedUser
        localStorage.setItem('user', JSON.stringify(updatedUser))
      }
    } catch (apiError: any) {
      console.warn('Failed to refresh user profile:', apiError)
      // Don't set error state for background refresh failures
    }
  }

  const initializeAuth = () => {
    // Check if user data exists in localStorage
    const storedUser = localStorage.getItem('user')
    const accessToken = localStorage.getItem('access_token')
    
    if (storedUser && accessToken) {
      try {
        const user = JSON.parse(storedUser)
        currentUser.value = user
        
        // Optionally refresh user data from server
        refreshProfile()
      } catch (error) {
        console.error('Failed to parse stored user:', error)
        localStorage.removeItem('user')
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    currentUser,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    isAdmin,
    isPlatformUser,
    
    // Actions
    login,
    logout,
    register,
    updateProfile,
    changePassword,
    refreshProfile,
    initializeAuth,
    clearError
  }
})

