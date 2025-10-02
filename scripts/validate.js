#!/usr/bin/env node
import { readdir, readFile } from 'fs/promises'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const rootDir = join(__dirname, '..')

// List of 12 legitimate verbs with empty Turoyo fields
const LEGITIMATE_EMPTY_TUROYO = [
  'ḥrm',
  'ḥsk',
  'ḥšd',
  'mlḥ',
  'mšʕ',
  'qtl',
  'šlḥ',
  'šql',
  'špq',
  'škr',
  'škḥ',
  'štq'
]

class DataValidator {
  constructor() {
    this.errors = []
    this.warnings = []
    this.rootsSeen = new Set()
    this.allRoots = new Set()
  }

  addError(message) {
    this.errors.push(message)
  }

  addWarning(message) {
    this.warnings.push(message)
  }

  async loadVerbs() {
    const sourceDir = join(rootDir, 'data/source/verbs')
    let allVerbs = []

    try {
      const files = await readdir(sourceDir)
      const jsonFiles = files.filter(f => f.endsWith('.json'))

      if (jsonFiles.length === 0) {
        console.log('⚠️  No source files found, loading from turoyo_verbs_complete.json...')
        const completeFile = join(rootDir, 'data/turoyo_verbs_complete.json')
        const data = JSON.parse(await readFile(completeFile, 'utf-8'))
        allVerbs = data.verbs
      } else {
        console.log(`📂 Loading ${jsonFiles.length} source files...`)
        for (const file of jsonFiles) {
          const data = JSON.parse(await readFile(join(sourceDir, file), 'utf-8'))
          if (data.verbs && Array.isArray(data.verbs)) {
            allVerbs.push(...data.verbs)
          }
        }
      }
    } catch (error) {
      console.log('⚠️  Source directory not found, loading from turoyo_verbs_complete.json...')
      const completeFile = join(rootDir, 'data/turoyo_verbs_complete.json')
      const data = JSON.parse(await readFile(completeFile, 'utf-8'))
      allVerbs = data.verbs
    }

    return allVerbs
  }

  validateVerb(verb) {
    // Check required fields
    if (!verb.root) {
      this.addError(`Verb missing 'root' field`)
      return
    }

    const root = verb.root

    // Check for duplicate roots
    if (this.rootsSeen.has(root)) {
      this.addError(`Duplicate root found: ${root}`)
    }
    this.rootsSeen.add(root)
    this.allRoots.add(root)

    // Validate etymology
    if (!verb.etymology || typeof verb.etymology !== 'object') {
      this.addWarning(`Verb ${root}: missing or invalid etymology`)
    } else {
      if (!verb.etymology.source) {
        this.addWarning(`Verb ${root}: missing etymology.source`)
      }
      if (!verb.etymology.meaning) {
        this.addWarning(`Verb ${root}: missing etymology.meaning`)
      }
    }

    // Validate stems
    if (!verb.stems || !Array.isArray(verb.stems)) {
      this.addError(`Verb ${root}: missing or invalid stems array`)
      return
    }

    if (verb.stems.length === 0) {
      this.addWarning(`Verb ${root}: empty stems array`)
    }

    for (let i = 0; i < verb.stems.length; i++) {
      this.validateStem(root, verb.stems[i], i)
    }

    // Validate uncertain field
    if (typeof verb.uncertain !== 'boolean') {
      this.addWarning(`Verb ${root}: 'uncertain' field should be boolean`)
    }

    // Validate cross_reference
    if (verb.cross_reference !== null && typeof verb.cross_reference !== 'string') {
      this.addError(`Verb ${root}: invalid cross_reference (should be string or null)`)
    }
  }

  validateStem(root, stem, index) {
    // Check stem
    if (!stem.stem) {
      this.addError(`Verb ${root}, stem ${index}: missing stem`)
    }

    // Check forms
    if (!stem.forms || !Array.isArray(stem.forms)) {
      this.addError(`Verb ${root}, stem ${index}: missing or invalid forms array`)
    } else if (stem.forms.length === 0) {
      this.addWarning(`Verb ${root}, stem ${index}: empty forms array`)
    }

    // Check conjugations
    if (!stem.conjugations || typeof stem.conjugations !== 'object') {
      this.addError(`Verb ${root}, stem ${index}: missing or invalid conjugations`)
      return
    }

    let hasExamples = false
    for (const [conjugationType, examples] of Object.entries(stem.conjugations)) {
      if (!Array.isArray(examples)) {
        this.addError(`Verb ${root}, stem ${index}, ${conjugationType}: should be an array`)
        continue
      }

      for (let j = 0; j < examples.length; j++) {
        hasExamples = true
        this.validateExample(root, stem.stem, conjugationType, examples[j], j)
      }
    }

    if (!hasExamples) {
      this.addWarning(`Verb ${root}, stem ${index}: no examples in conjugations`)
    }
  }

  validateExample(root, stem, conjugationType, example, index) {
    // Check turoyo field
    if (example.turoyo === undefined) {
      this.addError(`Verb ${root}, ${stem}, ${conjugationType}, example ${index}: missing 'turoyo' field`)
    } else if (example.turoyo === null || example.turoyo === '') {
      // Check if this is one of the legitimate empty cases
      if (!LEGITIMATE_EMPTY_TUROYO.includes(root)) {
        this.addError(`Verb ${root}, ${stem}, ${conjugationType}, example ${index}: empty 'turoyo' field (not in legitimate list)`)
      }
    } else if (typeof example.turoyo !== 'string') {
      this.addError(`Verb ${root}, ${stem}, ${conjugationType}, example ${index}: 'turoyo' should be a string`)
    }

    // Check translations
    if (!example.translations) {
      this.addWarning(`Verb ${root}, ${stem}, ${conjugationType}, example ${index}: missing 'translations' field`)
    } else if (!Array.isArray(example.translations)) {
      this.addError(`Verb ${root}, ${stem}, ${conjugationType}, example ${index}: 'translations' should be an array`)
    } else if (example.translations.length === 0) {
      this.addWarning(`Verb ${root}, ${stem}, ${conjugationType}, example ${index}: empty 'translations' array`)
    }

    // Check references
    if (!example.references) {
      this.addWarning(`Verb ${root}, ${stem}, ${conjugationType}, example ${index}: missing 'references' field`)
    } else if (!Array.isArray(example.references)) {
      this.addError(`Verb ${root}, ${stem}, ${conjugationType}, example ${index}: 'references' should be an array`)
    }
  }

  validateCrossReferences(verbs) {
    console.log('\n🔗 Validating cross-references...')

    for (const verb of verbs) {
      if (verb.cross_reference) {
        if (!this.allRoots.has(verb.cross_reference)) {
          this.addError(`Verb ${verb.root}: cross-reference points to non-existent verb '${verb.cross_reference}'`)
        }
      }
    }
  }

  async validate() {
    console.log('🔍 Starting validation...\n')

    const verbs = await this.loadVerbs()
    console.log(`📚 Loaded ${verbs.length} verbs\n`)

    // Validate each verb
    for (const verb of verbs) {
      this.validateVerb(verb)
    }

    // Validate cross-references
    this.validateCrossReferences(verbs)

    // Print results
    console.log('\n' + '='.repeat(60))
    console.log('📊 VALIDATION RESULTS')
    console.log('='.repeat(60))

    if (this.errors.length === 0 && this.warnings.length === 0) {
      console.log('\n✅ All validations passed! Data integrity is perfect.')
    } else {
      if (this.errors.length > 0) {
        console.log(`\n❌ ERRORS (${this.errors.length}):\n`)
        this.errors.forEach((error, i) => {
          console.log(`${i + 1}. ${error}`)
        })
      }

      if (this.warnings.length > 0) {
        console.log(`\n⚠️  WARNINGS (${this.warnings.length}):\n`)
        this.warnings.forEach((warning, i) => {
          console.log(`${i + 1}. ${warning}`)
        })
      }
    }

    console.log('\n' + '='.repeat(60))
    console.log(`Total verbs validated: ${verbs.length}`)
    console.log(`Unique roots: ${this.allRoots.size}`)
    console.log(`Errors: ${this.errors.length}`)
    console.log(`Warnings: ${this.warnings.length}`)
    console.log('='.repeat(60))

    // Exit with error code if there are errors
    if (this.errors.length > 0) {
      console.log('\n❌ Validation failed due to errors.')
      process.exit(1)
    } else if (this.warnings.length > 0) {
      console.log('\n⚠️  Validation passed with warnings.')
      process.exit(0)
    } else {
      console.log('\n✅ Validation completed successfully.')
      process.exit(0)
    }
  }
}

// Run validation
const validator = new DataValidator()
validator.validate().catch(error => {
  console.error('❌ Validation script failed:', error)
  process.exit(1)
})
