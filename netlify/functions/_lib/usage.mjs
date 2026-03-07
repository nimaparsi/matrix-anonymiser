import { sha256Hex } from './common.mjs'

const memoryCounters = new Map()

function upstashConfig() {
  const url = process.env.REDIS_REST_URL
  const token = process.env.REDIS_REST_TOKEN
  if (!url || !token) return null
  return { url: url.replace(/\/$/, ''), token }
}

async function upstashIncr(key, ttlSeconds) {
  const cfg = upstashConfig()
  if (!cfg) return null

  const headers = { Authorization: `Bearer ${cfg.token}` }
  const incrRes = await fetch(`${cfg.url}/incr/${encodeURIComponent(key)}`, { headers })
  if (!incrRes.ok) throw new Error('upstash incr failed')
  const incrData = await incrRes.json()
  const current = Number(incrData.result || 0)

  if (current === 1) {
    await fetch(`${cfg.url}/expire/${encodeURIComponent(key)}/${ttlSeconds}`, { headers })
  }

  return current
}

export function makeUsageKey(ip, userAgent, isPro) {
  const day = new Date().toISOString().slice(0, 10).replace(/-/g, '')
  const salt = process.env.USAGE_SALT || 'change-me'
  const raw = `${ip}|${userAgent}|${day}|${salt}`
  const digest = sha256Hex(raw)
  return `usage:${isPro ? 'pro' : 'free'}:${digest}`
}

export async function checkAndIncrementUsage(key, isPro) {
  const freeLimit = Number(process.env.FREE_DAILY_LIMIT || 5)
  const proLimit = Number(process.env.PRO_DAILY_LIMIT || 500)
  const limit = isPro ? proLimit : freeLimit
  const ttl = 60 * 60 * 48

  let used
  try {
    const redisUsed = await upstashIncr(key, ttl)
    if (redisUsed !== null) used = redisUsed
  } catch {
    used = undefined
  }

  if (typeof used !== 'number') {
    const current = (memoryCounters.get(key) || 0) + 1
    memoryCounters.set(key, current)
    used = current
  }

  return { allowed: used <= limit, used, limit }
}
