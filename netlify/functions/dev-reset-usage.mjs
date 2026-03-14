import { getClientIp, json, makeSetCookie } from './_lib/common.mjs'
import { makeUsageKey, resetUsageKey } from './_lib/usage.mjs'
import { resetProAccess } from './_lib/pro-access.mjs'

export async function handler(event) {
  if (event.httpMethod !== 'POST') return json(405, { error: 'Method not allowed' })
  if ((process.env.ENV || 'dev') === 'production') return json(403, { detail: 'Disabled in production' })

  const userAgent = event.headers['user-agent'] || 'unknown'
  const ip = getClientIp(event)

  await resetUsageKey(makeUsageKey(ip, userAgent, false))
  await resetUsageKey(makeUsageKey(ip, userAgent, true))
  await resetProAccess(event)

  const clearCookie = makeSetCookie('pro_token', '', 0, false)
  return json(
    200,
    { ok: true, message: 'Usage and pro token reset' },
    { 'set-cookie': clearCookie },
  )
}
