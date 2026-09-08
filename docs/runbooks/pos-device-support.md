# Runbook: POS / Device Support Triage

**Simulated Support Data.** Northstar Retail / OrderFlow is fictional; this runbook is a portfolio demonstration.

## When to Use This Runbook

A store associate reports a hardware or in-store connectivity issue: a register, receipt printer, barcode scanner, or store Wi-Fi/network problem.

## Step 1 — Scope the Impact

- **Single device (one register, one printer, one scanner):** Individual/Team impact. Continue with this runbook.
- **Whole store affected (all registers down, store-wide network outage):** Escalate immediately to Network Support and treat as higher priority — check whether other stores are affected too.

## Step 2 — Confirm It's Not an OrderFlow/Application Issue

Ask whether other registers or devices at the same store are working normally.

- If other devices work fine, this is a local hardware/connectivity issue — continue below.
- If all devices at the store show the same symptom and it correlates with an OrderFlow or network incident, escalate per [Incident Escalation and Prioritization](incident-escalation.md) instead.

## Step 3 — Basic Hardware Checks (Before Requesting a Replacement)

- **Receipt printer:** Check for paper jams, reseat the USB/network connection, print a test receipt.
- **Barcode scanner:** Confirm keyboard-entry workaround is available, check cable/battery, re-pair if wireless.
- **Wi-Fi/network:** Check signal strength at the affected location, compare to a wired device on the same network, note whether it's intermittent or constant.

## Step 4 — Apply a Workaround

- Route transactions to a working register/lane where possible.
- Use keyboard entry in place of a failing scanner.
- Use a wired connection in place of unreliable Wi-Fi where available.

## Step 5 — Escalate If Hardware Is Confirmed Faulty

- Ship a replacement device per the standard POS hardware process.
- For persistent network coverage issues, log a request for a site survey or access-point adjustment.

## Step 6 — Document and Close

- Record whether the issue was resolved remotely, with a workaround, or required a hardware swap.
- For recurring device issues at the same store, note it for a proactive hardware check.

## Related

- [Incident Escalation and Prioritization](incident-escalation.md)
