# Incident Summary — INC-20260817-001

**Simulated Support Data.** Northstar Retail / OrderFlow is a fictional company and system created for portfolio demonstration only.

- Incident ID: INC-20260817-001
- Date: 2026-08-17
- Window: 07:50 – 12:10 (local)
- Severity: MEDIUM (multi-user access disruption, no application outage)
- Status: Resolved
- Related tickets: TCK-1001, TCK-1002, TCK-1003, TCK-1004, TCK-1005, TCK-1006, TCK-1023

## Summary

Between 07:50 and 08:35 on 17 Aug 2026, three OrderFlow users (two Finance analysts and one Operations coordinator) were locked out after repeated failed logins following password resets. In the same window, two additional users hit MFA verification failures traced to stale authenticator enrollments after device replacement. All affected users were restored within their SLA targets. OrderFlow application health checks, API response times, and background jobs remained normal throughout — this was an identity/access event, not a service outage.

## Timeline

| Time | Event |
| --- | --: |
| 07:50 | First password reset requested (finance.analyst01) |
| 08:08 – 08:21 | Failed logins escalate to account lockouts for three users |
| 08:10 | First unlock performed by Service Desk |
| 08:25 – 08:35 | MFA failures reported for two additional users (stale enrollment) |
| 11:00 | Final lockout-related unlock completed |
| 11:56 | Final MFA re-enrollment completed |
| 12:10 | Incident closed; 24-hour monitoring window begins |

## Impact

- 5 individual users affected across Finance and Operations.
- No OrderFlow outage: health checks stayed at 100% success, average API response time ~113ms, all scheduled jobs completed successfully.
- All affected tickets met their SLA targets.

## Root Cause

Users who completed a password reset attempted to sign in with cached or previously-typed credentials before the reset had propagated, triggering the failed-login threshold and an automatic lockout. Independently, two users had stale MFA enrollments following recent device replacements, which caused verification failures unrelated to the password-reset cluster.

See [Root-Cause Analysis](root-cause-analysis.md) for the full analysis and see the [Account Lockout](runbooks/account-lockout.md) and [MFA Troubleshooting](runbooks/mfa-troubleshooting.md) runbooks used to resolve individual tickets.

## Resolution

- Identity & Access verified each user and unlocked accounts per policy.
- Users were pointed to password-reset guidance to avoid retrying old credentials.
- MFA enrollments were reset for the two affected users after identity verification.
- No application-side changes were required.

## Follow-up Actions

- Add lockout guidance directly to the password-reset confirmation email.
- Surface a remaining-attempts counter on the login page (product backlog item).
- Trigger an MFA enrollment review whenever a device-replacement ticket is closed.
- Continue monitoring the affected accounts for 24 hours (completed with no recurrence).
