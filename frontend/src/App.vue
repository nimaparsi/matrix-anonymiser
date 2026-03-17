<script setup lang="ts">
import LandingHeader from './components/landing/LandingHeader.vue'
import HeroDemoSection from './components/landing/HeroDemoSection.vue'
import CompatibilityStrip from './components/landing/CompatibilityStrip.vue'
import FeaturesSection from './components/landing/FeaturesSection.vue'
import HowItWorksSection from './components/landing/HowItWorksSection.vue'
import ExpansionSection from './components/landing/ExpansionSection.vue'
import UseCasesSection from './components/landing/UseCasesSection.vue'
import PrivacySection from './components/landing/PrivacySection.vue'
import FinalCtaSection from './components/landing/FinalCtaSection.vue'
import LandingFooter from './components/landing/LandingFooter.vue'
</script>

<template>
  <div class="landing-page">
    <LandingHeader />

    <main class="landing-page__main">
      <HeroDemoSection id="demo" class="landing-page__section landing-page__section--hero" />
      <CompatibilityStrip class="landing-page__section landing-page__section--strip" />
      <FeaturesSection id="features" class="landing-page__section" />
      <HowItWorksSection id="how-it-works" class="landing-page__section" />
      <ExpansionSection id="extensions" class="landing-page__section" />
      <UseCasesSection id="use-cases" class="landing-page__section" />
      <PrivacySection id="privacy" class="landing-page__section" />
      <FinalCtaSection id="final-cta" class="landing-page__section" />
      <LandingFooter />
    </main>
  </div>
</template>

<style lang="scss" src="./global.scss"></style>
<style scoped lang="scss" src="./App.scss"></style>
