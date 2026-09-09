# WCAG 2.1 AA Audit & Remediation — Summary

Scope: the secure job search platform's React frontend (19 distinct routed views, audited as a job seeker, a recruiter, and an admin — logged in via the real login flow for each role). Tools: axe-core 4.10 (via `@axe-core/playwright`, WCAG tags `wcag2a,wcag2aa,wcag21a,wcag21aa` only) and Lighthouse 11's accessibility category, both run headless against the live local app. Full machine-readable results are in `baseline-report.md` / `after-report.md` and `raw/baseline/`, `raw/after/`.

## Before / after

| Metric | Baseline | After |
|---|---|---|
| Average Lighthouse accessibility score (19 pages) | 97 | **100** |
| Pages scoring 100 | 12 / 19 | **19 / 19** |
| Axe violations — critical | 8 | **0** |
| Axe violations — serious / moderate / minor | 0 / 0 / 0 | 0 / 0 / 0 |
| Total axe violations | 8 | **0** |

Per-page Lighthouse score, before → after:

| Role | Page | Before | After |
|---|---|---|---|
| public | `/` | 100 | 100 |
| public | `/login` | 100 | 100 |
| public | `/register` | 100 | 100 |
| public | `/verify-otp` | 100 | 100 |
| jobseeker | `/dashboard` | 100 | 100 |
| jobseeker | `/profile` | 94 | 100 |
| jobseeker | `/applications` | 93 | 100 |
| jobseeker | `/messages` | 100 | 100 |
| jobseeker | `/resumes` | 88 | 100 |
| jobseeker | `/jobs/search` | 94 | 100 |
| recruiter | `/dashboard` | 100 | 100 |
| recruiter | `/company` | 100 | 100 |
| recruiter | `/jobs` | 94 | 100 |
| recruiter | `/applications` | 93 | 100 |
| recruiter | `/messages` | 100 | 100 |
| admin | `/dashboard` | 100 | 100 |
| admin | `/admin/users` | 100 | 100 |
| admin | `/admin/system` | 100 | 100 |
| admin | `/admin/audit` | 94 | 100 |

All 8 baseline axe violations were `select-name`/`label` (WCAG **4.1.2**, critical impact) — bare `<select>` elements and one file `<input>` with no accessible name. Note on the intermediate step: fixing the missing `<h1>` on the Profile page (see below) initially introduced a new Lighthouse `heading-order` finding (h1 → h3, skipping h2) that a pure axe-only re-check would have missed — the four section headings on that page were h3 and needed to become h2. Caught it in the same re-audit pass and fixed it before calling this done; final numbers above already include that fix.

## WCAG 2.1 AA criteria addressed

| SC | What was wrong | Fix |
|---|---|---|
| **4.1.2** Name, Role, Value | 8 `<select>`/`<input>` elements with zero accessible name (axe-flagged) | Added `aria-label` or `id`/`htmlFor` label pairing |
| **4.1.2** Name, Role, Value | ~15 additional `<label>` elements visually adjacent to a control but not programmatically associated (no `htmlFor`/`id`) — passed axe's fallback-to-placeholder check but the *visible* label text wasn't what a screen reader would announce | Paired every such label with its control via matching `id`/`htmlFor` |
| **4.1.2** Name, Role, Value | ~20 placeholder-only inputs (`GroupMessagingPage`, `EnhancedProfilePage`, `CompanyManagementPage`, `AdminUserManagementPage`, `LoginPage`'s reset form) relying on placeholder-as-accessible-name, which disappears once text is entered | Added explicit `aria-label` or `sr-only` `<label>` to each |
| **1.3.1** Info and Relationships | 3 pages (`JobSearchPage`, `AdminAuditPage`, `ApplicationStatusPage`) rendered their own `<main>` nested inside the shared layout's `<main>`, producing duplicate/ambiguous landmarks | Changed the inner element to `<div>` — one `main` landmark per page |
| **1.3.1** / **2.4.6** Headings and Labels | 5 pages (`EnhancedProfilePage`, `JobManagementPage`, `EnhancedResumePage`, `GroupMessagingPage`, `AdminUserManagementPage`) had no `<h1>` — their only heading was an `<h2>`, so the page had no top-level landmark in the heading outline | Promoted the page title to `<h1>`; demoted `EnhancedProfilePage`'s now-orphaned `<h3>` subsections to `<h2>` to keep the outline sequential |
| **1.4.3** Contrast (Minimum) | Disabled "Applied" button text (`slate-400` on `slate-100`, ~2.4:1) — not caught by axe, which exempts disabled controls from its contrast check, but still visible to low-vision users | Changed to `slate-600` on `slate-200` (~6.3:1) |
| **2.4.1** Bypass Blocks | No explicit mechanism to skip the header/sidebar before reaching page content (automated check passed only because landmarks/headings exist) | Added a visible-on-focus "Skip to main content" link as the first focusable element |
| **4.1.3** Status Messages | 5 loading spinners (`Loader`, dashboard, applications, company, audit-log pages) gave no indication to screen reader users that content was loading | Added `role="status" aria-live="polite"` to the spinner containers, `aria-hidden="true"` on the decorative spinner graphic |
| **1.1.1** Non-text Content | Hamburger/close icon `<svg>`s relied solely on adjacent `sr-only` text; unhidden SVGs can be exposed to the accessibility tree as an empty graphics-document node by some browser/AT combinations | Added `aria-hidden="true" focusable="false"` to both decorative SVGs |
| **2.4.3** Focus Order (mobile nav) | The mobile sidebar drawer opened without moving focus into it, had no Escape-to-close, and didn't return focus to the hamburger button on close | Added focus-on-open (first nav link), Escape-to-close, focus-return-to-trigger, and a Tab focus trap while open |
| **4.1.2** Name, Role, Value / **2.4.3** Focus Order (OTP dialog) | The raw-DOM "virtual keyboard OTP" modal (used for every high-risk action — job post/update, resume download/delete, admin suspend/delete/reactivate, key rotation) had no dialog role, no accessible name, didn't move focus in on open, didn't restore focus on close, and had no Escape handling | Added `role="dialog" aria-modal="true" aria-labelledby aria-describedby`, focus-on-open (first keypad digit), focus-restore-on-close, Escape-to-cancel, Tab focus trap, and a live region announcing the digits selected so far |

## Files changed

- `frontend/src/components/Loader.jsx`
- `frontend/src/components/Navbar.jsx`
- `frontend/src/components/Sidebar.jsx`
- `frontend/src/components/Layout.jsx`
- `frontend/src/services/api.js`
- `frontend/src/pages/EnhancedProfilePage.jsx`
- `frontend/src/pages/GroupMessagingPage.jsx`
- `frontend/src/pages/JobManagementPage.jsx`
- `frontend/src/pages/EnhancedResumePage.jsx`
- `frontend/src/pages/AdminUserManagementPage.jsx`
- `frontend/src/pages/ApplicationStatusPage.jsx`
- `frontend/src/pages/JobSearchPage.jsx`
- `frontend/src/pages/AdminAuditPage.jsx`
- `frontend/src/pages/CompanyManagementPage.jsx`
- `frontend/src/pages/RoleBasedDashboard.jsx`
- `frontend/src/pages/LoginPage.jsx`

(`frontend/src/pages/*.js` — the non-`.jsx` `HomePage.js`, `LoginPage.js`, `RegisterPage.js`, `DashboardPage.js`, `ProfilePage.jsx`, `ResumePage.jsx`, `AdminDashboard.js` — are dead code, not imported by `App.jsx`'s router, and were left untouched.)

## Things I did not fix, and why

- **Error/status banner announcements**: the inline red/green message banners (login errors, form save confirmations, etc. — plain `<p>` elements that appear after a state change) do not use `aria-live`. I didn't add it because several of these banners sit far from the field that triggered them or above content that re-renders a moment later, and blindly wrapping all of them in a live region risks over-announcing or announcing stale text on unrelated re-renders. This needs a per-form judgment call I didn't want to guess at — flagged for manual review below.
- **Background inert-ness behind the mobile sidebar and the OTP modal**: both now trap `Tab` correctly, but I did not add `inert` (or `aria-hidden="true"` toggling) to the rest of the page behind them. A screen reader's virtual cursor (arrow-key browsing, not `Tab`) can still reach content behind the overlay even though it's visually covered. This is a real gap; I left it because reliably toggling `aria-hidden` across a arbitrary React tree from a vanilla-DOM modal (the OTP one) without accidentally hiding the modal itself needed more certainty than I had — better to flag it than ship a half-right ARIA change.
- **`Navbar`'s desktop-only "Profile" link** (`hidden sm:inline-flex`) stays in the DOM (and thus in the accessibility tree / tab order) even when visually hidden on mobile widths. Not fixed — out of the original triage list, noted for awareness.

## MANUAL TESTING NEEDED (please verify with keyboard + NVDA)

Automated tools cannot verify these — please check by hand:

**Keyboard-only, full login → dashboard flow (all 3 roles):**
- [ ] Tab order matches visual reading order on every page, especially the card grids on `RoleBasedDashboard` and the filter grid on `JobSearchPage`.
- [ ] First `Tab` press on any page reveals the "Skip to main content" link; `Enter` moves focus to the page content.
- [ ] Open the mobile sidebar (narrow viewport or resize below `md`): focus lands on the first nav link, `Tab`/`Shift+Tab` cycles within the sidebar only, `Escape` closes it and returns focus to the hamburger button.
- [ ] Trigger the virtual-keyboard OTP modal (e.g. recruiter → Job Management → submit a job; or job seeker → Resumes → Download/Delete an uploaded resume): focus moves into the modal, `Tab` cycles only within it, `Escape` cancels and returns focus to the triggering button.
- [ ] Confirm no keyboard trap exists anywhere else, and that every button/link in every page (including the export CSV/JSON/print buttons on Audit Logs, the connection accept/remove buttons on Profile) is reachable and operable via `Tab` + `Enter`/`Space`.

**NVDA pass through the same flow:**
- [ ] Landmark navigation (`Insert+F7` → Landmarks): confirm exactly one `main` region per page now (3 pages had duplicates before this pass).
- [ ] Heading navigation (`Insert+F7` → Headings, or `H` key): confirm one `h1` per page and no skipped levels — I fixed 5 missing-`h1` pages and one `h1`→`h3` skip, but did not exhaustively re-check every page's full heading tree by ear.
- [ ] Listen to how each fixed `<select>` is announced (e.g. "Select job to view applicants, combo box") — automated tools only confirm *a* name exists, not that it's the *right*, non-redundant name.
- [ ] Virtual OTP keypad: since digits are randomized per button for security, confirm NVDA announces each digit clearly as `Tab` moves focus across the keypad, and that the dialog's title ("Virtual Keyboard OTP") and purpose ("Job action completed with PKI + virtual OTP verification" type context) is announced on open via the `aria-labelledby`/`aria-describedby` I added.
- [ ] Confirm the `role="status"` loading announcements ("Loading...") are actually spoken when they appear — live-region announcement timing varies by how the node enters the DOM, and I could not verify actual NVDA output myself.
- [ ] Listen for the arrow-key virtual cursor while the mobile sidebar / OTP modal is open — confirm whether background page content is still reachable (see "inert-ness" gap above); if NVDA can read past the overlay, that's a real bug to file.
- [ ] Confirm the per-applicant status `<select>` on Applicant Management announces sensibly even when applicant data is incomplete (fallback text is `"applicant #<id>"`).
- [ ] Confirm the disabled "Applied" button on Job Search is announced as unavailable/dimmed, and that the higher-contrast text is legible at 200% browser zoom.
