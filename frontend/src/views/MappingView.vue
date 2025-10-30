<template>
  <div class="mapping-view">
    <div class="page-header">
      <h1>
        <i class="pi pi-sitemap"></i>
        Field Mapping
      </h1>
      <p>Map source fields to target schema with AI-powered suggestions</p>
    </div>

    <Card>
      <template #content>
        <div class="coming-soon">
          <i class="pi pi-cog" style="font-size: 4rem; color: var(--p-primary-color); margin-bottom: 1rem;"></i>
          <h2>Coming Soon</h2>
          <p>The field mapping interface is being built with advanced PrimeVue components including:</p>
          <ul>
            <li>Interactive data tables with filtering and sorting</li>
            <li>AI-powered mapping suggestions</li>
            <li>Drag-and-drop field mapping</li>
            <li>Bulk template upload/download</li>
            <li>Real-time validation and feedback</li>
          </ul>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
// Field mapping logic will be implemented here
</script>

<style scoped>
.mapping-view {
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
