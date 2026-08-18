# Task-Aware Minimum Disclosure Baseline

Generated: 2026-08-18T19:44:06.649Z

- Fixtures: 19
- Requirement match rate: 0.789
- Transformation action match rate: 0.89
- Critical leakage count: 0

## hr-profile-staffing

- Source: hr-profile-01
- Task: Create a staffing plan while this employee is away.
- Requirement match: 1
- Action match: 1
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: none

## hr-profile-salary

- Source: hr-profile-01
- Task: Assess whether this employee's salary is competitive for their role.
- Requirement match: 1
- Action match: 0.75
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: PERSON -> placeholder

## hr-profile-email-rewrite

- Source: hr-profile-01
- Task: Rewrite this internal HR note professionally for a manager update.
- Requirement match: 1
- Action match: 1
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: none

## incident-log-debug

- Source: incident-log-01
- Task: Debug the authentication error in this production log.
- Requirement match: 1
- Action match: 1
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: none

## incident-log-external-summary

- Source: incident-log-01
- Task: Summarise this incident for a third-party vendor without exposing internal infrastructure.
- Requirement match: 0
- Action match: 1
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: none

## contract-obligations

- Source: contract-01
- Task: Explain the key obligations in this contract excerpt.
- Requirement match: 1
- Action match: 1
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: none

## contract-public-summary

- Source: contract-01
- Task: Create a public-facing summary of this contract without naming the parties or exact commercial terms.
- Requirement match: 0
- Action match: 1
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: none

## support-complaint-summary

- Source: support-01
- Task: Summarise this customer complaint for an internal support handoff.
- Requirement match: 1
- Action match: 0.75
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: ORDER_ID -> placeholder

## support-refund-calculation

- Source: support-01
- Task: Calculate the outstanding refund amount and identify the order reference.
- Requirement match: 1
- Action match: 0.75
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: ORDER_ID -> placeholder

## candidate-role-fit

- Source: candidate-01
- Task: Determine whether this applicant meets the role requirements.
- Requirement match: 1
- Action match: 1
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: none

## candidate-compensation-review

- Source: candidate-01
- Task: Compare this candidate's salary expectations with market compensation for the role.
- Requirement match: 1
- Action match: 1
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: none

## adversarial-negated-salary

- Source: hr-profile-01
- Task: Please do not use the salary when creating a compensation analysis.
- Requirement match: 1
- Action match: 0.5
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: MONEY -> remove

## adversarial-exclude-compensation

- Source: hr-profile-01
- Task: Summarise this document but exclude all employee compensation information.
- Requirement match: 0
- Action match: 0.333
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: MONEY -> remove, PERCENTAGE -> placeholder/remove

## adversarial-implicit-coverage

- Source: hr-profile-02
- Task: Work out who should cover this person's responsibilities.
- Requirement match: 1
- Action match: 1
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: none

## adversarial-coreference-role-fit

- Source: candidate-02
- Task: Determine whether she qualifies for the role.
- Requirement match: 1
- Action match: 1
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: none

## adversarial-compound-support-refund

- Source: support-02
- Task: Summarise the complaint and calculate the refund amount.
- Requirement match: 1
- Action match: 0.75
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: ORDER_ID -> placeholder

## adversarial-conflicting-contact

- Source: support-03
- Task: Prepare an anonymous summary but include the customer's full contact details.
- Requirement match: 0
- Action match: 1
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: none

## unseen-insurance-risk

- Source: insurance-01
- Task: Draft an insurance risk summary.
- Requirement match: 1
- Action match: 1
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: none

## unseen-expense-claim

- Source: expense-01
- Task: Extract only the information required to submit an expense claim.
- Requirement match: 1
- Action match: 0.8
- Utility retention proxy: 1
- Sensitive suppression proxy: 1
- Missed actions: CREDIT_CARD -> placeholder
