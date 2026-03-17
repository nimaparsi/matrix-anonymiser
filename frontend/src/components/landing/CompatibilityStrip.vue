<script setup lang="ts">
type ToolKind = 'chatgpt' | 'claude' | 'gemini' | 'email' | 'docs'

const tools: Array<{ name: string; kind: ToolKind }> = [
  { name: 'ChatGPT', kind: 'chatgpt' },
  { name: 'Claude', kind: 'claude' },
  { name: 'Gemini', kind: 'gemini' },
  { name: 'Email', kind: 'email' },
  { name: 'Docs', kind: 'docs' },
]
</script>

<template>
  <section class="compat-strip" aria-label="Compatibility">
    <p class="compat-strip__label">Compatible with</p>
    <ul class="compat-strip__list">
      <li v-for="tool in tools" :key="tool.name" class="compat-strip__item">
        <span class="compat-strip__icon" :class="`compat-strip__icon--${tool.kind}`" aria-hidden="true">
          <svg v-if="tool.kind === 'chatgpt'" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 3.5c1.7 0 3.1 1.4 3.1 3.1v.2h.2a3.1 3.1 0 0 1 3.1 3.1c0 1.7-1.4 3.1-3.1 3.1h-.2v.2a3.1 3.1 0 0 1-3.1 3.1A3.1 3.1 0 0 1 8.9 13v-.2h-.2a3.1 3.1 0 0 1-3.1-3.1c0-1.7 1.4-3.1 3.1-3.1h.2v-.2C8.9 4.9 10.3 3.5 12 3.5Z"
              stroke="currentColor"
              stroke-width="1.8"
            />
          </svg>
          <svg v-else-if="tool.kind === 'claude'" viewBox="0 0 24 24" fill="none">
            <path d="M6 7.5h12M6 12h12M6 16.5h7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            <path d="M15 16.5l2 2 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <svg v-else-if="tool.kind === 'gemini'" viewBox="0 0 24 24" fill="none">
            <path d="M12 3.2 14.6 9.4 20.8 12l-6.2 2.6L12 20.8l-2.6-6.2L3.2 12l6.2-2.6L12 3.2Z" stroke="currentColor" stroke-width="1.7" />
          </svg>
          <svg v-else-if="tool.kind === 'email'" viewBox="0 0 24 24" fill="none">
            <rect x="3.8" y="6.2" width="16.4" height="11.6" rx="2.1" stroke="currentColor" stroke-width="1.7" />
            <path d="m5.2 8 6.2 5a1 1 0 0 0 1.2 0l6.2-5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none">
            <path d="M8 4.5h6.5l4 4V19a1.5 1.5 0 0 1-1.5 1.5H8A1.5 1.5 0 0 1 6.5 19V6A1.5 1.5 0 0 1 8 4.5Z" stroke="currentColor" stroke-width="1.7" />
            <path d="M14.5 4.8v3.7h3.7" stroke="currentColor" stroke-width="1.7" />
            <path d="M9 12h6M9 15h4.2" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
          </svg>
        </span>
        <span>{{ tool.name }}</span>
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
    background: linear-gradient(180deg, #ffffff, #f8fbff);
    color: #1e293b;
    padding: 0.36rem 0.68rem 0.36rem 0.5rem;
    font-size: 0.84rem;
    font-weight: 600;
    box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
    transition: transform 160ms ease, box-shadow 180ms ease, border-color 180ms ease;
  }

  &__item:hover {
    transform: translateY(-1px);
    border-color: #bfdbfe;
    box-shadow: 0 8px 18px rgba(37, 99, 235, 0.11);
  }

  &__icon {
    width: 1.2rem;
    height: 1.2rem;
    border-radius: 999px;
    display: inline-grid;
    place-items: center;
    border: 1px solid transparent;
    background: #eef5ff;
    color: #1d4ed8;
    flex-shrink: 0;

    svg {
      width: 0.82rem;
      height: 0.82rem;
    }
  }

  &__icon--chatgpt {
    background: #ecfdf5;
    color: #047857;
    border-color: #a7f3d0;
  }

  &__icon--claude {
    background: #fff7ed;
    color: #c2410c;
    border-color: #fdba74;
  }

  &__icon--gemini {
    background: #f3e8ff;
    color: #7e22ce;
    border-color: #d8b4fe;
  }

  &__icon--email {
    background: #eff6ff;
    color: #1d4ed8;
    border-color: #bfdbfe;
  }

  &__icon--docs {
    background: #f0fdfa;
    color: #0f766e;
    border-color: #99f6e4;
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
