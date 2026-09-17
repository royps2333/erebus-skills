# Boundary and Recovery Decision Table

| Observation | What it establishes | Next check or action |
| --- | --- | --- |
| Later verification supersedes an older failure report | Historical finding was resolved within its verified scope | Check for new evidence; do not repeat a completed repair |
| Deliberately injected failure produces a duplicate | Failure mode is reproducible under that injection | Record a reproduced risk; do not label it an observed natural incident |
| No durable intake row | Work may not have been accepted; logs may be incomplete | Check webhook response/poll offset, retention and transaction outcome before replay |
| Intake exists; no saved reply | Generation unfinished, failed or commit missing | Check active ownership, timeout and late-result fencing; recover generation only if needed |
| Reply exists; no attempted send | Output survived generation | Deliver saved output under a single atomic claim |
| Confirmed API rejection | This attempt failed according to the responding API | Classify payload/auth/recipient versus rate limit; preserve reply; check earlier attempts separately |
| Timeout/reset/proxy failure during send | Remote acceptance is unknown | Hold or retry according to documented product tradeoff; do not regenerate output |
| Telegram receipt observed; local receipt commit failed | Acceptance occurred, but durable local knowledge may be lost | Recover known receipt if available; otherwise preserve uncertainty across restart |
| Restart finds `sending` | Crash could precede or follow remote acceptance | Treat as unknown; lease expiry alone does not prove nonacceptance |
| Saved receipt; user reports no reply | API acceptance was recorded | Verify chat/topic, payload, later deletion and client state within access scope |
| First part sent; later part failed | Partial logical reply | Resume only eligible unsent parts; do not replay the whole batch |
| One history pair; two remote messages | Generation may be idempotent while delivery is not | Compare outbound attempts and receipt-loss window |

An explicit rejection applies to that attempt, not every attempt sharing its
logical key. An HTTP status from an intermediary may not be a Telegram rejection.
When no reliable evidence distinguishes acceptance from nonacceptance, retain
that uncertainty in the diagnosis.

## Offline simulator

`simulate.py` models durable intake, saved generation, an atomic send claim,
a fake remote inbox and local receipt persistence. It contrasts:

- `hold`: retain unknown sends without replay;
- `retry`: explicitly reset an unknown attempt and risk another remote delivery.

The fake remote inbox is an oracle available only to the test. A production bot
cannot assume it can enumerate sent-message history to reconcile arbitrary sends.
Tests reopen the local database while preserving the fake remote inbox, modeling
application restart. Faults are injected before generation, before remote
acceptance, after acceptance with lost response, and during local receipt commit.

This is a teaching fixture, not a production queue. It does not implement live
Telegram errors, rate limiting, multi-process scheduling, cancellation, multipart
messages, security boundaries, webhook delivery, or a real power-loss test.
