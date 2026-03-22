<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <main class="terms-page">
    <section class="terms-page__hero">
      <p class="terms-page__eyebrow">Legal</p>
      <h1>Terms of Service</h1>
      <p>These terms govern use of SanitiseAI across the web tool, related pages, and connected workflows.</p>
    </section>

    <section class="terms-page__section">
      <h2>1. Service Scope</h2>
      <p>SanitiseAI provides text sanitisation and anonymisation utilities. The service is provided on an as-available basis and may evolve over time.</p>
    </section>

    <section class="terms-page__section">
      <h2>2. User Responsibilities</h2>
      <p>You are responsible for the content you submit and for ensuring your use of SanitiseAI complies with applicable laws, contracts, and internal policies.</p>
    </section>

    <section class="terms-page__section">
      <h2>3. Acceptable Use</h2>
      <p>You must not use the service for illegal activity, abuse, unauthorized access attempts, or actions that disrupt platform availability.</p>
    </section>

    <section class="terms-page__section">
      <h2>4. Liability</h2>
      <p>To the maximum extent permitted by law, SanitiseAI and its operators are not liable for indirect, incidental, or consequential losses arising from use of the service.</p>
    </section>

    <section class="terms-page__section">
      <h2>5. Changes</h2>
      <p>These terms may be updated from time to time. Continued use after updates constitutes acceptance of revised terms.</p>
    </section>

    <section class="terms-page__section">
      <h2>6. Contact</h2>
      <p>
        For legal questions, use the
        <RouterLink :to="{ path: '/contact', query: { topic: 'general-enquiry' } }">contact page</RouterLink>.
      </p>
    </section>
  </main>
</template>

<style scoped lang="scss">
.terms-page {
  width: min(980px, calc(100% - 2.4rem));
  margin: 0 auto;
  padding: 2rem 0 1.2rem;

  &__hero {
    margin-bottom: 1.8rem;

    h1 {
      margin: 0.5rem 0 0;
      font-size: clamp(2.3rem, 6vw, 4rem);
      line-height: 0.95;
      letter-spacing: -0.045em;
    }

    p {
      margin: 0.92rem 0 0;
      color: var(--text-2);
      max-width: 60ch;
      line-height: 1.62;
    }
  }

  &__eyebrow {
    margin: 0;
    display: inline-block;
    border-radius: 999px;
    background: color-mix(in srgb, var(--accent-soft), white 52%);
    border: 1px solid color-mix(in srgb, var(--accent-1), transparent 78%);
    color: var(--accent-3);
    font-size: 0.64rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 760;
    padding: 0.24rem 0.62rem;
  }

  &__section {
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 34%);
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 36%);
    border-radius: 14px;
    padding: 0.92rem 1rem;
    margin-bottom: 0.7rem;

    h2 {
      margin: 0;
      font-size: 1rem;
      letter-spacing: -0.02em;
    }

    p {
      margin: 0.48rem 0 0;
      color: var(--text-2);
      line-height: 1.62;
    }

    a {
      color: var(--accent-1);
      text-decoration: none;

      &:hover,
      &:focus-visible {
        text-decoration: underline;
      }
    }
  }
}

@media (max-width: 980px) {
  .terms-page {
    width: min(980px, calc(100% - 1rem));
  }
}
</style>
