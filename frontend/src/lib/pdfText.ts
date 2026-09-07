export type PdfTextItem = {
  str: string
  transform: number[]
  width: number
  height: number
  hasEOL?: boolean
  dir?: string
}

// Keep PDF.js reading order. Geometry is used for spacing, never to guess words
// or interleave columns by globally sorting text fragments.
export function assemblePdfText(items: unknown[]): string {
  let output = ''
  let previous: PdfTextItem | null = null
  for (const value of items) {
    if (!value || typeof value !== 'object' || !('str' in value)) continue
    const item = value as PdfTextItem
    if (!Array.isArray(item.transform)) continue
    const text = item.str.replace(/\u00a0/g, ' ')
    if (!text) {
      if (item.hasEOL && output && !output.endsWith('\n')) output += '\n'
      continue
    }
    if (previous && output && !output.endsWith('\n')) {
      const fontSize = Math.max(Math.hypot(item.transform[2], item.transform[3]), item.height, 1)
      const previousSize = Math.max(Math.hypot(previous.transform[2], previous.transform[3]), previous.height, 1)
      const size = Math.min(fontSize, previousSize)
      const dx = item.transform[4] - previous.transform[4]
      const dy = item.transform[5] - previous.transform[5]
      const angle = Math.atan2(previous.transform[1], previous.transform[0])
      const acrossLine = Math.abs(-dx * Math.sin(angle) + dy * Math.cos(angle))
      const advance = dx * Math.cos(angle) + dy * Math.sin(angle)
      const gap = item.dir === 'rtl' ? -advance - item.width : advance - previous.width
      if (previous.hasEOL || acrossLine > size * 0.45) output += '\n'
      else if (!/\s$/.test(output) && !/^\s/.test(text)) {
        if (gap > size * 2.5) output += '\t'
        else if (gap > size * 0.15) output += ' '
      }
    }
    output += text
    if (item.hasEOL && !output.endsWith('\n')) output += '\n'
    previous = item
  }
  return output.replace(/[ \t]+\n/g, '\n').trim()
}
