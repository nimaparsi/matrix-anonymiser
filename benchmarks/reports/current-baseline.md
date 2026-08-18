# SanitiseAI Anonymisation Baseline

Generated: 2026-08-18T18:45:26.616Z

## Summary

- Fixtures: 15
- Expected entities: 103
- Matched expected entities: 91
- Detected entities: 105
- Recall: 0.883
- Precision proxy: 0.867
- F1 proxy: 0.875
- Average latency: 3.56ms
- Critical misses: 0

## Fixture Results

### analytics-payload

- Domain: product
- Recall: 1
- Matched: 7/7
- Detected: 7
- Latency: 24.06ms
- Misses: none
- Critical misses: none

### customer-call-summary

- Domain: conversation
- Recall: 0.714
- Matched: 5/7
- Detected: 8
- Latency: 15.95ms
- Misses: PERSON(Jordan), ORG(Rivergate Housing)
- Critical misses: none

### developer-secret-rotation

- Domain: engineering
- Recall: 0.833
- Matched: 5/6
- Detected: 8
- Latency: 1.18ms
- Misses: URL(brightedge/api-gateway)
- Critical misses: none

### finance-statement

- Domain: finance
- Recall: 0.875
- Matched: 7/8
- Detected: 8
- Latency: 1.96ms
- Misses: TRANSACTION_ID(PAY-7HJ29K)
- Critical misses: none

### github-pr-comment

- Domain: engineering
- Recall: 0.833
- Matched: 5/6
- Detected: 6
- Latency: 0.57ms
- Misses: FILE_PATH(config/staging.yml)
- Critical misses: none

### hr-onboarding

- Domain: hr
- Recall: 1
- Matched: 7/7
- Detected: 7
- Latency: 0.86ms
- Misses: none
- Critical misses: none

### immigration-cover-note

- Domain: immigration
- Recall: 0.857
- Matched: 6/7
- Detected: 9
- Latency: 0.9ms
- Misses: PERSON(Oliver Grant)
- Critical misses: none

### incident-response-log

- Domain: security
- Recall: 1
- Matched: 8/8
- Detected: 8
- Latency: 0.9ms
- Misses: none
- Critical misses: none

### legal-contract-first-page

- Domain: legal
- Recall: 0.889
- Matched: 8/9
- Detected: 9
- Latency: 0.61ms
- Misses: ORG(Westbridge Procurement Ltd)
- Critical misses: none

### nhs-referral-note

- Domain: healthcare
- Recall: 0.857
- Matched: 6/7
- Detected: 6
- Latency: 0.51ms
- Misses: PERSON(Dr Marcus Lee)
- Critical misses: none

### procurement-email

- Domain: procurement
- Recall: 0.857
- Matched: 6/7
- Detected: 6
- Latency: 0.55ms
- Misses: PERSON(Bethany Clarke)
- Critical misses: none

### property-tenancy

- Domain: property
- Recall: 0.714
- Matched: 5/7
- Detected: 6
- Latency: 0.38ms
- Misses: PERSON(Rachel Owens), PERSON(Karim Haddad)
- Critical misses: none

### sales-slack-thread

- Domain: conversation
- Recall: 0.8
- Matched: 4/5
- Detected: 4
- Latency: 0.59ms
- Misses: PERSON(Eleanor Brooks)
- Critical misses: none

### support-chat-payment

- Domain: support
- Recall: 1
- Matched: 6/6
- Detected: 7
- Latency: 4.08ms
- Misses: none
- Critical misses: none

### travel-itinerary

- Domain: travel
- Recall: 1
- Matched: 6/6
- Detected: 6
- Latency: 0.36ms
- Misses: none
- Critical misses: none
