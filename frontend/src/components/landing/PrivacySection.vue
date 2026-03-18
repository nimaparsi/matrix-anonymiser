<script setup lang="ts">
import { PhCheckCircle } from '@phosphor-icons/vue'

const bullets = ['We don’t store your data', 'Processing happens instantly', 'You stay in control']
</script>

<template>
  <section class="privacy" aria-labelledby="privacy-title">
    <div class="privacy__box">
      <p class="privacy__eyebrow">Privacy</p>
      <h2 id="privacy-title">Built to protect sensitive text before sharing</h2>
      <ul class="privacy__list">
        <li v-for="item in bullets" :key="item" class="privacy__item">
          <PhCheckCircle class="privacy__check" :size="18" weight="duotone" aria-hidden="true" />
          <span>{{ item }}</span>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped lang="scss">
.privacy {
  &__box {
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 8%);
    border-radius: 18px;
    background: var(--surface-0);
    box-shadow: var(--shadow-sm);
    padding: 1.1rem;
  }

  &__eyebrow {
    margin: 0;
    color: var(--accent-2);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  h2 {
    margin: 0.5rem 0 0;
    font-size: clamp(1.6rem, 3.4vw, 2.1rem);
    line-height: 1.12;
    letter-spacing: -0.03em;
  }

  &__list {
    margin: 0.9rem 0 0;
    padding: 0;
    list-style: none;
    display: grid;
    gap: 0.56rem;
  }

  &__item {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-2);
    font-size: 0.95rem;
    font-weight: 600;
  }

  &__check {
    color: var(--accent-2);
    flex-shrink: 0;
  }
}
</style>
