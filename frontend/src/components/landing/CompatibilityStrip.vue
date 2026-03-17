<script setup lang="ts">
const tools = ['ChatGPT', 'Claude', 'Gemini', 'Email', 'Docs']
</script>

<template>
  <section class="compat-strip" aria-label="Compatibility">
    <p class="compat-strip__label">Compatible with</p>
    <ul class="compat-strip__list">
      <li v-for="tool in tools" :key="tool" class="compat-strip__item">
        <span class="compat-strip__dot" aria-hidden="true"></span>
        <span>{{ tool }}</span>
      </li>
    </ul>
  </section>
</template>

<style scoped lang="scss">
.compat-strip {
  border: 1px solid #dde6f7;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
  padding: 0.8rem 0.95rem;
  display: flex;
  align-items: center;
  gap: 1rem;

  &__label {
    margin: 0;
    color: #475569;
    font-size: 0.85rem;
    font-weight: 700;
    white-space: nowrap;
  }

  &__list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.65rem;
  }

  &__item {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    border: 1px solid #d6e2f7;
    border-radius: 999px;
    background: #ffffff;
    color: #1e293b;
    padding: 0.35rem 0.62rem;
    font-size: 0.84rem;
    font-weight: 600;
  }

  &__dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: linear-gradient(135deg, #2563eb, #4338ca);
  }
}

@media (max-width: 900px) {
  .compat-strip {
    align-items: flex-start;
    flex-direction: column;
    gap: 0.65rem;
  }
}

</style>
