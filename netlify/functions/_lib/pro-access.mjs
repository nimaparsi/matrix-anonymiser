import { getClientIp, sha256Hex } from './common.mjs'

const memoryGrants = new Map()

function upstashConfig() {
  const url = process.env.REDIS_REST_URL
  const token = process.env.REDIS_REST_TOKEN
  if (!url || !token) return null
  return { url: url.replace(/\/$/, ''), token }
}

function nowSeconds() {
  return Math.floor(Date.now() / 1000)
}

export function makeProAccessKey(ip) {
  const salt = process.env.PRO_ACCESS_SALT || process.env.USAGE_SALT || 'change-me'
  const digest = sha256Hex(`${ip}|${salt}`)
  return `pro-access:${digest}`
}

export async function grantProAccess(event, ttlSeconds) {
  const ip = getClientIp(event)
  const key = makeProAccessKey(ip)
  const ttl = Math.max(60, Number(ttlSeconds || 0))
  const expiresAt = nowSeconds() + ttl

  memoryGrants.set(key, expiresAt)

  const cfg = upstashConfig()
  if (!cfg) return

  const headers = { Authorization: `Bearer ${cfg.token}` }
  try {
    await fetch(`${cfg.url}/set/${encodeURIComponent(key)}/1`, { headers })
    await fetch(`${cfg.url}/expire/${encodeURIComponent(key)}/${ttl}`, { headers })
  } catch {
    // Keep memory fallback only.
  }
}

export async function hasProAccess(event) {
  const ip = getClientIp(event)
  const key = makeProAccessKey(ip)
  const now = nowSeconds()

  const inMemory = memoryGrants.get(key)
  if (typeof inMemory === 'number') {
    if (inMemory > now) return true
    memoryGrants.delete(key)
  }

  const cfg = upstashConfig()
  if (!cfg) return false

  const headers = { Authorization: `Bearer ${cfg.token}` }
  try {
    const res = await fetch(`${cfg.url}/get/${encodeURIComponent(key)}`, { headers })
    if (!res.ok) return false
    const data = await res.json()
    return data.result === '1' || data.result === 1
  } catch {
    return false
  }
}

export async function resetProAccess(event) {
  const ip = getClientIp(event)
  const key = makeProAccessKey(ip)
  memoryGrants.delete(key)

  const cfg = upstashConfig()
  if (!cfg) return

  const headers = { Authorization: `Bearer ${cfg.token}` }
  try {
    await fetch(`${cfg.url}/del/${encodeURIComponent(key)}`, { headers })
  } catch {
    // Ignore redis delete failures.
  }
}
