/**
 * WCAG 2.1 AA audit runner.
 * Logs in as each role, visits every routed page, runs axe-core + Lighthouse
 * (accessibility category only) against each, and writes:
 *   - audit/raw/<phase>-full.json      (everything, machine readable)
 *   - audit/raw/<phase>/<slug>.axe.json
 *   - audit/<phase>-report.md          (human readable summary)
 *
 * Usage: node scripts/run-audit.mjs baseline
 *        node scripts/run-audit.mjs after
 */
import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";
import lighthouse from "lighthouse";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const BASE_URL = "http://localhost:3000";
const CDP_PORT = 9222;

const phase = process.argv[2] || "baseline";
const RAW_DIR = path.join(ROOT, "raw", phase);
fs.mkdirSync(RAW_DIR, { recursive: true });

const CREDS = {
  jobseeker: { email: "a11y.jobseeker@example.com", password: "AccessAudit#2026" },
  recruiter: { email: "a11y.recruiter@example.com", password: "AccessAudit#2026" },
  admin: { email: "a11y.admin@example.com", password: "AccessAudit#2026" },
};

const PUBLIC_PAGES = [
  { label: "public-home", path: "/", role: "public" },
  { label: "public-login", path: "/login", role: "public" },
  { label: "public-register", path: "/register", role: "public" },
  { label: "public-verify-otp", path: "/verify-otp?email=a11y.jobseeker%40example.com", role: "public" },
];

const ROLE_PAGES = {
  jobseeker: [
    { label: "jobseeker-dashboard", path: "/dashboard" },
    { label: "jobseeker-profile", path: "/profile" },
    { label: "jobseeker-applications", path: "/applications" },
    { label: "jobseeker-messages", path: "/messages" },
    { label: "jobseeker-resumes", path: "/resumes" },
    { label: "jobseeker-job-search", path: "/jobs/search" },
  ],
  recruiter: [
    { label: "recruiter-dashboard", path: "/dashboard" },
    { label: "recruiter-company", path: "/company" },
    { label: "recruiter-jobs", path: "/jobs" },
    { label: "recruiter-applications", path: "/applications" },
    { label: "recruiter-messages", path: "/messages" },
  ],
  admin: [
    { label: "admin-dashboard", path: "/dashboard" },
    { label: "admin-users", path: "/admin/users" },
    { label: "admin-system", path: "/admin/system" },
    { label: "admin-audit", path: "/admin/audit" },
  ],
};

const WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"];

function wcagCriteriaFromTags(tags) {
  const out = new Set();
  for (const t of tags) {
    const m = /^wcag(\d)(\d)(\d{1,2})$/.exec(t);
    if (m) out.add(`${m[1]}.${m[2]}.${m[3]}`);
  }
  return [...out];
}

async function settle(page) {
  try {
    await page.waitForLoadState("networkidle", { timeout: 10000 });
  } catch {
    /* dev server may keep a websocket open; ignore */
  }
  try {
    await page
      .locator(".animate-spin")
      .first()
      .waitFor({ state: "detached", timeout: 5000 });
  } catch {
    /* no spinner present, or never resolved; continue anyway */
  }
  await page.waitForTimeout(400);
}

async function runAxe(page, entry) {
  const results = await new AxeBuilder({ page }).withTags(WCAG_TAGS).analyze();
  fs.writeFileSync(
    path.join(RAW_DIR, `${entry.label}.axe.json`),
    JSON.stringify(results, null, 2)
  );
  const bySeverity = { critical: 0, serious: 0, moderate: 0, minor: 0 };
  const criteria = new Set();
  const items = [];
  for (const v of results.violations) {
    bySeverity[v.impact ?? "minor"] = (bySeverity[v.impact ?? "minor"] || 0) + 1;
    wcagCriteriaFromTags(v.tags).forEach((c) => criteria.add(c));
    items.push({
      id: v.id,
      impact: v.impact,
      help: v.help,
      helpUrl: v.helpUrl,
      wcag: wcagCriteriaFromTags(v.tags),
      nodeCount: v.nodes.length,
      sampleSelector: v.nodes[0]?.target?.join(" ") ?? "",
      sampleHtml: (v.nodes[0]?.html ?? "").slice(0, 200),
    });
  }
  return {
    violationCount: results.violations.length,
    bySeverity,
    criteria: [...criteria].sort(),
    items,
  };
}

async function runLighthouseA11y(url, entry) {
  const runnerResult = await lighthouse(url, {
    port: CDP_PORT,
    output: "json",
    onlyCategories: ["accessibility"],
    disableStorageReset: true,
    logLevel: "error",
    formFactor: "desktop",
    screenEmulation: { disabled: true },
  });
  const lhr = runnerResult.lhr;
  fs.writeFileSync(
    path.join(RAW_DIR, `${entry.label}.lighthouse.json`),
    JSON.stringify(lhr, null, 2)
  );
  const score = lhr.categories.accessibility.score;
  const failedAudits = Object.values(lhr.audits)
    .filter((a) => a.score !== null && a.score < 1 && lhr.categories.accessibility.auditRefs.some((r) => r.id === a.id))
    .map((a) => ({ id: a.id, title: a.title, score: a.score }));
  return { score: score === null ? null : Math.round(score * 100), failedAudits };
}

async function loginAs(page, email, password) {
  await page.goto(`${BASE_URL}/login`, { waitUntil: "domcontentloaded" });
  await page.evaluate(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  });
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.fill("#email", email);
  await page.fill("#password", password);
  await Promise.all([
    page.waitForURL("**/dashboard", { timeout: 15000 }),
    page.click('button[type="submit"]'),
  ]);
  await settle(page);
}

async function auditEntry(page, entry) {
  const url = `${BASE_URL}${entry.path}`;
  console.log(`  -> ${entry.label} (${entry.path})`);
  try {
    if (page.url() !== url) {
      await page.goto(url, { waitUntil: "domcontentloaded" });
    }
    await settle(page);
    const axe = await runAxe(page, entry);
    const lh = await runLighthouseA11y(url, entry);
    return { ...entry, url, ok: true, axe, lighthouse: lh };
  } catch (err) {
    console.error(`     ERROR on ${entry.label}: ${err.message}`);
    return { ...entry, url, ok: false, error: err.message };
  }
}

async function main() {
  const userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), "a11y-audit-"));
  const context = await chromium.launchPersistentContext(userDataDir, {
    headless: true,
    args: [`--remote-debugging-port=${CDP_PORT}`],
  });
  const page = context.pages()[0] ?? (await context.newPage());
  await page.goto(BASE_URL, { waitUntil: "domcontentloaded" });

  const allResults = [];

  console.log(`\n[${phase}] Public pages`);
  for (const entry of PUBLIC_PAGES) {
    await page.evaluate(() => {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    });
    allResults.push({ role: "public", ...(await auditEntry(page, entry)) });
  }

  for (const role of Object.keys(ROLE_PAGES)) {
    console.log(`\n[${phase}] Logging in as ${role}`);
    await loginAs(page, CREDS[role].email, CREDS[role].password);
    for (const entry of ROLE_PAGES[role]) {
      allResults.push({ role, ...(await auditEntry(page, entry)) });
    }
  }

  await context.close();
  fs.rmSync(userDataDir, { recursive: true, force: true });

  fs.writeFileSync(
    path.join(ROOT, "raw", `${phase}-full.json`),
    JSON.stringify(allResults, null, 2)
  );

  writeReport(allResults, phase);
  console.log(`\nDone. See audit/${phase}-report.md`);
}

function writeReport(results, phase) {
  const lines = [];
  lines.push(`# ${phase === "baseline" ? "Baseline" : "Post-remediation"} Accessibility Audit Report`);
  lines.push("");
  lines.push(`Generated: ${new Date().toISOString()}`);
  lines.push("");
  lines.push("Tools: axe-core (via @axe-core/playwright), tags `wcag2a,wcag2aa,wcag21a,wcag21aa`; Lighthouse accessibility category (Chromium, desktop).");
  lines.push("");

  lines.push("## Summary table");
  lines.push("");
  lines.push("| Role | Page | Lighthouse A11y | Axe violations | Critical | Serious | Moderate | Minor | WCAG SC violated |");
  lines.push("|---|---|---|---|---|---|---|---|---|");
  let totals = { critical: 0, serious: 0, moderate: 0, minor: 0, violations: 0 };
  for (const r of results) {
    if (!r.ok) {
      lines.push(`| ${r.role} | ${r.path} | ERROR | ERROR | - | - | - | - | ${r.error} |`);
      continue;
    }
    const s = r.axe.bySeverity;
    totals.critical += s.critical;
    totals.serious += s.serious;
    totals.moderate += s.moderate;
    totals.minor += s.minor;
    totals.violations += r.axe.violationCount;
    lines.push(
      `| ${r.role} | \`${r.path}\` | ${r.lighthouse.score ?? "n/a"} | ${r.axe.violationCount} | ${s.critical} | ${s.serious} | ${s.moderate} | ${s.minor} | ${r.axe.criteria.join(", ") || "-"} |`
    );
  }
  lines.push("");
  lines.push(
    `**Totals: ${totals.violations} axe violations (critical=${totals.critical}, serious=${totals.serious}, moderate=${totals.moderate}, minor=${totals.minor})**`
  );
  lines.push("");

  const avgScores = results.filter((r) => r.ok && r.lighthouse.score !== null).map((r) => r.lighthouse.score);
  const avg = avgScores.length ? Math.round(avgScores.reduce((a, b) => a + b, 0) / avgScores.length) : "n/a";
  lines.push(`**Average Lighthouse accessibility score across ${avgScores.length} pages: ${avg}**`);
  lines.push("");

  lines.push("## Per-page detail");
  for (const r of results) {
    if (!r.ok) continue;
    lines.push("");
    lines.push(`### ${r.role} — \`${r.path}\` (${r.label})`);
    lines.push(`Lighthouse accessibility score: **${r.lighthouse.score ?? "n/a"}**`);
    lines.push("");
    if (r.axe.items.length === 0) {
      lines.push("No axe violations detected.");
    } else {
      lines.push("| Rule | Impact | WCAG | Nodes | Help | Sample selector |");
      lines.push("|---|---|---|---|---|---|");
      for (const it of r.axe.items) {
        lines.push(
          `| ${it.id} | ${it.impact} | ${it.wcag.join(", ") || "-"} | ${it.nodeCount} | ${it.help} | \`${it.sampleSelector}\` |`
        );
      }
    }
    if (r.lighthouse.failedAudits.length) {
      lines.push("");
      lines.push("Lighthouse failed audits:");
      for (const a of r.lighthouse.failedAudits) {
        lines.push(`- ${a.title} (score ${a.score})`);
      }
    }
  }

  fs.writeFileSync(path.join(ROOT, `${phase}-report.md`), lines.join("\n") + "\n");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
