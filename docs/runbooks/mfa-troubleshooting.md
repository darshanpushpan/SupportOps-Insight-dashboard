# Runbook: MFA Troubleshooting

**Simulated Support Data.** Northstar Retail / OrderFlow is fictional; this runbook is a portfolio demonstration.

## When to Use This Runbook

A user's password is accepted but multi-factor authentication (MFA) fails, or you see `mfa_failure` or `mfa_enrollment_mismatch` events in `logs/authentication.log`.

## Step 1 — Confirm This Is an MFA Issue, Not a Password Issue

If the user reports "invalid credentials," that's a password/lockout problem — see [Account Lockout](account-lockout.md) instead. This runbook applies only when the password step succeeds and the MFA/verification step fails.

## Step 2 — Verify Identity

MFA resets and re-enrollments are sensitive actions. Confirm identity per policy before clearing any enrollment.

## Step 3 — Ask About Recent Device Changes

The most common cause of MFA failure is a recent phone replacement, factory reset, or authenticator app reinstall that left a stale enrollment on the account.

- If the user replaced a device recently, this is almost certainly a stale-enrollment issue. Proceed to Step 4.
- If not, ask whether the authenticator's clock is in sync (rare, but can cause code rejection) and whether they're using the correct account within their authenticator app.

## Step 4 — Clear the Stale Enrollment and Re-enroll

1. Remove the stale MFA factor per the identity-and-access procedure.
2. Guide the user through re-enrollment on their current device.
3. Confirm a full successful sign-in (password + MFA) before closing.

## Step 5 — Document and Prevent Recurrence

- Note `stale_device` or `stale_factor` as the reason in the ticket.
- Suggest linking MFA-enrollment review to device-replacement tickets going forward, so this doesn't require a separate support contact (see [Root-Cause Analysis](../root-cause-analysis.md) for the related corrective action).

## Related

- [User Cannot Sign In](user-cannot-sign-in.md)
- [Account Lockout](account-lockout.md)
