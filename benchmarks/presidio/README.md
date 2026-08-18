# Presidio Baseline Plan

This is the starting point for a recognised-baseline comparison. Microsoft Presidio is not vendored into this repository yet because it requires a separate Python service/runtime and language models.

The comparison should measure:

- Conventional PII detection recall and critical misses.
- False positives on technical/log text.
- Context retained after anonymisation.
- Whether any task-aware transformation exists. Presidio is expected to be strong at entity detection but not task-specific minimum-disclosure planning without custom orchestration.

Next implementation step:

- Run Presidio Analyzer/Anonymizer as a local service or Docker container.
- Add a runner that sends the existing 30 benchmark fixtures and the task-awareness fixtures to that service.
- Record detection output, anonymised output, latency, critical misses, and task-utility scores using the same evaluation harness as `benchmarks/privacy-utility`.
