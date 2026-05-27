# Phase 6 Runtime Command And Environment Gap Survey

This note records the bounded control-surface gap between the Phase 6 Zigux roadmap packet and the much broader runtime command, session, and persisted environment surfaces described in the attached ZAR runtime references.

## Why this survey exists

Phase 6 is intentionally narrow in the product roadmap. Its job is to land low-risk leaf helpers only:

- `lib/base64.c`
- `lib/bsearch.c`
- `lib/checksum.c`
- `lib/hexdump.c`

The attached ZAR runtime archive already documents richer runtime-control surfaces that sit well beyond that helper tranche. Keeping this gap written down makes the Phase 6 packet more truthful: it prevents those runtime-control capabilities from being mistaken for current Zigux Phase 6 scope, and it gives later phases a small owner note they can cite instead of widening helper evidence by implication.

## Runtime control surfaces visible in the attached runtime archive

The attached `docs/operations.md`, `docs/zig-port/ZAR_VS_ZIGOS_SHELL_CONTROL_SLICE_PLAN.md`, and `docs/zig-port/ZAR_VS_ZIGOS_TTY_CONTROL_SLICE_PLAN.md` show four relevant control-surface families:

### 1. Bounded shell command control

The shell-control slice documents a bounded shell layer over existing builtins and framed tool-service routes, including:

- `shell-run <command[;command...]>`
- `shell-expand <pattern>`
- bounded command batching
- bounded glob expansion
- bounded stdin, stdout, and stderr redirection
- typed framed `SHELLRUN` and `SHELLEXPAND` requests

That is a runtime command substrate, not a Phase 6 leaf-helper replay.

### 2. Bounded TTY and session control

The TTY-control slice documents persisted session state and typed command submission surfaces, including:

- `tty-open`, `tty-close`, `tty-info`, `tty-read`
- `tty-send <name> <command>`
- `tty-shell <name> <script>`
- persisted receipts under `/runtime/tty/<name>/`
- `/dev/tty/...` and `/sys/tty/...` exports
- typed `TTY*` request families over the framed control path

That is session and command-routing behavior, not helper-only Phase 6 evidence.

### 3. Typed runtime-service control

The operations snapshot also describes a typed runtime-service bridge with:

- `RUNTIMECALL`
- `RUNTIMESNAPSHOT`
- `RUNTIMESESSIONS`
- `RUNTIMESESSION`

It explicitly ties those calls to persisted runtime-state readback such as `/runtime/state/runtime-state.json`. This is a real runtime control surface rather than a narrow helper portability slice.

### 4. Persisted environment and orchestration state

The same runtime snapshot records persisted control-state families under `/runtime`, including:

- persisted install layout under `/runtime/install`
- runtime snapshot and service state under `/runtime/state/`
- persisted workspace definitions under `/runtime/workspaces/`
- persisted workspace-run receipts under `/runtime/workspace-runs/`
- persisted app autorun receipts under `/runtime/apps/`

These are environment-plumbing and orchestrator-state surfaces. They are valuable reference pressure, but they are not truthful evidence that Zigux Phase 6 already owns a runtime command or persisted environment subsystem.

## What this means for Zigux Phase 6

The roadmap-backed Phase 6 packet should stay bounded to the four helper anchors and their direct helper, parity, fixture, checker, and perf evidence.

This survey therefore treats the runtime command, TTY, runtime-service, and persisted environment-control families as:

- relevant future pressure from the attached runtime archive
- useful comparison material for later roadmap phases
- out of scope for current Phase 6 progress claims

A fresh current-master reread on 2026-05-27 did not change that boundary. The four roadmap-backed helper anchors remain the only truthful Phase 6 product scope, and the broader runtime command and persisted environment surfaces are still comparison material rather than helper evidence.

## Honest next-step boundary

While this survey is part of the shared Phase 6 evidence packet, it should only be used as a boundary note.

Do not use it to claim that Zigux Phase 6 has already landed:

- shell execution semantics
- TTY session control
- runtime RPC/session control
- persisted workspace or app-runtime environment orchestration

Those surfaces belong to later product phases if and when the roadmap deliberately widens into tooling or runtime pilot work.

## Source grounding

This survey is grounded in:

- `agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md`
- `agent_files/ZAR-Zig-Agent-Runtime-main (11).zip`
  - `docs/operations.md`
  - `docs/zig-port/ZAR_VS_ZIGOS_SHELL_CONTROL_SLICE_PLAN.md`
  - `docs/zig-port/ZAR_VS_ZIGOS_TTY_CONTROL_SLICE_PLAN.md`

Reopen this note only when the shared Phase 6 packet needs to restate the boundary between helper-only progress and broader runtime command or persisted environment plumbing work.
