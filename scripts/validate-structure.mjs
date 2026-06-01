#!/usr/bin/env node
// Sidekick plugin structure validator (plan 01).
// Zero-dependency. Verifies the on-disk layout against docs/ARCHITECTURE.md §12,
// the plugin manifest, every skill's frontmatter, and all cross-references.
// Prints PASS / WARN / FAIL per check and exits non-zero on any FAIL.
//
// Run:  node scripts/validate-structure.mjs

import { readFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve, relative } from 'node:path';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

let fails = 0;
let warns = 0;
const rel = (p) => relative(ROOT, p).replaceAll('\\', '/');
function pass(msg) { console.log(`PASS  ${msg}`); }
function warn(msg) { console.log(`WARN  ${msg}`); warns++; }
function fail(msg) { console.log(`FAIL  ${msg}`); fails++; }
function info(msg) { console.log(`      ${msg}`); }

// The five skills and their expected reference files, per ARCHITECTURE §12.
const SKILLS = ['sidekick', 'sidekick-init', 'sidekick-triage', 'sidekick-checkin', 'sidekick-archive'];

const EXPECTED_TREE = [
  '.claude-plugin/plugin.json',
  'skills/sidekick/SKILL.md',
  'skills/sidekick/references/interaction-style.md',
  'skills/sidekick/references/database-discipline.md',
  'skills/sidekick/references/brain-protocol.md',
  'skills/sidekick/references/write-disciplines.md',
  'skills/sidekick/references/project-claude-template.md',
  'skills/sidekick/references/agenda-template.md',
  'skills/sidekick-init/SKILL.md',
  'skills/sidekick-init/references/settings-template.md',
  'skills/sidekick-triage/SKILL.md',
  'skills/sidekick-triage/references/triage-template.md',
  'skills/sidekick-checkin/SKILL.md',
  'skills/sidekick-archive/SKILL.md',
  'docs/ARCHITECTURE.md',
  'README.md',
];

// --- Check 1: expected tree exists -----------------------------------------
console.log('\n# Check 1 — expected tree (ARCHITECTURE §12)');
for (const p of EXPECTED_TREE) {
  if (existsSync(join(ROOT, p))) pass(p);
  else fail(`${p} is missing`);
}
// Nothing other than plugin.json inside .claude-plugin/
const cpDir = join(ROOT, '.claude-plugin');
if (existsSync(cpDir)) {
  const extras = readdirSync(cpDir).filter((f) => f !== 'plugin.json');
  if (extras.length === 0) pass('.claude-plugin/ holds only plugin.json');
  else fail(`.claude-plugin/ has unexpected entries: ${extras.join(', ')}`);
}

// --- Check 2: manifest ------------------------------------------------------
console.log('\n# Check 2 — plugin.json manifest');
const manifestPath = join(ROOT, '.claude-plugin/plugin.json');
let manifest = null;
try {
  manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
  pass('plugin.json parses as JSON');
} catch (e) {
  fail(`plugin.json does not parse: ${e.message}`);
}
if (manifest) {
  // Required by Cowork/Claude Code: only `name`.
  if (typeof manifest.name === 'string' && manifest.name.length > 0) pass(`name present ("${manifest.name}")`);
  else fail('name is missing or empty (required)');
  if (manifest.name && manifest.name !== 'sidekick') {
    warn(`name is "${manifest.name}", expected "sidekick" (repo + main skill folder)`);
  }
  // Present in current manifest; warn if absent (not fatal).
  for (const f of ['version', 'description', 'author']) {
    if (manifest[f] !== undefined) pass(`${f} present`);
    else warn(`${f} absent (recommended)`);
  }
  // Release-polish fields — warn only (added in plan 13).
  for (const f of ['repository', 'license', 'keywords', 'homepage']) {
    if (manifest[f] === undefined) warn(`optional ${f} absent (add at release, plan 13)`);
  }
}

// --- frontmatter parse helper ----------------------------------------------
function parseFrontmatter(text) {
  if (!text.startsWith('---')) return null;
  const end = text.indexOf('\n---', 3);
  if (end === -1) return null;
  const block = text.slice(text.indexOf('\n') + 1, end);
  const out = {};
  for (const line of block.split('\n')) {
    const m = line.match(/^([A-Za-z_][\w-]*):\s*(.*)$/);
    if (m) out[m[1]] = m[2].trim();
  }
  return out;
}

// --- Check 3: skill frontmatter --------------------------------------------
console.log('\n# Check 3 — SKILL.md frontmatter');
const skillBodies = {}; // name -> { path, body }
for (const skill of SKILLS) {
  const skillPath = join(ROOT, 'skills', skill, 'SKILL.md');
  if (!existsSync(skillPath)) { fail(`${rel(skillPath)} missing`); continue; }
  const text = readFileSync(skillPath, 'utf8');
  const fm = parseFrontmatter(text);
  skillBodies[skill] = { path: skillPath, text };
  if (!fm) { fail(`${skill}: no YAML frontmatter`); continue; }
  if (!fm.name) fail(`${skill}: frontmatter missing name`);
  else if (fm.name !== skill) fail(`${skill}: frontmatter name "${fm.name}" != folder "${skill}"`);
  else pass(`${skill}: name matches folder`);
  if (!fm.description) fail(`${skill}: frontmatter missing description`);
  else if (fm.description.length < 20) warn(`${skill}: description suspiciously short (${fm.description.length} chars)`);
  else if (fm.description.length > 1024) warn(`${skill}: description very long (${fm.description.length} chars)`);
  else pass(`${skill}: description present (${fm.description.length} chars)`);
}

// --- Check 4: reference paths resolve --------------------------------------
console.log('\n# Check 4 — references/... paths resolve');
const REF_RE = /(?:\.\.\/sidekick\/)?references\/[A-Za-z0-9._/-]+\.md/g;
let refCount = 0;
for (const skill of SKILLS) {
  const entry = skillBodies[skill];
  if (!entry) continue;
  const skillDir = dirname(entry.path);
  const seen = new Set(entry.text.match(REF_RE) || []);
  for (const ref of seen) {
    refCount++;
    const target = resolve(skillDir, ref);
    const crossSkill = ref.startsWith('../');
    if (existsSync(target)) {
      pass(`${skill} → ${ref}${crossSkill ? '  (cross-skill)' : ''}`);
    } else {
      fail(`${skill} → ${ref} does NOT resolve (${rel(target)})`);
    }
  }
}
if (refCount === 0) warn('no references/... paths found in any SKILL.md (unexpected)');

// --- Check 5: dead /sidekick-* command references --------------------------
console.log('\n# Check 5 — /sidekick-* command references');
const CMD_RE = /\/sidekick(?:-[a-z]+)?/g;
const derived = new Set();
for (const skill of SKILLS) {
  const entry = skillBodies[skill];
  if (!entry) continue;
  for (const cmd of entry.text.match(CMD_RE) || []) derived.add(cmd);
}
for (const cmd of [...derived].sort()) {
  const folder = cmd.slice(1); // strip leading /
  if (existsSync(join(ROOT, 'skills', folder))) pass(`${cmd} → skills/${folder}/ exists`);
  else fail(`${cmd} referenced but skills/${folder}/ does not exist`);
}

// --- Informational: derived command names (form not asserted, plan 12) -----
console.log('\n# Info — derived command names (form verified on install, plan 12)');
info('Skills present (model-invocable regardless of typed form):');
for (const skill of SKILLS) {
  info(`  ${skill}  →  namespaced /sidekick:${skill}  |  bare /${skill}`);
}

// --- Summary ----------------------------------------------------------------
console.log(`\n${'-'.repeat(60)}`);
console.log(`Result: ${fails === 0 ? 'PASS' : 'FAIL'}  (${fails} fail, ${warns} warn)`);
process.exit(fails === 0 ? 0 : 1);
