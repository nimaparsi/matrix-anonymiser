# SanitiseAI Task-Awareness R&D Audit

Audit target: `c9d852f` plus follow-up hardening in this working change set.
Date: 2026-08-18.

## Executive Finding

SanitiseAI is now task-conditioned, but it is not yet a general task-understanding system.

What is genuinely new is an explicit task input path and a deterministic planning layer that changes transformations according to the stated downstream task. What remains mostly heuristic is task interpretation, fact extraction beyond the base anonymiser, relevance assignment, and role substitution. There is no model, embedding search, LLM reasoning, ontology, or learned task/fact relationship model in the adaptive path.

Practical conclusion: this is a credible research prototype for task-aware minimum disclosure, not proof that the central R&D problem is solved.

## 1. Task-Awareness Path Through Code

Complete path:

1. Frontend task input: `frontend/src/pages/ToolPage.vue` exposes `taskDescription` and sends it to `/api/anonymize` as `task_description` when provided.
2. API handler: `netlify/functions/anonymize.mjs` reads `task_description`, runs the existing `anonymizeText`, then conditionally calls `adaptiveAnalyze`.
3. Task interpretation: `netlify/functions/_lib/adaptive-engine.mjs` uses `inferTaskRequirements` to match the task against deterministic keyword/regex rules.
4. Fact extraction: `buildSensitiveFacts` starts from existing detected entities, then adds regex-detected facts for money, percentage, duration, role, commercial confidentiality, labelled people, labelled secrets, phone numbers, and generic capitalised names.
5. Task relevance: `conceptImportance` maps fact concepts to `required`, `useful`, `irrelevant`, or `unknown` using predefined concept rules.
6. Transformation decision: `planTransformation` chooses `allow`, `placeholder`, `remove`, `generalise`, `role_substitute`, or `block` based on entity type, sensitivity, task relevance, and task keywords.
7. Output: `applyAdaptiveTransformations` applies those decisions from right to left over the original text and returns `adaptive_text` alongside normal anonymised output.

Precise capability assessment:

- Task intent representation: list of concept requirements such as `employee_role`, `amount_due`, `credential`, `personal_contact`.
- Concept extraction from task: yes, but through hand-written regex rules only.
- Relationship between task and source facts: shallow mapping from task concepts to fact concepts. No relational reasoning over source text.
- Keyword rules: yes, heavily.
- Regex reliance: yes, heavily.
- Entity-type reliance: yes, central to planner decisions.
- Semantic heuristics: only in the weak sense of hand-authored concept names and keyword categories. Do not call this semantic understanding.
- ML/model/embedding use: none in the adaptive layer.
- Task relevance inference: predefined, not learned or generally inferred.

## 2. Same Document, Different Tasks

Source:

```text
Nima Parsi is a Senior Frontend Engineer. Salary: £90,000. Location: Stoke-on-Trent. Leave: eight working days in September 2026. Manager: Michael Trier.
```

Observed variation:

| Fact | Staffing plan | Salary competitiveness | Public absence announcement |
| --- | --- | --- | --- |
| Nima Parsi | role_substitute -> `the senior frontend` | placeholder -> `[Person 1]` | role_substitute -> `the senior frontend` |
| Senior Frontend Engineer | allow | allow | allow |
| Salary label | placeholder | placeholder | placeholder |
| £90,000 | remove | generalise -> `approximately £90000` | remove |
| eight working days | allow | allow | allow |
| Michael Trier | role_substitute -> `the manager` | placeholder -> `[Person 1]` | role_substitute -> `the manager` |

This is meaningful variation for money and person handling. It is not deep understanding. Location remains in the output for these cases, and duration is allowed even for the salary task because it is low-sensitivity context under current rules.

## 3. Generalisation Beyond Expected Keywords

Adversarial/unseen fixtures were added for:

- Negated salary instructions.
- Excluding compensation.
- Implicit coverage planning.
- Coreference role-fit task.
- Compound support/refund task.
- Conflicting anonymous/contact instruction.
- Insurance risk summary.
- Expense claim extraction.

Latest task benchmark:

- Fixtures: 19.
- Unique source documents: 11.
- Action match rate: 0.890.
- Requirement match rate: 0.789.
- Critical leakage count: 0.

Generalisation finding:

- Works best when task wording falls into known categories: staffing, compensation, debug/logs, contract, support, recruitment, finance, healthcare, expense/refund.
- Brittle when wording is abstract, negated, or conflict-heavy.
- Requirement matching still fails on public summaries and some adversarial exclusion cases.
- The benchmark now contains failures by design; those failures are useful evidence, not regressions.

## 4. Transformation Audit

Implemented behaviours:

- `allow`: fact remains unchanged. Example: `eight working days` is allowed for staffing coverage because duration is required.
- `placeholder`: fact is replaced with a structured token. Example: `Hannah Price` -> `[Person 1]` when direct identity is unnecessary.
- `remove`: fact is replaced with removal marker. Example: salary in staffing task -> `[Removed amount]`.
- `generalise`: money/date are coarsened. Example: `£90,000` -> `approximately £90000`; `18 September 2026` -> `September 2026`.
- `role_substitute`: person is replaced with nearest detected role. Example: `Michael Trier` near `Manager:` -> `the manager`.
- `block`: credential-like facts become `[Blocked secret]`.

Important limitation: `block` is currently fact-level replacement, not request-level blocking. The request still returns output, copying is not prevented, and the UI does not yet show a hard-block warning. This is not a true policy-enforcement block.

## 5. Generalisation Quality

Current generalisation is useful but primitive.

- `£92,430` becomes approximately rounded amount, preserving broad magnitude.
- `18 September 2026` becomes `September 2026`, preserving month-level timing.
- Address generalisation such as `17 Bishopsgate, London EC2N 3AR -> central London` is not implemented.
- Age generalisation such as `37 years old -> late 30s` is not implemented.
- Money formatting currently outputs `approximately £90000`, not the more human `approximately £90k`.
- Generalisation can preserve task utility but may still leave identifying combinations when role, location, seniority, and date remain together.

## 6. Role Substitute Quality

Role substitution is now closer than the first version because it chooses the nearest role-like phrase, not simply the first role in the window. It still remains brittle.

Observed cases:

- `Dr Sarah Patel / Consultant cardiologist` -> `the consultant` rather than `the consultant cardiologist`.
- `James Martin / Customer success manager` -> `the manager`, losing useful specificity.
- `Olivia Hart / Partner at Westbridge Legal` -> `the partner` is the intended behaviour, but nearby organisation/legal terms remain a risk.
- `Senior frontend engineer Nima Parsi` -> `the senior frontend`, acceptable but partial.
- Two people with same role both become the same role substitute, creating ambiguity.
- No role present falls back to `[Person 1]`, which is correct.

Conclusion: role substitute is promising but not robust enough to market as role inference.

## 7. Block Behaviour

Secrets tested/covered through fixtures include API keys, private key snippets, passwords, connection strings, JWT-like tokens, GitHub tokens, and OAuth/client-secret patterns.

Current meaning of `block`:

- Specific fact is replaced with `[Blocked secret]`.
- Whole request is not blocked.
- No explicit UI warning yet.
- Copy/export are not prevented.
- It appears only in adaptive preview when task input triggers the adaptive path.

This should be renamed in UI/copy if exposed, or upgraded to real blocking semantics.

## 8. Task-Aware Benchmark Audit

Current task-awareness benchmark:

- Fixtures: 19.
- Unique source documents: 11.
- Multi-task source documents: 5 source groups have at least 2 task variants.
- Deliberately adversarial fixtures: 8.
- Expected transformation decisions: encoded as allowed action sets by entity type.
- Ambiguous cases: negation, conflicting instructions, public summaries, implicit coverage, coreference.

Overfitting risk:

- High. The fixtures are written against the current planner vocabulary and concepts.
- Expected decisions are coarse by entity type, not by each specific fact instance.
- Some cases were created after observing current behaviour.
- Passing the benchmark should be treated as a regression guard, not validation of general intelligence.

## 9. Re-identification Benchmark Audit

Current re-identification probe tests synthetic cases involving:

- Rare role.
- Precise location.
- Salary.
- Dates.
- Employer/organisation context.
- Alias/account linkage.
- Clinical identifiers.
- Developer secrets.
- Contract parties.

Latest result:

- Fixtures: 4.
- Critical re-identification failures: 0.
- High or critical cases: 0.

Weakness:

- Too small.
- Mostly single-document.
- Does not yet test nationality thoroughly.
- Does not yet test multi-document alias linkage where two sanitised outputs can be joined.
- Residual context model is transparent and factor-based, but still very rough.

## 10. Residual Context Risk Model

Added `netlify/functions/_lib/residual-risk.mjs`.

It returns factor-based output, not percentages:

```json
{
  "risk": "medium",
  "score": 4,
  "factors": [
    { "id": "precise_location", "label": "precise location", "weight": 2 },
    { "id": "exact_salary", "label": "exact salary or exact monetary value", "weight": 2 }
  ]
}
```

Factors currently include rare role, precise location, exact salary/value, age, nationality/birthplace, employer context, specific dates, project/codename, and alias linkage.

## 11. Privacy-Utility Experiment

Added `benchmarks/privacy-utility` comparing:

- A. Original text.
- B. Standard SanitiseAI redaction.
- C. Adaptive SanitiseAI transformation.

Latest result:

- Fixtures: 5.
- Average utility: original 0.933, standard 0.833, adaptive 0.833.
- Sensitive leaks: original 16, standard 7, adaptive 1.
- Critical leaks: original 4, standard 0, adaptive 0.

Interpretation:

- Adaptive transformation reduced unnecessary sensitive disclosure compared with standard redaction in this small deterministic set.
- It did not improve utility over standard redaction yet.
- Strongest current evidence: privacy improvement without utility loss in the tested cases.
- Missing evidence: adaptive preserving materially more task-useful facts than standard redaction.

## 12. Presidio Baseline

A Presidio comparison plan was added under `benchmarks/presidio/README.md`.

It is not yet executable because Presidio requires a separate Python/service runtime and model dependencies that are not vendored in this repo. The next practical step is to run Presidio as a local service/Docker container and feed it the existing benchmark fixtures.

## 13. Public Site Recheck

Searched public frontend/backend copy for overclaims including:

`local-first`, `edge`, `on-device`, `never leaves`, `semantic`, `AI-powered`, `ML-driven`, `risk score`, `compliant`, `certified`, `zero trust`, `automated remediation`, `SOC2`, `ISO 27001`, `HIPAA`, and enterprise/dashboard/account language.

Fixes made:

- Tool copy now says `minimum-disclosure guidance`, not risk score.
- Security page uses `Pre-sharing sanitisation`, not edge sanitisation.
- Privacy page uses `Privacy & Data Handling` and removes account/workspace/billing rights language.
- Contact page says request-scoped processing, not local-first processing.

Remaining copy risk:

- Marketing should avoid claiming task-aware privacy broadly until we can show stronger generalisation and utility evidence.
- Safe framing: `task-aware preview`, `minimum-disclosure guidance`, `experimental adaptive transformation`, `request-scoped API processing`.

## 14. R&D Readiness Reassessment

Scores are evidence-weighted, not feature-count weighted.

| Area | Score / 10 | Evidence |
| --- | ---: | --- |
| Problem severity | 8 | Clear AI/data-sharing privacy problem. |
| Prototype maturity | 7 | Production UI/API plus benchmarks exist. |
| Detection quality | 6.5 | 30-fixture benchmark recall 0.868, no critical misses; still heuristic. |
| Task-awareness | 5.5 | Task-conditioned planner exists, but keyword/rule based. |
| Transformation sophistication | 6 | Multiple actions exist; generalisation/role substitution are shallow. |
| Technical novelty | 6 | Task-aware minimum disclosure is differentiated, implementation is not yet deep. |
| Technical uncertainty | 8 | Core uncertainty remains: can task/fact relevance generalise? |
| Benchmark maturity | 5.5 | Better adversarial coverage now, still small and overfit-prone. |
| Privacy-utility evidence | 5 | First comparison exists; adaptive reduces leaks but not utility gain. |
| Re-identification evidence | 4.5 | Factor model and probe exist; needs multi-document/alias expansion. |
| Competitor evidence | 2 | Presidio plan only; no executable comparison yet. |
| Security credibility | 6 | Copy is now more truthful; block semantics need upgrade. |
| Customer validation | 2 | Not evidenced in repo. |
| Commercial proposition | 6 | Product story is credible if claims stay grounded. |
| Innovate UK readiness | 5.5 | Better R&D framing, but evidence base still early. |

Overall: approximately 6.3/10 as an R&D-backed product prototype. The previous work moved the project from polished utility toward measurable research, but not yet to defensible technical differentiation.

## 15. Strongest Technical Uncertainty

The strongest uncertainty is whether SanitiseAI can infer what information is necessary for a downstream task without hard-coded task categories.

The next step-change toward 8/10 requires:

- Larger same-document/different-task benchmark.
- Multi-document re-identification/linkage tests.
- Better role/fact relation extraction.
- Executable Presidio baseline.
- Utility tests where adaptive preserves useful context that standard redaction destroys.
