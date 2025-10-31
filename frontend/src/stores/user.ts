import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { AuthAPI, handleApiError } from '@/services/api'

export interface User {
  id: number
  email: string
  display_name: string
  role: 'admin' | 'platform_user' | 'user'
  is_admin: boolean
  is_platform_user: boolean
  is_active: boolean
  last_login?: string
  date_joined: string
}

export const useUserStore = defineStore('user', () => {
  const currentUser = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  const isAuthenticated = computed(() => currentUser.value !== null)
  const isAdmin = computed(() => currentUser.value?.is_admin || false)
  const isPlatformUser = computed(() => currentUser.value?.is_platform_user || false)

  const getCurrentUser = async () => {
    loading.value = true
    error.value = null
    
    try {
      // Try to get current user from backend (like original app's AuthManager.get_current_user())
      const response = await AuthAPI.getCurrentUser()
      currentUser.value = response
      return { success: true }
    } catch (apiError: any) {
      console.warn('Failed to get current user from Databricks context:', apiError)
      
      // Set a default user if we can't detect from Databricks context (for development)
      currentUser.value = {
        id: 1,
        email: 'user@gainwell.com',
        display_name: 'Current User',
        role: 'platform_user',
        is_admin: false,
        is_platform_user: true,
        is_active: true,
        date_joined: new Date().toISOString()
      }
      
      error.value = 'Using default user - Databricks authentication not available'
      return { success: false, error: error.value }
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
      }
    } catch (apiError: any) {
      console.warn('Failed to refresh user profile:', apiError)
      // Fallback to getting current user from Databricks context
      await getCurrentUser()
    }
  }

  const initializeAuth = async () => {
    // Automatically detect user from Databricks context (like original app)
    await getCurrentUser()
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
    getCurrentUser,
    refreshProfile,
    initializeAuth,
    clearError
  }
})