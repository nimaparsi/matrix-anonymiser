<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  PhCheckCircle,
  PhCopy,
  PhDownloadSimple,
  PhEraser,
  PhMagicWand,
  PhShieldCheck,
  PhSparkle,
  PhUploadSimple,
} from '@phosphor-icons/vue'
import pdfWorkerUrl from 'pdfjs-dist/legacy/build/pdf.worker.min.mjs?url'

type DetectorKey =
  | 'person'
  | 'organisation'
  | 'email'
  | 'phone'
  | 'date'
  | 'address'
  | 'ip'
  | 'secret'
  | 'id'
  | 'invoice'
  | 'username'

type TokenType =
  | 'Person'
  | 'Organisation'
  | 'Email'
  | 'Phone'
  | 'Date'
  | 'Address'
  | 'IP'
  | 'Secret'
  | 'ID'
  | 'Invoice'
  | 'Username'

type MinimumDisclosureSummary = {
  task_context: string
  task_label: string
  total_entities: number
  critical_entities: number
  high_entities: number
  medium_entities: number
  recommended_actions: Record<string, number>
  guidance: string
}

type TaskContext = 'ai_prompt' | 'external_document' | 'support_handoff' | 'developer_logs'
type ToolExample = { text: string; context: TaskContext; task: string }
type AdaptiveRequirement = { concept: string; importance: string; reason: string }
type AdaptiveDecision = { factId: string; action: string; replacement?: string | null; taskRelevance: string; sensitivity: string; reason: string }
type AdaptivePreview = {
  mode: string
  methodology_version: string
  task: string
  purpose: string
  destination: string
  requirements: AdaptiveRequirement[]
  decisions: AdaptiveDecision[]
  adaptive_text: string
  metrics: {
    required_fact_retention: number
    irrelevant_sensitive_suppression: number
    critical_leakage_count: number
  }
}

type SanitiseResult = {
  output: string
  counts: Record<TokenType, number>
  total: number
  detectedLabels: string[]
  minimumDisclosure?: MinimumDisclosureSummary
  adaptive?: AdaptivePreview
}

class SanitiseApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message)
    this.name = 'SanitiseApiError'
  }
}

function defaultDetectorState(): Record<DetectorKey, boolean> {
  return {
    person: true,
    organisation: true,
    email: true,
    phone: true,
    date: true,
    address: true,
    ip: true,
    secret: true,
    id: true,
    invoice: true,
    username: true,
  }
}

function splitOutputByTokens(output: string): Array<{ text: string; tokenType?: TokenType }> {
  const tokenRegex = /\[(Person|Organisation|Email|Phone|Date|Address|IP|Secret|ID|Invoice|Username)\s+\d+\]/g
  const result: Array<{ text: string; tokenType?: TokenType }> = []
  let lastIndex = 0

  for (const match of output.matchAll(tokenRegex)) {
    const index = match.index ?? 0
    if (index > lastIndex) {
      result.push({ text: output.slice(lastIndex, index) })
    }
    result.push({ text: match[0], tokenType: match[1] as TokenType })
    lastIndex = index + match[0].length
  }

  if (lastIndex < output.length) {
    result.push({ text: output.slice(lastIndex) })
  }

  return result
}

const route = useRoute()

const inputText = ref('')
const outputText = ref('')
const inputRef = ref<HTMLTextAreaElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const outputPanelRef = ref<HTMLElement | null>(null)
const isProcessing = ref(false)
const isUploading = ref(false)
const copyLabel = ref('Copy result')
const uploadLabel = ref('Upload .txt or .pdf')
const mode = ref<'automatic' | 'custom'>('automatic')
const isCustomRulesOpen = ref(false)
const detectorState = ref(defaultDetectorState())
const reversePronounsEnabled = ref(false)
const taskContext = ref<TaskContext>('ai_prompt')
const taskDescription = ref('')
const result = ref<SanitiseResult | null>(null)
const statusText = ref('')
const lastSignature = ref('')
const outputReveal = ref(false)
let revealTimer: ReturnType<typeof setTimeout> | null = null
let exampleCursor = -1

const taskOptions = [
  { value: 'ai_prompt', label: 'AI prompt', hint: 'Keep meaning, remove identifiers' },
  { value: 'external_document', label: 'External doc', hint: 'Prepare text for sharing' },
  { value: 'support_handoff', label: 'Support handoff', hint: 'Keep case context' },
  { value: 'developer_logs', label: 'Dev logs', hint: 'Prioritise secrets and infra' },
] as const

const TOOL_EXAMPLES: ToolExample[] = [
  {
    context: 'external_document',
    task: 'Summarise renewal and liability risks for an external lawyer while keeping direct contacts anonymised.',
    text: [
      'Software subscription agreement (first page excerpt)',
      'Agreement date: 18 March 2026',
      'Customer: Westbridge Procurement Ltd',
      'Customer signatory: Hannah Price (h.price@westbridge.co.uk)',
      'Vendor signatory: Mark Ellis (mark.ellis@orbitstack.io)',
      'Registered address: 17 Bishopsgate, London EC2N 3AR',
      'Invoice reference: INV-2026-0318-778',
      'Emergency contact: +44 7700 932100',
      'Clause note: renewal auto-extends unless either party gives 60 days notice.',
    ].join('\n'),
  },
  {
    context: 'external_document',
    task: 'Prepare a litigation update for counsel, preserving dates and filing references but removing people and contact details.',
    text: [
      'Law firm redline memo',
      'Matter: Ashton v. Keldon Manufacturing',
      'Partner Olivia Hart asked Leo Bennett to review the indemnity wording before 22 April 2026.',
      'Client email: legalteam@ashtonholdings.com',
      'Counsel email: olivia.hart@westbridgelegal.co.uk',
      'Call Olivia on +44 7700 947301 if the court filing ID CF-2026-11873 is missing from the bundle.',
    ].join('\n'),
  },
  {
    context: 'external_document',
    task: 'Extract commercial obligations from this MSA amendment for a procurement summary without exposing contacts.',
    text: [
      'MSA amendment summary',
      'Client: BrightEdge Consulting Ltd',
      'Legal contact Sarah Thompson confirmed by email at sarah.thompson@brightedge.co.uk that support cover changes on 1 May 2026.',
      'Phone: +44 7700 900123',
      'Registered office: 1 Finsbury Square, London EC2A 1AE',
      'Invoice #: INV-88421',
      'Commercial issue: clause 4.2 narrows the response-time remedy to service credits only.',
    ].join('\n'),
  },
  {
    context: 'ai_prompt',
    task: 'Summarise clinical next steps while anonymising patient, clinician, NHS number, dates of birth, and contact details.',
    text: [
      'NHS referral note',
      'Patient: Eleanor Matthews (DOB: 14/02/1988)',
      'NHS no: 943 476 1820',
      'Consultant: Dr James Holloway',
      'Email: james.holloway@westbrook-hospital.nhs.uk',
      'Phone: +44 7700 901144',
      'Address: 43 Hawthorn Road, Leeds LS7 2AA',
      'GP practice: Westbrook Family Clinic',
      'Follow-up date: 29 March 2026',
      'Referral reason: persistent headaches after a minor cycling accident; no loss of consciousness reported.',
    ].join('\n'),
  },
  {
    context: 'support_handoff',
    task: 'Create a safe handoff for the next support agent, keeping order context but removing customer identity and location.',
    text: [
      'Chat transcript - customer escalation',
      'Agent Mia: I can help with the delayed delivery.',
      'Customer Priya Nair: Please call me on +44 7700 945611. The order ORD-884129 was meant to arrive yesterday.',
      'Priya: My email is priya.nair@contoso.com and the delivery address is 9 Rivington Street, London EC2A 3DT.',
      'Agent Mia: I will escalate this to fulfilment and note that the parcel contains replacement medical equipment.',
    ].join('\n'),
  },
  {
    context: 'developer_logs',
    task: 'Debug the failed deployment without exposing passwords, API keys, SSH keys, IP addresses, usernames, or emails.',
    text: [
      'Production auth incident - API gateway',
      'Owner Alice Morgan saw 401 spikes from host 10.12.8.32 at 02:14 UTC.',
      'GitHub user: alice-morgan-dev',
      'Email: alice.morgan@contoso.dev',
      'Pager: +44 7700 900456',
      'GitHub SSH key: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH8G2Ud4h6ZcF1b8Q8kTWX5q2e4w9rjQ7w2L2N2 alice@contoso',
      'Access token: ghp_u7QxY3nN9aK1dL4mZ8tW2pR6hC0vB5e',
      'AWS key: AKIAIOSFODNN7EXAMPLE',
      'Password found in env dump: N0rthstar!2026',
      'JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.signatureExampleTokenValue',
    ].join('\n'),
  },
  {
    context: 'developer_logs',
    task: 'Share a safe incident summary with an LLM for root-cause analysis, suppressing secrets and personal contact routes.',
    text: [
      'DevOps handover note',
      'Engineer Nikhil Rao used username nrao_ops on bastion host 172.16.44.19.',
      'He rotated client_secret svc_auth_8fVd39xQ2lRm17cS after Terraform failed against eu-west-2.',
      'Temporary password: B1ueHarbour$2026',
      'On-call phone: +44 7700 917245',
      'Slack note: deployment queue backed up after the Redis node rejected TLS renegotiation.',
    ].join('\n'),
  },
  {
    context: 'external_document',
    task: 'Summarise payment status and invoice references for finance review without exposing bank or personal contact details.',
    text: [
      'Finance remittance advice',
      'Supplier: Northfield Retail Operations Ltd',
      'Accounts contact Lucas Meyer emailed lucas.meyer@northfieldretail.com about two overdue invoices.',
      'Mobile: +44 7700 911874',
      'Company registration: 08451277',
      'Bank account: GB29NWBK60161331926819',
      'Invoice IDs: INV-90331, INV-90332',
      'Payment ref: TXN-2026-03-88211',
      'The dispute is about a duplicate VAT line, not the payment method.',
    ].join('\n'),
  },
  {
    context: 'support_handoff',
    task: 'Prepare an insurance claim handoff that keeps policy and incident context but hides claimant identity and contacts.',
    text: [
      'Insurance claim intake summary',
      'Claimant Priya Nair reported water damage under policy POL-443-778-19.',
      'She used email priya.nair@oakfieldmail.com and phone +44 7700 938550.',
      'Incident address: 9 Rivington Street, London EC2A 3DT',
      'Assigned adjuster: Miles Kwan (miles.kwan@insureline.co.uk)',
      'Claim note: kitchen ceiling leak started after upstairs boiler service on 8 February 2026.',
    ].join('\n'),
  },
  {
    context: 'external_document',
    task: 'Share candidate feedback with a hiring manager while removing identity, contact details, employer, and home address.',
    text: [
      'Recruiter interview debrief',
      'Candidate Daniel Hughes, email daniel.hughes@careersmail.com, mobile 07912 123456.',
      'Current employer: Green Horizon Research',
      'Home address: 21 Cedar Avenue, Manchester M3 1AA',
      'Feedback: strong systems design answers, weaker on incident communication, salary expectation £92,000.',
    ].join('\n'),
  },
  {
    context: 'external_document',
    task: 'Turn this HR note into an anonymised case summary for external advice without names, employee IDs, or private contact details.',
    text: [
      'HR performance case note',
      'Employee Chloe Baker met manager Hannah Price on 4 April 2026 about repeated missed handover notes.',
      'Employee ID: EMP-77214',
      'Email: chloe.baker@northshorelabs.com',
      'Personal mobile: +44 7700 926411',
      'Home address: 2 Hanover Street, Edinburgh EH2 2DL',
      'Context: the issue appears linked to a workload spike after two resignations in the operations team.',
    ].join('\n'),
  },
  {
    context: 'external_document',
    task: 'Extract lease obligations and dates for a property lawyer while anonymising tenant contacts and property address.',
    text: [
      'Real estate lease abstract',
      'Tenant: Fairline Studio Group Ltd',
      'Tenant representative James Patel emailed j.patel@fairlinegroup.co.uk about the break clause.',
      'Property: 88 Kingsway, London WC2B 6AA',
      'Lease reference: LEASE-2026-4412',
      'Agent mobile: +44 7700 944108',
      'Break option must be served no later than 30 September 2026.',
    ].join('\n'),
  },
  {
    context: 'support_handoff',
    task: 'Create a safeguarding handoff that keeps the concern and timeline but removes child and family identifiers.',
    text: [
      'School safeguarding referral',
      'Student Emily Carter told form tutor Mr Lewis that she had not eaten breakfast for three days.',
      'Parent contact: Laura Carter',
      'Parent email: laura.carter.family@mailbox.com',
      'Parent phone: +44 7700 959114',
      'Home address: 41 Brook Lane, Bristol BS1 5TR',
      'Case reference: SG-2026-2901',
      'The DSL asked for a same-day welfare call and a follow-up meeting next Monday.',
    ].join('\n'),
  },
  {
    context: 'ai_prompt',
    task: 'Rewrite the renewal email in a neutral tone for an AI assistant without exposing customer or billing identifiers.',
    text: [
      'Customer success renewal email draft',
      'Daria Ivanov at OrbitStack Health asked whether quote Q-2026-7731 can be split across two cost centres.',
      'Email: daria.ivanov@orbitstackhealth.com',
      'Phone: +44 7700 940882',
      'Billing address: 5 Queen Square, Bath BA1 2HA',
      'Draft sentence: We can hold the 14% discount until Friday if procurement signs the updated order form.',
    ].join('\n'),
  },
  {
    context: 'support_handoff',
    task: 'Summarise the travel disruption for operations while hiding passenger identity, booking references, and contacts.',
    text: [
      'Travel operations disruption brief',
      'Passenger Nathan Cole missed connection BA-447 after the Manchester inbound was delayed by 94 minutes.',
      'Booking reference: BK-88Q2LM',
      'Ticket reference: TKT-4431107',
      'Email: nathan.cole@mailhub.co.uk',
      'Phone: +44 7700 934210',
      'Hotel address: 22 Strand, London WC2N 5HR',
      'Ops note: passenger requested overnight accommodation and rebooking before 09:00.',
    ].join('\n'),
  },
  {
    context: 'external_document',
    task: 'Prepare a board-safe project update, keeping themes and risks while anonymising people, locations, and invoices.',
    text: [
      'Board update draft',
      'Prepared by Anna Carter for Green Horizon Research.',
      'Contacts: anna.carter@example.com, daniel.hughes@ecologiclab.org',
      'Project locations: 14 Willow Lane, Brighton BN1 4AB and 28 Riverside Road, Cambridge CB1 3QA',
      'Finance tracker invoice: INV-55619',
      'Risk note: field trial slipped two weeks because supplier onboarding was incomplete.',
    ].join('\n'),
  },
  {
    context: 'ai_prompt',
    task: 'Summarise investor follow-up actions without exposing founder contact details, registration numbers, or local file paths.',
    text: [
      'Startup fundraising data room request',
      'Founder Ruben Malik spoke to Claire Hughes at Northbridge VC on 12 June 2026.',
      'Investor contact: claire.hughes@northbridgevc.com',
      'Founder email: ruben@heliogrid.ai',
      'Mobile: +44 7700 952177',
      'Company registration: 13190422',
      'Cap table file path: /Users/ruben/Documents/fundraise/CapTable_March2026.xlsx',
      'Request: send ARR bridge, current runway, and customer pipeline before Monday.',
    ].join('\n'),
  },
  {
    context: 'developer_logs',
    task: 'Share this GitHub Actions failure safely for debugging while blocking credentials and infrastructure identifiers.',
    text: [
      'GitHub Actions deploy failure',
      'Run ID: 7822441901 triggered by GitHub user maya-release on repo brightedge/payments-api.',
      'Commit author: Maya Singh <maya.singh@brightedge.dev>',
      'Runner IP: 192.168.24.18',
      'DATABASE_URL=postgres://prod_user:VioletRiver2026!@db.internal:5432/payments',
      'NPM_TOKEN=npm_7yJ39xFq8pLm0TzQw4bA1rVc',
      'Stripe key: [Stripe live secret key pasted here]',
      'Error: migration 20260418_add_refunds.sql failed on duplicate constraint.',
    ].join('\n'),
  },
]

const detectorOptions: Array<{ key: DetectorKey; label: string; hint: string }> = [
  { key: 'person', label: 'Names', hint: 'People and named contacts' },
  { key: 'organisation', label: 'Organisations', hint: 'Companies, clinics, schools' },
  { key: 'email', label: 'Emails', hint: 'Personal and work addresses' },
  { key: 'phone', label: 'Phone numbers', hint: 'Mobile and landline formats' },
  { key: 'date', label: 'Dates / DOB', hint: 'Dates, birthdays, deadlines' },
  { key: 'address', label: 'Addresses', hint: 'Street and location details' },
  { key: 'id', label: 'Government / Tax IDs', hint: 'Employee, company, official IDs' },
  { key: 'invoice', label: 'Invoice IDs', hint: 'Orders, bookings, transactions' },
  { key: 'ip', label: 'IP addresses', hint: 'Network and host identifiers' },
  { key: 'secret', label: 'Secret keys', hint: 'Tokens, keys, bank details' },
  { key: 'username', label: 'Usernames', hint: 'Handles and account names' },
]

const essentialDetectorKeys: DetectorKey[] = ['person', 'email', 'phone', 'address', 'id', 'secret']

const DETECTOR_TO_BACKEND_ENTITY: Record<DetectorKey, string[]> = {
  person: ['PERSON'],
  organisation: ['ORG'],
  email: ['EMAIL'],
  phone: ['PHONE'],
  date: ['DATE'],
  address: ['ADDRESS'],
  ip: ['IP_ADDRESS'],
  secret: ['API_KEY', 'PRIVATE_KEY', 'CREDIT_CARD', 'BANK_ACCOUNT', 'CRYPTO_WALLET'],
  id: ['GOVERNMENT_ID', 'COMPANY_REGISTRATION_NUMBER', 'EMPLOYEE_ID'],
  invoice: ['INVOICE_NUMBER', 'BOOKING_REFERENCE', 'TICKET_REFERENCE', 'ORDER_ID', 'TRANSACTION_ID'],
  username: ['USERNAME'],
}

const BACKEND_LABEL_TO_UI: Record<string, TokenType> = {
  PERSON: 'Person',
  ORGANISATION: 'Organisation',
  ORGANIZATION: 'Organisation',
  ORG: 'Organisation',
  EMAIL: 'Email',
  PHONE: 'Phone',
  ADDRESS: 'Address',
  LOCATION: 'Address',
  DATE: 'Date',
  IP: 'IP',
  IP_ADDRESS: 'IP',
  API_KEY: 'Secret',
  PRIVATE_KEY: 'Secret',
  CREDIT_CARD: 'Secret',
  BANK_ACCOUNT: 'Secret',
  CRYPTO_WALLET: 'Secret',
  GOVERNMENT_ID: 'ID',
  COMPANY_REGISTRATION_NUMBER: 'ID',
  EMPLOYEE_ID: 'ID',
  INVOICE_NUMBER: 'Invoice',
  ORDER_ID: 'Invoice',
  BOOKING_REFERENCE: 'Invoice',
  TICKET_REFERENCE: 'Invoice',
  TRANSACTION_ID: 'Invoice',
  USERNAME: 'Username',
}

const activeDetectors = computed<Record<DetectorKey, boolean>>(() => {
  if (mode.value === 'automatic') {
    return defaultDetectorState()
  }
  return detectorState.value
})

const effectiveReversePronouns = computed(() => mode.value === 'custom' && reversePronounsEnabled.value)

const profileState = computed(() => {
  const detectors = activeDetectors.value
  return {
    pii:
      detectors.person ||
      detectors.organisation ||
      detectors.email ||
      detectors.phone ||
      detectors.date ||
      detectors.address ||
      detectors.id ||
      detectors.invoice ||
      detectors.username,
    secrets: detectors.secret,
    network: detectors.ip,
  }
})

const signature = computed(
  () => `${inputText.value}::${mode.value}::${JSON.stringify(activeDetectors.value)}::${effectiveReversePronouns.value}::${taskContext.value}::${taskDescription.value}`,
)
const hasInput = computed(() => inputText.value.trim().length > 0)
const hasOutput = computed(() => outputText.value.trim().length > 0)
const needsSanitise = computed(() => hasInput.value && signature.value !== lastSignature.value)
const hasStaleOutput = computed(() => hasOutput.value && needsSanitise.value)
const redactionCount = computed(() => result.value?.total ?? 0)
const enabledDetectorCount = computed(
  () => Object.values(detectorState.value).filter(Boolean).length,
)
const detectorTotal = detectorOptions.length
const hasEnabledDetectors = computed(() => enabledDetectorCount.value > 0)
const hasActiveDetectionProfile = computed(() => mode.value === 'automatic' || hasEnabledDetectors.value)
const customDetectorSummary = computed(
  () => `${enabledDetectorCount.value} of ${detectorTotal} rules active`,
)

const renderedLines = computed(() => {
  if (!outputText.value) return [] as Array<Array<{ text: string; tokenType?: TokenType }>>
  return outputText.value.split('\n').map((line) => splitOutputByTokens(line))
})

const adaptiveRenderedLines = computed(() => {
  const adaptiveOutput = result.value?.adaptive?.adaptive_text || ''
  if (!adaptiveOutput) return [] as Array<Array<{ text: string; tokenType?: TokenType }>>
  return canonicalizeBackendTokens(adaptiveOutput).split('\n').map((line) => splitOutputByTokens(line))
})

const adaptiveSummary = computed(() => {
  const adaptive = result.value?.adaptive
  if (!adaptive) return [] as string[]
  const actionLabels: Record<string, string> = {
    allow: 'kept context',
    placeholder: 'anonymised',
    remove: 'removed',
    block: 'blocked',
    generalise: 'generalised',
    role_substitute: 'role context',
  }
  const actions = adaptive.decisions.reduce<Record<string, number>>((acc, decision) => {
    const label = actionLabels[decision.action] || decision.action.replace(/_/g, ' ')
    acc[label] = (acc[label] || 0) + 1
    return acc
  }, {})
  return Object.entries(actions).map(([action, count]) => `${action} x ${count}`)
})

const detectedSummary = computed(() => {
  if (!result.value || result.value.total === 0) return 'No sensitive entities detected.'
  return `${result.value.total} entities detected`
})

const ctaLabel = computed(() => {
  if (isProcessing.value) return 'Sanitising...'
  if (!hasInput.value) return 'Paste text to sanitise'
  if (!needsSanitise.value) return 'Sanitised'
  return 'Sanitise now'
})

function tokenClass(type: TokenType) {
  return `tool-page__token--${type.toLowerCase()}`
}

function isMobileViewport() {
  return typeof window !== 'undefined' && window.matchMedia('(max-width: 900px)').matches
}

function setInputFocus() {
  if (isMobileViewport()) return
  nextTick(() => {
    inputRef.value?.focus()
    const length = inputText.value.length
    inputRef.value?.setSelectionRange(length, length)
  })
}

function scrollToOutputOnMobile() {
  if (!isMobileViewport()) return
  nextTick(() => {
    outputPanelRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

function clearAll() {
  inputText.value = ''
  outputText.value = ''
  result.value = null
  statusText.value = ''
  copyLabel.value = 'Copy result'
  uploadLabel.value = 'Upload .txt or .pdf'
  lastSignature.value = ''
  setInputFocus()
}

function applyExample(autoSanitise = true) {
  exampleCursor = (exampleCursor + 1) % TOOL_EXAMPLES.length
  const example = TOOL_EXAMPLES[exampleCursor]
  inputText.value = example.text
  taskContext.value = example.context
  taskDescription.value = example.task
  if (autoSanitise) {
    void runSanitise()
  }
  setInputFocus()
}

function toggleDetector(key: DetectorKey) {
  if (detectorState.value[key] && enabledDetectorCount.value === 1) {
    statusText.value = 'Keep at least one detection rule active.'
    return
  }
  detectorState.value[key] = !detectorState.value[key]
}

function setAllDetectors(enabled: boolean) {
  if (!enabled) {
    for (const key of Object.keys(detectorState.value) as DetectorKey[]) {
      detectorState.value[key] = essentialDetectorKeys.includes(key)
    }
    statusText.value = 'Essential rules selected.'
    return
  }

  for (const key of Object.keys(detectorState.value) as DetectorKey[]) {
    detectorState.value[key] = true
  }
  statusText.value = 'All detection rules selected.'
}

function openCustomRules() {
  mode.value = 'custom'
  isCustomRulesOpen.value = true
}

function closeCustomRules() {
  isCustomRulesOpen.value = false
}

function triggerFilePicker() {
  if (isUploading.value || isProcessing.value) return
  fileInputRef.value?.click()
}

function isPdf(file: File) {
  return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
}

function isTextLike(file: File) {
  if (file.type.startsWith('text/')) return true
  const name = file.name.toLowerCase()
  return /\.(txt|md|csv|json|log|xml|yaml|yml|tsv|rtf)$/i.test(name)
}

async function extractPdfText(file: File) {
  const pdfjs = await import('pdfjs-dist/legacy/build/pdf.mjs')
  pdfjs.GlobalWorkerOptions.workerSrc = pdfWorkerUrl

  const data = new Uint8Array(await file.arrayBuffer())
  const document = await pdfjs.getDocument({ data }).promise
  const pages: string[] = []

  for (let pageNumber = 1; pageNumber <= document.numPages; pageNumber += 1) {
    const page = await document.getPage(pageNumber)
    const textContent = await page.getTextContent()
    const pageText = textContent.items
      .map((item: unknown) => {
        if (typeof item === 'object' && item !== null && 'str' in item) {
          return String((item as { str: string }).str)
        }
        return ''
      })
      .join(' ')
      .replace(/\s+/g, ' ')
      .trim()

    if (pageText) {
      pages.push(pageText)
    }
  }

  return pages.join('\n\n')
}

async function readUploadedFile(file: File) {
  if (isPdf(file)) {
    return extractPdfText(file)
  }
  if (isTextLike(file)) {
    return (await file.text()).replace(/\r\n/g, '\n')
  }
  throw new Error('Unsupported file type')
}

async function onFileSelected(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  target.value = ''
  if (!file) return

  isUploading.value = true
  uploadLabel.value = `Loading ${file.name}...`

  try {
    const extracted = await readUploadedFile(file)
    if (!extracted.trim()) {
      throw new Error('No readable text found')
    }

    inputText.value = extracted
    uploadLabel.value = `Loaded ${file.name}`
    statusText.value = `Loaded ${file.name}`
    await runSanitise()
    if (!isMobileViewport()) {
      setInputFocus()
    }
  } catch {
    uploadLabel.value = 'Could not read this file'
    statusText.value = 'Could not read this file type yet. Try .txt, .md, .csv, .json, .log, or .pdf.'
  } finally {
    isUploading.value = false
  }
}

function normalizeBackendLabel(rawLabel: string) {
  return String(rawLabel || '')
    .trim()
    .replace(/\s+/g, ' ')
    .replace(/[_-]+/g, '_')
    .toUpperCase()
}

function canonicalizeBackendTokens(value: string) {
  if (!value) return ''

  const convertedUnderscore = value.replace(/\[([A-Z_]+)_(\d+)\]/g, (full, rawLabel: string, index: string) => {
    const mapped = BACKEND_LABEL_TO_UI[normalizeBackendLabel(rawLabel)]
    return mapped ? `[${mapped} ${index}]` : full
  })

  return convertedUnderscore.replace(/\[([A-Za-z][A-Za-z _-]+)\s+(\d+)\]/g, (full, rawLabel: string, index: string) => {
    const normalized = normalizeBackendLabel(rawLabel)
    const mapped = BACKEND_LABEL_TO_UI[normalized] || BACKEND_LABEL_TO_UI[normalized.replace(/\s+/g, '_')]
    return mapped ? `[${mapped} ${index}]` : full
  })
}

function zeroCounts(): Record<TokenType, number> {
  return {
    Person: 0,
    Organisation: 0,
    Email: 0,
    Phone: 0,
    Date: 0,
    Address: 0,
    IP: 0,
    Secret: 0,
    ID: 0,
    Invoice: 0,
    Username: 0,
  }
}

function buildDetectedLabels(counts: Record<TokenType, number>) {
  return (Object.entries(counts) as Array<[TokenType, number]>)
    .filter(([, count]) => count > 0)
    .sort((a, b) => b[1] - a[1])
    .map(([type, count]) => `${type} x ${count}`)
}

function buildEntityTypes(detectors: Record<DetectorKey, boolean>) {
  const selected = new Set<string>()
  for (const [key, enabled] of Object.entries(detectors) as Array<[DetectorKey, boolean]>) {
    if (!enabled) continue
    for (const entity of DETECTOR_TO_BACKEND_ENTITY[key]) {
      selected.add(entity)
    }
  }
  return [...selected]
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

async function readErrorPayload(response: Response) {
  const contentType = response.headers.get('content-type') || ''
  if (!contentType.includes('application/json')) return null

  try {
    const payload = await response.json()
    return isRecord(payload) ? payload : null
  } catch {
    return null
  }
}

function getApiErrorMessage(status: number, payload: Record<string, unknown> | null) {
  const detail = payload?.detail

  if (isRecord(detail) && detail.code === 'USAGE_LIMIT_EXCEEDED') {
    const used = Number(detail.used)
    const limit = Number(detail.limit)
    const hasUsage = Number.isFinite(used) && Number.isFinite(limit)
    return hasUsage
      ? `Daily limit reached (${used}/${limit} runs used). Try again tomorrow or contact us if you need more capacity.`
      : 'Daily limit reached. Try again tomorrow or contact us if you need more capacity.'
  }

  if (isRecord(detail) && detail.code === 'BOT_CHALLENGE_REQUIRED') {
    return 'Usage check required before this request can run. Please refresh the page and try again.'
  }

  if (typeof detail === 'string') {
    const normalized = detail.toLowerCase()
    if (normalized.includes('input exceeds character limit')) {
      return 'This text is too long to sanitise in one run. Shorten it or split it into smaller sections.'
    }
    if (normalized.includes('text is required')) {
      return 'Paste text before running the sanitiser.'
    }
    if (normalized.includes('no valid entity types selected')) {
      return 'Enable at least one detection rule before running the sanitiser.'
    }
    return detail
  }

  if (status === 413) return 'This text is too long to sanitise in one run. Shorten it or split it into smaller sections.'
  if (status === 429) return 'Daily limit reached. Try again tomorrow or contact us if you need more capacity.'
  if (status === 403) return 'This request was blocked by the usage check. Please refresh the page and try again.'
  if (status >= 500) return 'Sanitisation service is temporarily unavailable. Please try again shortly.'
  return 'Could not sanitise this text. Please check the input and try again.'
}

async function anonymiseViaApi(
  text: string,
  detectors: Record<DetectorKey, boolean>,
  reversePronouns = false,
  purpose = taskContext.value,
) {
  const entity_types = buildEntityTypes(detectors)
  if (entity_types.length === 0) throw new Error('NO_DETECTORS')

  const response = await fetch('/api/anonymize', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      text,
      entity_types,
      tag_style: 'standard',
      reverse_pronouns: reversePronouns,
      reversePronouns: reversePronouns,
      task_context: purpose,
      task_description: taskDescription.value.trim(),
      research_preview: Boolean(taskDescription.value.trim()),
    }),
  })

  if (!response.ok) {
    const payload = await readErrorPayload(response)
    throw new SanitiseApiError(getApiErrorMessage(response.status, payload), response.status)
  }

  const payload = (await response.json()) as {
    anonymized_text?: string
    counts?: Record<string, unknown>
    warning?: string
    analysis?: { summary?: MinimumDisclosureSummary }
    adaptive?: AdaptivePreview
  }

  const output = canonicalizeBackendTokens(String(payload?.anonymized_text || ''))
  const counts = zeroCounts()
  for (const [rawKey, rawValue] of Object.entries(payload?.counts || {})) {
    const count = Number(rawValue)
    if (!Number.isFinite(count) || count <= 0) continue
    const normalized = normalizeBackendLabel(rawKey)
    const mapped = BACKEND_LABEL_TO_UI[normalized] || BACKEND_LABEL_TO_UI[normalized.replace(/\s+/g, '_')]
    if (!mapped) continue
    counts[mapped] += count
  }

  const total = (Object.values(counts) as number[]).reduce((sum, count) => sum + count, 0)
  const detectedLabels = buildDetectedLabels(counts)
  const warning = payload?.warning ? String(payload.warning).trim() : ''

  const result: SanitiseResult = {
    output,
    counts,
    total,
    detectedLabels,
    minimumDisclosure: payload?.analysis?.summary,
    adaptive: payload?.adaptive,
  }

  return { result, warning }
}

async function runSanitise() {
  if (!hasInput.value) return

  if (isMobileViewport()) {
    inputRef.value?.blur()
  }

  isProcessing.value = true
  await new Promise((resolve) => setTimeout(resolve, 260))

  try {
    const { result: sanitised, warning } = await anonymiseViaApi(
      inputText.value,
      activeDetectors.value,
      effectiveReversePronouns.value,
      taskContext.value,
    )
    outputText.value = sanitised.output
    result.value = sanitised
    lastSignature.value = signature.value
    if (warning) {
      statusText.value = warning
    } else {
      statusText.value = sanitised.total > 0 ? `${sanitised.total} entities anonymised` : 'No sensitive entities detected'
    }
    copyLabel.value = 'Copy result'
    outputReveal.value = false
    if (revealTimer) clearTimeout(revealTimer)
    revealTimer = setTimeout(() => {
      outputReveal.value = true
      revealTimer = null
    }, 20)
    scrollToOutputOnMobile()
  } catch (error) {
    if ((error as Error)?.message === 'NO_DETECTORS') {
      statusText.value = 'Enable at least one detection rule.'
    } else if (error instanceof SanitiseApiError) {
      outputText.value = ''
      result.value = null
      statusText.value = error.message
    } else {
      outputText.value = ''
      result.value = null
      statusText.value = 'Network connection lost. Check your connection and try again.'
    }
  } finally {
    isProcessing.value = false
  }
}

async function copyOutput() {
  if (!hasOutput.value) return
  await navigator.clipboard.writeText(outputText.value)
  copyLabel.value = 'Copied'
  window.setTimeout(() => {
    copyLabel.value = 'Copy result'
  }, 1400)
}

function exportText() {
  if (!hasOutput.value) return
  const blob = new Blob([outputText.value], { type: 'text/plain;charset=utf-8' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = 'sanitised-output.txt'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(link.href)
}

function maybeRunDemoFromQuery() {
  if (route.query.demo === '1') {
    applyExample(true)
  }
}

watch(
  () => route.query.demo,
  () => {
    maybeRunDemoFromQuery()
  },
)

watch(mode, (nextMode) => {
  if (nextMode === 'automatic') {
    reversePronounsEnabled.value = false
    isCustomRulesOpen.value = false
  }
})

onMounted(() => {
  maybeRunDemoFromQuery()
  setInputFocus()
})
</script>

<template>
  <main class="tool-page">
    <section class="tool-page__meta">
      <div class="tool-page__intro">
        <p>SanitiseAI tool</p>
        <h1>Paste text. Detect sensitive data. Copy anonymised output.</h1>
      </div>
      <div class="tool-page__secure-pill">
        <span class="tool-page__secure-dot" aria-hidden="true"></span>
        <span>HTTPS processing</span>
      </div>
    </section>

    <section class="tool-page__workspace" aria-label="Sanitiser workspace">
      <article class="tool-page__panel tool-page__panel--input">
        <header class="tool-page__panel-head tool-page__panel-head--input">
          <div class="tool-page__title-wrap">
            <PhMagicWand :size="18" weight="regular" aria-hidden="true" />
            <div>
              <p>Source text</p>
              <small>Paste or upload content</small>
            </div>
          </div>
          <div class="tool-page__head-actions">
            <button class="btn btn--secondary" type="button" @click="applyExample(true)">
              <PhSparkle :size="16" weight="regular" aria-hidden="true" />
              <span>Try example</span>
            </button>
            <button class="btn btn--secondary" type="button" :disabled="isUploading || isProcessing" @click="triggerFilePicker">
              <PhUploadSimple :size="16" weight="regular" aria-hidden="true" />
              <span>{{ isUploading ? 'Uploading...' : 'Upload doc' }}</span>
            </button>
            <input
              ref="fileInputRef"
              class="tool-page__file-input"
              type="file"
              accept=".txt,.md,.csv,.json,.log,.xml,.yaml,.yml,.tsv,.rtf,.pdf,text/*,application/pdf"
              @change="onFileSelected"
            />
          </div>
        </header>

        <textarea
          ref="inputRef"
          v-model="inputText"
          class="tool-page__textarea"
          aria-label="Text to sanitise"
          placeholder="Paste sensitive text, logs, contracts, prompts, medical notes, support chats, or code secrets..."
          @keydown.meta.enter.prevent="runSanitise"
          @keydown.ctrl.enter.prevent="runSanitise"
        ></textarea>

        <div class="tool-page__controls">
          <p class="tool-page__upload-note">{{ uploadLabel }}</p>
          <div class="tool-page__mode" role="group" aria-label="Detection mode">
            <button
              type="button"
              class="tool-page__mode-btn"
              :class="{ 'tool-page__mode-btn--active': mode === 'automatic' }"
              :aria-pressed="mode === 'automatic'"
              @click="mode = 'automatic'"
            >
              Automatic
            </button>
            <button
              type="button"
              class="tool-page__mode-btn"
              :class="{ 'tool-page__mode-btn--active': mode === 'custom' }"
              :aria-pressed="mode === 'custom'"
              @click="openCustomRules"
            >
              Custom rules
            </button>
          </div>

          <div v-if="isCustomRulesOpen" class="tool-page__rules-modal" role="dialog" aria-modal="true" aria-labelledby="custom-rules-title" @keydown.esc="closeCustomRules">
            <div class="tool-page__rules-backdrop" aria-hidden="true" @click="closeCustomRules"></div>
            <section class="tool-page__rules-sheet">
              <header class="tool-page__rules-head">
                <div>
                  <p id="custom-rules-title">Custom detection rules</p>
                  <small>{{ customDetectorSummary }}</small>
                </div>
                <button class="tool-page__rules-close" type="button" aria-label="Close custom rules" @click="closeCustomRules">×</button>
              </header>

              <div class="tool-page__custom-actions" aria-label="Custom rule presets">
                <button type="button" @click="setAllDetectors(true)">All rules</button>
                <button type="button" @click="setAllDetectors(false)">Essential only</button>
              </div>

              <div class="tool-page__detectors">
                <button
                  v-for="item in detectorOptions"
                  :key="item.key"
                  type="button"
                  class="tool-page__detector"
                  :class="{ 'tool-page__detector--active': detectorState[item.key] }"
                  :aria-pressed="detectorState[item.key]"
                  @click="toggleDetector(item.key)"
                >
                  <span class="tool-page__detector-check" aria-hidden="true">
                    <PhCheckCircle :size="13" weight="fill" />
                  </span>
                  <span>
                    <strong>{{ item.label }}</strong>
                    <small>{{ item.hint }}</small>
                  </span>
                </button>
              </div>

              <div class="tool-page__reverse-toggle">
                <div class="tool-page__reverse-copy">
                  <span>Reverse pronouns</span>
                  <small>Optional output transform for English text</small>
                </div>
                <button
                  type="button"
                  class="tool-page__reverse-switch"
                  :class="{ 'tool-page__reverse-switch--active': reversePronounsEnabled }"
                  :aria-pressed="reversePronounsEnabled"
                  :aria-label="reversePronounsEnabled ? 'Disable reverse pronouns' : 'Enable reverse pronouns'"
                  @click="reversePronounsEnabled = !reversePronounsEnabled"
                >
                  <span class="tool-page__reverse-knob" aria-hidden="true"></span>
                </button>
              </div>
            </section>
          </div>

          <div class="tool-page__actions">
            <p class="tool-page__privacy-note">
              Privacy Note: Text is sent to the sanitisation API over HTTPS for processing. Raw input is not stored.
            </p>
            <button class="btn btn--ghost" type="button" :disabled="!hasInput || isProcessing" @click="clearAll">
              <PhEraser :size="16" weight="regular" aria-hidden="true" />
              <span>Clear</span>
            </button>
            <button
              class="btn btn--primary"
              type="button"
              :disabled="!hasInput || isProcessing || !needsSanitise || !hasActiveDetectionProfile"
              @click="runSanitise"
            >
              <PhMagicWand :size="16" weight="fill" aria-hidden="true" />
              <span>{{ ctaLabel }}</span>
            </button>
          </div>
        </div>
      </article>

      <div class="tool-page__output-column">
        <article ref="outputPanelRef" class="tool-page__panel tool-page__panel--output">
          <header class="tool-page__panel-head tool-page__panel-head--output">
            <div class="tool-page__title-wrap tool-page__title-wrap--light">
              <PhShieldCheck :size="18" weight="fill" aria-hidden="true" />
              <div>
                <p>Sanitised output</p>
              </div>
            </div>
            <span class="tool-page__result-badge">{{ redactionCount }} redactions</span>
          </header>

          <div class="tool-page__output-shell">
            <div
              class="tool-page__output"
              :class="{ 'tool-page__output--reveal': outputReveal }"
              role="region"
              aria-label="Sanitised result"
              aria-live="polite"
            >
              <div v-if="hasStaleOutput" class="tool-page__stale-notice" role="status">
                Input or detection settings changed. Run sanitise again before copying this result.
              </div>

              <template v-if="renderedLines.length">
                <p v-for="(line, lineIndex) in renderedLines" :key="lineIndex" class="tool-page__line">
                  <template v-for="(part, partIndex) in line" :key="`${lineIndex}-${partIndex}`">
                    <span v-if="part.tokenType" class="tool-page__token" :class="tokenClass(part.tokenType)">{{ part.text }}</span>
                    <span v-else>{{ part.text }}</span>
                  </template>
                </p>
              </template>
              <p v-else class="tool-page__placeholder">Anonymised output appears here after detection runs.</p>
            </div>

            <div v-if="isProcessing" class="tool-page__spinner" role="status" aria-live="polite">
              <span class="tool-page__spinner-ring" aria-hidden="true"></span>
              <span>Processing</span>
            </div>
          </div>

          <footer v-if="result && result.detectedLabels.length" class="tool-page__summary" role="status" aria-live="polite">
            <PhShieldCheck :size="16" weight="fill" aria-hidden="true" />
            <ul>
              <li v-for="label in result.detectedLabels" :key="label">{{ label }}</li>
            </ul>
          </footer>

          <footer v-else-if="statusText" class="tool-page__summary tool-page__summary--empty" role="status" aria-live="polite">
            <PhCheckCircle :size="16" weight="regular" aria-hidden="true" />
            <p>{{ statusText }}</p>
          </footer>

          <div class="tool-page__output-actions">
            <button class="btn tool-page__action-btn tool-page__action-btn--light" type="button" :disabled="!hasOutput || hasStaleOutput || isProcessing" @click="copyOutput">
              <PhCopy :size="16" weight="regular" aria-hidden="true" />
              <span>{{ hasStaleOutput ? 'Run again first' : copyLabel }}</span>
            </button>
            <button class="btn btn--primary tool-page__action-btn" type="button" :disabled="!hasOutput || hasStaleOutput || isProcessing" @click="exportText">
              <PhDownloadSimple :size="16" weight="regular" aria-hidden="true" />
              <span>Export .txt</span>
            </button>
          </div>
        </article>

        <aside class="tool-page__profile" :class="{ 'tool-page__profile--guidance': result?.minimumDisclosure }">
          <template v-if="result?.minimumDisclosure">
            <div class="tool-page__profile-copy">
              <span class="tool-page__profile-kicker">
                <PhSparkle :size="14" weight="fill" aria-hidden="true" />
                Minimum disclosure
                <span
                  class="tool-page__tooltip"
                  tabindex="0"
                  role="img"
                  aria-label="AI context helps SanitiseAI decide what can be safely removed while preserving useful meaning."
                  title="AI context helps SanitiseAI decide what can be safely removed while preserving useful meaning."
                >?</span>
              </span>
              <strong>{{ result.minimumDisclosure.task_label }}</strong>
              <p>{{ result.minimumDisclosure.guidance }}</p>
            </div>
            <dl class="tool-page__profile-metrics" aria-label="Minimum disclosure summary">
              <div>
                <dt>Critical</dt>
                <dd>{{ result.minimumDisclosure.critical_entities }}</dd>
              </div>
              <div>
                <dt>High</dt>
                <dd>{{ result.minimumDisclosure.high_entities }}</dd>
              </div>
              <div>
                <dt>Review</dt>
                <dd>{{ result.minimumDisclosure.recommended_actions.review || 0 }}</dd>
              </div>
            </dl>
          </template>
          <template v-else>
            <p>Detection profile</p>
            <ul>
              <li :class="{ 'is-on': profileState.pii }">
                <PhCheckCircle :size="14" weight="fill" aria-hidden="true" />
                PII
              </li>
              <li :class="{ 'is-on': profileState.secrets }">
                <PhCheckCircle :size="14" weight="fill" aria-hidden="true" />
                Secrets
              </li>
              <li :class="{ 'is-on': profileState.network }">
                <PhCheckCircle :size="14" weight="fill" aria-hidden="true" />
                Network
              </li>
            </ul>
          </template>
        </aside>
      </div>
    </section>

    <section v-if="result?.adaptive" class="tool-page__insights tool-page__insights--single" aria-label="Task-aware preview">
      <article class="tool-page__adaptive-card" role="status">
        <header>
          <div>
            <span class="tool-page__insight-kicker">Task-aware preview</span>
            <strong>{{ result.adaptive.metrics.irrelevant_sensitive_suppression * 100 }}% unnecessary sensitive facts suppressed</strong>
          </div>
          <ul v-if="adaptiveSummary.length" class="tool-page__adaptive-summary">
            <li v-for="item in adaptiveSummary" :key="item">{{ item }}</li>
          </ul>
        </header>
        <div class="tool-page__adaptive-output">
          <p v-for="(line, lineIndex) in adaptiveRenderedLines" :key="`adaptive-${lineIndex}`">
            <template v-for="(part, partIndex) in line" :key="`adaptive-${lineIndex}-${partIndex}`">
              <span v-if="part.tokenType" class="tool-page__token" :class="tokenClass(part.tokenType)">{{ part.text }}</span>
              <span v-else>{{ part.text }}</span>
            </template>
          </p>
        </div>
      </article>
    </section>
  </main>
</template>

<style scoped lang="scss">
.tool-page {
  width: min(1320px, calc(100% - 2.4rem));
  margin: 0 auto;
  padding-top: 1.1rem;

  &__meta {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 0.9rem;

    > p {
      margin: 0;
      color: var(--text-3);
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-weight: 760;
    }
  }

  &__intro {
    min-width: 0;

    p {
      margin: 0;
      color: var(--accent-1);
      font-size: 0.68rem;
      font-weight: 780;
      letter-spacing: 0.16em;
      text-transform: uppercase;
    }

    h1 {
      margin: 0.22rem 0 0;
      color: var(--text-1);
      font-family: Manrope, Inter, sans-serif;
      font-size: clamp(1.55rem, 2.4vw, 2.35rem);
      line-height: 1.06;
      letter-spacing: 0;
      font-weight: 820;
    }
  }

  &__secure-pill {
    border-radius: var(--radius-sm);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 32%);
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 28%);
    padding: 0.5rem 0.82rem;
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;

    span {
      color: var(--text-2);
      font-size: 0.8rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
  }

  &__secure-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #16a34a;
    box-shadow: 0 0 0 6px color-mix(in srgb, #16a34a, transparent 84%);
  }

  &__workspace {
    margin-top: 0.8rem;
    display: grid;
    grid-template-columns: minmax(0, 1.08fr) minmax(0, 0.9fr);
    gap: 1rem;
    height: clamp(500px, calc(100vh - 218px), 720px);
    height: clamp(500px, calc(100dvh - 218px), 720px);
  }

  &__panel {
    border-radius: var(--radius-lg);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 36%);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    min-height: 0;
    height: 100%;
  }

  &__panel--input {
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 26%);
    position: relative;
  }

  &__panel--output {
    background: #0b1735;
    color: #e6efff;
    border: 0;
    box-shadow: none;
    position: relative;

    &::before {
      content: '';
      position: absolute;
      inset: 0;
      background-image: radial-gradient(circle at center, rgba(74, 113, 220, 0.22) 1px, transparent 1.4px);
      background-size: 22px 22px;
      opacity: 0.28;
      pointer-events: none;
    }
  }

  &__output-column {
    display: grid;
    gap: 0.8rem;
    grid-template-rows: minmax(0, 1fr) auto;
    min-height: 0;
  }

  &__panel-head {
    position: relative;
    z-index: 1;
    padding: 1rem 1rem 0.9rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.7rem;
    border-bottom: 1px solid color-mix(in srgb, var(--border-1), transparent 30%);
  }

  &__panel-head--output {
    border-bottom-color: rgba(146, 174, 255, 0.15);
  }

  &__head-actions {
    display: inline-flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.48rem;

    .btn {
      min-height: 40px;
      padding-inline: 0.82rem;
    }
  }

  &__file-input {
    display: none;
  }

  &__title-wrap {
    display: inline-flex;
    align-items: center;
    gap: 0.52rem;

    svg {
      color: var(--accent-1);
      flex-shrink: 0;
    }

    p {
      margin: 0;
      color: var(--text-1);
      font-size: 0.92rem;
      font-weight: 770;
      letter-spacing: -0.01em;
      text-transform: none;
    }

    small {
      color: var(--text-3);
      font-size: 0.68rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-weight: 760;
    }
  }

  &__title-wrap--light {
    svg,
    p,
    small {
      color: #d9e8ff;
    }

    small {
      color: #9db5e8;
    }
  }

  &__result-badge {
    border-radius: var(--radius-sm);
    background: rgba(47, 95, 222, 0.4);
    border: 1px solid rgba(118, 152, 236, 0.42);
    color: #8db5ff;
    padding: 0.24rem 0.54rem;
    font-size: 0.66rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 760;
  }

  &__textarea {
    margin: 0;
    width: 100%;
    min-height: 0;
    flex: 1;
    resize: vertical;
    border: 0;
    background: transparent;
    color: var(--text-1);
    padding: 1.05rem 1.1rem;
    font-size: 0.98rem;
    line-height: 1.7;
    scrollbar-gutter: stable;

    &:focus-visible {
      outline: none;
      box-shadow: inset var(--ring);
    }
  }

  &__controls {
    border-top: 1px solid color-mix(in srgb, var(--border-1), transparent 28%);
    padding: 0.86rem 1rem 1rem;
    display: grid;
    gap: 0.66rem;
  }

  &__upload-note {
    margin: 0;
    color: var(--text-3);
    font-size: 0.72rem;
    letter-spacing: 0.04em;
    font-weight: 670;
  }

  &__mode {
    width: fit-content;
    max-width: 100%;
    display: inline-grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.25rem;
    padding: 0.24rem;
    border-radius: var(--radius-sm);
    background: color-mix(in srgb, var(--surface-2), white 24%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 36%);
  }

  &__mode-btn {
    border: 1px solid transparent;
    border-radius: 6px;
    background: transparent;
    color: var(--text-3);
    font-size: 0.8rem;
    font-weight: 700;
    padding: 0.44rem 0.64rem;
    cursor: pointer;
    transition: background 180ms ease, color 180ms ease, border-color 180ms ease;

    &:hover,
    &:focus-visible {
      color: var(--text-1);
      box-shadow: var(--ring);
    }
  }

  &__mode-btn--active {
    color: var(--text-1);
    border-color: color-mix(in srgb, var(--border-2), transparent 34%);
    background: color-mix(in srgb, var(--surface-0), var(--accent-soft) 10%);
    box-shadow: 0 2px 4px rgba(14, 22, 38, 0.05);
  }

  &__rules-modal {
    position: absolute;
    inset: 0;
    z-index: 20;
    display: grid;
    min-height: 0;
  }

  &__rules-backdrop {
    position: absolute;
    inset: 0;
    background: rgba(247, 249, 253, 0.76);
    backdrop-filter: blur(10px);
  }

  &__rules-sheet {
    position: relative;
    z-index: 1;
    margin: 0.7rem;
    border-radius: var(--radius-lg);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 28%);
    background: rgba(255, 255, 255, 0.95);
    box-shadow: 0 24px 60px rgba(15, 35, 82, 0.14);
    overflow: auto;
    display: flex;
    flex-direction: column;
    gap: 0.72rem;
    padding: 0.78rem;
  }

  &__rules-head {
    position: sticky;
    top: -0.78rem;
    z-index: 2;
    margin: -0.78rem -0.78rem 0;
    padding: 0.82rem 0.88rem;
    border-bottom: 1px solid color-mix(in srgb, var(--border-1), transparent 44%);
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(12px);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.75rem;

    p {
      margin: 0;
      color: var(--text-1);
      font-size: 0.95rem;
      font-weight: 820;
    }

    small {
      display: block;
      margin-top: 0.12rem;
      color: var(--text-3);
      font-size: 0.7rem;
      font-weight: 680;
    }
  }

  &__rules-close {
    width: 34px;
    height: 34px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 34%);
    border-radius: 999px;
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 26%);
    color: var(--text-2);
    font-size: 1.25rem;
    line-height: 1;
    font-weight: 650;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: transform 160ms ease, color 160ms ease, border-color 160ms ease;

    &:hover,
    &:focus-visible {
      color: var(--accent-3);
      border-color: color-mix(in srgb, var(--accent-1), transparent 48%);
      transform: scale(1.04);
      box-shadow: var(--ring);
    }
  }

  &__custom-actions {
    display: inline-flex;
    align-items: center;
    gap: 0.36rem;
    flex-shrink: 0;

    button {
      border: 1px solid color-mix(in srgb, var(--border-1), transparent 26%);
      border-radius: 999px;
      background: color-mix(in srgb, var(--surface-0), var(--surface-2) 34%);
      color: var(--text-2);
      min-height: 32px;
      padding: 0.26rem 0.62rem;
      font-size: 0.7rem;
      font-weight: 740;
      cursor: pointer;

      &:hover,
      &:focus-visible {
        color: var(--accent-3);
        border-color: color-mix(in srgb, var(--accent-1), transparent 48%);
      }
    }
  }

  &__detectors {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(168px, 1fr));
    gap: 0.42rem;
  }

  &__detector {
    border-radius: var(--radius-sm);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 34%);
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 38%);
    min-height: 58px;
    padding: 0.48rem 0.54rem;
    text-align: left;
    cursor: pointer;
    color: var(--text-2);
    transition: border-color 180ms ease, background 180ms ease, color 180ms ease;
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    align-items: start;
    gap: 0.42rem;

    strong {
      display: block;
      color: inherit;
      font-size: 0.74rem;
      line-height: 1.22;
      font-weight: 740;
    }

    small {
      display: block;
      margin-top: 0.12rem;
      color: var(--text-3);
      font-size: 0.66rem;
      line-height: 1.28;
      font-weight: 620;
    }

    &:focus-visible {
      box-shadow: var(--ring);
    }
  }

  &__detector--active {
    border-color: color-mix(in srgb, var(--accent-2), transparent 44%);
    background: color-mix(in srgb, var(--accent-soft), white 56%);
    color: var(--accent-3);

    .tool-page__detector-check {
      color: var(--accent-1);
      opacity: 1;
    }
  }

  &__detector-check {
    color: var(--text-3);
    opacity: 0.32;
    line-height: 0;
    margin-top: 0.12rem;
  }

  &__reverse-toggle {
    margin-top: 0.08rem;
    padding-top: 0.5rem;
    border-top: 1px solid color-mix(in srgb, var(--border-1), transparent 46%);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.8rem;
  }

  &__reverse-copy {
    display: grid;
    gap: 0.16rem;

    span {
      font-size: 0.76rem;
      font-weight: 740;
      line-height: 1.18;
      color: var(--text-2);
    }

    small {
      font-size: 0.67rem;
      color: var(--text-3);
      font-weight: 640;
    }
  }

  &__reverse-switch {
    width: 44px;
    height: 26px;
    flex-shrink: 0;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 24%);
    border-radius: 999px;
    background: color-mix(in srgb, var(--surface-2), white 12%);
    padding: 2px;
    cursor: pointer;
    transition: background 180ms ease, border-color 180ms ease, box-shadow 180ms ease;

    &:focus-visible {
      box-shadow: var(--ring);
    }
  }

  &__reverse-switch--active {
    background: color-mix(in srgb, var(--accent-1), white 14%);
    border-color: color-mix(in srgb, var(--accent-2), transparent 36%);
  }

  &__reverse-knob {
    display: block;
    width: 20px;
    height: 20px;
    border-radius: 999px;
    background: white;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.18);
    transition: transform 180ms ease;
  }

  &__reverse-switch--active &__reverse-knob {
    transform: translateX(18px);
  }

  &__actions {
    display: grid;
    grid-template-columns: 1fr auto auto;
    align-items: center;
    gap: 0.6rem;

    .btn {
      min-height: 44px;
    }

    .btn--primary {
      min-width: 132px;
    }
  }

  &__privacy-note {
    margin: 0;
    color: #126d45;
    font-size: 0.84rem;
    line-height: 1.45;
    font-weight: 640;
  }

  &__output-shell {
    position: relative;
    z-index: 1;
    flex: 1;
    padding: 0;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  &__output {
    border-radius: 0;
    border: 0;
    background: transparent;
    padding: 1rem 1rem 0.8rem;
    min-height: 0;
    max-height: none;
    flex: 1;
    overflow: auto;
    color: #dde9ff;
    font-size: 0.98rem;
    line-height: 1.76;
  }

  &__output--reveal {
    animation: output-fade-in 360ms cubic-bezier(0.22, 0.9, 0.3, 1) both;
  }

  &__line {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
  }

  &__placeholder {
    margin: 0;
    color: #a8bde6;
    font-size: 0.9rem;
  }

  &__stale-notice {
    margin: 0 0 0.78rem;
    border-radius: var(--radius-sm);
    border: 1px solid rgba(251, 191, 36, 0.38);
    background: rgba(120, 76, 5, 0.42);
    color: #fde68a;
    padding: 0.56rem 0.68rem;
    font-size: 0.82rem;
    line-height: 1.45;
    font-weight: 720;
  }

  &__token {
    display: inline-flex;
    align-items: center;
    border-radius: 6px;
    border: 1px solid transparent;
    padding: 0.15rem 0.58rem;
    margin: 0.04rem 0.14rem;
    white-space: nowrap;
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.82rem;
    font-weight: 720;
    letter-spacing: -0.01em;
  }

  &__token--person {
    background: color-mix(in srgb, #dbeafe, white 18%);
    border-color: color-mix(in srgb, #3b82f6, transparent 38%);
    color: color-mix(in srgb, #1d4ed8, black 8%);
  }

  &__token--organisation {
    background: color-mix(in srgb, #ede9fe, white 14%);
    border-color: color-mix(in srgb, #8b5cf6, transparent 38%);
    color: color-mix(in srgb, #6d28d9, black 8%);
  }

  &__token--email {
    background: color-mix(in srgb, #dbeafe, white 22%);
    border-color: color-mix(in srgb, #2563eb, transparent 36%);
    color: color-mix(in srgb, #1e40af, black 8%);
  }

  &__token--phone {
    background: color-mix(in srgb, #cffafe, white 24%);
    border-color: color-mix(in srgb, #0891b2, transparent 40%);
    color: color-mix(in srgb, #155e75, black 8%);
  }

  &__token--date {
    background: color-mix(in srgb, #fef3c7, white 18%);
    border-color: color-mix(in srgb, #d97706, transparent 42%);
    color: color-mix(in srgb, #92400e, black 6%);
  }

  &__token--address {
    background: color-mix(in srgb, #dcfce7, white 24%);
    border-color: color-mix(in srgb, #16a34a, transparent 40%);
    color: color-mix(in srgb, #166534, black 10%);
  }

  &__token--ip,
  &__token--id,
  &__token--secret,
  &__token--invoice,
  &__token--username {
    background: color-mix(in srgb, #fee2e2, white 22%);
    border-color: color-mix(in srgb, #dc2626, transparent 42%);
    color: color-mix(in srgb, #991b1b, black 6%);
  }

  &__spinner {
    position: absolute;
    right: 1.2rem;
    bottom: 0.6rem;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    border-radius: var(--radius-sm);
    border: 1px solid rgba(118, 152, 236, 0.44);
    background: rgba(11, 29, 72, 0.88);
    padding: 0.24rem 0.52rem;
    color: #a2c0ff;
    font-size: 0.75rem;
    font-weight: 700;
  }

  &__spinner-ring {
    width: 11px;
    height: 11px;
    border-radius: 999px;
    border: 2px solid rgba(118, 152, 236, 0.24);
    border-top-color: #6b95ff;
    animation: spin 680ms linear infinite;
  }

  &__summary {
    position: relative;
    z-index: 1;
    margin: 0.7rem 1rem 0;
    border-radius: var(--radius-sm);
    border: 1px solid rgba(118, 152, 236, 0.2);
    background: rgba(12, 28, 66, 0.72);
    padding: 0.54rem 0.66rem;
    display: flex;
    align-items: center;
    gap: 0.52rem;

    svg {
      color: #84acff;
      flex-shrink: 0;
    }

    ul {
      margin: 0;
      padding: 0;
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      gap: 0.42rem;

      li {
        border-radius: 6px;
        background: rgba(49, 90, 184, 0.34);
        color: #a7c4ff;
        padding: 0.2rem 0.48rem;
        font-size: 0.72rem;
        font-weight: 760;
      }
    }

    p {
      margin: 0;
      color: #b4c9f3;
      font-size: 0.83rem;
      font-weight: 650;
    }
  }

  &__summary--empty {
    background: rgba(12, 28, 66, 0.56);
  }

  &__output-actions {
    position: relative;
    z-index: 1;
    margin-top: auto;
    padding: 1rem;
    border-top: 1px solid rgba(146, 174, 255, 0.18);
    background: rgba(4, 12, 32, 0.72);
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.62rem;
  }

  &__action-btn {
    min-height: 54px;
    font-size: 0.92rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-weight: 760;
    justify-content: center;
  }

  &__action-btn--light {
    background: #edf1fa;
    border-color: #dbe4f4;
    color: #121827;
  }

  &__profile {
    border-radius: var(--radius-lg);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 34%);
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 30%);
    padding: 0.86rem 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;

    p {
      margin: 0;
      color: var(--text-3);
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-weight: 760;
    }

    ul {
      margin: 0;
      padding: 0;
      list-style: none;
      display: inline-flex;
      align-items: center;
      gap: 1rem;

      li {
        color: var(--text-3);
        font-size: 0.95rem;
        font-weight: 650;
        display: inline-flex;
        align-items: center;
        gap: 0.36rem;

        svg {
          color: color-mix(in srgb, var(--text-3), transparent 14%);
        }
      }

      li.is-on {
        color: var(--text-2);

        svg {
          color: var(--accent-1);
        }
      }
    }
  }

  &__profile--guidance {
    padding: 0.78rem 0.92rem;
    align-items: center;
  }

  &__profile-copy {
    min-width: 0;
    display: grid;
    gap: 0.16rem;

    strong {
      color: var(--text-1);
      font-size: 0.88rem;
      line-height: 1.18;
      font-weight: 800;
    }

    p {
      max-width: 46ch;
      margin: 0;
      color: var(--text-3);
      font-size: 0.72rem;
      line-height: 1.32;
      letter-spacing: 0;
      text-transform: none;
      font-weight: 650;
    }
  }

  &__profile-kicker {
    color: var(--text-3);
    font-family: var(--font-label);
    font-size: 0.58rem;
    font-weight: 780;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    display: inline-flex;
    align-items: center;
    gap: 0.28rem;

    svg {
      color: var(--accent-1);
    }
  }

  &__tooltip {
    width: 15px;
    height: 15px;
    border-radius: 999px;
    background: color-mix(in srgb, var(--accent-soft), white 22%);
    color: var(--accent-3);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.62rem;
    font-weight: 850;
    cursor: help;
  }

  &__profile-metrics {
    margin: 0;
    display: grid;
    grid-template-columns: repeat(3, minmax(62px, 1fr));
    gap: 0.42rem;
    flex-shrink: 0;

    div {
      min-width: 0;
      border-radius: 10px;
      background: color-mix(in srgb, var(--surface-0), var(--accent-soft) 18%);
      padding: 0.42rem 0.5rem;
    }

    dt {
      color: var(--text-3);
      font-size: 0.52rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      font-weight: 800;
    }

    dd {
      margin: 0.08rem 0 0;
      color: var(--accent-3);
      font-size: 0.92rem;
      line-height: 1;
      font-weight: 840;
    }
  }

  &__insights {
    margin-top: 0.8rem;
    display: grid;
    grid-template-columns: minmax(0, 0.82fr) minmax(0, 1.18fr);
    gap: 0.9rem;
    align-items: stretch;
  }

  &__insights--single {
    grid-template-columns: 1fr;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.tool-page__disclosure-card,
.tool-page__adaptive-card {
  min-width: 0;
  border-radius: var(--radius-lg);
  border: 1px solid color-mix(in srgb, var(--border-1), transparent 44%);
  background: linear-gradient(135deg, color-mix(in srgb, var(--surface-0), white 20%), color-mix(in srgb, var(--surface-0), var(--accent-soft) 10%));
  box-shadow: none;
}

.tool-page__insight-kicker {
  display: block;
  margin-bottom: 0.28rem;
  color: var(--text-3);
  font-family: var(--font-label);
  font-size: 0.64rem;
  font-weight: 780;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.tool-page__disclosure-card {
  padding: 1rem;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: center;

  strong {
    display: block;
    color: var(--text-1);
    font-size: 1rem;
    line-height: 1.2;
    font-weight: 800;
  }

  p {
    max-width: 54ch;
    margin: 0.32rem 0 0;
    color: var(--text-3);
    font-size: 0.82rem;
    line-height: 1.45;
    font-weight: 620;
  }

  dl {
    margin: 0;
    display: grid;
    grid-template-columns: repeat(3, minmax(74px, 1fr));
    gap: 0.5rem;
  }

  dl > div {
    border-radius: var(--radius-sm);
    background: color-mix(in srgb, var(--surface-0), var(--accent-soft) 22%);
    padding: 0.55rem 0.65rem;
  }

  dt {
    color: var(--text-3);
    font-size: 0.58rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 780;
  }

  dd {
    margin: 0.1rem 0 0;
    color: var(--accent-3);
    font-size: 1.05rem;
    line-height: 1;
    font-weight: 840;
  }
}

.tool-page__adaptive-card {
  padding: 1rem;
  display: grid;
  gap: 0.9rem;

  > header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    align-items: flex-start;
  }

  strong {
    display: block;
    color: var(--text-1);
    font-size: 1rem;
    line-height: 1.25;
    font-weight: 800;
  }
}

.tool-page__adaptive-summary {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 0.38rem;
  max-width: 320px;
}

.tool-page__adaptive-summary li {
  border-radius: 999px;
  background: color-mix(in srgb, var(--accent-soft), white 32%);
  color: var(--accent-3);
  padding: 0.22rem 0.5rem;
  font-size: 0.68rem;
  line-height: 1.15;
  font-weight: 760;
}

.tool-page__adaptive-output {
  max-height: 220px;
  overflow: auto;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #0b1735, #08122b);
  color: #dde9ff;
  padding: 0.8rem;
  font-size: 0.82rem;
  line-height: 1.6;

  p {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
  }
}

@keyframes output-fade-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1180px) {
  .tool-page {
    width: min(1320px, calc(100% - 1rem));

    &__workspace {
      grid-template-columns: 1fr;
      height: auto;
    }

    &__output-column {
      grid-template-rows: minmax(0, 1fr) auto;
    }

    &__panel {
      min-height: 520px;
      height: auto;
    }

    &__panel--output {
      min-height: 480px;
    }
  }
}

@media (max-width: 900px) {
  .tool-page {
    &__head-actions {
      width: 100%;

      .btn {
        flex: 1 1 170px;
      }
    }

    &__panel-head--input {
      align-items: flex-start;
    }

    &__meta {
      justify-content: space-between;
      align-items: flex-end;
    }

    &__actions {
      grid-template-columns: 1fr;

      .btn {
        width: 100%;
      }
    }

    &__profile {
      flex-direction: column;
      align-items: flex-start;

      ul {
        width: 100%;
        justify-content: space-between;
      }
    }

    &__insights {
      grid-template-columns: 1fr;
    }

    &__disclosure-card {
      grid-template-columns: 1fr;
    }

    &__detectors {
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    }

    &__textarea {
      min-height: 280px;
    }

    &__reverse-toggle {
      align-items: flex-start;
    }
  }
}

@media (max-width: 680px) {
  .tool-page {
    width: min(1320px, calc(100% - 0.75rem));
    padding-top: 0.7rem;

    &__meta {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }

    &__intro h1 {
      font-size: clamp(1.45rem, 8vw, 2rem);
    }

    &__secure-pill {
      width: 100%;
      justify-content: center;
      padding: 0.46rem 0.6rem;
    }

    &__panel-head {
      flex-direction: column;
      align-items: flex-start;
    }

    &__head-actions {
      width: 100%;

      .btn {
        width: 100%;
      }
    }

    &__panel {
      min-height: auto;
    }

    &__panel--input,
    &__panel--output {
      min-height: 440px;
    }

    &__panel-head,
    &__controls,
    &__output,
    &__output-actions {
      padding-inline: 0.78rem;
    }

    &__mode {
      width: 100%;
    }

    &__mode-btn {
      min-height: 40px;
    }

    &__rules-sheet {
      margin: 0.5rem;
      padding: 0.62rem;
    }

    &__rules-head {
      top: -0.62rem;
      margin: -0.62rem -0.62rem 0;
      padding: 0.72rem;
    }

    &__custom-actions,
    &__custom-actions button {
      width: 100%;
    }

    &__custom-actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
    }

    &__detectors {
      grid-template-columns: 1fr;
    }

    &__adaptive-card > header {
      flex-direction: column;
    }

    &__adaptive-summary {
      justify-content: flex-start;
      max-width: none;
    }

    &__detector {
      min-height: 56px;
    }

    &__reverse-toggle {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.6rem;
    }

    &__output-actions {
      grid-template-columns: 1fr;
    }

    &__profile {
      ul {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
      }
    }
  }
}

</style>
