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

type SanitiseResult = {
  output: string
  counts: Record<TokenType, number>
  total: number
  detectedLabels: string[]
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
const detectorState = ref(defaultDetectorState())
const result = ref<SanitiseResult | null>(null)
const statusText = ref('')
const lastSignature = ref('')
const outputReveal = ref(false)
let revealTimer: ReturnType<typeof setTimeout> | null = null
let exampleCursor = -1

const TOOL_EXAMPLES = [
  [
    'Software subscription agreement (first page excerpt)',
    'Agreement date: 18 March 2026',
    'Customer: Westbridge Procurement Ltd',
    'Customer signatory: Hannah Price (h.price@westbridge.co.uk)',
    'Vendor signatory: Mark Ellis (mark.ellis@orbitstack.io)',
    'Registered address: 17 Bishopsgate, London EC2N 3AR',
    'Invoice reference: INV-2026-0318-778',
    'Emergency contact: +44 7700 932100',
  ].join('\n'),
  [
    'MSA amendment summary',
    'Client: BrightEdge Consulting Ltd',
    'Legal contact: Sarah Thompson',
    'Email: sarah.thompson@brightedge.co.uk',
    'Phone: +44 7700 900123',
    'Registered office: 1 Finsbury Square, London EC2A 1AE',
    'Invoice #: INV-88421',
  ].join('\n'),
  [
    'NHS referral note',
    'Patient: Eleanor Matthews (DOB: 14/02/1988)',
    'NHS no: 943 476 1820',
    'Consultant: Dr James Holloway',
    'Email: james.holloway@westbrook-hospital.nhs.uk',
    'Phone: +44 7700 901144',
    'Address: 43 Hawthorn Road, Leeds LS7 2AA',
    'GP practice: Westbrook Family Clinic',
    'Follow-up date: 29 March 2026',
  ].join('\n'),
  [
    'Chat transcript - customer escalation',
    'User: We need this complaint summary rewritten before sending to support.',
    'Assistant: Share the details and I can draft it.',
    'User: Customer is Priya Nair, email priya.nair@contoso.com, callback +44 7700 945611.',
    'User: Order ID ORD-884129, delivery address 9 Rivington Street, London EC2A 3DT.',
    'Assistant: Noted. I will anonymise identifiers first.',
  ].join('\n'),
  [
    'Production auth incident - API gateway',
    'Owner: Alice Morgan',
    'GitHub user: alice-morgan-dev',
    'Email: alice.morgan@contoso.dev',
    'Pager: +44 7700 900456',
    'Host: 10.12.8.32',
    'GitHub SSH key: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH8G2Ud4h6ZcF1b8Q8kTWX5q2e4w9rjQ7w2L2N2 alice@contoso',
    'Access token: ghp_u7QxY3nN9aK1dL4mZ8tW2pR6hC0vB5e',
    'AWS key: AKIAIOSFODNN7EXAMPLE',
    'JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.signatureExampleTokenValue',
  ].join('\n'),
  [
    'Finance remittance advice',
    'Supplier: Northfield Retail Operations Ltd',
    'Accounts contact: lucas.meyer@northfieldretail.com',
    'Mobile: +44 7700 911874',
    'Company registration: 08451277',
    'Bank account: GB29NWBK60161331926819',
    'Invoice IDs: INV-90331, INV-90332',
    'Payment ref: TXN-2026-03-88211',
  ].join('\n'),
  [
    'Recruiter interview debrief',
    'Candidate: Daniel Hughes',
    'Email: daniel.hughes@careersmail.com',
    'Mobile: 07912 123456',
    'Current employer: Green Horizon Research',
    'Home address: 21 Cedar Avenue, Manchester M3 1AA',
  ].join('\n'),
  [
    'Board update draft',
    'Prepared by: Anna Carter',
    'Organisation: Green Horizon Research',
    'Contacts: anna.carter@example.com, daniel.hughes@ecologiclab.org',
    'Project locations: 14 Willow Lane, Brighton BN1 4AB and 28 Riverside Road, Cambridge CB1 3QA',
    'Finance tracker invoice: INV-55619',
  ].join('\n'),
]

const detectorOptions: Array<{ key: DetectorKey; label: string }> = [
  { key: 'person', label: 'Names' },
  { key: 'organisation', label: 'Organisations' },
  { key: 'email', label: 'Emails' },
  { key: 'phone', label: 'Phone numbers' },
  { key: 'date', label: 'Dates / DOB' },
  { key: 'address', label: 'Addresses' },
  { key: 'id', label: 'Government / Tax IDs' },
  { key: 'invoice', label: 'Invoice IDs' },
  { key: 'ip', label: 'IP addresses' },
  { key: 'secret', label: 'Secret keys' },
  { key: 'username', label: 'Usernames' },
]

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

const signature = computed(() => `${inputText.value}::${mode.value}::${JSON.stringify(activeDetectors.value)}`)
const hasInput = computed(() => inputText.value.trim().length > 0)
const hasOutput = computed(() => outputText.value.trim().length > 0)
const needsSanitise = computed(() => hasInput.value && signature.value !== lastSignature.value)
const redactionCount = computed(() => result.value?.total ?? 0)

const renderedLines = computed(() => {
  if (!outputText.value) return [] as Array<Array<{ text: string; tokenType?: TokenType }>>
  return outputText.value.split('\n').map((line) => splitOutputByTokens(line))
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

function setInputFocus() {
  nextTick(() => {
    inputRef.value?.focus()
    const length = inputText.value.length
    inputRef.value?.setSelectionRange(length, length)
  })
}

function isMobileViewport() {
  return typeof window !== 'undefined' && window.matchMedia('(max-width: 900px)').matches
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
  inputText.value = TOOL_EXAMPLES[exampleCursor]
  if (autoSanitise) {
    void runSanitise()
  }
  setInputFocus()
}

function toggleDetector(key: DetectorKey) {
  detectorState.value[key] = !detectorState.value[key]
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

async function anonymiseViaApi(text: string, detectors: Record<DetectorKey, boolean>) {
  const entity_types = buildEntityTypes(detectors)
  if (entity_types.length === 0) throw new Error('NO_DETECTORS')

  const response = await fetch('/api/anonymize', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      text,
      entity_types,
      tag_style: 'standard',
    }),
  })

  if (!response.ok) {
    throw new Error(`API_${response.status}`)
  }

  const payload = (await response.json()) as {
    anonymized_text?: string
    counts?: Record<string, unknown>
    warning?: string
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
    const { result: sanitised, warning } = await anonymiseViaApi(inputText.value, activeDetectors.value)
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
    } else {
      statusText.value = 'Sanitisation service unavailable. Please try again.'
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

onMounted(() => {
  maybeRunDemoFromQuery()
  setInputFocus()
})
</script>

<template>
  <main class="tool-page">
    <section class="tool-page__meta">
      <div class="tool-page__secure-pill">
        <span class="tool-page__secure-dot" aria-hidden="true"></span>
        <span>Secure environment</span>
      </div>
    </section>

    <section class="tool-page__workspace" aria-label="Sanitiser workspace">
      <article class="tool-page__panel tool-page__panel--input">
        <header class="tool-page__panel-head tool-page__panel-head--input">
          <div class="tool-page__title-wrap">
            <PhMagicWand :size="18" weight="duotone" aria-hidden="true" />
            <div>
              <p>Input Terminal</p>
              <small>Paste sensitive data</small>
            </div>
          </div>
          <div class="tool-page__head-actions">
            <button class="btn btn--secondary" type="button" @click="applyExample(true)">
              <PhSparkle :size="16" weight="duotone" aria-hidden="true" />
              <span>Try example</span>
            </button>
            <button class="btn btn--secondary" type="button" :disabled="isUploading || isProcessing" @click="triggerFilePicker">
              <PhUploadSimple :size="16" weight="duotone" aria-hidden="true" />
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
          placeholder="Paste sensitive text, logs, contracts, prompts, or notes..."
          @keydown.meta.enter.prevent="runSanitise"
          @keydown.ctrl.enter.prevent="runSanitise"
        ></textarea>

        <div class="tool-page__controls">
          <p class="tool-page__upload-note">{{ uploadLabel }}</p>
          <div class="tool-page__mode">
            <button
              type="button"
              class="tool-page__mode-btn"
              :class="{ 'tool-page__mode-btn--active': mode === 'automatic' }"
              @click="mode = 'automatic'"
            >
              Automatic
            </button>
            <button
              type="button"
              class="tool-page__mode-btn"
              :class="{ 'tool-page__mode-btn--active': mode === 'custom' }"
              @click="mode = 'custom'"
            >
              Custom rules
            </button>
          </div>

          <div v-if="mode === 'custom'" class="tool-page__detectors">
            <button
              v-for="item in detectorOptions"
              :key="item.key"
              type="button"
              class="tool-page__detector"
              :class="{ 'tool-page__detector--active': detectorState[item.key] }"
              @click="toggleDetector(item.key)"
            >
              <span>{{ item.label }}</span>
            </button>
          </div>

          <div class="tool-page__actions">
            <p class="tool-page__privacy-note">
              Privacy Note: Text is sent to the sanitisation API over HTTPS for processing. Raw input is not stored.
            </p>
            <button class="btn btn--ghost" type="button" :disabled="!hasInput || isProcessing" @click="clearAll">
              <PhEraser :size="16" weight="duotone" aria-hidden="true" />
              <span>Clear</span>
            </button>
            <button
              class="btn btn--primary"
              type="button"
              :disabled="!hasInput || isProcessing || !needsSanitise"
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
                <p>Sanitised Preview</p>
              </div>
            </div>
            <span class="tool-page__result-badge">{{ redactionCount }} REDACTIONS</span>
          </header>

          <div class="tool-page__output-shell">
            <div class="tool-page__output" :class="{ 'tool-page__output--reveal': outputReveal }">
              <template v-if="renderedLines.length">
                <p v-for="(line, lineIndex) in renderedLines" :key="lineIndex" class="tool-page__line">
                  <template v-for="(part, partIndex) in line" :key="`${lineIndex}-${partIndex}`">
                    <span v-if="part.tokenType" class="tool-page__token" :class="tokenClass(part.tokenType)">{{ part.text }}</span>
                    <span v-else>{{ part.text }}</span>
                  </template>
                </p>
              </template>
              <p v-else class="tool-page__placeholder">Sanitised output appears here after you run the tool.</p>
            </div>

            <div v-if="isProcessing" class="tool-page__spinner" role="status" aria-live="polite">
              <span class="tool-page__spinner-ring" aria-hidden="true"></span>
              <span>Processing</span>
            </div>
          </div>

          <footer v-if="result && result.detectedLabels.length" class="tool-page__summary">
            <PhShieldCheck :size="16" weight="fill" aria-hidden="true" />
            <ul>
              <li v-for="label in result.detectedLabels" :key="label">{{ label }}</li>
            </ul>
          </footer>

          <footer v-else-if="statusText" class="tool-page__summary tool-page__summary--empty">
            <PhCheckCircle :size="16" weight="duotone" aria-hidden="true" />
            <p>{{ statusText }}</p>
          </footer>

          <div class="tool-page__output-actions">
            <button class="btn tool-page__action-btn tool-page__action-btn--light" type="button" :disabled="!hasOutput || isProcessing" @click="copyOutput">
              <PhCopy :size="16" weight="duotone" aria-hidden="true" />
              <span>{{ copyLabel }}</span>
            </button>
            <button class="btn btn--primary tool-page__action-btn" type="button" :disabled="!hasOutput || isProcessing" @click="exportText">
              <PhDownloadSimple :size="16" weight="duotone" aria-hidden="true" />
              <span>Export .txt</span>
            </button>
          </div>
        </article>

        <aside class="tool-page__profile">
          <p>Detection Profile</p>
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
        </aside>
      </div>
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
    justify-content: flex-end;
    align-items: center;
    gap: 0.9rem;

    p {
      margin: 0;
      color: var(--text-3);
      font-size: 0.76rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-weight: 760;
    }
  }

  &__secure-pill {
    border-radius: 12px;
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
  }

  &__panel {
    border-radius: 18px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 36%);
    box-shadow: 0 18px 36px rgba(14, 22, 38, 0.08);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    min-height: 640px;
  }

  &__panel--input {
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 26%);
  }

  &__panel--output {
    background: #0a1431;
    color: #e6efff;
    border-color: #1e2d55;
    box-shadow:
      0 20px 44px rgba(7, 17, 40, 0.45),
      inset 0 1px 0 rgba(146, 174, 255, 0.08);
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
    border-radius: 999px;
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
    min-height: 400px;
    flex: 1;
    resize: vertical;
    border: 0;
    background: transparent;
    color: var(--text-1);
    padding: 1.05rem 1.1rem;
    font-size: 0.98rem;
    line-height: 1.7;

    &:focus-visible {
      outline: none;
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
    border-radius: 10px;
    background: color-mix(in srgb, var(--surface-2), white 24%);
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 36%);
  }

  &__mode-btn {
    border: 1px solid transparent;
    border-radius: 8px;
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
    }
  }

  &__mode-btn--active {
    color: var(--text-1);
    border-color: color-mix(in srgb, var(--border-2), transparent 34%);
    background: color-mix(in srgb, var(--surface-0), var(--accent-soft) 10%);
    box-shadow: 0 2px 4px rgba(14, 22, 38, 0.05);
  }

  &__detectors {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.42rem;
  }

  &__detector {
    border-radius: 9px;
    border: 1px solid color-mix(in srgb, var(--border-1), transparent 34%);
    background: color-mix(in srgb, var(--surface-0), var(--surface-1) 38%);
    padding: 0.4rem 0.5rem;
    text-align: left;
    cursor: pointer;
    color: var(--text-2);
    font-size: 0.76rem;
    font-weight: 650;
    transition: border-color 180ms ease, background 180ms ease;
  }

  &__detector--active {
    border-color: color-mix(in srgb, var(--accent-2), transparent 44%);
    background: color-mix(in srgb, var(--accent-soft), white 56%);
    color: var(--accent-3);
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
    color: #0d8a53;
    font-size: 0.84rem;
    line-height: 1.45;
    font-weight: 640;
  }

  &__output-shell {
    position: relative;
    z-index: 1;
    flex: 1;
    padding: 1rem 1rem 0;
  }

  &__output {
    border-radius: 12px;
    border: 1px solid rgba(108, 143, 231, 0.2);
    background: rgba(8, 19, 48, 0.58);
    padding: 1rem;
    min-height: 390px;
    max-height: 560px;
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

  &__token {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    border: 1px solid transparent;
    padding: 0.15rem 0.58rem;
    margin: 0.04rem 0.14rem;
    white-space: nowrap;
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.83rem;
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
    border-radius: 999px;
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
    border-radius: 10px;
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
        border-radius: 999px;
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
    border-radius: 14px;
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
}

@keyframes spin {
  to {
    transform: rotate(360deg);
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
    }

    &__output-column {
      grid-template-rows: minmax(0, 1fr) auto;
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

    &__meta {
      justify-content: space-between;
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

    &__detectors {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }
}

@media (max-width: 680px) {
  .tool-page {
    &__meta {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }

    &__secure-pill {
      width: 100%;
      justify-content: center;
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

    &__detectors {
      grid-template-columns: 1fr;
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
