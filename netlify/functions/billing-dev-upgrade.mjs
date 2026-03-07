import { json, makeSetCookie, signToken } from './_lib/common.mjs'

export async function handler() {
  if ((process.env.ENV || 'dev') === 'production') {
    return json(403, { detail: 'Disabled in production' })
  }
  const days = Number(process.env.PRO_TOKEN_DAYS || 30)
  const secret = process.env.JWT_SECRET || 'dev-secret-change-me'
  const token = signToken({ tier: 'pro' }, secret, days)
  const secure = (process.env.COOKIE_SECURE || 'false').toLowerCase() === 'true'
  return json(200, { ok: true, tier: 'pro' }, {
    'set-cookie': makeSetCookie('pro_token', token, days * 86400, secure),
  })
}
