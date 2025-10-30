<template>
  <div class="config-view">
    <div class="page-header">
      <h1>
        <i class="pi pi-cog"></i>
        Configuration
      </h1>
      <p>Manage database connections, AI models, and system settings</p>
    </div>

    <Card>
      <template #content>
        <div class="coming-soon">
          <i class="pi pi-cog" style="font-size: 4rem; color: var(--p-primary-color); margin-bottom: 1rem;"></i>
          <h2>Coming Soon</h2>
          <p>The configuration interface will include:</p>
          <ul>
            <li>Database connection management</li>
            <li>AI model endpoint configuration</li>
            <li>Vector search index settings</li>
            <li>Security and access controls</li>
            <li>System health monitoring</li>
          </ul>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
// Configuration logic will be implemented here
</script>

<style scoped>
.config-view {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 0.5rem 0;
  color: var(--p-text-color);
  font-size: 2rem;
}

.page-header p {
  margin: 0;
  color: var(--p-text-muted-color);
  font-size: 1.125rem;
}

.coming-soon {
  text-align: center;
  padding: 3rem 2rem;
}

.coming-soon h2 {
  margin: 0 0 1rem 0;
  color: var(--p-text-color);
}

.coming-soon p {
  margin: 0 0 1.5rem 0;
  color: var(--p-text-muted-color);
  font-size: 1.125rem;
}

.coming-soon ul {
  text-align: left;
  max-width: 400px;
  margin: 0 auto;
  color: var(--p-text-muted-color);
}

.coming-soon li {
  margin-bottom: 0.5rem;
}
</style>
