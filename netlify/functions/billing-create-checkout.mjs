import { json, parseBody } from './_lib/common.mjs'

function formEncode(obj) {
  const p = new URLSearchParams()
  for (const [k, v] of Object.entries(obj)) p.append(k, String(v))
  return p.toString()
}

export async function handler(event) {
  if (event.httpMethod !== 'POST') return json(405, { detail: 'Method not allowed' })

  const body = parseBody(event)
  if (!body) return json(400, { detail: 'Invalid JSON body' })

  const key = process.env.STRIPE_SECRET_KEY || ''
  const price = process.env.STRIPE_PRICE_ID || ''
  if (!key || !price) return json(503, { detail: 'Billing not configured' })

  const success = String(body.success_url || '')
  const cancel = String(body.cancel_url || '')
  if (!success || !cancel) return json(400, { detail: 'success_url and cancel_url are required' })

  const payload = formEncode({
    mode: 'subscription',
    success_url: `${success}?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: cancel,
    'line_items[0][price]': price,
    'line_items[0][quantity]': 1,
    allow_promotion_codes: true,
  })

  const res = await fetch('https://api.stripe.com/v1/checkout/sessions', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${key}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: payload,
  })

  const data = await res.json()
  if (!res.ok) {
    return json(400, { detail: data.error?.message || 'Stripe session creation failed' })
  }

  return json(200, { url: data.url })
}
