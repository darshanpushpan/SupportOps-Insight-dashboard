# Support Metrics Summary

**Simulated Support Data.** Northstar Retail / OrderFlow is fictional. Metrics below are computed from the 26 simulated tickets in `data/tickets.json` for portfolio demonstration only.

For live, filterable versions of these metrics, see the [Tickets](/tickets) and [Operations](/operations) dashboards — this document is a point-in-time snapshot for reference and printing.

## Volume by Status

| Status | Count |
| --- | ---: |
| Closed | 15 |
| Resolved | 3 |
| In Progress | 3 |
| Open | 3 |
| Escalated | 2 |

## Volume by Priority

| Priority | Count |
| --- | ---: |
| P1 | 0 |
| P2 | 7 |
| P3 | 14 |
| P4 | 5 |

## Volume by Category

| Category | Count |
| --- | ---: |
| Account Lockout | 4 |
| MFA Failure | 3 |
| Password Reset | 3 |
| Knowledge Base / How-To Request | 3 |
| POS Issue | 3 |
| Application Error | 2 |
| Performance / Slow Response | 2 |
| Data Sync / Integration | 2 |
| Network / Connectivity | 2 |
| User Access / Permissions | 2 |

## SLA Performance

| SLA Status | Count |
| --- | ---: |
| Met | 22 |
| At Risk | 4 |
| Breached | 0 |

## Recurring Categories (2+ tickets)

Recurring categories are a signal for runbook gaps or process fixes rather than one-off incidents. The three access-related categories (Account Lockout, MFA Failure, Password Reset) account for 10 of 26 tickets and are concentrated on 2026-08-17, reflecting the [INC-20260817-001](../docs/incident-summary.md) cluster.

## How to Regenerate

This snapshot mirrors the metrics computed live by `utils/ticket_store.compute_ticket_metrics()`. To regenerate ticket data itself, run:

```
python scripts/generate_sample_tickets.py
```

To regenerate the authentication log analysis, run:

```
python scripts/analyze_auth_logs.py
```
