import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: string
  name: string
  email: string
  role: 'admin' | 'user'
}

export const useUserStore = defineStore('user', () => {
  const currentUser = ref<User | null>(null)
  const isAuthenticated = computed(() => currentUser.value !== null)
  const isAdmin = computed(() => currentUser.value?.role === 'admin')

  const login = async (email: string, password: string) => {
    // TODO: Replace with actual API call
    try {
      // Mock authentication - replace with real API
      const mockUser: User = {
        id: '1',
        name: 'David Galluzzo',
        email: email,
        role: email.includes('admin') ? 'admin' : 'user'
      }
      
      currentUser.value = mockUser
      
      // Store in localStorage for persistence
      localStorage.setItem('user', JSON.stringify(mockUser))
      
      return { success: true }
    } catch (error) {
      return { success: false, error: 'Invalid credentials' }
    }
  }

  const logout = () => {
    currentUser.value = null
    localStorage.removeItem('user')
  }

  const initializeAuth = () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        currentUser.value = JSON.parse(storedUser)
      } catch (error) {
        console.error('Failed to parse stored user:', error)
        localStorage.removeItem('user')
      }
    }
  }

  return {
    currentUser,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    initializeAuth
  }
})

