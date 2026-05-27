# Phase 6 Runtime Task, Poll, And Event-Loop Gap Survey

This note records the bounded gap between the current Phase 6 Zigux helper packet and the broader runtime task, polling, and event-loop substrate visible in the attached ZAR runtime references.

## Why this survey exists

Phase 6 remains intentionally narrow in the product roadmap. Its approved helper anchors are still:

- `lib/base64.c`
- `lib/bsearch.c`
- `lib/checksum.c`
- `lib/hexdump.c`

The attached runtime archive already shows richer task, polling, and scheduler-oriented control surfaces. Writing that down keeps the current Phase 6 packet truthful: it makes those runtime substrates reviewable as comparison material without implying that Zigux Phase 6 has already widened into runtime pilot or event-loop delivery work.

## Runtime task and polling surfaces visible in the attached archive

The attached `docs/operations.md`, `src/runtime/tool_runtime.zig`, and `src/runtime/task_receipts.zig` show four relevant runtime-substrate families:

### 1. Polling-based session and task update delivery

The runtime contract describes polling-based update delivery for both session events and task receipts, including:

- ACP `eventDelivery.mode = "poll"`
- `acp.sessions.events`
- `tasks.events`
- `tasks.get`

That is a live runtime update-delivery substrate, not a Phase 6 leaf-helper replay.

### 2. Process polling and long-running runtime work

The runtime service also exposes a dedicated process-poll surface, including:

- `process.poll`
- process state readback
- running and finished timestamps
- stdout and stderr byte counts
- timeout and signal status

That is runtime task orchestration pressure, not helper-only Phase 6 evidence.

### 3. Persisted task receipts and task-event recording

The task-receipt layer records durable task metadata and task-event trails, including:

- `recordTaskReceipt(...)`
- `recordTaskEvent(...)`
- `recordSessionEvent(...)`
- persisted task summaries, step counts, and status updates

That is runtime task-state bookkeeping, not a bounded helper portability slice.

### 4. Scheduler and wake/timer probe pressure

The runtime operations snapshot also documents a broad scheduler and timer validation surface, including:

- scheduler baseline, disable/enable, reset, policy-switch, saturation, and priority-budget probes
- timer wake, timer quantum, timer cancel, and periodic timer probes
- wake-queue, task-resume, and scheduler-wake timer-clear probes

That is event-loop and dispatch substrate pressure, not truthful evidence that Zigux Phase 6 already owns a scheduler or polling runtime.

## What this means for Zigux Phase 6

The roadmap-backed Phase 6 packet should stay bounded to the four helper anchors and their direct helper, parity, fixture, checker, and perf evidence.

This survey therefore treats the runtime task, polling, and event-loop families as:

- relevant future pressure from the attached runtime archive
- useful comparison material for later runtime-facing phases
- out of scope for current Phase 6 progress claims

A fresh attached-reference reread on 2026-05-27 did not change that boundary. The truthful Phase 6 product scope is still the four helper anchors above, while the runtime task, polling, and event-loop substrate remains comparison material rather than shipped helper evidence.

## Honest next-step boundary

Use this note only as a boundary reminder.

Do not use it to claim that Zigux Phase 6 has already landed:

- task receipt orchestration
- polling-based runtime update delivery
- process lifecycle polling
- scheduler dispatch, wake, or timer-loop ownership

Those surfaces belong to later product phases if and when the roadmap deliberately widens into tooling, runtime pilots, or deeper runtime substrate work.

## Source grounding

This survey is grounded in:

- `agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md`
- `agent_files/ZAR-Zig-Agent-Runtime-main (11).zip`
  - `docs/operations.md`
  - `src/runtime/tool_runtime.zig`
  - `src/runtime/task_receipts.zig`

Reopen this note only when the shared Phase 6 packet needs to restate the boundary between helper-only progress and broader runtime task, polling, or event-loop substrate work.
