# Root-Cause Analysis — INC-20260817-001

**Simulated Support Data.** Northstar Retail / OrderFlow is fictional; this analysis is a portfolio demonstration, not a real postmortem.

## Problem Statement

Between 07:50 and 08:35 on 17 Aug 2026, three OrderFlow users were locked out of their accounts and two additional users experienced MFA verification failures, all within the same 45-minute window. Support initially needed to determine whether this was a single coordinated incident or a set of unrelated tickets.

## Five Whys — Account Lockouts

1. **Why did users get locked out?** They exceeded the failed-login threshold (3 attempts in a short window).
2. **Why did their logins fail?** They entered credentials that did not match the account's current password.
3. **Why didn't the credentials match?** Each user had just completed a password reset and retried with their previous (now stale) password before the reset had been acknowledged by the user.
4. **Why did they retry with the old password?** The reset confirmation did not clearly instruct users to use the *new* password immediately, and the login error message did not distinguish "wrong password" from "reset pending."
5. **Why does this matter operationally?** Without correlating the three lockouts by time and reset activity, each ticket could be treated as an isolated user error, delaying recognition of the underlying pattern and any needed communication to affected teams.

**Root cause:** Ambiguous post-reset guidance combined with a generic invalid-credentials error message caused predictable retry failures immediately after a password reset.

## Five Whys — MFA Failures

1. **Why did MFA verification fail?** The authenticator code did not match the enrolled factor.
2. **Why didn't it match?** The user had replaced their device and the old MFA enrollment was still active.
3. **Why wasn't the enrollment updated automatically?** Device replacement and MFA re-enrollment are separate, unlinked workflows.
4. **Why is that a gap?** Nothing in the device-replacement process prompts a review of MFA enrollment status.
5. **Why does this matter?** Users are blocked from signing in until Identity & Access manually clears the stale factor, adding avoidable resolution time.

**Root cause:** Device-replacement and MFA-enrollment workflows are not linked, leaving stale enrollments that fail silently until the next sign-in attempt.

## Contributing Factors

- No automated correlation of lockouts by time window meant three separate tickets had to be manually recognized as related.
- Application health signals (checks, API latency, job success) were healthy throughout, which helped rule out an OrderFlow outage quickly once reviewed — but this cross-check was not automatic.

## Corrective Actions

| Action | Owner | Status |
| --- | --- | --- |
| Add explicit "use your new password now" guidance to reset emails | Identity & Access | Planned |
| Distinguish "invalid credentials" from "reset pending" in the login error copy | Product | Backlog |
| Link MFA-enrollment review to device-replacement ticket closure | Identity & Access | Planned |
| Add a dashboard alert when 3+ lockouts occur within 15 minutes | Support Tooling | Planned |

## Verification

No recurrence was observed in the 24-hour monitoring window following the incident (see [Incident Summary](incident-summary.md)).
