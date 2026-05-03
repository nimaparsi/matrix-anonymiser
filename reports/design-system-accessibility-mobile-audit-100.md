# SanitiseAI Improvement Audit

This audit captures 100 concrete improvements for a stronger version of the SanitiseAI web experience.

## Design System

1. Consolidate page widths to a shared 1180px content rhythm.
2. Use smaller, consistent card radii across product surfaces.
3. Reserve pill radii for real status chips, not broad containers.
4. Reduce heavy shadows on panels to improve product-tool credibility.
5. Remove hover lift from global buttons for calmer interaction.
6. Standardise primary button labels around direct actions.
7. Make secondary buttons supportive, not competing CTAs.
8. Use one accent blue scale instead of multiple saturated blues.
9. Keep green reserved for success or privacy state.
10. Use neutral surfaces for repeated cards.
11. Keep dark output preview visually distinct from input.
12. Replace oversized brand header treatment with a tighter product header.
13. Keep icon sizing consistent in page headers.
14. Use shared focus ring tokens across links, buttons, fields, and textareas.
15. Add reduced-motion handling for animations and transitions.
16. Stop scaling buttons on hover to prevent layout jitter.
17. Use stable min heights for workspace panels.
18. Improve scrollbar styling without overpowering content.
19. Align page hero typography with tool UI hierarchy.
20. Make final CTA sections calmer and less marketing-heavy.

## Consistency

21. Rename “App” navigation to “Sanitiser”.
22. Change “Get Started” to “Try demo” where it loads an example.
23. Use “Open sanitiser” consistently across pages.
24. Use “Load example” for demo-starting routes.
25. Use British spelling: “sanitise”, “anonymise”, “organisation”.
26. Remove mixed “sanitized/sanitised” wording.
27. Replace “Input Terminal” with “Source text”.
28. Replace “Sanitised Preview” with “Sanitised output”.
29. Lowercase legal and product headings where sentence case reads better.
30. Make “Detection profile” casing consistent.
31. Align integrations page with current capabilities.
32. Remove dashboard/team-management copy where the app does not expose it.
33. Remove unsupported “enterprise-grade proxy” claims.
34. Remove unsupported “Slack Enterprise active” claims.
35. Replace roadmap dates with broader planned states.
36. Keep privacy and security pages aligned on data lifecycle language.
37. Use the same CTA tone in privacy, security, contact, and integrations.
38. Keep route destination behavior reflected in link labels.
39. Use common labels for HTTPS processing.
40. Make footer and header brand scale less divergent.

## Brand And Trust

41. Replace “world’s most advanced” with concrete product value.
42. Remove “without compromise” style claims.
43. Replace “Transparent Fortress” with plain security language.
44. Replace “100% Stateless” with “No raw-text storage”.
45. Replace “99.9% reliability” claims with practical controls.
46. Avoid “AES-256 transport” unless independently verified in docs.
47. Clarify raw input is sent to the API over HTTPS.
48. Keep claims tied to implemented behavior.
49. Make the homepage about the real workflow, not a generic platform pitch.
50. Present supported use cases without invented user-count social proof.
51. Keep security visuals secondary to data-flow explanation.
52. Use less theatrical language in compliance CTAs.
53. Replace “Talk to Security Experts” with “Contact us”.
54. Avoid “free trial” where no trial flow exists.
55. Avoid “enterprise sales” where contact form is the available path.
56. Explain structured placeholders as the core product value.
57. Make custom rules a clear differentiator.
58. Position integrations as workflow targets instead of live claims.
59. Keep privacy language transparent about API processing.
60. Make support copy describe real help topics.

## Text Quality

61. Shorten hero copy for faster scanning.
62. Use active, direct verbs in CTAs.
63. Remove duplicated privacy claims across the same viewport.
64. Replace “No Barriers” with “No account wall”.
65. Replace vague “backend privacy engine” with context-preserving detection.
66. Make feature cards explain outcomes, not internal slogans.
67. Clarify upload support in the tool header.
68. Make stale-output warning actionable.
69. Make contact form helper text specific.
70. Replace generic ecosystem language with practical workflow language.
71. Reduce title-case overuse in page headings.
72. Use “sensitive text” consistently as the product object.
73. Tighten microcopy around custom rules.
74. Avoid speculative compliance wording.
75. Keep roadmap copy separate from live capability copy.
76. Make legal page copy scan as product terms, not marketing.
77. Keep security lifecycle names clear and sequential.
78. Use “structured output” where placeholders preserve meaning.
79. Make example workflows industry-specific but not inflated.
80. Remove redundant “privacy-first” claims when nearby text explains behavior.

## Accessibility And Mobile

81. Keep primary navigation accessible on mobile instead of hiding it.
82. Add horizontal overflow handling for compact mobile navigation.
83. Preserve a visible focus state for all interactive controls.
84. Add an accessible label to the sanitiser textarea.
85. Add pressed state semantics to mode buttons.
86. Add pressed state semantics to detector buttons.
87. Add pressed state semantics to the reverse-pronoun control.
88. Add live-region semantics to sanitised output.
89. Add status semantics to result summaries.
90. Use larger tap targets in the mobile header.
91. Stack tool actions on narrow screens.
92. Give mobile textareas enough height for real input.
93. Prevent mobile output buttons from squeezing into unreadable columns.
94. Avoid text overflowing button labels on smaller screens.
95. Keep detector chips as full-width rows on very small screens.
96. Keep the detection profile readable when stacked.
97. Improve focus handling inside the textarea without removing the ring.
98. Respect reduced-motion user preferences.
99. Remove transform-based hover motion that can trigger vestibular discomfort.
100. Keep mobile page gutters tighter but predictable.
