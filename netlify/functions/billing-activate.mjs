import { json, makeSetCookie, signToken } from './_lib/common.mjs'

export async function handler(event) {
  const sessionId = event.queryStringParameters?.session_id || ''
  if (!sessionId) return json(400, { detail: 'session_id is required' })

  const key = process.env.STRIPE_SECRET_KEY || ''
  if (key) {
    const res = await fetch(`https://api.stripe.com/v1/checkout/sessions/${encodeURIComponent(sessionId)}`, {
      headers: { Authorization: `Bearer ${key}` },
    })
    const data = await res.json()
    if (!res.ok) return json(400, { detail: data.error?.message || 'Stripe verification failed' })
    if (!['paid', 'no_payment_required'].includes(data.payment_status || '')) {
      return json(402, { detail: 'Payment not completed' })
    }
  }

  const days = Number(process.env.PRO_TOKEN_DAYS || 30)
  const secure = (process.env.COOKIE_SECURE || 'true').toLowerCase() === 'true'
  const secret = process.env.JWT_SECRET || 'dev-secret-change-me'
  const token = signToken({ tier: 'pro' }, secret, days)

  return json(200, { ok: true, tier: 'pro' }, {
    'set-cookie': makeSetCookie('pro_token', token, days * 86400, secure),
  })
}
