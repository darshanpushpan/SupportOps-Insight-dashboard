# Runbook: Application Performance Triage

**Simulated Support Data.** Northstar Retail / OrderFlow is fictional; this runbook is a portfolio demonstration.

## When to Use This Runbook

A user reports OrderFlow feels slow — a page, report, or list takes longer than usual to load — but the application is otherwise functioning (orders save, users can sign in).

## Step 1 — Confirm It's Slowness, Not a Failure

Distinguish "slow" from "broken":

- The page/feature eventually loads or completes → performance issue, use this runbook.
- The page/feature errors out or never completes → treat as an [Application Error](#related) instead, and check for wider impact.

## Step 2 — Check Application Health

Review the [Operations](/operations) dashboard:

- **Health checks near 100% and API response times near baseline:** Likely a specific heavy operation (large date range, large report, peak-hour load), not a systemic issue. Proceed to Step 3.
- **Health checks degraded or API times elevated across the board:** Possible systemic performance incident — escalate to Application Support L2 and consider linking related tickets per [Incident Escalation and Prioritization](incident-escalation.md).

## Step 3 — Narrow the Cause

Ask or check for:

- Unusually wide date ranges on reports.
- Large batch operations (e.g., wide pick-waves, bulk exports).
- Time of day — many performance tickets cluster around peak hours (e.g., receiving windows, month-end reporting).

## Step 4 — Apply a Workaround

- Suggest narrowing the date range or batch size.
- For recurring peak-hour slowness, note it as a candidate for caching or query optimization (product/engineering follow-up), not a support-side fix.

## Step 5 — Document and Close

- Record the average API time and health-check status observed at the time, for comparison against future reports.
- Close once the user confirms acceptable performance with the workaround, or once the underlying query/report has been optimized.

## Related

- [Incident Escalation and Prioritization](incident-escalation.md)
