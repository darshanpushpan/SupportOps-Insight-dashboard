# Runbook: Account Lockout

**Simulated Support Data.** Northstar Retail / OrderFlow is fictional; this runbook is a portfolio demonstration.

## When to Use This Runbook

A user reports an "account locked" message after failed sign-in attempts, or you see `account_lockout` events for the user in `logs/authentication.log`.

## Step 1 — Verify Identity

Confirm the user's identity per company access-control policy before discussing the account or performing an unlock. Never unlock an account based on an unverified request.

## Step 2 — Check for a Pattern Before Unlocking

Search the authentication log or the [Operations](/operations) dashboard for other lockouts in the same time window.

- **One user, isolated:** Likely a typo, Caps Lock, or a one-off mistake. Proceed to Step 3.
- **Multiple users, same window:** Treat as a possible multi-user access incident. See [Incident Escalation and Prioritization](incident-escalation.md) before working tickets individually — related tickets should be linked to one incident record.

## Step 3 — Determine the Trigger

Check whether the lockout followed a recent password reset:

- If yes, the user likely retried with their previous password. After unlocking, explicitly tell them to use the *new* password from the reset email, not to retry the old one.
- If no, ask about Caps Lock, keyboard layout, or a saved/autofilled old password in their browser.

## Step 4 — Unlock the Account

1. Unlock per the identity-and-access unlock procedure.
2. Do not reset the password unless the user specifically requests it or has forgotten it — unlocking and resetting are different actions.
3. Ask the user to sign in immediately while you're on the call/chat to confirm success.

## Step 5 — Document and Prevent Recurrence

- Note the trigger (post-reset retry, typo, etc.) in `root_cause_category`.
- If post-reset retries are a repeat pattern, flag it as a candidate for clearer reset-confirmation copy (see [Incident Communication Templates](../incident-communication.md) for messaging).
- Close only after the user confirms they can sign in.

## Related

- [User Cannot Sign In](user-cannot-sign-in.md)
- [MFA Troubleshooting](mfa-troubleshooting.md)
- [Incident Escalation and Prioritization](incident-escalation.md)
