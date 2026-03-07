import crypto from 'node:crypto'

export function json(statusCode, body, extraHeaders = {}) {
  return {
    statusCode,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      ...extraHeaders,
    },
    body: JSON.stringify(body),
  }
}

export function parseBody(event) {
  try {
    return event.body ? JSON.parse(event.body) : {}
  } catch {
    return null
  }
}

export function parseCookies(cookieHeader = '') {
  const out = {}
  for (const pair of cookieHeader.split(';')) {
    const i = pair.indexOf('=')
    if (i === -1) continue
    const key = pair.slice(0, i).trim()
    const val = pair.slice(i + 1).trim()
    if (key) out[key] = decodeURIComponent(val)
  }
  return out
}

export function getClientIp(event) {
  return (
    event.headers['x-nf-client-connection-ip'] ||
    event.headers['x-forwarded-for']?.split(',')[0]?.trim() ||
    '0.0.0.0'
  )
}

function base64url(input) {
  return Buffer.from(input)
    .toString('base64')
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
}

function fromBase64url(input) {
  const pad = input.length % 4 ? '='.repeat(4 - (input.length % 4)) : ''
  const b64 = input.replace(/-/g, '+').replace(/_/g, '/') + pad
  return Buffer.from(b64, 'base64').toString('utf8')
}

export function signToken(payload, secret, expiresDays = 30) {
  const header = { alg: 'HS256', typ: 'JWT' }
  const now = Math.floor(Date.now() / 1000)
  const fullPayload = { ...payload, iat: now, exp: now + expiresDays * 86400 }
  const encodedHeader = base64url(JSON.stringify(header))
  const encodedPayload = base64url(JSON.stringify(fullPayload))
  const data = `${encodedHeader}.${encodedPayload}`
  const sig = crypto
    .createHmac('sha256', secret)
    .update(data)
    .digest('base64')
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
  return `${data}.${sig}`
}

export function verifyToken(token, secret) {
  try {
    const [h, p, s] = token.split('.')
    if (!h || !p || !s) return null
    const data = `${h}.${p}`
    const expected = crypto
      .createHmac('sha256', secret)
      .update(data)
      .digest('base64')
      .replace(/=/g, '')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
    if (expected !== s) return null
    const payload = JSON.parse(fromBase64url(p))
    const now = Math.floor(Date.now() / 1000)
    if (payload.exp && now > payload.exp) return null
    return payload
  } catch {
    return null
  }
}

export function sha256Hex(input) {
  return crypto.createHash('sha256').update(input).digest('hex')
}

export function makeSetCookie(name, value, maxAgeSeconds, secure) {
  const flags = [
    `${name}=${encodeURIComponent(value)}`,
    'Path=/',
    `Max-Age=${maxAgeSeconds}`,
    'HttpOnly',
    'SameSite=Lax',
  ]
  if (secure) flags.push('Secure')
  return flags.join('; ')
}
