# Telegram API boundaries

Checked against official documentation on 2026-09-17. Recheck before implementation.

- [Making requests](https://core.telegram.org/bots/api#making-requests): API results
  distinguish success from failure. Validate the response; an HTTP exchange alone
  is not sufficient evidence of a successful bot operation.
- [sendMessage](https://core.telegram.org/bots/api#sendmessage): success returns a
  Message. Its documented parameters do not expose a caller-supplied idempotency
  key. Do not invent one or assume a local outbox provides remote deduplication.
- [ResponseParameters](https://core.telegram.org/bots/api#responseparameters):
  `retry_after` supplies a flood-control wait in seconds when provided.
- [getUpdates](https://core.telegram.org/bots/api#getupdates): advancing offset
  past an update confirms it; persist accepted work before that advance.

The inference for retry design: losing the response after acceptance creates an
uncertain window. A local receipt transaction cannot atomically commit with the
remote Telegram send. This is a distributed-systems limitation, not a documented
promise that every timeout produces a duplicate.

Other protocols may offer different deduplication contracts. A protocol migration
requires its own authentication, persistence, replay and failure validation; it
is outside this skill's default repair scope.
