<script setup lang="ts">
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
          <span class="privacy__check" aria-hidden="true">✓</span>
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
    gap: 0.52rem;
    color: var(--text-2);
    font-size: 0.95rem;
    font-weight: 600;
  }

  &__check {
    width: 20px;
    height: 20px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: var(--accent-ink);
    font-size: 0.72rem;
    background: linear-gradient(145deg, var(--accent-1), var(--accent-2));
    box-shadow: var(--shadow-xs);
  }
}

</style>
