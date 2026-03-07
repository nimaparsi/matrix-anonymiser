import { json } from './_lib/common.mjs'

export async function handler() {
  return json(200, {
    ok: true,
    version: 'v1-netlify',
    nlp_available: false,
  })
}
