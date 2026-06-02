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

// The skills and their expected reference files, per ARCHITECTURE §12.
// Note: the always-on main skill folder is `sidekick-core`, NOT `sidekick`. The
// plugin itself is named `sidekick`, so a skill folder named `sidekick` would
// collide (`sidekick:sidekick`) and break Cowork command resolution.
const SKILLS = ['sidekick-core', 'sidekick-init', 'sidekick-triage', 'sidekick-checkin', 'sidekick-archive', 'sidekick-status', 'sidekick-find', 'sidekick-report'];

const EXPECTED_TREE = [
  '.claude-plugin/plugin.json',
  '.claude-plugin/marketplace.json',
  'skills/sidekick-core/SKILL.md',
  'skills/sidekick-core/references/interaction-style.md',
  'skills/sidekick-core/references/data-discipline.md',
  'skills/sidekick-core/references/brain-protocol.md',
  'skills/sidekick-core/references/write-disciplines.md',
  'skills/sidekick-core/references/project-structure.md',
  'skills/sidekick-core/references/reporting.md',
  'skills/sidekick-core/references/ui-kit.md',
  'skills/sidekick-core/references/project-claude-template.md',
  'skills/sidekick-core/references/agenda-template.md',
  'skills/sidekick-core/assets/ui.css',
  'skills/sidekick-core/assets/ui.js',
  'skills/sidekick-core/scripts/data.py',
  'skills/sidekick-init/SKILL.md',
  'skills/sidekick-init/references/settings-template.md',
  'skills/sidekick-triage/SKILL.md',
  'skills/sidekick-triage/references/triage-template.md',
  'skills/sidekick-checkin/SKILL.md',
  'skills/sidekick-archive/SKILL.md',
  'skills/sidekick-status/SKILL.md',
  'skills/sidekick-find/SKILL.md',
  'skills/sidekick-report/SKILL.md',
  'commands/sidekick-init.md',
  'commands/sidekick-triage.md',
  'commands/sidekick-checkin.md',
  'commands/sidekick-archive.md',
  'commands/sidekick-status.md',
  'commands/sidekick-find.md',
  'commands/sidekick-report.md',
  'docs/ARCHITECTURE.md',
  'README.md',
];

// The explicit-action skills. Each needs a flat commands/<name>.md file —
// that is what Cowork turns into a typed `/<name>` command (skills/ alone only
// gives model-invocation + a menu entry). Modeled on the working solidcortex
// plugin. The plugin is named `sidekick`; the always-on main skill is therefore
// named `sidekick-core` (a skill named `sidekick` would collide with the plugin
// → `sidekick:sidekick` → broken resolution). The main skill is model-invoked
// (no command file).
const EXPLICIT_SKILLS = ['sidekick-init', 'sidekick-triage', 'sidekick-checkin', 'sidekick-archive', 'sidekick-status', 'sidekick-find', 'sidekick-report'];

// --- Check 1: expected tree exists -----------------------------------------
console.log('\n# Check 1 — expected tree (ARCHITECTURE §12)');
for (const p of EXPECTED_TREE) {
  if (existsSync(join(ROOT, p))) pass(p);
  else fail(`${p} is missing`);
}
// Only the two manifests belong inside .claude-plugin/
const cpDir = join(ROOT, '.claude-plugin');
const CP_ALLOWED = new Set(['plugin.json', 'marketplace.json']);
if (existsSync(cpDir)) {
  const extras = readdirSync(cpDir).filter((f) => !CP_ALLOWED.has(f));
  if (extras.length === 0) pass('.claude-plugin/ holds only plugin.json + marketplace.json');
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
    warn(`name is "${manifest.name}", expected "sidekick"`);
  }
  // The real install-blocker found 2026-06-01: `repository` as an OBJECT makes the
  // manifest invalid (schema wants a string), so Cowork loaded skills but rejected
  // the commands. Must be a string.
  if (manifest.repository !== undefined && typeof manifest.repository !== 'string') {
    fail('repository must be a STRING (an object fails manifest validation and breaks command registration)');
  } else if (typeof manifest.repository === 'string') {
    pass('repository is a string');
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

// --- Check 2b: marketplace manifest ----------------------------------------
console.log('\n# Check 2b — marketplace.json');
const mpPath = join(ROOT, '.claude-plugin/marketplace.json');
let marketplace = null;
try {
  marketplace = JSON.parse(readFileSync(mpPath, 'utf8'));
  pass('marketplace.json parses as JSON');
} catch (e) {
  fail(`marketplace.json does not parse: ${e.message}`);
}
if (marketplace) {
  if (typeof marketplace.name === 'string' && marketplace.name.length > 0) pass(`marketplace name present ("${marketplace.name}")`);
  else fail('marketplace name is missing or empty (required)');
  if (marketplace.owner && typeof marketplace.owner.name === 'string') pass('owner.name present');
  else fail('owner.name is missing (required)');
  if (Array.isArray(marketplace.plugins) && marketplace.plugins.length > 0) {
    pass(`plugins[] present (${marketplace.plugins.length})`);
    for (const p of marketplace.plugins) {
      if (!p.name) { fail('a plugin entry is missing name'); continue; }
      if (p.source === undefined) { fail(`plugin "${p.name}" is missing source`); continue; }
      // Relative-path source must start with ./ and resolve to a plugin root.
      if (typeof p.source === 'string') {
        if (!p.source.startsWith('./')) fail(`plugin "${p.name}" source "${p.source}" must start with "./"`);
        const target = join(ROOT, p.source, '.claude-plugin/plugin.json');
        if (existsSync(target)) pass(`plugin "${p.name}" → ${p.source} (resolves to ${rel(target)})`);
        else fail(`plugin "${p.name}" source "${p.source}" has no .claude-plugin/plugin.json`);
      } else {
        pass(`plugin "${p.name}" uses a non-relative source (${p.source.source || 'object'}) — not checked here`);
      }
      // Consistency: the self-referenced plugin name should match plugin.json.
      if (manifest && p.source === './' && p.name !== manifest.name) {
        warn(`marketplace lists "${p.name}" but plugin.json name is "${manifest.name}"`);
      }
    }
  } else fail('plugins[] is missing or empty (required)');
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
// Matches both own refs (`references/x.md`) and cross-skill refs
// (`../sidekick-core/references/x.md`); the `../<dir>/` prefix is generic.
const REF_RE = /(?:\.\.\/[A-Za-z0-9._-]+\/)?references\/[A-Za-z0-9._/-]+\.md/g;
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
// Only typed `/sidekick-<name>` commands are real; a bare `/sidekick` is not a
// command (the main skill is model-invoked) and would also false-match the
// filesystem path `plugins/sidekick/…`. So require the `-<name>` suffix.
const CMD_RE = /\/sidekick-[a-z]+/g;
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

// --- Check 6: commands/ files back each explicit skill ---------------------
console.log('\n# Check 6 — commands/ files (typed /<skill>, solidcortex pattern)');
for (const skill of EXPLICIT_SKILLS) {
  const cmdPath = join(ROOT, 'commands', `${skill}.md`);
  if (!existsSync(cmdPath)) { fail(`missing commands/${skill}.md`); continue; }
  const fm = parseFrontmatter(readFileSync(cmdPath, 'utf8'));
  if (!fm) { fail(`commands/${skill}.md has no frontmatter`); continue; }
  if (fm.name !== skill) fail(`commands/${skill}.md name "${fm.name}" != "${skill}"`);
  else if (!fm.description) fail(`commands/${skill}.md missing description`);
  else pass(`commands/${skill}.md → /${skill}`);
}

// --- Informational: command forms ------------------------------------------
console.log('\n# Info — Cowork command forms (modeled on the solidcortex plugin)');
info('Always-on (model-invoked, no command file): sidekick');
info('Explicit skills: commands/<name>.md → bare /<name> (plugin name ≠ "sidekick"):');
for (const skill of EXPLICIT_SKILLS) {
  info(`  ${skill}  →  /${skill}`);
}

// --- Summary ----------------------------------------------------------------
console.log(`\n${'-'.repeat(60)}`);
console.log(`Result: ${fails === 0 ? 'PASS' : 'FAIL'}  (${fails} fail, ${warns} warn)`);
process.exit(fails === 0 ? 0 : 1);
