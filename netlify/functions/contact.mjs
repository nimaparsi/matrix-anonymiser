import { getClientIp, json, parseBody } from './_lib/common.mjs'

function cleanHeaderText(value, fallback = '') {
  const raw = String(value ?? fallback)
  return raw.replace(/[\r\n]+/g, ' ').trim() || fallback
}

function cleanBodyText(value, fallback = '') {
  const raw = String(value ?? fallback).trim()
  return raw || fallback
}

export async function handler(event) {
  if (event.httpMethod !== 'POST') return json(405, { detail: 'Method not allowed' })

  const body = parseBody(event)
  if (!body) return json(400, { detail: 'Invalid JSON body' })

  // Lightweight honeypot for bot form posts.
  if (String(body.website || '').trim()) {
    return json(200, { ok: true, message: 'Message accepted' })
  }

  const name = cleanBodyText(body.name)
  const email = cleanBodyText(body.email)
  const company = cleanBodyText(body.company, '-')
  const topic = cleanHeaderText(body.topic, 'General enquiry')
  const message = cleanBodyText(body.message)

  if (!name || !message) return json(400, { detail: 'Name and message are required' })
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json(400, { detail: 'Please provide a valid email address' })
  }

  const resendKey = process.env.RESEND_API_KEY || ''
  const contactTo = process.env.CONTACT_TO_EMAIL || 'nimaparsi@icloud.com'
  const contactFrom = process.env.CONTACT_FROM_EMAIL || 'SanitiseAI Contact <onboarding@resend.dev>'

  if (!resendKey) {
    return json(503, { detail: 'Contact service not configured (missing RESEND_API_KEY)' })
  }

  const sourceIp = getClientIp(event)
  const userAgent = event.headers['user-agent'] || 'unknown'
  const subject = `[SanitiseAI] ${topic}`

  const text = [
    'New contact request from sanitiseai.com',
    '',
    `Topic: ${topic}`,
    `Name: ${name}`,
    `Email: ${email}`,
    `Company: ${company}`,
    '',
    'Message:',
    message,
    '',
    `Source IP: ${sourceIp}`,
    `User-Agent: ${userAgent}`,
  ].join('\n')

  const resendRes = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${resendKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: contactFrom,
      to: [contactTo],
      reply_to: email,
      subject,
      text,
    }),
  })

  const payload = await resendRes.json().catch(() => ({}))
  if (!resendRes.ok) {
    const message = payload?.message || payload?.error || 'Unable to deliver contact message'
    return json(502, { detail: message })
  }

  return json(200, { ok: true, id: payload?.id || null, message: 'Contact request sent' })
}
