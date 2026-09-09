# Baseline Accessibility Audit Report

Generated: 2026-09-09T12:35:40.556Z

Tools: axe-core (via @axe-core/playwright), tags `wcag2a,wcag2aa,wcag21a,wcag21aa`; Lighthouse accessibility category (Chromium, desktop).

## Summary table

| Role | Page | Lighthouse A11y | Axe violations | Critical | Serious | Moderate | Minor | WCAG SC violated |
|---|---|---|---|---|---|---|---|---|
| public | `/` | 100 | 0 | 0 | 0 | 0 | 0 | - |
| public | `/login` | 100 | 0 | 0 | 0 | 0 | 0 | - |
| public | `/register` | 100 | 0 | 0 | 0 | 0 | 0 | - |
| public | `/verify-otp?email=a11y.jobseeker%40example.com` | 100 | 0 | 0 | 0 | 0 | 0 | - |
| jobseeker | `/dashboard` | 100 | 0 | 0 | 0 | 0 | 0 | - |
| jobseeker | `/profile` | 94 | 1 | 1 | 0 | 0 | 0 | 4.1.2 |
| jobseeker | `/applications` | 93 | 1 | 1 | 0 | 0 | 0 | 4.1.2 |
| jobseeker | `/messages` | 100 | 0 | 0 | 0 | 0 | 0 | - |
| jobseeker | `/resumes` | 88 | 2 | 2 | 0 | 0 | 0 | 4.1.2 |
| jobseeker | `/jobs/search` | 94 | 1 | 1 | 0 | 0 | 0 | 4.1.2 |
| recruiter | `/dashboard` | 100 | 0 | 0 | 0 | 0 | 0 | - |
| recruiter | `/company` | 100 | 0 | 0 | 0 | 0 | 0 | - |
| recruiter | `/jobs` | 94 | 1 | 1 | 0 | 0 | 0 | 4.1.2 |
| recruiter | `/applications` | 93 | 1 | 1 | 0 | 0 | 0 | 4.1.2 |
| recruiter | `/messages` | 100 | 0 | 0 | 0 | 0 | 0 | - |
| admin | `/dashboard` | 100 | 0 | 0 | 0 | 0 | 0 | - |
| admin | `/admin/users` | 100 | 0 | 0 | 0 | 0 | 0 | - |
| admin | `/admin/system` | 100 | 0 | 0 | 0 | 0 | 0 | - |
| admin | `/admin/audit` | 94 | 1 | 1 | 0 | 0 | 0 | 4.1.2 |

**Totals: 8 axe violations (critical=8, serious=0, moderate=0, minor=0)**

**Average Lighthouse accessibility score across 19 pages: 97**

## Per-page detail

### public — `/` (public-home)
Lighthouse accessibility score: **100**

No axe violations detected.

### public — `/login` (public-login)
Lighthouse accessibility score: **100**

No axe violations detected.

### public — `/register` (public-register)
Lighthouse accessibility score: **100**

No axe violations detected.

### public — `/verify-otp?email=a11y.jobseeker%40example.com` (public-verify-otp)
Lighthouse accessibility score: **100**

No axe violations detected.

### jobseeker — `/dashboard` (jobseeker-dashboard)
Lighthouse accessibility score: **100**

No axe violations detected.

### jobseeker — `/profile` (jobseeker-profile)
Lighthouse accessibility score: **94**

| Rule | Impact | WCAG | Nodes | Help | Sample selector |
|---|---|---|---|---|---|
| select-name | critical | 4.1.2 | 1 | Select element must have an accessible name | `select` |

Lighthouse failed audits:
- Select elements do not have associated label elements. (score 0)

### jobseeker — `/applications` (jobseeker-applications)
Lighthouse accessibility score: **93**

| Rule | Impact | WCAG | Nodes | Help | Sample selector |
|---|---|---|---|---|---|
| select-name | critical | 4.1.2 | 1 | Select element must have an accessible name | `select` |

Lighthouse failed audits:
- Select elements do not have associated label elements. (score 0)

### jobseeker — `/messages` (jobseeker-messages)
Lighthouse accessibility score: **100**

No axe violations detected.

### jobseeker — `/resumes` (jobseeker-resumes)
Lighthouse accessibility score: **88**

| Rule | Impact | WCAG | Nodes | Help | Sample selector |
|---|---|---|---|---|---|
| label | critical | 4.1.2 | 1 | Form elements must have labels | `input` |
| select-name | critical | 4.1.2 | 1 | Select element must have an accessible name | `select` |

Lighthouse failed audits:
- Form elements do not have associated labels (score 0)
- Select elements do not have associated label elements. (score 0)

### jobseeker — `/jobs/search` (jobseeker-job-search)
Lighthouse accessibility score: **94**

| Rule | Impact | WCAG | Nodes | Help | Sample selector |
|---|---|---|---|---|---|
| select-name | critical | 4.1.2 | 3 | Select element must have an accessible name | `div:nth-child(2) > select` |

Lighthouse failed audits:
- Select elements do not have associated label elements. (score 0)

### recruiter — `/dashboard` (recruiter-dashboard)
Lighthouse accessibility score: **100**

No axe violations detected.

### recruiter — `/company` (recruiter-company)
Lighthouse accessibility score: **100**

No axe violations detected.

### recruiter — `/jobs` (recruiter-jobs)
Lighthouse accessibility score: **94**

| Rule | Impact | WCAG | Nodes | Help | Sample selector |
|---|---|---|---|---|---|
| select-name | critical | 4.1.2 | 2 | Select element must have an accessible name | `.p-4.rounded.border:nth-child(3) > select` |

Lighthouse failed audits:
- Select elements do not have associated label elements. (score 0)

### recruiter — `/applications` (recruiter-applications)
Lighthouse accessibility score: **93**

| Rule | Impact | WCAG | Nodes | Help | Sample selector |
|---|---|---|---|---|---|
| select-name | critical | 4.1.2 | 2 | Select element must have an accessible name | `select:nth-child(1)` |

Lighthouse failed audits:
- Select elements do not have associated label elements. (score 0)

### recruiter — `/messages` (recruiter-messages)
Lighthouse accessibility score: **100**

No axe violations detected.

### admin — `/dashboard` (admin-dashboard)
Lighthouse accessibility score: **100**

No axe violations detected.

### admin — `/admin/users` (admin-users)
Lighthouse accessibility score: **100**

No axe violations detected.

### admin — `/admin/system` (admin-system)
Lighthouse accessibility score: **100**

No axe violations detected.

### admin — `/admin/audit` (admin-audit)
Lighthouse accessibility score: **94**

| Rule | Impact | WCAG | Nodes | Help | Sample selector |
|---|---|---|---|---|---|
| select-name | critical | 4.1.2 | 1 | Select element must have an accessible name | `select` |

Lighthouse failed audits:
- Select elements do not have associated label elements. (score 0)
