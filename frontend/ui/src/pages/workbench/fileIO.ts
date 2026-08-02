const EXTENSION_BY_MIME: Record<string, string> = {
  'image/png': 'png',
  'image/jpeg': 'jpg',
  'image/gif': 'gif',
  'image/webp': 'webp',
  'application/octet-stream': 'bin',
}

function mimeBase(outputMime: string | undefined): string | undefined {
  return outputMime?.split(';')[0]?.trim()
}

export function extensionFor(outputMime: string | undefined, operationIdOrLabel: string): string {
  const base = mimeBase(outputMime)
  if (base && EXTENSION_BY_MIME[base]) return EXTENSION_BY_MIME[base]
  if (base?.startsWith('image/')) return base.slice('image/'.length)
  if (/gzip|zlib|compress/i.test(operationIdOrLabel)) return 'bin'
  return 'txt'
}

function base64ToBlob(base64: string, mime: string): Blob {
  const binary = atob(base64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
  return new Blob([bytes], { type: mime })
}

export function downloadWorkbenchOutput(output: string, outputMime: string | undefined, filenameBase: string): void {
  const ext = extensionFor(outputMime, filenameBase)
  const base = mimeBase(outputMime)
  const isBase64Mime = !!outputMime && /;base64/i.test(outputMime)
  const blob = isBase64Mime && base
    ? base64ToBlob(output, base)
    : new Blob([output], { type: 'text/plain;charset=utf-8' })

  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${filenameBase}-output.${ext}`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
