<template>
  <div class="login-container">
    <Card class="login-card">
      <template #header>
        <div class="login-header">
          <img src="/favicon.ico" alt="Logo" class="login-logo" />
          <h2>Gainwell Source-to-Target Platform</h2>
          <p>Sign in to access the mapping platform</p>
        </div>
      </template>
      
      <template #content>
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="field">
            <label for="email">Email</label>
            <InputText 
              id="email"
              v-model="email"
              type="email"
              placeholder="Enter your email"
              :class="{ 'p-invalid': emailError }"
              required
            />
            <small v-if="emailError" class="p-error">{{ emailError }}</small>
          </div>
          
          <div class="field">
            <label for="password">Password</label>
            <Password 
              id="password"
              v-model="password"
              placeholder="Enter your password"
              :class="{ 'p-invalid': passwordError }"
              :feedback="false"
              toggleMask
              required
            />
            <small v-if="passwordError" class="p-error">{{ passwordError }}</small>
          </div>
          
          <Button 
            type="submit" 
            label="Sign In" 
            class="login-button"
            :loading="loading"
            :disabled="!email || !password"
          />
          
          <Message v-if="error" severity="error" :closable="false">
            {{ error }}
          </Message>
        </form>
      </template>
      
      <template #footer>
        <div class="login-footer">
          <p><small>Demo credentials: admin@gainwell.com / user@gainwell.com (any password)</small></p>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const emailError = ref('')
const passwordError = ref('')

const validateForm = () => {
  emailError.value = ''
  passwordError.value = ''
  
  if (!email.value) {
    emailError.value = 'Email is required'
    return false
  }
  
  if (!email.value.includes('@')) {
    emailError.value = 'Please enter a valid email'
    return false
  }
  
  if (!password.value) {
    passwordError.value = 'Password is required'
    return false
  }
  
  return true
}

const handleLogin = async () => {
  if (!validateForm()) return
  
  loading.value = true
  error.value = ''
  
  try {
    const result = await userStore.login(email.value, password.value)
    
    if (result.success) {
      router.push('/')
    } else {
      error.value = result.error || 'Login failed'
    }
  } catch (err) {
    error.value = 'An unexpected error occurred'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, var(--p-primary-50) 0%, var(--p-primary-100) 100%);
  padding: 2rem;
}

.login-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  padding: 2rem 2rem 0;
}

.login-logo {
  height: 3rem;
  width: 3rem;
  margin-bottom: 1rem;
}

.login-header h2 {
  margin: 0 0 0.5rem 0;
  color: var(--p-text-color);
  font-size: 1.5rem;
}

.login-header p {
  margin: 0;
  color: var(--p-text-muted-color);
}

.login-form {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field label {
  font-weight: 600;
  color: var(--p-text-color);
}

.login-button {
  margin-top: 1rem;
}

.login-footer {
  text-align: center;
  padding: 0 2rem 2rem;
  color: var(--p-text-muted-color);
}
</style>
