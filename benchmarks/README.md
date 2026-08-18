# SanitiseAI Benchmarks

This folder benchmarks the production Netlify anonymisation engine against labelled synthetic fixtures.

Run from the repository root:

```bash
node benchmarks/run.mjs
```

Outputs:

- `benchmarks/reports/current-baseline.json`
- `benchmarks/reports/current-baseline.md`

The benchmark intentionally uses synthetic examples only. It is a regression harness for product quality, not a public accuracy certification.
