<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import MvpHeader from './components/mvp/MvpHeader.vue'
import MvpFooter from './components/mvp/MvpFooter.vue'

const route = useRoute()
const isTool = computed(() => route.name === 'tool')
</script>

<template>
  <div class="app-shell">
    <MvpHeader />
    <RouterView />
    <MvpFooter v-if="!isTool" />
  </div>
</template>

<style lang="scss" src="./global.scss"></style>
<style scoped lang="scss" src="./App.scss"></style>
