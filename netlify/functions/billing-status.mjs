import { json, parseCookies, verifyToken } from './_lib/common.mjs'
import { hasProAccess } from './_lib/pro-access.mjs'

export async function handler(event) {
  if (event.httpMethod !== 'GET') return json(405, { error: 'Method not allowed' })

  const cookies = parseCookies(event.headers.cookie || '')
  const secret = process.env.JWT_SECRET || 'dev-secret-change-me'
  const payload = cookies.pro_token ? verifyToken(cookies.pro_token, secret) : null
  const cookiePro = payload?.tier === 'pro'
  const fallbackPro = cookiePro ? false : await hasProAccess(event)
  const isPro = cookiePro || fallbackPro

  return json(200, {
    ok: true,
    tier: isPro ? 'pro' : 'free',
    source: cookiePro ? 'cookie' : fallbackPro ? 'ip' : 'none',
  })
}
