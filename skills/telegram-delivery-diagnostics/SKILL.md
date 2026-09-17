---
name: telegram-delivery-diagnostics
description: >-
  Investigate reported missing or duplicate Telegram bot replies and review retry
  behavior by tracing intake, generation, sends, and receipts. Establish whether
  a current defect exists before proposing a repair. Use for delivery diagnostics
  and outbox reviews, not general bot setup or formatting.
---

# Telegram Delivery Diagnostics

Locate the last proven boundary of one logical reply before changing retry behavior.
A timeout is an unknown outcome unless evidence establishes that no send occurred.

## 1. Establish Current Status

Start with the report or review question, not an assumed incident. Check the
latest relevant deployment, repair, recovery and closure evidence before relying
on an older finding. Classify the result:

| Status | Required distinction | Appropriate outcome |
| --- | --- | --- |
| Current failure observed | Evidence matches the affected version and time window | Diagnose the failed boundary |
| Previously resolved | Later evidence supersedes the old finding | Report resolution; do not repeat the repair |
| Failure mode reproduced | A fixture or deliberate fault triggers the behavior | Describe a risk or known limitation, not a spontaneous incident |
| Not reproduced / insufficient evidence | Available observations cannot establish the reported failure | State what remains unknown; propose only the missing check |
| No defect found within scope | Relevant checks passed for the stated scope | Report that scope; no repair required |

A recovered connection may need no restart. A deliberate lost-receipt test does
not establish a natural outage. Missing historical logs establish an evidence
gap, not either a failure or error-free operation. Keep these conclusions bounded
by the evidence date; historical closure is not proof of current health.

## 2. Trace the Evidence

Identify the affected bot, transport (HTTP Bot API or another protocol), recipient
scope, time window, symptom and permitted work. Use existing context; ask only for
missing facts that block diagnosis. Diagnosis alone does not authorize a live test
message, webhook replacement, queue reset or transport migration.

Read relevant code and sanitized operational evidence. Track one update through:

`received → durably accepted → reply saved → send attempted → remote accepted → receipt saved`

Use a scoped update key, logical outbound key, attempt identifier, timestamps and
state transitions. Include recipient/topic identity in routing checks, but redact
it from shared reports. Do not log bot tokens, token-bearing URLs, raw private
messages or complete exception objects. Source code establishes a possible failure
window; it does not prove that a particular live incident occurred there.

## 3. Identify the Boundary

Read [the decision table](references/decision-table.md). Distinguish absence of a
record from proof of absence when logging coverage is incomplete.

- **Intake:** check persistence relative to webhook acknowledgement or polling
  offset advancement. Acknowledging before durable intake can lose work on crash.
- **Generation:** determine whether a reply already exists. Reuse saved output
  during delivery recovery. A generation timeout can leave a late result; fence
  stale completions before they overwrite newer state.
- **Delivery:** separate a proven rejection from ambiguous transport failure.
  Inspect SDK/proxy retries as well as application retries.
- **Receipt:** remote acceptance and local receipt persistence are separate
  commits. A crash between them cannot be repaired by a local transaction alone.
- **Visibility:** an API acknowledgement does not establish device rendering or
  human reading. Check destination and topic before calling an acknowledged reply
  missing or sending a replacement.

## 4. Select a Scoped Response

If no current repair is justified, stop with the diagnostic finding. A known
limitation can be documented without changing production.

Preserve the application's chosen tradeoff. If it is unspecified and affects the
repair, explain the choice: retrying unknown sends favors eventual delivery but
can duplicate; holding them favors duplicate avoidance but can omit a reply.
Neither policy establishes exactly-once delivery.

For local idempotency, scope intake keys to the bot/source and update. Persist
reply and outbox transition atomically where possible. Separate inbound identity
from outbound part identity; chunked messages require per-part receipts. Serialize
or atomically claim sends; leases need fencing and explicit treatment of expired
in-flight sends. Do not blindly reset `sending` to `ready` after restart.

Honor a confirmed rate-limit response's retry delay, add bounded scheduling, and
surface exhausted or held work. Permanent recipient/auth/payload rejections need
correction, not an infinite retry loop. A format fallback is another send: use it
only after a confirmed rejection that establishes nonacceptance for that attempt.
A gateway error or timeout alone does not establish that.

Do not prescribe a new queue, database or protocol unless the diagnosed failure
requires it. Recheck current Telegram method contracts before transport-specific
changes; see [API boundaries](references/api-boundaries.md).

## 5. Verify and Report

Use the bundled offline simulator to understand the uncertainty window:

```sh
cd "<skill-directory>"
python3 -B scripts/simulate.py
python3 -B -m unittest discover -s scripts -p 'test_*.py'
```

It uses only Python's standard library, synthetic data and temporary SQLite.
It never connects to Telegram. See its limits in the decision-table reference.
Adapt tests to the actual implementation before claiming a production repair.
Relevant cases include duplicate intake, generation failure, saved-output retry,
confirmed rejection, rate-limit delay, acceptance with lost response, receipt-save
failure, restart during send, concurrent workers and partial multipart delivery.
Run the cases relevant to the changed boundary; don't claim untested coverage.

Use this compact reporting structure, omitting inapplicable fields:

- **Status:** current failure, resolved, reproduced risk, insufficient evidence,
  or no defect found within scope.
- **Evidence:** version/time window, last proven boundary and supporting records.
- **Conclusion:** what is established, what is inferred and what remains unknown.
- **Action:** no change, further observation, or the justified scoped repair.
- **Verification:** tests actually run and the limits of their results.

Distinguish code reproduction, deployment verification, Telegram acceptance and
observed client delivery. Never describe a demonstrated limitation as eliminated
unless the verification actually establishes that result.
