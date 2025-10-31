<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: var(--p-font-family);
  background: var(--p-surface-ground);
  color: var(--p-text-color);
  }

#app {
  min-height: 100vh;
}
</style>
