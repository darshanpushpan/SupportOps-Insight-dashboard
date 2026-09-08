# Incident Communication Templates

**Simulated Support Data.** These templates use the fictional Northstar Retail / OrderFlow scenario for portfolio demonstration.

Use these as starting points when communicating about an active or resolved incident. Fill in the bracketed fields and remove any section that doesn't apply.

## Initial Notification (within 15 minutes of confirming multi-user impact)

```
Subject: [INVESTIGATING] OrderFlow access issue — [team/department] affected

We're investigating reports of sign-in issues affecting [N] users in [department].
OrderFlow itself is healthy (health checks and background jobs normal); this
appears to be an access/authentication issue, not an application outage.

Impact: [describe who/what is affected]
Started: [time]
Next update: [time, typically 30 min]
```

## Progress Update

```
Subject: [UPDATE] OrderFlow access issue — [team/department] affected

Status: [investigating / identified / monitoring]
What we know: [root cause if known, or leading theory]
What we're doing: [current mitigation steps]
Workaround: [if any]
Next update: [time]
```

## Resolution Notice

```
Subject: [RESOLVED] OrderFlow access issue — [team/department] affected

This issue is resolved as of [time]. Affected users have confirmed access is
restored. Root cause: [one-sentence summary].

We're monitoring for recurrence over the next 24 hours. Follow-up actions are
tracked in [link to incident summary / root-cause analysis].
```

## Guidance for Distinguishing Access Issues from Outages

Before declaring an application outage, confirm:

1. Are the affected users' login attempts failing with an *authentication* error (invalid credentials, lockout, MFA) rather than a page load or API error?
2. Do OrderFlow health checks, API response times, and background jobs look normal for the same window?
3. Are unaffected users still signing in and using the application successfully?

If the answer to all three is yes, communicate this as an access/identity issue, not an OrderFlow outage — this avoids unnecessary escalation to application engineering and sets the right expectation with affected users. See [Incident Escalation and Prioritization](runbooks/incident-escalation.md) for the full decision guide.

## Internal Handoff Note (when escalating between shifts or teams)

```
Ticket(s): [ticket IDs]
What happened: [1-2 sentences]
What's been tried: [steps taken so far]
What's still needed: [next steps]
Who to contact: [approver / SME if applicable]
```
