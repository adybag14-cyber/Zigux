# Phase 6 Runtime Command and Environment Gap Survey

This note records the current control-surface gap between the ZAR runtime archive and the bounded Phase 6 Zigux roadmap slice.

## Why this note exists

Phase 6 is intentionally narrow: the roadmap names only four greenfield leaf helpers under `lib/` and describes the product goal as low-risk helper delivery without runtime-core expansion. The ZAR runtime archive, however, already carries a much broader command, session, and persisted environment-control surface. This survey keeps that contrast explicit so later review does not accidentally treat runtime control plumbing as already belonging to the Phase 6 helper tranche.

## Roadmap-backed Phase 6 scope

- product goal: low-risk new helper code in Zigux without taking runtime-core risk
- roadmap anchors:
  - `lib/base64.c`
  - `lib/bsearch.c`
  - `lib/checksum.c`
  - `lib/hexdump.c`
- required features:
  - leaf helper portability
  - clear API parity
  - perf gates for math-sensitive helpers
- transfer-table reminder: the roadmap's ZAR-to-Zigux mapping marks shell, TTY, and tool-service runtime work as indirect product value that should inform later tooling or validation UX, not expand the near-term product surface by itself

## ZAR runtime command surfaces already present

The attached runtime archive already exposes bounded command and control surfaces that are materially broader than the Phase 6 helper tranche:

- bounded shell-control slice:
  - `shell-run <command[;command...]>`
  - `shell-expand <pattern>`
  - direct wrapper bypass for `shell-run`, `tty-send`, and `tty-shell`
- bounded TTY/session control slice:
  - `tty-list`
  - `tty-open <name>`
  - `tty-send <name> <command>`
  - `tty-shell <name> <script>`
  - `tty-clear <name>`
  - `tty-close <name>`
- typed tool-service and runtime control verbs from the runtime operations notes:
  - `CMD`
  - `EXEC`
  - `APPSTATE`
  - `APPRUN`
  - `DISPLAYINFO`
  - `DISPLAYSET`
  - `TRUSTLIST`
  - `TRUSTSELECT`
  - `RUNTIMESNAPSHOT`
  - `RUNTIMESESSION`

## ZAR persisted environment-control surfaces already present

The same runtime archive also carries persisted control and state paths that go beyond helper-local Phase 6 work:

- `/runtime/tty/<name>/`
- `/dev/tty/sessions/<name>/{info,input,pending,stdout,stderr,events,transcript}`
- `/sys/tty/sessions/<name>/{info,input,pending,stdout,stderr,events,transcript}`
- `/runtime/state/runtime-state.json`
- `/runtime/workspaces/<name>.txt`

These are real runtime control surfaces, not leaf-helper parity artifacts.

## Current Phase 6 review posture

- keep the Phase 6 packet tied to `lib/base64.zig`, `lib/bsearch.zig`, `lib/checksum.zig`, and `lib/hexdump.zig` plus their bounded evidence surfaces
- treat this survey as a truthfulness guard only; it does not authorize Phase 6 to absorb shell, TTY, tool-service, app-lifecycle, display-control, trust-store, or runtime-session plumbing
- if later lanes need these ZAR surfaces, route them through future roadmap-backed tooling or runtime work instead of widening the Phase 6 helper tranche

## Evidence used

- roadmap source: `agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md`
- runtime archive sources:
  - `agent_files/ZAR-Zig-Agent-Runtime-main (11).zip :: docs/operations.md`
  - `agent_files/ZAR-Zig-Agent-Runtime-main (11).zip :: docs/zig-port/ZAR_VS_ZIGOS_SHELL_CONTROL_SLICE_PLAN.md`
  - `agent_files/ZAR-Zig-Agent-Runtime-main (11).zip :: docs/zig-port/ZAR_VS_ZIGOS_TTY_CONTROL_SLICE_PLAN.md`
