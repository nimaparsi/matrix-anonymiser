<script setup lang="ts">
import { PhCheckCircle } from '@phosphor-icons/vue'

const bullets = [
  'We do not store your data',
  'Processing happens instantly',
  'You stay in control',
]
</script>

<template>
  <section class="privacy" aria-labelledby="privacy-title">
    <div class="privacy__box">
      <p class="privacy__eyebrow">Privacy</p>
      <h2 id="privacy-title">Designed for trust from day one</h2>
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
    border: 1px solid var(--border-1);
    border-radius: 20px;
    background:
      radial-gradient(120% 130% at 100% 0%, color-mix(in srgb, var(--accent-2), transparent 88%), transparent 50%),
      linear-gradient(
        170deg,
        color-mix(in srgb, var(--surface-0), white 9%),
        color-mix(in srgb, var(--surface-1), transparent 2%)
      );
    box-shadow: var(--shadow-sm);
    padding: 1rem;
  }

  &__eyebrow {
    margin: 0;
    color: var(--accent-2);
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  h2 {
    margin: 0.45rem 0 0;
    color: var(--text-1);
    font-size: clamp(1.35rem, 3.4vw, 1.85rem);
    letter-spacing: -0.02em;
  }

  &__list {
    list-style: none;
    padding: 0;
    margin: 0.86rem 0 0;
    display: grid;
    gap: 0.58rem;
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
    color: color-mix(in srgb, var(--accent-2), var(--accent-1) 44%);
    flex-shrink: 0;
  }
}
</style>
