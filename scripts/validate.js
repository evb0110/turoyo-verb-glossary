#!/usr/bin/env node
import { readFile } from 'fs/promises'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const rootDir = join(__dirname, '..')

async function loadApiVerb(root) {
  const path = join(rootDir, 'data/api/verbs', `${root}.json`)
  return JSON.parse(await readFile(path, 'utf-8'))
}

async function loadSourceHtml() {
  const path = join(rootDir, 'source/Turoyo_all_2024.html')
  return await readFile(path, 'utf-8')
}

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function findEntryFragment(html, root) {
  const letters = 'ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə'
  const rootRe = new RegExp(
    `<p[^>]*class="western"[^>]*>[\\s\\S]*?<span[^>]*>(?:&shy;)?([${letters}]{2,6})(?:\\s*\\d+)?<\\/span>`,
    'g'
  )
  const matches = [...html.matchAll(rootRe)]
  const idx = matches.findIndex(m => m[1] === root)
  if (idx === -1) return null
  const start = matches[idx].index
  const end = idx + 1 < matches.length ? matches[idx + 1].index : html.length
  return html.slice(start, end)
}

function normalizeText(s) {
  return s.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
}

async function parityCheck(root) {
  const [apiVerb, html] = await Promise.all([loadApiVerb(root), loadSourceHtml()])
  const frag = findEntryFragment(html, root)
  if (!frag) return { root, ok: false, reason: 'source fragment not found' }

  const headerRaw = apiVerb.lemma_header_raw || ''
  const headerTextApi = normalizeText(headerRaw).slice(0, 220)
  const headerTextSrc = normalizeText(frag).slice(0, 220)

  // Counts
  const stemCountApi = (apiVerb.stems || []).length
  const stemCountSrc = (frag.match(/<font size="4"/g) || []).length

  // Example count rough
  const exampleCountApi = (apiVerb.stems || []).reduce((s, st) => s + Object.values(st.conjugations || {}).reduce((a, ex) => a + ex.length, 0), 0)
  const exampleCountSrc = (frag.match(/<td[^>]*>/g) || []).length // rough cell count

  return {
    root,
    ok: true,
    headerPreviewApi: headerTextApi,
    headerPreviewSrc: headerTextSrc,
    stemCountApi,
    stemCountSrc,
    exampleCountApi,
    exampleCountSrc
  }
}

async function main() {
  const roots = process.argv.slice(2)
  if (!roots.length) {
    console.log('Usage: node scripts/validate.js <root1> <root2> ...')
    process.exit(1)
  }
  for (const r of roots) {
    const res = await parityCheck(r)
    console.log(JSON.stringify(res, null, 2))
  }
}

if (import.meta.url === `file://${__filename}`) {
  main().catch(e => { console.error(e); process.exit(1) })
}
