import { json, parseCookies, verifyToken } from './_lib/common.mjs'

export async function handler(event) {
  if (event.httpMethod !== 'GET') return json(405, { error: 'Method not allowed' })

  const cookies = parseCookies(event.headers.cookie || '')
  const secret = process.env.JWT_SECRET || 'dev-secret-change-me'
  const payload = cookies.pro_token ? verifyToken(cookies.pro_token, secret) : null
  const isPro = payload?.tier === 'pro'

  return json(200, {
    ok: true,
    tier: isPro ? 'pro' : 'free',
  })
}
