<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE || ''
const IS_DEV = Boolean(import.meta.env.DEV)
const FREE_MAX_CHARS = 5000
const PRO_MAX_CHARS = 50000
const MAX_UPLOAD_BYTES = 8 * 1024 * 1024
const TRY_EXAMPLE_RESET_MS = 10000
const LIVE_PREVIEW_DEBOUNCE_MS = 320
const DEMO_TEXTS = [
  `Referral Letter
Date: 12 March 2026

To whom it may concern,

I am referring Ms Anna Carter (DOB: 20 March 1992) for an eligibility review.
Current address: 14 Willow Lane, Brighton BN1 4AB.
Primary contact: anna.carter@example.com | +44 7700 900123.
Employer: Green Horizon Research Ltd.

Please send correspondence to the above address and copy me at daniel.hughes@ecologiclab.org.

Kind regards,
Daniel Hughes
Senior Analyst`,
  `Client Intake Form
Case ID: C-UK-2026-00419
Submitted: 13/03/2026

Applicant Name: Sofia Martinez
Nationality: Spanish
Email: sofia.martinez@urbangrowth.co.uk
Phone: +44 7700 903876
Home Address: 55 Orchard Street, Manchester M1 2WD
Sponsor Organisation: Urban Growth Initiative

Emergency Contact:
Name: Ravi Patel
Phone: +44 7700 905112
Email: ravi.patel@futureenergy.org`,
  `Meeting Minutes - Compliance Review
Date: 14 March 2026
Location: Ecologic Lab, 28 Riverside Road, Cambridge CB1 3QA

Attendees:
- Anna Carter (Green Horizon Research) - anna.carter@example.com
- Daniel Hughes (Ecologic Lab) - daniel.hughes@ecologiclab.org
- Emily Foster (Coastal Lab) - emily.foster@coastallab.net

Actions:
1. Daniel to submit revised documentation by 18 March 2026.
2. Emily to send verification logs from +44 7700 907331 contact line.
3. Anna to circulate draft to external reviewers.`,
  `Support Ticket Export
Ticket: TKT-882-431
Order: ORD-UK-77A
Raised by: Brian Cole <brian.cole@coastallab.net>
Phone on file: 07700 912300
Service address: 91 King Street, Glasgow G1 2FF

Issue summary:
Customer reported duplicate billing entries linked to invoice #44392 and transaction TXN-98A122.
Requested callback window: 09:00-11:00 UK time.`,
  `Employment Verification Document
Employee: Aisha Rahman
Employee ID: HR-11892
Role: Product Designer
Company: Northfield Systems Ltd
Work Address: 12 Elm Road, Manchester M1 2AB
Personal Email: aisha.rahman@northfield.io
Company Email: a.rahman@northfieldsystems.com
Contact Number: +44 7700 900245
Manager: Sarah Khan

This letter confirms current employment status as of 15 March 2026.`,
  `Incident Handover Note
Incident time: 09:42 on 14/03/2026
Reporter: Ravi Patel
Reporter Email: ravi.patel@futureenergy.org
Reporter Phone: +44 7700 905112

Observed IPs: 203.0.113.27, 198.51.100.18
Impacted accounts: @ravi_ops, @northfield-admin
File path in error trace: /srv/apps/finance/payments/exports/march/recon.csv

Escalation owner: Emily Foster, Coastal Lab, 3 Harbour View Road, Southampton SO14 2RT.`,
  `Travel Reimbursement Claim
Claimant: Maria Rossi
Email: maria.rossi@harborlegal.co.uk
Phone: +44 7700 901245

Journey details:
- Outbound: London to Leeds on 13 March 2026 (Booking Reference: BK-90812)
- Return: Leeds to London on 14 March 2026 (Ticket Reference: TKT-991-220)

Billing Address: 220 Orchard Drive, Birmingham B1 1AA
Invoice Number: INV-889120
Card used: Visa ending 4242`,
  `Project Coordination Memo
Project: Regional Sustainability Pilot
Prepared by: Anna Carter
Date: 15 March 2026

Contacts
- Anna Carter, Green Horizon Research, anna.carter@example.com, +44 7700 900123
- Daniel Hughes, Ecologic Lab, daniel.hughes@ecologiclab.org, +44 7700 901245
- Sofia Martinez, Urban Growth Initiative, sofia.martinez@urbangrowth.co.uk, +44 7700 903876
- Ravi Patel, Future Energy Alliance, ravi.patel@futureenergy.org, +44 7700 905112

Addresses referenced:
- 14 Willow Lane, Brighton BN1 4AB
- 28 Riverside Road, Cambridge CB1 3QA
- 55 Orchard Street, Manchester M1 2WD`,
  `ChatGPT Conversation Export
User:
I'm preparing a case summary for external review. Please rewrite it clearly:
"My name is Daniel Hughes, I live at 28 Riverside Road, Cambridge CB1 3QA. You can reach me at daniel.hughes@ecologiclab.org or +44 7700 901245. My colleague Anna Carter from Green Horizon Research will join the meeting on 18 March 2026."

Assistant:
Sure. Here's a cleaner draft:
"Daniel Hughes confirmed attendance for 18 March 2026 and will be joined by Anna Carter of Green Horizon Research. Contact details are available in the internal case file."`,
  `Chat Transcript
User:
Can you draft an email to my client?
Client details:
Name: Sofia Martinez
Email: sofia.martinez@urbangrowth.co.uk
Phone: +44 7700 903876
Address: 55 Orchard Street, Manchester M1 2WD
Company: Urban Growth Initiative

Assistant:
Of course. Draft below:
"Hi Sofia, following our call, I have attached the revised timeline and budget assumptions for Urban Growth Initiative. Please confirm if 14 March 2026 still works for final sign-off."`,
  `AI Prompt Thread
User:
Summarise this incident report for leadership:
Reporter: Ravi Patel
Email: ravi.patel@futureenergy.org
Phone: +44 7700 905112
Escalation owner: Emily Foster, Coastal Lab
Address: 3 Harbour View Road, Southampton SO14 2RT
Ticket: TKT-991-220

Assistant:
Summary:
"An incident was reported and escalated to the designated owner. Investigation is in progress under ticket TKT-991-220, with follow-up communication coordinated through internal channels."`,
] as const
const TRY_EXAMPLE_LABELS = [
  'Try example',
  'Another?',
  'One more?',
  'Keep going?',
  'Try a different one?',
  'Show another sample?',
  'Next example?',
  'More?',
] as const
const STATS_KEY = 'matrix_global_stats_v1'
const TEXT_EXTENSIONS = new Set(['txt', 'md', 'csv', 'json', 'log'])
const ENTITY_PREFS_KEY = 'matrix_anonymiser_entity_types_v1'
const PRO_UI_HINT_KEY = 'matrix_pro_ui_hint_v1'
const DEFAULT_ENTITY_KEYS = ['PERSON', 'EMAIL', 'PHONE', 'ADDRESS', 'ORG', 'DATE', 'URL', 'COMPANY_REGISTRATION_NUMBER', 'INVOICE_NUMBER', 'EMPLOYEE_ID', 'BOOKING_REFERENCE', 'TICKET_REFERENCE', 'ORDER_ID', 'TRANSACTION_ID']
let pdfRuntimePromise = null

function apiUrl(path) {
  const base = API_BASE.replace(/\/$/, '')
  return base ? `${base}/api/${path}` : `/api/${path}`
}

const text = ref('')
const loading = ref(false)
const error = ref('')
const result = ref(null)
const limitState = ref(null)
const emojiTags = ref(false)
const highlightCensored = ref(true)
const reversePronouns = ref(false)
const redactionMode = ref(false)
const resultSection = ref(null)
const inputArea = ref(null)
const inputHighlighted = ref(false)
const fileBusy = ref(false)
const uploadStatus = ref('')
const loadedFileName = ref('')
const dropActive = ref(false)
const copyFeedback = ref('Copy result')
const protectAllSensitive = ref(true)
const submitGlow = ref(false)
const devResetMessage = ref('')
const customCursorEnabled = ref(false)
const customCursorVisible = ref(false)
const customCursorX = ref(0)
const customCursorY = ref(0)
const tier = ref<'free' | 'pro'>('free')
const lastDemoIndex = ref<number>(-1)
const tryExampleClickCount = ref(0)
const demoSwapActive = ref(false)
const showEntityDetail = ref(false)
const showProCelebration = ref(false)
const livePreviewCounts = ref<Record<string, number>>({})
let tryExampleResetTimer: ReturnType<typeof window.setTimeout> | null = null
let proCelebrationTimer: ReturnType<typeof window.setTimeout> | null = null
let livePreviewDebounceTimer: ReturnType<typeof window.setTimeout> | null = null
let livePreviewController: AbortController | null = null
const stats = ref({
  charactersProcessed: 0,
  entitiesRemoved: 0,
  requestsProcessed: 0,
})

const entityGroups = [
  {
    key: 'IDENTITY',
    label: 'Identity',
    items: [
      { key: 'PERSON', label: 'People' },
      { key: 'ORG', label: 'Organisation' },
      { key: 'USERNAME', label: 'Username' },
    ],
  },
  {
    key: 'CONTACT',
    label: 'Contact',
    items: [
      { key: 'EMAIL', label: 'Email' },
      { key: 'PHONE', label: 'Phone' },
      { key: 'ADDRESS', label: 'Address' },
    ],
  },
  {
    key: 'SECURITY',
    label: 'Security',
    items: [
      { key: 'API_KEY', label: 'API key' },
      { key: 'PRIVATE_KEY', label: 'Private key' },
      { key: 'IP_ADDRESS', label: 'IP address' },
    ],
  },
  {
    key: 'FINANCIAL',
    label: 'Financial',
    items: [
      { key: 'CREDIT_CARD', label: 'Credit card' },
      { key: 'BANK_ACCOUNT', label: 'Bank account' },
      { key: 'GOVERNMENT_ID', label: 'Government ID' },
    ],
  },
  {
    key: 'TECHNICAL',
    label: 'Technical',
    items: [
      { key: 'URL', label: 'URL' },
      { key: 'FILE_PATH', label: 'File path' },
      { key: 'COORDINATE', label: 'Coordinate' },
    ],
  },
  {
    key: 'METADATA',
    label: 'Metadata',
    items: [
      { key: 'DATE', label: 'Date' },
      { key: 'COMPANY_REGISTRATION_NUMBER', label: 'Company reg number' },
      { key: 'INVOICE_NUMBER', label: 'Invoice number' },
      { key: 'EMPLOYEE_ID', label: 'Employee ID' },
      { key: 'BOOKING_REFERENCE', label: 'Booking reference' },
      { key: 'TICKET_REFERENCE', label: 'Ticket reference' },
      { key: 'ORDER_ID', label: 'Order ID' },
      { key: 'TRANSACTION_ID', label: 'Transaction ID' },
    ],
  },
]
const allEntityKeys = entityGroups.flatMap((group) => group.items.map((item) => item.key))
const enabled = ref(new Set(DEFAULT_ENTITY_KEYS))

const selectedTypes = computed(() => Array.from(enabled.value))
const activeMaxChars = computed(() => (tier.value === 'pro' ? PRO_MAX_CHARS : FREE_MAX_CHARS))
const charCountLabel = computed(() => `${text.value.length.toLocaleString()} / ${activeMaxChars.value.toLocaleString()}`)
const charLimitHint = computed(() =>
  tier.value === 'pro'
    ? 'Supports up to 50,000 characters per request'
    : 'Supports up to 5,000 characters per request (50,000 on Pro)'
)
const activeEntityTypes = computed(() => (protectAllSensitive.value ? allEntityKeys : selectedTypes.value))
const canSubmit = computed(() => text.value.trim().length > 0 && !loading.value && activeEntityTypes.value.length > 0)
const resultWarning = computed(() => result.value?.warning || '')
const resultTotalEntities = computed<number>(() => {
  const counts = (result.value?.counts || {}) as Record<string, number | string | null | undefined>
  let total = 0
  for (const value of Object.values(counts)) {
    total += Number(value ?? 0)
  }
  return total
})

const summaryLine = computed(() => {
  if (!result.value) return ''
  const total = resultTotalEntities.value
  const processing = Number(result.value?.meta?.processing_ms || 0)
  const timeText = Number.isFinite(processing) && processing > 0 ? `${processing}ms` : 'n/a'
  return `${total} ${total === 1 ? 'entity' : 'entities'} detected · Processing time: ${timeText}`
})

const successEntityDetails = computed(() => {
  const counts = (result.value?.counts || {}) as Record<string, number | string | null | undefined>
  const labelMap: Record<string, string> = {
    PERSON: 'person',
    EMAIL: 'email',
    PHONE: 'phone',
    ADDRESS: 'address',
    LOCATION: 'location',
    ORG: 'organisation',
    DATE: 'date',
    URL: 'url',
    API_KEY: 'api key',
    PRIVATE_KEY: 'private key',
    GOVERNMENT_ID: 'government ID',
    BANK_ACCOUNT: 'bank account',
    CREDIT_CARD: 'credit card',
    IP_ADDRESS: 'ip address',
    USERNAME: 'username',
    COORDINATE: 'coordinate',
    FILE_PATH: 'file path',
    COMPANY_REGISTRATION_NUMBER: 'company reg number',
    INVOICE_NUMBER: 'invoice number',
    EMPLOYEE_ID: 'employee ID',
    BOOKING_REFERENCE: 'booking reference',
    TICKET_REFERENCE: 'ticket reference',
    ORDER_ID: 'order ID',
    TRANSACTION_ID: 'transaction ID',
  }

  return Object.entries(counts)
    .map(([key, value]) => ({ key, count: Number(value ?? 0) }))
    .filter((item) => item.count > 0)
    .sort((a, b) => b.count - a.count)
    .map((item) => {
      const singular = labelMap[item.key] || item.key.toLowerCase().replace(/_/g, ' ')
      const plural = singular.endsWith('s') ? singular : `${singular}s`
      return {
        key: item.key,
        text: `${item.count} ${item.count === 1 ? singular : plural}`,
      }
    })
})

const statsCharactersLabel = computed(() => stats.value.charactersProcessed.toLocaleString())
const statsEntitiesLabel = computed(() => stats.value.entitiesRemoved.toLocaleString())
const statsRequestsLabel = computed(() => stats.value.requestsProcessed.toLocaleString())
const hasLocalStats = computed(() =>
  stats.value.charactersProcessed > 0 ||
  stats.value.entitiesRemoved > 0 ||
  stats.value.requestsProcessed > 0
)
const tryExampleLabel = computed(() => {
  if (tryExampleClickCount.value === 0) {
    return TRY_EXAMPLE_LABELS[0]
  }
  const rotating = TRY_EXAMPLE_LABELS.slice(1)
  return rotating[(tryExampleClickCount.value - 1) % rotating.length]
})
const customCursorStyle = computed(() => ({
  transform: `translate3d(${customCursorX.value - 20}px, ${customCursorY.value - 20}px, 0)`,
}))
const isProTier = computed(() => tier.value === 'pro')
const LIVE_PREVIEW_LABELS: Record<string, string> = {
  PERSON: 'Person',
  EMAIL: 'Email',
  PHONE: 'Phone',
  ADDRESS: 'Address',
  ORG: 'Organisation',
  DATE: 'Date',
  URL: 'URL',
  API_KEY: 'API key',
  PRIVATE_KEY: 'Private key',
  GOVERNMENT_ID: 'Government ID',
  BANK_ACCOUNT: 'Bank account',
  CREDIT_CARD: 'Credit card',
  IP_ADDRESS: 'IP address',
  USERNAME: 'Username',
  COORDINATE: 'Coordinate',
  FILE_PATH: 'File path',
  COMPANY_REGISTRATION_NUMBER: 'Company reg number',
  INVOICE_NUMBER: 'Invoice number',
  EMPLOYEE_ID: 'Employee ID',
  BOOKING_REFERENCE: 'Booking reference',
  TICKET_REFERENCE: 'Ticket reference',
  ORDER_ID: 'Order ID',
  TRANSACTION_ID: 'Transaction ID',
}

const liveDetectedCounts = computed(() => livePreviewCounts.value)
const liveDetectedCount = computed(() => Object.values(liveDetectedCounts.value).reduce((sum, count) => sum + count, 0))
const liveDetectedLabel = computed(() => {
  const count = liveDetectedCount.value
  if (!text.value.trim()) return ''
  return count > 0
    ? `Sensitive entities detected: ${count}`
    : 'No obvious sensitive entities detected yet'
})
const liveDetectedTypesLabel = computed(() => {
  const entries = Object.entries(liveDetectedCounts.value)
    .filter(([, count]) => count > 0)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4)
    .map(([type]) => LIVE_PREVIEW_LABELS[type] || type)

  return entries.join(' · ')
})
const submitLabel = computed(() => {
  if (loading.value) return 'Processing...'
  const count = liveDetectedCount.value
  if (count > 0) {
    return `Sanitise ${count} ${count === 1 ? 'item' : 'items'}`
  }
  return 'Sanitise Text'
})

function clearLivePreviewTimers() {
  if (livePreviewDebounceTimer) {
    window.clearTimeout(livePreviewDebounceTimer)
    livePreviewDebounceTimer = null
  }
  if (livePreviewController) {
    livePreviewController.abort()
    livePreviewController = null
  }
}

async function fetchLivePreviewNow() {
  const previewText = String(text.value || '')
  if (!previewText.trim()) {
    livePreviewCounts.value = {}
    return
  }

  if (livePreviewController) {
    livePreviewController.abort()
  }

  const controller = new AbortController()
  livePreviewController = controller

  try {
    const res = await fetch(apiUrl('anonymize-preview'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      signal: controller.signal,
      body: JSON.stringify({
        text: previewText,
        entity_types: activeEntityTypes.value,
      }),
    })

    if (!res.ok) {
      livePreviewCounts.value = {}
      return
    }

    const data = await res.json().catch(() => ({}))
    const countsObject = (data?.counts || {}) as Record<string, unknown>
    const normalized: Record<string, number> = {}
    for (const [key, value] of Object.entries(countsObject)) {
      const num = Number(value ?? 0)
      if (Number.isFinite(num) && num > 0) {
        normalized[key] = num
      }
    }
    livePreviewCounts.value = normalized
  } catch (_) {
    if (!controller.signal.aborted) {
      livePreviewCounts.value = {}
    }
  } finally {
    if (livePreviewController === controller) {
      livePreviewController = null
    }
  }
}

function queueLivePreview() {
  clearLivePreviewTimers()
  if (!text.value.trim()) {
    livePreviewCounts.value = {}
    return
  }

  livePreviewDebounceTimer = window.setTimeout(() => {
    livePreviewDebounceTimer = null
    void fetchLivePreviewNow()
  }, LIVE_PREVIEW_DEBOUNCE_MS)
}

function canonicalizeBackendTokens(rawText) {
  const labelMap = {
    PERSON: 'Person',
    EMAIL: 'Email',
    PHONE: 'Phone',
    ADDRESS: 'Location',
    LOCATION: 'Location',
    ORG: 'Organisation',
    ORGANISATION: 'Organisation',
    ORGANIZATION: 'Organisation',
    DATE: 'Date',
    URL: 'Web Address',
    WEB_ADDRESS: 'Web Address',
    API_KEY: 'API Key',
    PRIVATE_KEY: 'Private Key',
    GOVERNMENT_ID: 'Government ID',
    BANK_ACCOUNT: 'Bank Account',
    CREDIT_CARD: 'Credit Card',
    IP_ADDRESS: 'IP Address',
    USERNAME: 'Username',
    COORDINATE: 'Coordinate',
    FILE_PATH: 'File Path',
    COMPANY_REGISTRATION_NUMBER: 'Company Registration Number',
    INVOICE_NUMBER: 'Invoice Number',
    EMPLOYEE_ID: 'Employee ID',
    BOOKING_REFERENCE: 'Booking Reference',
    TICKET_REFERENCE: 'Ticket Reference',
    ORDER_ID: 'Order ID',
    TRANSACTION_ID: 'Transaction ID',
  }

  return String(rawText || '').replace(/\[([A-Z]+(?:_[A-Z]+)*)(?:_(\d+))?\]/g, (_, rawLabel: string, rawIndex: string | undefined) => {
    const label = labelMap[rawLabel] || rawLabel.replace(/_/g, ' ')
    if (rawIndex) {
      return `[${label} ${rawIndex}]`
    }
    return `[${label}]`
  })
}

function countEntitiesFromCounts(counts: Record<string, number | string | null | undefined> | null | undefined): number {
  let total = 0
  for (const value of Object.values(counts || {})) {
    total += Number(value ?? 0)
  }
  return total
}

function saveStats() {
  try {
    window.localStorage.setItem(STATS_KEY, JSON.stringify(stats.value))
  } catch (_) {
    // Ignore stats storage failures (private mode/quota).
  }
}

function applyTier(nextTier: 'free' | 'pro') {
  tier.value = nextTier
  try {
    if (nextTier === 'pro') {
      window.localStorage.setItem(PRO_UI_HINT_KEY, '1')
    } else {
      window.localStorage.removeItem(PRO_UI_HINT_KEY)
    }
  } catch (_) {
    // Ignore storage failures.
  }
}

function triggerProCelebration() {
  showProCelebration.value = true
  if (proCelebrationTimer) {
    window.clearTimeout(proCelebrationTimer)
  }
  proCelebrationTimer = window.setTimeout(() => {
    showProCelebration.value = false
    proCelebrationTimer = null
  }, 2600)
}

async function loadBillingTier() {
  try {
    const res = await fetch(apiUrl('billing/status'), {
      method: 'GET',
      credentials: 'include',
    })
    if (!res.ok) return
    const data = await res.json().catch(() => ({}))
    const serverTier = data?.tier === 'pro' ? 'pro' : 'free'
    if (serverTier === 'free') {
      try {
        if (window.localStorage.getItem(PRO_UI_HINT_KEY) === '1') {
          return
        }
      } catch (_) {
        // Ignore local storage read failures.
      }
    }
    applyTier(serverTier)
  } catch (_) {
    // Ignore billing status failures.
  }
}

function handleCursorMove(event: MouseEvent) {
  customCursorX.value = event.clientX
  customCursorY.value = event.clientY
  customCursorVisible.value = true
}

function handleCursorLeave() {
  customCursorVisible.value = false
}

function clearTryExampleResetTimer() {
  if (tryExampleResetTimer) {
    window.clearTimeout(tryExampleResetTimer)
    tryExampleResetTimer = null
  }
}

function scheduleTryExampleLabelReset() {
  if (tryExampleClickCount.value === 0) return
  clearTryExampleResetTimer()
  tryExampleResetTimer = window.setTimeout(() => {
    tryExampleClickCount.value = 0
    tryExampleResetTimer = null
  }, TRY_EXAMPLE_RESET_MS)
}
const displayAnonymizedText = computed(() => {
  const raw = canonicalizeBackendTokens(result.value?.anonymized_text || '')
  if (emojiTags.value) {
    return raw
      .replace(/\[(?:👤\s*)?Person\s+(\d+)\]/g, '👤 Person $1')
      .replace(/\[(?:📧\s*)?Email\s+(\d+)\]/g, '📧 Email $1')
      .replace(/\[(?:🔑\s*)?API Key\s+(\d+)\]/g, '🔑 API Key $1')
      .replace(/\[(?:🔐\s*)?Private Key\s+(\d+)\]/g, '🔐 Private Key $1')
      .replace(/\[(?:🪪\s*)?Government ID\s+(\d+)\]/g, '🪪 Government ID $1')
      .replace(/\[(?:🏦\s*)?Bank Account\s+(\d+)\]/g, '🏦 Bank Account $1')
      .replace(/\[(?:💳\s*)?Credit Card\s+(\d+)\]/g, '💳 Credit Card $1')
      .replace(/\[(?:📞\s*)?Phone\s+(\d+)\]/g, '📞 Phone $1')
      .replace(/\[(?:🌐\s*)?IP Address\s+(\d+)\]/g, '🌐 IP Address $1')
      .replace(/\[(?:🔗\s*)?Web Address\s+(\d+)\]/g, '🔗 Web Address $1')
      .replace(/\[(?:📍\s*)?Location\s+(\d+)\]/g, '📍 Location $1')
      .replace(/\[(?:🏢\s*)?Organisation\s+(\d+)\]/g, '🏢 Organisation $1')
      .replace(/\[(?:📅\s*)?Date\s+(\d+)\]/g, '📅 Date $1')
      .replace(/\[(?:🏷\s*)?Username\s+(\d+)\]/g, '🏷 Username $1')
      .replace(/\[(?:🧭\s*)?Coordinate\s+(\d+)\]/g, '🧭 Coordinate $1')
      .replace(/\[(?:🗂\s*)?File Path\s+(\d+)\]/g, '🗂 File Path $1')
      .replace(/\b(👤|📧|🔑|🔐|🪪|🏦|💳|📞|🌐|🔗|📍|🏢|📅|🏷|🧭|🗂)\s+(Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\2\s+(\d+)\b/g, '$1 $2 $3')
  }
  return raw
    .replace(/\[(?:👤\s*)?Person\s+(\d+)\]/g, 'Person $1')
    .replace(/\[(?:📧\s*)?Email\s+(\d+)\]/g, 'Email $1')
    .replace(/\[(?:🔑\s*)?API Key\s+(\d+)\]/g, 'API Key $1')
    .replace(/\[(?:🔐\s*)?Private Key\s+(\d+)\]/g, 'Private Key $1')
    .replace(/\[(?:🪪\s*)?Government ID\s+(\d+)\]/g, 'Government ID $1')
    .replace(/\[(?:🏦\s*)?Bank Account\s+(\d+)\]/g, 'Bank Account $1')
    .replace(/\[(?:💳\s*)?Credit Card\s+(\d+)\]/g, 'Credit Card $1')
    .replace(/\[(?:📞\s*)?Phone\s+(\d+)\]/g, 'Phone $1')
    .replace(/\[(?:🌐\s*)?IP Address\s+(\d+)\]/g, 'IP Address $1')
    .replace(/\[(?:🔗\s*)?Web Address\s+(\d+)\]/g, 'Web Address $1')
    .replace(/\[(?:📍\s*)?Location\s+(\d+)\]/g, 'Location $1')
    .replace(/\[(?:🏢\s*)?Organisation\s+(\d+)\]/g, 'Organisation $1')
    .replace(/\[(?:📅\s*)?Date\s+(\d+)\]/g, 'Date $1')
    .replace(/\[(?:🏷\s*)?Username\s+(\d+)\]/g, 'Username $1')
    .replace(/\[(?:🧭\s*)?Coordinate\s+(\d+)\]/g, 'Coordinate $1')
    .replace(/\[(?:🗂\s*)?File Path\s+(\d+)\]/g, 'File Path $1')
    .replace(/\b(Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\1\s+(\d+)\b/g, '$1 $2')
})

const outputForDisplay = computed(() => {
  const base = displayAnonymizedText.value
  if (!redactionMode.value) return base
  return applyRedactionMode(base)
})

const tokenTooltipMap = computed(() => {
  const map = new Map()
  const entities = Array.isArray(result.value?.entities) ? result.value.entities : []
  const source = text.value

  for (const entity of entities) {
    const original = source.slice(Number(entity.start || 0), Number(entity.end || 0)).trim()
    const replacement = String(entity.replacement || '').trim()
    if (!original || !replacement) continue

    const tooltip = map.get('__raw__') || new Map()
    for (const key of tokenKeysFromReplacement(replacement)) {
      const values = tooltip.get(key) || new Set()
      values.add(original)
      tooltip.set(key, values)
    }
    map.set('__raw__', tooltip)
  }

  const raw = map.get('__raw__')
  if (!raw) return new Map()

  const flattened = new Map()
  for (const [key, values] of raw.entries()) {
    flattened.set(key, Array.from(values).slice(0, 3).join(' / '))
  }
  return flattened
})

const anonymizedRenderHtml = computed(() => {
  const escaped = escapeHtml(outputForDisplay.value)
  const tokenPattern = /(\[[^\]\n]{2,80}\]|\b(?:Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\d+\b|(?:👤|📧|🔑|🔐|🪪|🏦|💳|📞|🌐|🔗|📍|🏢|📅|🏷|🧭|🗂)\s+(?:Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\d+\b|\[REDACTED\])/g

  if (!highlightCensored.value) {
    return escaped
  }

  return escaped.replace(tokenPattern, (token) => {
    const key = normalizeTokenKey(token)
    const tooltip = redactionMode.value ? '' : tokenTooltipMap.value.get(key) || ''
    const tooltipAttr = tooltip ? ` title="${escapeHtml(`Original: ${tooltip}`)}"` : ''
    return `<mark class="sanitise-app__token-highlight"${tooltipAttr}>${token}</mark>`
  })
})

function normalizeTokenKey(token) {
  const cleaned = String(token || '')
    .replace(/\[|\]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/^(👤|📧|🔑|🔐|🪪|🏦|💳|📞|🌐|🔗|📍|🏢|📅|🏷|🧭|🗂)\s*/, '')
  return cleaned.toLowerCase()
}

function tokenKeysFromReplacement(replacement) {
  const forms = new Set()
  const raw = String(replacement || '').trim()
  const clean = raw.replace(/^\[|\]$/g, '').trim()
  const plain = clean.replace(/^(👤|📧|🔑|🔐|🪪|🏦|💳|📞|🌐|🔗|📍|🏢|📅|🏷|🧭|🗂)\s*/, '')

  const addForm = (value) => {
    const key = normalizeTokenKey(value)
    if (key) forms.add(key)
  }

  addForm(raw)
  addForm(clean)
  addForm(plain)
  addForm(`[${plain}]`)

  const parsed = plain.match(/^(Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+(\d+)$/i)
  if (parsed) {
    const label = parsed[1]
    const number = parsed[2]
    const emojiByLabel = {
      person: '👤',
      email: '📧',
      'api key': '🔑',
      'private key': '🔐',
      'government id': '🪪',
      'bank account': '🏦',
      'credit card': '💳',
      phone: '📞',
      'ip address': '🌐',
      'web address': '🔗',
      location: '📍',
      organisation: '🏢',
      date: '📅',
      username: '🏷',
      coordinate: '🧭',
      'file path': '🗂',
    }
    const emoji = emojiByLabel[label.toLowerCase()]
    if (emoji) {
      addForm(`${emoji} ${label} ${number}`)
      addForm(`[${emoji} ${label} ${number}]`)
    }
  }

  return Array.from(forms)
}

function applyRedactionMode(value) {
  return canonicalizeBackendTokens(String(value || '')).replace(
    /(\[[^\]\n]{2,80}\]|\b(?:Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\d+\b|(?:👤|📧|🔑|🔐|🪪|🏦|💳|📞|🌐|🔗|📍|🏢|📅|🏷|🧭|🗂)\s+(?:Person|Email|API Key|Private Key|Government ID|Bank Account|Credit Card|Phone|IP Address|Web Address|Location|Organisation|Date|Username|Coordinate|File Path)\s+\d+\b)/g,
    '[REDACTED]',
  )
}

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\"/g, '&quot;')
    .replace(/'/g, '&#39;')
}
function toggleType(key) {
  const current = new Set(enabled.value)
  if (protectAllSensitive.value) {
    protectAllSensitive.value = false
    allEntityKeys.forEach((typeKey) => current.add(typeKey))
  }
  if (current.has(key)) {
    if (current.size === 1) return
    current.delete(key)
  } else {
    current.add(key)
  }
  enabled.value = current
}

function toggleProtectAllSensitive() {
  protectAllSensitive.value = !protectAllSensitive.value
}

function clearInputText() {
  text.value = ''
  uploadStatus.value = ''
  loadedFileName.value = ''
  error.value = ''
  result.value = null
  window.requestAnimationFrame(() => {
    inputArea.value?.focus({ preventScroll: true })
  })
}

async function resetDevUsage() {
  if (!IS_DEV) return
  devResetMessage.value = ''
  error.value = ''
  try {
    const res = await fetch(apiUrl('dev/reset-usage'), {
      method: 'POST',
      credentials: 'include',
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      throw new Error(typeof data?.detail === 'string' ? data.detail : 'Reset failed')
    }
    limitState.value = null
    result.value = null
    stats.value = { charactersProcessed: 0, entitiesRemoved: 0, requestsProcessed: 0 }
    saveStats()
    applyTier('free')
    devResetMessage.value = 'Dev usage reset.'
  } catch (e) {
    error.value = e.message || 'Reset failed'
  }
}

function fillExample() {
  clearTryExampleResetTimer()
  let nextIndex = Math.floor(Math.random() * DEMO_TEXTS.length)
  if (DEMO_TEXTS.length > 1) {
    while (nextIndex === lastDemoIndex.value) {
      nextIndex = Math.floor(Math.random() * DEMO_TEXTS.length)
    }
  }
  lastDemoIndex.value = nextIndex
  text.value = DEMO_TEXTS[nextIndex]
  tryExampleClickCount.value += 1
  demoSwapActive.value = true
  window.setTimeout(() => {
    demoSwapActive.value = false
  }, 280)
  uploadStatus.value = ''
  loadedFileName.value = ''
  error.value = ''
  result.value = null
}

function handleInputKeydown(event) {
  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
    event.preventDefault()
    anonymize()
  }
}

async function anonymize() {
  if (!canSubmit.value) return
  submitGlow.value = true
  window.setTimeout(() => {
    submitGlow.value = false
  }, 150)
  loading.value = true
  error.value = ''
  limitState.value = null
  result.value = null

  try {
    const res = await fetch(apiUrl('anonymize'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        text: text.value,
        entity_types: activeEntityTypes.value,
        tag_style: emojiTags.value ? 'emoji' : 'standard',
        reversePronouns: reversePronouns.value,
        reverse_pronouns: reversePronouns.value,
      })
    })

    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      const detailObject = typeof data?.detail === 'object' && data.detail ? data.detail : null
      if (res.status === 429 && detailObject?.code === 'USAGE_LIMIT_EXCEEDED') {
        limitState.value = {
          message: detailObject.message || 'Daily limit reached',
          used: Number(detailObject.used || 0),
          limit: Number(detailObject.limit || 0)
        }
        result.value = null
        return
      }

      const detail = typeof data?.detail === 'string' ? data.detail : detailObject?.message || 'Anonymisation failed'
      throw new Error(detail)
    }

    result.value = data
    const nextTier = data?.meta?.tier === 'pro' ? 'pro' : 'free'
    const celebrateUpgrade = nextTier === 'pro' && tier.value !== 'pro'
    applyTier(nextTier)
    if (celebrateUpgrade) {
      triggerProCelebration()
    }
    showEntityDetail.value = false
    stats.value = {
      charactersProcessed: stats.value.charactersProcessed + text.value.length,
      entitiesRemoved: stats.value.entitiesRemoved + countEntitiesFromCounts(data?.counts || {}),
      requestsProcessed: stats.value.requestsProcessed + 1,
    }
    saveStats()
    copyFeedback.value = 'Copy result'
    await nextTick()
    resultSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } catch (e) {
    error.value = e.message || 'Unexpected error'
  } finally {
    loading.value = false
  }
}

function getFileExtension(name) {
  const value = String(name || '')
  const dot = value.lastIndexOf('.')
  if (dot < 0) return ''
  return value.slice(dot + 1).toLowerCase()
}

function isTextLikeFile(file) {
  const ext = getFileExtension(file?.name)
  if (TEXT_EXTENSIONS.has(ext)) return true
  const type = String(file?.type || '').toLowerCase()
  return type.startsWith('text/') || type === 'application/json'
}

function rebuildPdfPageText(content) {
  const items = content.items
    .filter((item) => 'str' in item && item.str)
    .map((item) => ({
      str: String(item.str || ''),
      x: Array.isArray(item.transform) ? Number(item.transform[4] || 0) : 0,
      y: Array.isArray(item.transform) ? Number(item.transform[5] || 0) : 0,
      width: Number(item.width || 0),
      hasEOL: Boolean(item.hasEOL),
    }))

  if (items.length === 0) return ''

  const lines = []
  let currentLine = ''
  let prev = null

  const pushLine = () => {
    const clean = currentLine.replace(/[ \t]+/g, ' ').trim()
    if (clean) lines.push(clean)
    currentLine = ''
  }

  for (const token of items) {
    const tokenText = token.str.replace(/\s+/g, ' ')
    if (!tokenText.trim()) continue

    if (prev) {
      const yDelta = Math.abs(token.y - prev.y)
      const movedBack = token.x + 1 < prev.x
      if (prev.hasEOL || (yDelta > 2 && movedBack)) {
        pushLine()
      } else if (currentLine) {
        const prevRight = prev.x + Math.max(prev.width, 0)
        const gap = token.x - prevRight
        const prevAvgChar = prev.str.length > 0 ? prev.width / prev.str.length : 0
        const gapThreshold = Math.max(1.5, prevAvgChar * 0.45)
        const needsSpace = gap > gapThreshold && !currentLine.endsWith(' ') && !tokenText.startsWith(' ')
        if (needsSpace) currentLine += ' '
      }
    }

    currentLine += tokenText
    prev = token

    if (token.hasEOL) {
      pushLine()
      prev = null
    }
  }

  pushLine()
  return lines.join('\n')
}

async function extractPdfText(file) {
  if (!pdfRuntimePromise) {
    pdfRuntimePromise = Promise.all([
      import('pdfjs-dist/legacy/build/pdf.mjs'),
      import('pdfjs-dist/legacy/build/pdf.worker.mjs?url'),
    ]).then(([pdfjs, worker]) => {
      pdfjs.GlobalWorkerOptions.workerSrc = worker.default
      return pdfjs
    })
  }
  const { getDocument } = await pdfRuntimePromise

  const bytes = new Uint8Array(await file.arrayBuffer())
  const pdf = await getDocument({ data: bytes }).promise
  const pages = []
  for (let pageNum = 1; pageNum <= pdf.numPages; pageNum += 1) {
    const page = await pdf.getPage(pageNum)
    const content = await page.getTextContent({
      normalizeWhitespace: true,
      disableCombineTextItems: false,
    })
    const pageText = rebuildPdfPageText(content)
    pages.push(pageText)
  }
  return pages.join('\n\n')
}

function normalizeLoadedText(raw) {
  return String(raw || '').replace(/\u0000/g, '').trim()
}

async function loadFile(file) {
  if (!file) return

  fileBusy.value = true
  uploadStatus.value = ''
  loadedFileName.value = ''
  error.value = ''
  result.value = null

  try {
    if (file.size > MAX_UPLOAD_BYTES) {
      throw new Error('File too large. Max 8MB for upload in this version.')
    }

    let loaded = ''
    const ext = getFileExtension(file.name)
    if (ext === 'pdf' || file.type === 'application/pdf') {
      loaded = await extractPdfText(file)
    } else if (isTextLikeFile(file)) {
      loaded = await file.text()
    } else {
      throw new Error('Unsupported file type. Use PDF or text files (.txt, .md, .csv, .json, .log).')
    }

    const normalized = normalizeLoadedText(loaded)
    if (!normalized) {
      throw new Error('No readable text found in this file.')
    }

    const maxChars = activeMaxChars.value
    if (normalized.length > maxChars) {
      text.value = normalized.slice(0, maxChars)
      uploadStatus.value = `Input trimmed to ${maxChars.toLocaleString()} characters.`
    } else {
      text.value = normalized
      uploadStatus.value = ''
    }
    loadedFileName.value = file.name

    await nextTick()
    inputArea.value?.focus({ preventScroll: true })
    inputArea.value?.select()
  } catch (e) {
    error.value = e.message || 'Failed to read file'
    uploadStatus.value = ''
  } finally {
    fileBusy.value = false
  }
}

async function handleFileSelect(event) {
  const input = event.target
  const file = input.files?.[0]
  if (!file) return
  await loadFile(file)
  input.value = ''
}

async function pasteFromClipboard() {
  error.value = ''
  loadedFileName.value = ''

  try {
    const clipboardText = await navigator.clipboard.readText()
    const normalized = String(clipboardText || '').trim()
    if (!normalized) {
      uploadStatus.value = 'Clipboard is empty.'
      return
    }

    const maxChars = activeMaxChars.value
    text.value = normalized.length > maxChars ? normalized.slice(0, maxChars) : normalized
    uploadStatus.value =
      normalized.length > maxChars
        ? `Input trimmed to ${maxChars.toLocaleString()} characters.`
        : 'Pasted from clipboard.'
    result.value = null

    await nextTick()
    inputArea.value?.focus({ preventScroll: true })
  } catch (_) {
    error.value = 'Clipboard access blocked. Use Cmd/Ctrl + V in the text area.'
  }
}

function handleDragOver(event) {
  event.preventDefault()
  dropActive.value = true
}

function handleDragLeave() {
  dropActive.value = false
}

async function handleDrop(event) {
  event.preventDefault()
  dropActive.value = false

  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    await loadFile(files[0])
    return
  }

  const droppedText = String(event.dataTransfer?.getData('text/plain') || '').trim()
  if (!droppedText) return

  const maxChars = activeMaxChars.value
  text.value = droppedText.length > maxChars ? droppedText.slice(0, maxChars) : droppedText
  loadedFileName.value = ''
  uploadStatus.value = droppedText.length > maxChars
    ? `Input trimmed to ${maxChars.toLocaleString()} characters.`
    : ''
}

async function copyOutput() {
  const output = outputForDisplay.value
  if (!output) return
  await navigator.clipboard.writeText(output)
  copyFeedback.value = 'Copied'
  window.setTimeout(() => {
    copyFeedback.value = 'Copy result'
  }, 1300)
}

function downloadOutput() {
  const output = outputForDisplay.value
  if (!output) return
  const blob = new Blob([output], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'anonymized.txt'
  a.click()
  URL.revokeObjectURL(url)
}

async function upgrade() {
  error.value = ''
  try {
    const successUrl = `${window.location.origin}/`
    const cancelUrl = `${window.location.origin}/`
    const res = await fetch(apiUrl('billing/create-checkout'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ success_url: successUrl, cancel_url: cancelUrl })
    })

    if (res.ok) {
      const data = await res.json()
      window.location.href = data.url
      return
    }

    const devRes = await fetch(apiUrl('billing/dev-upgrade'), {
      method: 'POST',
      credentials: 'include'
    })
    if (!devRes.ok) {
      throw new Error('Upgrade unavailable right now')
    }
    const devData = await devRes.json().catch(() => ({}))
    applyTier(devData?.tier === 'pro' ? 'pro' : 'pro')
    triggerProCelebration()
  } catch (e) {
    error.value = e.message || 'Upgrade failed'
  }
}

onMounted(async () => {
  const hasFinePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches
  if (hasFinePointer) {
    customCursorEnabled.value = true
    document.body.classList.add('sanitise-app--custom-cursor-global')
    window.addEventListener('mousemove', handleCursorMove)
    window.addEventListener('mouseleave', handleCursorLeave)
  }

  try {
    const savedStats = JSON.parse(window.localStorage.getItem(STATS_KEY) || '{}')
    if (savedStats && typeof savedStats === 'object') {
      stats.value = {
        charactersProcessed: Number(savedStats.charactersProcessed || 0),
        entitiesRemoved: Number(savedStats.entitiesRemoved || 0),
        requestsProcessed: Number(savedStats.requestsProcessed || 0),
      }
    }
  } catch (_) {
    // Ignore invalid stats payload.
  }

  try {
    if (window.localStorage.getItem(PRO_UI_HINT_KEY) === '1') {
      tier.value = 'pro'
    }
  } catch (_) {
    // Ignore local tier hint errors.
  }

  try {
    const saved = JSON.parse(window.localStorage.getItem(ENTITY_PREFS_KEY) || '{}')
    if (Array.isArray(saved)) {
      const valid = saved.filter((key) => allEntityKeys.includes(key))
      if (valid.length > 0) {
        enabled.value = new Set(valid)
        protectAllSensitive.value = false
      }
    } else if (saved && typeof saved === 'object') {
      if (typeof saved.protect_all === 'boolean') {
        protectAllSensitive.value = saved.protect_all
      }
      if (Array.isArray(saved.selected)) {
        const valid = saved.selected.filter((key) => allEntityKeys.includes(key))
        if (valid.length > 0) {
          enabled.value = new Set(valid)
        }
      }
      if (typeof saved.emoji_tags === 'boolean') {
        emojiTags.value = saved.emoji_tags
      }
      if (typeof saved.reverse_pronouns === 'boolean') {
        reversePronouns.value = saved.reverse_pronouns
      }
      if (typeof saved.redaction_mode === 'boolean') {
        redactionMode.value = saved.redaction_mode
      }
      if (typeof saved.highlight_censored === 'boolean') {
        highlightCensored.value = saved.highlight_censored
      }
    }
  } catch (_) {
    // Ignore invalid saved preferences.
  }

  await nextTick()
  inputHighlighted.value = true
  const desktopPointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches
  if (desktopPointer) {
    inputArea.value?.focus({ preventScroll: true })
  }
  window.setTimeout(() => {
    inputHighlighted.value = false
  }, 1800)

  const sessionId = new URLSearchParams(window.location.search).get('session_id')
  if (sessionId) {
    try {
      const activationRes = await fetch(`${apiUrl('billing/activate')}?session_id=${encodeURIComponent(sessionId)}`, {
        credentials: 'include'
      })
      if (activationRes.ok) {
        applyTier('pro')
        triggerProCelebration()
      }
    } catch (_) {
      // Do not block normal app usage if billing activation fails.
    }
  }

  await loadBillingTier()
})

onUnmounted(() => {
  clearLivePreviewTimers()
  clearTryExampleResetTimer()
  document.body.classList.remove('sanitise-app--custom-cursor-global')
  window.removeEventListener('mousemove', handleCursorMove)
  window.removeEventListener('mouseleave', handleCursorLeave)
  if (proCelebrationTimer) {
    window.clearTimeout(proCelebrationTimer)
    proCelebrationTimer = null
  }
})

watch(
  [protectAllSensitive, enabled, emojiTags, reversePronouns, redactionMode, highlightCensored],
  ([protectAll, selected, emoji, pronouns, redaction, highlight]) => {
    try {
      window.localStorage.setItem(ENTITY_PREFS_KEY, JSON.stringify({
        protect_all: Boolean(protectAll),
        selected: Array.from(selected),
        emoji_tags: Boolean(emoji),
        reverse_pronouns: Boolean(pronouns),
        redaction_mode: Boolean(redaction),
        highlight_censored: Boolean(highlight),
      }))
    } catch (_) {
      // Ignore storage errors (private mode/quota).
    }
  },
  { deep: false }
)

watch(
  [text, activeEntityTypes],
  () => {
    queueLivePreview()
  },
  { deep: false }
)
</script>

<template>
  <div class="matrix-bg" aria-hidden="true"></div>
  <main :class="['sanitise-app', { 'sanitise-app--custom-cursor': customCursorEnabled }]">
    <header class="sanitise-app__hero">
      <div class="sanitise-app__brand-row">
        <p class="sanitise-app__brand">Sanitise AI</p>
        <span v-if="isProTier" class="sanitise-app__pro-badge">PRO</span>
      </div>
      <h1 class="sanitise-app__headline sanitise-app__headline--gradient">Sanitise sensitive text before sending it to AI</h1>
      <div class="sanitise-app__hero-logo-frame" aria-hidden="true">
        <img
          class="sanitise-app__hero-logo"
          src="/sanitise-ai-logo.png"
          alt="Sanitise AI logo"
          width="360"
          height="240"
          fetchpriority="high"
          decoding="async"
        />
      </div>
      <p class="sanitise-app__subtitle">A privacy layer between your data and AI. Automatically anonymise names, emails, phone numbers and addresses while preserving the structure AI needs to reason about the text.</p>
      <p class="sanitise-app__support-line">Structured placeholders help AI keep context intact.</p>
    </header>

    <Transition name="sanitise-app__pro-pop">
      <div v-if="showProCelebration" class="sanitise-app__pro-pop" role="status" aria-live="polite">
        <p class="sanitise-app__pro-pop-copy">🎆 You've gone Pro!</p>
        <div class="sanitise-app__pro-pop-bursts" aria-hidden="true">
          <span class="sanitise-app__burst sanitise-app__burst--a">✦</span>
          <span class="sanitise-app__burst sanitise-app__burst--b">✶</span>
          <span class="sanitise-app__burst sanitise-app__burst--c">✦</span>
          <span class="sanitise-app__burst sanitise-app__burst--d">✶</span>
          <span class="sanitise-app__burst sanitise-app__burst--e">✦</span>
          <span class="sanitise-app__burst sanitise-app__burst--f">✶</span>
        </div>
      </div>
    </Transition>

    <section class="sanitise-app__composer">
      <div class="sanitise-app__input-header">
        <div class="sanitise-app__input-title-row">
          <label for="input" class="sanitise-app__label">Paste sensitive content</label>
          <button
            type="button"
            class="sanitise-app__btn sanitise-app__btn--secondary sanitise-app__btn--compact"
            :disabled="loading || fileBusy"
            @click="pasteFromClipboard"
          >
            Paste here
          </button>
        </div>
        <div class="sanitise-app__input-tools">
          <button
            type="button"
            class="sanitise-app__btn sanitise-app__btn--link"
            :disabled="loading || fileBusy"
            @click="fillExample"
            @mouseenter="clearTryExampleResetTimer"
            @mouseleave="scheduleTryExampleLabelReset"
          >
            <Transition name="sanitise-app__try-label-fade" mode="out-in">
              <span :key="tryExampleLabel">{{ tryExampleLabel }}</span>
            </Transition>
          </button>
          <label for="file-upload" class="sanitise-app__btn sanitise-app__upload-btn">
            {{ fileBusy ? 'Reading file...' : 'Upload PDF or text' }}
          </label>
        </div>
        <input
          id="file-upload"
          class="sanitise-app__file-input"
          type="file"
          accept=".pdf,.txt,.md,.csv,.json,.log,text/plain,application/pdf,application/json"
          :disabled="fileBusy || loading"
          @change="handleFileSelect"
        />
      </div>
      <p v-if="loadedFileName" class="sanitise-app__file-chip">Loaded file: {{ loadedFileName }}</p>
      <p v-if="uploadStatus" class="sanitise-app__charline">{{ uploadStatus }}</p>
      <div class="sanitise-app__input-wrap">
        <div
          :class="['sanitise-app__drop-zone', { 'sanitise-app__drop-zone--active': dropActive }]"
          @dragover="handleDragOver"
          @dragleave="handleDragLeave"
          @drop="handleDrop"
        >
          <textarea
            id="input"
            ref="inputArea"
            :class="[
              'sanitise-app__textarea',
              {
                'sanitise-app__textarea--highlighted': inputHighlighted,
                'sanitise-app__textarea--demo-swap': demoSwapActive,
              }
            ]"
            v-model="text"
            rows="10"
            :maxlength="activeMaxChars"
            placeholder="Paste text containing sensitive information or drop a document to anonymise"
            @keydown="handleInputKeydown"
          ></textarea>
          <div class="sanitise-app__charline sanitise-app__charline--inside">{{ charCountLabel }}</div>
        </div>
      </div>
      <section class="sanitise-app__flow-controls" aria-label="Sanitisation options">
        <div class="sanitise-app__flow-action-row">
          <div v-if="liveDetectedLabel" class="sanitise-app__live-detect">
            <p class="sanitise-app__live-detect-main">{{ liveDetectedLabel }}</p>
            <p v-if="liveDetectedTypesLabel" class="sanitise-app__live-detect-types">{{ liveDetectedTypesLabel }}</p>
          </div>
          <div class="sanitise-app__actions sanitise-app__actions--primary">
            <button
              v-if="text.trim()"
              type="button"
              class="sanitise-app__btn sanitise-app__btn--link"
              :disabled="loading"
              @click="clearInputText"
            >
              Clear
            </button>
            <button
              type="button"
              :class="['sanitise-app__btn', 'sanitise-app__btn--primary', { 'sanitise-app__btn--glowing': submitGlow }]"
              :disabled="!canSubmit"
              @click="anonymize"
            >
              {{ submitLabel }}
            </button>
          </div>
        </div>

        <div class="sanitise-app__flow-settings">
          <div class="sanitise-app__mode-selector" role="radiogroup" aria-label="Detection mode">
            <label class="sanitise-app__mode-option">
              <input
                type="radio"
                name="detection-mode"
                :checked="protectAllSensitive"
                @change="!protectAllSensitive && toggleProtectAllSensitive()"
              />
              <span>Automatic (recommended)</span>
            </label>
            <label class="sanitise-app__mode-option">
              <input
                type="radio"
                name="detection-mode"
                :checked="!protectAllSensitive"
                @change="protectAllSensitive && toggleProtectAllSensitive()"
              />
              <span>Custom rules</span>
            </label>
          </div>
          <div class="sanitise-app__transform-row">
            <label class="sanitise-app__option sanitise-app__option--quiet">
              <input v-model="reversePronouns" type="checkbox" />
              Reverse pronouns
            </label>
          </div>
        </div>

        <p class="sanitise-app__limit-hint">{{ charLimitHint }}</p>

        <div class="sanitise-app__flow-dev">
          <div v-if="IS_DEV" class="sanitise-app__dev-tools">
            <button type="button" class="sanitise-app__btn sanitise-app__btn--dev" @click="resetDevUsage">
              Reset Go Pro/usage (dev)
            </button>
            <p v-if="devResetMessage" class="sanitise-app__dev-note">{{ devResetMessage }}</p>
          </div>
        </div>
      </section>

      <div v-if="!protectAllSensitive" class="sanitise-app__entity-filter">
        <div class="sanitise-app__advanced-groups">
          <section v-for="group in entityGroups" :key="group.key" class="sanitise-app__entity-group">
            <p class="sanitise-app__entity-group-title">{{ group.label }}</p>
            <div class="sanitise-app__toggles sanitise-app__toggles--grouped">
              <button
                v-for="item in group.items"
                :key="item.key"
                type="button"
                :class="['sanitise-app__chip', { 'sanitise-app__chip--active': enabled.has(item.key) }]"
                @click="toggleType(item.key)"
              >
                {{ item.label }}
              </button>
            </div>
          </section>
        </div>
      </div>

      <div v-if="limitState" class="sanitise-app__limit-card" role="status" aria-live="polite">
        <p class="sanitise-app__limit-title">{{ limitState.message }}</p>
        <p class="sanitise-app__limit-copy">{{ limitState.used }}/{{ limitState.limit }} free anonymisations used today.</p>
        <div class="sanitise-app__actions sanitise-app__actions--limit">
          <button type="button" class="sanitise-app__btn sanitise-app__btn--primary" @click="upgrade">Go Pro</button>
          <button type="button" class="sanitise-app__btn" @click="limitState = null">Dismiss</button>
        </div>
      </div>
      <p v-if="error" class="sanitise-app__error">{{ error }}</p>
    </section>

    <Transition name="sanitise-app__success-fade-up">
      <section
        v-if="result && resultTotalEntities > 0"
        class="sanitise-app__success-banner"
        role="status"
        aria-live="polite"
      >
        <div class="sanitise-app__success-banner-main">
          <span class="sanitise-app__success-icon" aria-hidden="true">✓</span>
          <p class="sanitise-app__success-copy">
            {{ resultTotalEntities }} {{ resultTotalEntities === 1 ? 'entity' : 'entities' }} anonymised
          </p>
        </div>
        <button type="button" class="sanitise-app__success-toggle" @click="showEntityDetail = !showEntityDetail">
          {{ showEntityDetail ? 'Hide details' : 'Show details' }}
        </button>
        <ul v-if="showEntityDetail" class="sanitise-app__success-details">
          <li v-for="item in successEntityDetails" :key="item.key">• {{ item.text }}</li>
        </ul>
      </section>
    </Transition>

    <section v-if="result" ref="resultSection" class="sanitise-app__result-grid">
      <div class="sanitise-app__rerun-row">
        <button
          type="button"
          class="sanitise-app__btn sanitise-app__btn--primary sanitise-app__btn--rerun"
          :disabled="!canSubmit"
          @click="anonymize"
        >
          {{ submitLabel }}
        </button>
      </div>
      <div v-if="resultWarning" class="sanitise-app__warning-banner" role="status" aria-live="polite">
        ⚠ {{ resultWarning }}
      </div>
      <article class="sanitise-app__panel">
        <div class="sanitise-app__panel-title-row">
          <h2>Original</h2>
        </div>
        <pre class="sanitise-app__text-block">{{ text }}</pre>
      </article>
      <article class="sanitise-app__panel sanitise-app__panel--anonymised">
        <div class="sanitise-app__panel-title-row">
          <h2>Anonymised</h2>
          <div class="sanitise-app__panel-title-actions">
            <button
              type="button"
              class="sanitise-app__btn sanitise-app__btn--panel-action sanitise-app__btn--copy"
              :title="copyFeedback"
              :aria-label="copyFeedback"
              @click="copyOutput"
            >
              <span>{{ copyFeedback === 'Copied' ? 'Copied' : 'Copy' }}</span>
              <span aria-hidden="true">⧉</span>
            </button>
            <button
              type="button"
              class="sanitise-app__btn sanitise-app__btn--panel-action"
              title="Download text file"
              aria-label="Download text file"
              @click="downloadOutput"
            >
              <span>Download</span>
              <span class="sanitise-app__btn-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
                  <path
                    d="M12 3a1 1 0 0 1 1 1v8.59l2.3-2.29a1 1 0 1 1 1.4 1.41l-4 4a1 1 0 0 1-1.4 0l-4-4a1 1 0 1 1 1.4-1.41L11 12.59V4a1 1 0 0 1 1-1Zm-7 14a1 1 0 0 1 1 1v1h12v-1a1 1 0 1 1 2 0v2a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-2a1 1 0 0 1 1-1Z"
                    fill="currentColor"
                  />
                </svg>
              </span>
            </button>
          </div>
        </div>
        <pre class="sanitise-app__text-block" v-html="anonymizedRenderHtml"></pre>
        <div class="sanitise-app__option-row">
          <label class="sanitise-app__option">
            <input v-model="highlightCensored" type="checkbox" />
            Highlight
          </label>
          <label class="sanitise-app__option">
            <input v-model="emojiTags" type="checkbox" />
            Emoji
          </label>
          <label class="sanitise-app__option">
            <input v-model="redactionMode" type="checkbox" />
            Redact
          </label>
        </div>
        <div v-if="resultTotalEntities === 0" class="sanitise-app__no-sensitive-warning" role="status" aria-live="polite">
          <p class="sanitise-app__no-sensitive-note">⚠ No sensitive entities detected. Your text was not changed.</p>
          <p class="sanitise-app__no-sensitive-hint">Try Custom rules if you want stricter matching.</p>
        </div>
      </article>
    </section>

    <section v-if="result" class="sanitise-app__meta-section">
      <h2>Detection Summary</h2>
      <p class="sanitise-app__meta-line">{{ summaryLine }}</p>
      <div class="sanitise-app__counts">
        <span v-for="(count, key) in result.counts" :key="key" class="sanitise-app__count-item">{{ key }}: {{ count }}</span>
      </div>
      <div class="sanitise-app__actions">
        <p class="sanitise-app__promo-copy">Upgrade to Pro for higher limits (5,000 → 50,000 chars), advanced export features, and priority processing.</p>
        <button type="button" class="sanitise-app__btn" @click="upgrade">Get Pro access</button>
      </div>
    </section>

    <section v-if="result?.cta_visaprep" class="sanitise-app__meta-section sanitise-app__meta-section--cta">
      <h2>Need immigration-specific help next?</h2>
      <p>Your text looks immigration-related. You can continue safely with redacted content on Visaprep.</p>
      <a href="https://visaprep.uk" target="_blank" rel="noreferrer" class="sanitise-app__btn sanitise-app__btn--primary">Open Visaprep</a>
    </section>

    <section class="sanitise-app__feature-section" aria-label="Core features">
      <div class="sanitise-app__feature-grid">
        <article class="sanitise-app__feature-card sanitise-app__feature-card--protect">
          <div class="sanitise-app__feature-head">
            <span class="sanitise-app__feature-icon" aria-hidden="true">🛡</span>
            <span class="sanitise-app__feature-kicker">Detection</span>
          </div>
          <h2>Protect sensitive data</h2>
          <p>Detects names, emails, phones, addresses, usernames and IPs before text reaches AI.</p>
        </article>
        <article class="sanitise-app__feature-card sanitise-app__feature-card--preserve">
          <div class="sanitise-app__feature-head">
            <span class="sanitise-app__feature-icon" aria-hidden="true">🧠</span>
            <span class="sanitise-app__feature-kicker">Reasoning</span>
          </div>
          <h2>Preserve prompt meaning</h2>
          <p>Structured placeholders keep relationships intact so AI can still reason about the content.</p>
        </article>
        <article class="sanitise-app__feature-card sanitise-app__feature-card--storage">
          <div class="sanitise-app__feature-head">
            <span class="sanitise-app__feature-icon" aria-hidden="true">🔒</span>
            <span class="sanitise-app__feature-kicker">Privacy</span>
          </div>
          <h2>No raw text stored</h2>
          <p>Anonymisation happens before AI processing. Submitted text is not stored.</p>
        </article>
      </div>
    </section>

    <section class="sanitise-app__extension-section" aria-label="Extensions">
      <h2>Use Sanitise AI everywhere</h2>
      <p>Protect prompts before they reach AI tools across desktop and mobile workflows.</p>
      <div class="sanitise-app__extension-grid">
        <article class="sanitise-app__extension-card" aria-disabled="true">
          <div class="sanitise-app__extension-head">
            <div class="sanitise-app__extension-title-wrap">
              <span class="sanitise-app__extension-icon" aria-hidden="true">◔</span>
              <span class="sanitise-app__extension-title">Chrome Extension</span>
            </div>
            <span class="sanitise-app__extension-badge">Testing beta</span>
          </div>
          <p class="sanitise-app__extension-description">Protect prompts inside ChatGPT and other AI tools.</p>
        </article>
        <article class="sanitise-app__extension-card" aria-disabled="true">
          <div class="sanitise-app__extension-head">
            <div class="sanitise-app__extension-title-wrap">
              <span class="sanitise-app__extension-icon" aria-hidden="true">◑</span>
              <span class="sanitise-app__extension-title">iOS App</span>
            </div>
            <span class="sanitise-app__extension-badge">Testing beta</span>
          </div>
          <p class="sanitise-app__extension-description">Sanitise text on mobile before sharing with AI apps.</p>
        </article>
      </div>
    </section>

    <section v-if="hasLocalStats" class="sanitise-app__stats" aria-label="Your stats">
      <h2>Your stats</h2>
      <div class="sanitise-app__stats-grid">
        <article class="sanitise-app__stat">
          <p class="sanitise-app__stat-label">Total Characters Processed</p>
          <p class="sanitise-app__stat-value">{{ statsCharactersLabel }}</p>
        </article>
        <article class="sanitise-app__stat">
          <p class="sanitise-app__stat-label">Entities Removed</p>
          <p class="sanitise-app__stat-value">{{ statsEntitiesLabel }}</p>
        </article>
        <article class="sanitise-app__stat">
          <p class="sanitise-app__stat-label">Requests Processed</p>
          <p class="sanitise-app__stat-value">{{ statsRequestsLabel }}</p>
        </article>
      </div>
      <p class="sanitise-app__stats-trust">Shows anonymisations from your usage only. Raw text is not stored.</p>
    </section>

    <footer class="sanitise-app__footer">
      <p>Built by Nima Parsi</p>
      <p><a href="https://github.com/nimaparsi/matrix-anonymiser" target="_blank" rel="noreferrer">Open source on GitHub</a></p>
      <p><a href="/privacy.html">Privacy policy</a></p>
      <p>No data stored</p>
      <p>Sensitive data is anonymised before any AI processing.</p>
      <p class="sanitise-app__engine-credit">Powered by the Matrix Privacy Engine</p>
    </footer>
  </main>
  <div
    v-if="customCursorEnabled"
    :class="['sanitise-app__cursor', { 'sanitise-app__cursor--visible': customCursorVisible }]"
    :style="customCursorStyle"
    aria-hidden="true"
  ></div>
</template>

<style lang="scss" src="./global.scss"></style>
<style scoped lang="scss" src="./App.scss"></style>
