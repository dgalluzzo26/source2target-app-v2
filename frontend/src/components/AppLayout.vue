<template>
  <div class="layout-wrapper">
    <!-- Top Header -->
    <div class="layout-topbar">
      <div class="layout-topbar-logo">
        <img src="/favicon.ico" alt="Logo" class="logo" />
        <span class="logo-text">Gainwell Source-to-Target Mapping Platform</span>
      </div>
      
      <div class="layout-topbar-menu">
        <div class="user-info">
          <i class="pi pi-user"></i>
          <span>{{ userStore.currentUser?.name || 'User' }}</span>
          <Badge v-if="userStore.isAdmin" value="Admin" severity="info" />
          <Badge v-else value="User" severity="secondary" />
        </div>
        <Button 
          icon="pi pi-sign-out" 
          severity="secondary" 
          text 
          @click="logout"
          v-tooltip="'Logout'"
        />
      </div>
    </div>

    <!-- Sidebar Navigation -->
    <div class="layout-sidebar">
      <div class="layout-menu">
        <ul class="layout-menu-root">
          <li>
            <router-link to="/" class="layout-menuitem-link">
              <i class="layout-menuitem-icon pi pi-home"></i>
              <span class="layout-menuitem-text">Introduction</span>
            </router-link>
          </li>
          <li>
            <router-link to="/mapping" class="layout-menuitem-link">
              <i class="layout-menuitem-icon pi pi-sitemap"></i>
              <span class="layout-menuitem-text">Field Mapping</span>
            </router-link>
          </li>
          <li>
            <router-link to="/config" class="layout-menuitem-link">
              <i class="layout-menuitem-icon pi pi-cog"></i>
              <span class="layout-menuitem-text">Configuration</span>
            </router-link>
          </li>
          <li v-if="userStore.isAdmin">
            <router-link to="/admin" class="layout-menuitem-link">
              <i class="layout-menuitem-icon pi pi-shield"></i>
              <span class="layout-menuitem-text">Administration</span>
            </router-link>
          </li>
        </ul>
      </div>
    </div>

    <!-- Main Content -->
    <div class="layout-main-container">
      <div class="layout-main">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const logout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.layout-topbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 4rem;
  z-index: 997;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  background: var(--p-surface-0);
  border-bottom: 1px solid var(--p-surface-border);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.layout-topbar-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo {
  height: 2rem;
  width: 2rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--p-primary-color);
}

.layout-topbar-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--p-surface-50);
  border-radius: var(--p-border-radius);
}

.layout-sidebar {
  position: fixed;
  top: 4rem;
  left: 0;
  width: 16rem;
  height: calc(100vh - 4rem);
  z-index: 996;
  background: var(--p-surface-0);
  border-right: 1px solid var(--p-surface-border);
  overflow-y: auto;
}

.layout-menu {
  padding: 1rem;
}

.layout-menu-root {
  list-style: none;
  margin: 0;
  padding: 0;
}

.layout-menu-root > li {
  margin-bottom: 0.5rem;
}

.layout-menuitem-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: var(--p-text-color);
  text-decoration: none;
  border-radius: var(--p-border-radius);
  transition: all 0.2s;
}

.layout-menuitem-link:hover {
  background: var(--p-surface-100);
  color: var(--p-primary-color);
}

.layout-menuitem-link.router-link-active {
  background: var(--p-primary-color);
  color: var(--p-primary-contrast-color);
}

.layout-menuitem-icon {
  font-size: 1.125rem;
}

.layout-menuitem-text {
  font-weight: 500;
}

.layout-main-container {
  margin-left: 16rem;
  margin-top: 4rem;
  min-height: calc(100vh - 4rem);
}

.layout-main {
  padding: 2rem;
}

@media (max-width: 768px) {
  .layout-sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s;
  }
  
  .layout-main-container {
    margin-left: 0;
  }
  
  .logo-text {
    display: none;
  }
}
</style>

