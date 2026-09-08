# Runbook: Incident Escalation and Prioritization

**Simulated Support Data.** Northstar Retail / OrderFlow is fictional; this runbook is a portfolio demonstration.

## Purpose

Help support staff decide (1) whether several tickets represent one incident rather than isolated issues, and (2) what priority to assign.

## Step 1 — Look for Clustering

Before working a ticket in isolation, check whether similar tickets have opened in the same time window:

- Same category (e.g., multiple Account Lockout tickets)
- Same affected service or component
- Same time window (typically within 30–60 minutes)

If three or more related tickets appear in a short window, treat them as one incident. Create or reference a single incident ID and link every related ticket to it (see [Incident Summary](../incident-summary.md) for an example, INC-20260817-001).

## Step 2 — Confirm Scope with Application Health

Check the [Operations](/operations) dashboard for health-check success rate, average API response time, and background job status covering the same window.

- **Healthy app + clustered auth failures:** Identity/access incident, not an outage. Route to Identity & Access.
- **Degraded health checks or failed jobs:** Possible application incident. Route to Application Support L2 and consider a broader communication (see [Incident Communication Templates](../incident-communication.md)).

## Step 3 — Assign Priority

| Priority | Guidance |
| --- | --- |
| P1 | Organization-wide outage or complete loss of a critical function with no workaround |
| P2 | Department- or team-level impact, or individual impact to a critical/time-sensitive function, with SLA typically 4 hours |
| P3 | Individual or limited impact with a workaround available; standard SLA |
| P4 | How-to requests, supply requests, or cosmetic issues with no functional impact |

Re-evaluate priority as scope becomes clearer — a ticket opened as P3 may need to move to P2 once clustering is discovered (see TCK-1023 in the sample data, reclassified in hindsight as part of an access-incident chain).

## Step 4 — Escalate

- Identity/access clusters → Identity & Access group.
- Application errors, performance, or data-sync issues → Application Support L2.
- Store hardware or connectivity → POS Support or Network Support.
- Anything requiring a product or engineering fix (not a config or account action) → escalate to app owners with reproduction steps.

## Step 5 — Track to Resolution

- Keep individual tickets linked to the incident record.
- Do not close the incident until all linked tickets are resolved or explicitly separated as unrelated.
- Capture follow-up/prevention actions in a root-cause analysis when the incident affected multiple users (see [Root-Cause Analysis](../root-cause-analysis.md) for the template).

## Related

- [Incident Summary](../incident-summary.md)
- [Root-Cause Analysis](../root-cause-analysis.md)
- [Incident Communication Templates](../incident-communication.md)
