<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>
<template>
  <main class="not-found">
    <p>404 / Page not found</p>
    <h1>This page isn't here.</h1>
    <p>The link may be outdated. Your next step can still be straightforward.</p>
    <RouterLink class="btn btn--primary" to="/tool">Open sanitiser</RouterLink>
    <RouterLink class="btn btn--secondary" to="/">Return home</RouterLink>
  </main>
</template>
<style scoped>
.not-found { max-width: 60rem; margin: 4rem auto; padding: 2rem; min-height: 45vh; }
h1 { font-size: clamp(2rem, 6vw, 4rem); } .btn { margin: 1rem 1rem 0 0; }
</style>
