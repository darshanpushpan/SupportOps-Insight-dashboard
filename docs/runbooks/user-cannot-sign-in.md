# Runbook: User Cannot Sign In

**Simulated Support Data.** Northstar Retail / OrderFlow is fictional; this runbook is a portfolio demonstration.

## When to Use This Runbook

A user reports they cannot sign in to OrderFlow, and it is not yet clear whether this is a password issue, a lockout, an MFA problem, or something else. Use this as the entry point, then branch to a more specific runbook once you've identified the failure type.

## Step 1 — Verify Identity

Follow company identity-verification policy before discussing account details or taking any action. Never reset a password or discuss account status without confirming identity first.

## Step 2 — Classify the Failure

Ask the user exactly what they see, or check the authentication log for the user's alias:

| Symptom | Likely cause | Go to |
| --- | --- | --- |
| "Invalid credentials" repeatedly, then "account locked" | Lockout | [Account Lockout](account-lockout.md) |
| Password accepted, MFA code rejected | MFA/enrollment issue | [MFA Troubleshooting](mfa-troubleshooting.md) |
| Reset email never arrived | Mail delivery / spam filter | Step 3 below |
| Login succeeds but expected feature/role missing | Permissions, not a login failure | Escalate as an access request, not an incident |
| Multiple users affected in the same window | Possible incident | [Incident Escalation and Prioritization](incident-escalation.md) |

## Step 3 — Password Reset Not Received

1. Confirm the email address on file matches what the user expects.
2. Ask the user to check spam/junk folders.
3. If more than 15 minutes have passed with no delivery, check mail-flow status before resending.
4. Do not resend more than once within a short window — this can itself trigger a lockout pattern once the user retries.

## Step 4 — Check Application Health Before Assuming an Outage

Before treating this as an OrderFlow outage, check the [Operations](/operations) dashboard for health-check success rate, average API response time, and background job status. A single user's login failure is rarely an application outage if other users are signing in successfully.

## Step 5 — Document and Close

- Record the failure type and resolution in the ticket's root-cause category.
- Confirm with the user that access is restored before closing.
- If this is part of a pattern (3+ similar tickets in a short window), see [Incident Escalation and Prioritization](incident-escalation.md).

## Related

- [Account Lockout](account-lockout.md)
- [MFA Troubleshooting](mfa-troubleshooting.md)
- [Incident Escalation and Prioritization](incident-escalation.md)
