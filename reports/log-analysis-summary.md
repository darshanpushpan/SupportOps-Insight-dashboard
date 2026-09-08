# Authentication Log Analysis Summary

**Simulated Support Data.** Northstar Retail / OrderFlow is fictional. This report is generated from `logs/authentication.log` for portfolio demonstration only.

- Generated at: 2026-09-07 23:13:41
- Source: `authentication.log`
- Parsed events: 82
- Malformed lines skipped: 2
- Time window: 2026-08-17 06:05:00 to 2026-08-17 12:15:00
- Failed-login threshold: 3

## Event counts

| Event | Count |
| --- | ---: |
| login_success | 37 |
| failed_login | 15 |
| session_refresh | 8 |
| password_reset | 4 |
| mfa_failure | 4 |
| password_policy_ok | 4 |
| account_lockout | 3 |
| account_unlock | 3 |
| mfa_enrollment_mismatch | 2 |
| mfa_reenroll | 2 |

## Failed logins by user

| User | Failed logins | Over threshold |
| --- | ---: | --- |
| finance.analyst01 | 4 | Yes |
| ops.coordinator01 | 4 | Yes |
| finance.analyst02 | 3 | Yes |
| finance.coordinator01 | 2 | No |
| store.associate06 | 2 | No |

## Locked accounts

- finance.analyst01
- finance.analyst02
- ops.coordinator01

## Unlocked accounts

- finance.analyst01
- finance.analyst02
- ops.coordinator01

## MFA failures and enrollment mismatch

- finance.analyst03: mfa_failure, mfa_failure, mfa_enrollment_mismatch
- ops.coordinator02: mfa_failure, mfa_failure, mfa_enrollment_mismatch

## Recommended support actions

- Alert after 3 failed logins (observed users: finance.analyst01, ops.coordinator01, finance.analyst02).
- Treat clustered lockouts as a multi-user access incident, not isolated password mistakes.
- Link password-reset guidance before unlock workflows so users do not retry the old password.
- Review MFA enrollment after device replacement or authenticator reset.
- Keep application health checks in view so access issues are not declared as OrderFlow outages.
- Follow company access-control and identity-verification policy before unlocking accounts or resetting passwords.

## Interpretation

Repeated failed logins after password resets created account lockouts. A smaller set of stale MFA enrollments caused verification failures. Successful logins continued for other users throughout the window, which supports treating this as an authentication/access incident rather than an OrderFlow outage.
