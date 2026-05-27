# Phase 6 Runtime Task, Polling, and Event-Loop Gap Survey

This note records the current scheduler, task, polling, and event-loop substrate gap between the attached ZAR runtime archive and the bounded Phase 6 Zigux helper tranche.

## Why this note exists

Phase 6 is intentionally narrow in the roadmap: it allows new helper delivery under `lib/` without widening into runtime-core ownership. The attached ZAR runtime archive already exposes broader scheduler, task, polling, and event-loop surfaces, so this survey keeps that contrast explicit and reviewable.

## Roadmap-backed Phase 6 scope

- roadmap anchors: `lib/base64.c`, `lib/bsearch.c`, `lib/checksum.c`, and `lib/hexdump.c`
- required Phase 6 posture: leaf helper portability, clear API parity, and perf gates for math-sensitive helpers without runtime-core expansion

## Attached runtime surfaces already beyond the Phase 6 helper tranche

- scheduler substrate markers: `scheduler round-robin`, `scheduler priority budget`, `scheduler timeslice`, `scheduler disable-enable`, `scheduler reset`, `scheduler saturation`, and `scheduler wake-timer-clear`
- task lifecycle markers: `task lifecycle`, `active-task terminate`, `task resume interrupt-timeout`, `task resume timer-clear`, and `timer cancel task`
- polling and loop markers: `command-loop`, `telegram reply loop`, `pollDnsPacket`, `pollDnsPacketStrictInto`, `pollTcpPacketStrictInto`, and bounded receive timeouts
- tty event markers: `/runtime/tty/<name>/`, `events.log`, `transcript.log`, and `event_count`

## Current Phase 6 review posture

- review posture: keep this survey out of the bounded Phase 6 leaf-helper tranche and defer scheduler, task, polling, and event-loop substrate adoption to later roadmap-backed tooling or runtime lanes
- this note is a truthfulness survey only; it does not authorize Phase 6 to absorb scheduler policy, task state machines, timer queues, receive loops, or session event plumbing

## Evidence used

- evidence sources: `agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md`, `agent_files/ZAR-Zig-Agent-Runtime-main (11).zip`, `docs/operations.md`, and `src/baremetal/tty_runtime.zig`
