# SanitiseAI Anonymisation Baseline

Generated: 2026-08-18T18:58:45.684Z

## Summary

- Fixtures: 30
- Expected entities: 189
- Matched expected entities: 164
- Detected entities: 186
- Recall: 0.868
- Precision proxy: 0.882
- F1 proxy: 0.875
- Average latency: 1.95ms
- Critical misses: 0

## Fixture Results

### analytics-payload

- Domain: product
- Recall: 1
- Matched: 7/7
- Detected: 7
- Latency: 23.64ms
- Misses: none
- Critical misses: none

### api-error-json

- Domain: engineering
- Recall: 0.8
- Matched: 4/5
- Detected: 4
- Latency: 12.18ms
- Misses: USERNAME(noah_w_82)
- Critical misses: none

### bank-support-message

- Domain: finance
- Recall: 1
- Matched: 5/5
- Detected: 5
- Latency: 2.14ms
- Misses: none
- Critical misses: none

### board-minutes

- Domain: governance
- Recall: 0.75
- Matched: 6/8
- Detected: 10
- Latency: 2.09ms
- Misses: PERSON(Margaret Allen), TICKET_REFERENCE(FAC-2026-7712)
- Critical misses: none

### clinical-lab-results

- Domain: healthcare
- Recall: 1
- Matched: 5/5
- Detected: 5
- Latency: 0.61ms
- Misses: none
- Critical misses: none

### crypto-wallet-support

- Domain: finance
- Recall: 1
- Matched: 5/5
- Detected: 5
- Latency: 0.61ms
- Misses: none
- Critical misses: none

### customer-call-summary

- Domain: conversation
- Recall: 0.714
- Matched: 5/7
- Detected: 8
- Latency: 2.44ms
- Misses: PERSON(Jordan), ORG(Rivergate Housing)
- Critical misses: none

### customer-review-redaction

- Domain: support
- Recall: 0.6
- Matched: 3/5
- Detected: 3
- Latency: 0.79ms
- Misses: PERSON(James OBrien), ORG(Cedar Court York)
- Critical misses: none

### developer-secret-rotation

- Domain: engineering
- Recall: 0.833
- Matched: 5/6
- Detected: 8
- Latency: 1.02ms
- Misses: URL(brightedge/api-gateway)
- Critical misses: none

### executive-assistant-note

- Domain: conversation
- Recall: 0.833
- Matched: 5/6
- Detected: 5
- Latency: 0.77ms
- Misses: PERSON(Victoria Lane)
- Critical misses: none

### finance-statement

- Domain: finance
- Recall: 0.875
- Matched: 7/8
- Detected: 8
- Latency: 0.54ms
- Misses: TRANSACTION_ID(PAY-7HJ29K)
- Critical misses: none

### github-actions-env

- Domain: engineering
- Recall: 0.8
- Matched: 4/5
- Detected: 5
- Latency: 0.39ms
- Misses: PERSON(Tessa Long)
- Critical misses: none

### github-pr-comment

- Domain: engineering
- Recall: 0.833
- Matched: 5/6
- Detected: 6
- Latency: 0.45ms
- Misses: FILE_PATH(config/staging.yml)
- Critical misses: none

### hr-onboarding

- Domain: hr
- Recall: 1
- Matched: 7/7
- Detected: 7
- Latency: 0.58ms
- Misses: none
- Critical misses: none

### immigration-cover-note

- Domain: immigration
- Recall: 0.857
- Matched: 6/7
- Detected: 9
- Latency: 0.65ms
- Misses: PERSON(Oliver Grant)
- Critical misses: none

### incident-response-log

- Domain: security
- Recall: 1
- Matched: 8/8
- Detected: 8
- Latency: 0.39ms
- Misses: none
- Critical misses: none

### jira-ticket

- Domain: support
- Recall: 0.714
- Matched: 5/7
- Detected: 6
- Latency: 0.32ms
- Misses: PERSON(Lara Stone), USERNAME(iturner88)
- Critical misses: none

### legal-contract-first-page

- Domain: legal
- Recall: 0.889
- Matched: 8/9
- Detected: 9
- Latency: 0.45ms
- Misses: ORG(Westbridge Procurement Ltd)
- Critical misses: none

### legal-disclosure-index

- Domain: legal
- Recall: 0.833
- Matched: 5/6
- Detected: 5
- Latency: 3.2ms
- Misses: PERSON(Ahmed Farah)
- Critical misses: none

### llm-prompt-cleanup

- Domain: ai-workflow
- Recall: 0.8
- Matched: 4/5
- Detected: 5
- Latency: 0.49ms
- Misses: ORDER_ID(ORD-2026-90018)
- Critical misses: none

### loan-application

- Domain: finance
- Recall: 1
- Matched: 6/6
- Detected: 6
- Latency: 0.51ms
- Misses: none
- Critical misses: none

### nhs-referral-note

- Domain: healthcare
- Recall: 0.857
- Matched: 6/7
- Detected: 6
- Latency: 0.69ms
- Misses: PERSON(Dr Marcus Lee)
- Critical misses: none

### oauth-debug-log

- Domain: engineering
- Recall: 1
- Matched: 5/5
- Detected: 6
- Latency: 0.38ms
- Misses: none
- Critical misses: none

### procurement-email

- Domain: procurement
- Recall: 0.857
- Matched: 6/7
- Detected: 6
- Latency: 0.46ms
- Misses: PERSON(Bethany Clarke)
- Critical misses: none

### property-tenancy

- Domain: property
- Recall: 0.714
- Matched: 5/7
- Detected: 6
- Latency: 0.36ms
- Misses: PERSON(Rachel Owens), PERSON(Karim Haddad)
- Critical misses: none

### research-interview

- Domain: research
- Recall: 0.714
- Matched: 5/7
- Detected: 5
- Latency: 0.45ms
- Misses: EMPLOYEE_ID(P-102), DATE(March 2026)
- Critical misses: none

### sales-slack-thread

- Domain: conversation
- Recall: 0.8
- Matched: 4/5
- Detected: 4
- Latency: 0.64ms
- Misses: PERSON(Eleanor Brooks)
- Critical misses: none

### student-record

- Domain: education
- Recall: 1
- Matched: 6/6
- Detected: 6
- Latency: 0.51ms
- Misses: none
- Critical misses: none

### support-chat-payment

- Domain: support
- Recall: 1
- Matched: 6/6
- Detected: 7
- Latency: 0.44ms
- Misses: none
- Critical misses: none

### travel-itinerary

- Domain: travel
- Recall: 1
- Matched: 6/6
- Detected: 6
- Latency: 0.34ms
- Misses: none
- Critical misses: none
