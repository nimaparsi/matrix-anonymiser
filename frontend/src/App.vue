<script setup lang="ts">
import { RouterView } from 'vue-router'
import SiteHeader from './components/layout/SiteHeader.vue'
import SiteFooter from './components/layout/SiteFooter.vue'
</script>

<template>
  <div class="app-shell">
    <SiteHeader />
    <RouterView />
    <SiteFooter />
  </div>
</template>

<style lang="scss" src="./global.scss"></style>
<style scoped lang="scss" src="./App.scss"></style>
