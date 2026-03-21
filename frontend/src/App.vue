<script setup lang="ts">
import { RouterView } from 'vue-router'
import MvpHeader from './components/mvp/MvpHeader.vue'
import MvpFooter from './components/mvp/MvpFooter.vue'
</script>

<template>
  <div class="app-shell">
    <MvpHeader />
    <RouterView />
    <MvpFooter />
  </div>
</template>

<style lang="scss" src="./global.scss"></style>
<style scoped lang="scss" src="./App.scss"></style>
