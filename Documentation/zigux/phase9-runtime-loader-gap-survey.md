# Phase 9 Runtime Loader Gap Survey

This document records the shared boot/runtime loader gap that still separates
the landed `samples/zigux/runtime_*` starter surface from any future
`zigux/kernel/runtime_loader.zig` consumer.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-loader-gap-survey`
- `PHASE9_SURVEYED_COMMIT=a15760c3e46103fd41ae0da852b61f612e9116c6`
- scope: shared survey note, manifest-backed survey gate, explicit
  roadmap-boundary note for the mixed Phase 6 schedule wording, and a bounded
  shared runtime-loader request surface that keeps allocator plus init or exit
  handoff machine-checkable without claiming real runtime execution
- product boundary:
  - `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
  - `Documentation/zigux/phase9-runtime-loader-substrate-plan.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/freeze-map.md`
  - `zigux/tests/runtime_loader_gap_manifest.json`
  - `zigux/tests/runtime_loader_gap_survey.zig`
  - `zigux/tests/runtime_trace_events_manifest.json`
  - `zigux/tests/phase9_build.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `samples/zigux/runtime_atomic64_loader.zig`
  - `samples/zigux/runtime_bitmap_loader.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `samples/zigux/runtime_trace_events_loader.zig`
  - `samples/zigux/runtime_trace_events.zig`
  - `zigux/helpers/allocator_policy.zig`

## Why This Slice Exists

The schedule prompt for this lane mixes a `Phase 6` label with a runtime
allocator and init-flow topic.

The roadmap does not place runtime loader work in Phase 6. Phase 6 stays
limited to low-risk leaf helpers such as `lib/base64.zig`, `lib/bsearch.zig`,
`lib/checksum.zig`, and `lib/hexdump.zig`. Runtime pilot modules do not appear
until Phase 9, where the roadmap explicitly calls for `zigux/tests/runtime_*`
plus `samples/zigux/runtime_*`. The roadmap's first command and environment
plumbing surfaces also sit outside this runtime lane.

Those controls belong to `Phase 8`, where the product plan first points at the
exec-cmd and help control family and the live repo now lands them as
`tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig` rather than any
Phase 6 helper or already-landed Phase 9 runtime starter.

The live repo already reflects that split:

- the full bounded Phase 6 leaf-helper set is landed
- four Phase 9 runtime starter samples are landed under
  `samples/zigux/runtime_*`
- the earlier three sample-side loader plans baseline has now widened to four
  landed loader scaffolds under `samples/zigux/runtime_*_loader.zig`
- the fourth Phase 9 pilot, `samples/zigux/runtime_trace_events.zig`, now also
  carries a bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold,
  but it remains a sample-only blocked runtime pilot with respect to live
  runtime substrate ownership and tracepoint-registration execution
- a shared `zigux/kernel/runtime_loader.zig` request surface now exists

The current survey packet is pinned to `master` commit
`a15760c3e46103fd41ae0da852b61f612e9116c6`.

This keeps later runtime-loader handoff or governance edits from silently
drifting past this evidence note. This survey keeps the lane honest by
recording what is now landed and what is still blocked instead of pretending
that runtime scheduling, polling, or event-loop work should be pulled forward
into Phase 6. The freeze map also keeps the adjacent scheduler substrate
boundary explicit.

`Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in
`Study / Boundary Only`, so this shared runtime-loader packet may record
request-shape and blocker evidence, but it must not imply workqueue parity,
scheduler transport ownership, or any Architecture Council-approved status
change for that study-only anchor. The review checklist also remains part of
this bounded governance surface.

For this runtime-loader starter family, the checklist still needs to keep three
review cues explicit:

- no hidden runtime services
- no implicit allocation posture beyond the explicit allocator-handoff contract
- no unclear panic or unsafe ownership story

The same checklist packet also needs to keep the freeze-map coupling explicit
so `Documentation/zigux/freeze-map.md`, the study-only `kernel/workqueue.c`
status, and the Architecture Council reopen rule stay in the same reviewable
ownership packet beside the survey note, the shared request contract, the
sample-side loader plans, and `zigux/tests/phase9_build.zig`.

The shared substrate plan is part of the same delivery packet now.
`Documentation/zigux/phase9-runtime-loader-substrate-plan.md` keeps the shared
loader-stage vocabulary and the atomic64, bitmap, and kretprobe handoff
alignment explicit so the shared request surface does not silently drift away
from the sample-side loaders that already feed it.

## Delivery Ownership Map

The manifest-backed catalog for this slice now names which file owns each part
of the current delivery packet:

- `Documentation/zigux/phase9-runtime-loader-gap-survey.md` owns the
  roadmap-boundary note, blocker posture, and bounded replay contract
- `Documentation/zigux/phase9-runtime-loader-substrate-plan.md` owns the
  shared loader-stage vocabulary plus the atomic64, bitmap, and kretprobe
  handoff-alignment note for the same runtime packet
- `Documentation/zigux/review-checklist.md` owns the runtime review guardrails
  and ownership prompts for the same evidence packet
- `Documentation/zigux/freeze-map.md` owns the study-only `kernel/workqueue.c`
  boundary and the Architecture Council reopen rule for any status change tied
  to scheduler-facing runtime substrate work
- `zigux/tests/runtime_loader_gap_manifest.json` owns the manifest-backed catalog and ownership map for the current delivery packet
- `zigux/tests/runtime_loader_gap_survey.zig` owns the machine-checkable replay of the manifest, note, shared request surface, and without-substrate rollback posture
- `zigux/tests/phase9_build.zig` owns the shared Phase 9 runtime bundle replay
  entrypoint
- `zigux/kernel/runtime_loader.zig` owns the shared request contract plus
  allocator, selftest-hook, command-name, and init or exit handoff fields
- `samples/zigux/runtime_atomic64_loader.zig` owns the atomic64 loader-plan
  projection and without-substrate rollback path into the shared runtime
  request surface
- `samples/zigux/runtime_bitmap_loader.zig` owns the bitmap loader-plan
  projection and without-substrate rollback path into the shared runtime
  request surface
- `samples/zigux/runtime_kretprobe_loader.zig` owns the kretprobe loader-plan
  projection and without-substrate rollback path into the shared runtime
  request surface
- `samples/zigux/runtime_trace_events_loader.zig` owns the bounded trace-events loader-plan projection and without-substrate fallback while keeping `foo_bar_reg` and `foo_bar_unreg` review-only instead of executable registration
- `samples/zigux/runtime_trace_events.zig` plus `zigux/tests/runtime_trace_events_manifest.json` still own the sample-only blocked runtime pilot boundary around live runtime substrate, thread creation, polling or event-loop wiring, and tracepoint-registration execution so the shared loader-gap packet does not treat the still-blocked runtime path as solved

## Current Blocker Posture

The current runtime pilot surface already exposes reviewable loader inputs:

- `samples/zigux/runtime_atomic64_loader.zig` records explicit entry and exit
  symbol names, `requires_runtime_substrate`, `provides_selftest_hook`, and a
  bounded handoff stage
- `samples/zigux/runtime_bitmap_loader.zig` records explicit entry and exit
  symbol names, `requires_runtime_substrate`, `provides_selftest_hook`, and a
  bounded handoff stage
- `samples/zigux/runtime_kretprobe_loader.zig` records the same loader-shape
  inputs for the kretprobe starter
- `samples/zigux/runtime_trace_events_loader.zig` now records the same bounded
  init or exit handoff shape for the trace-events pilot, including review-only
  `foo_bar_reg` and `foo_bar_unreg` labels plus `waiting_on_runtime_substrate`
  to `released_without_substrate` fallback
- the atomic64 and bitmap loaders keep staged `zigux_runtime_*_init` and
  `zigux_runtime_*_exit` symbol names reviewable without claiming a live
  `module_init()` or `module_exit()` path, while the kretprobe loader keeps
  `register_kretprobe` and `unregister_kretprobe` as metadata-only labels
  instead of a live registration path
- the landed loader-plan trio still builds its shipped shared requests with
  `command_name = null`; the only non-null command-name evidence in this family
  is the synthetic preservation checks for `perf-runtime-atomic64`,
  `perf-runtime-bitmap`, and `perf-runtime-kretprobe` in
  `samples/zigux/runtime_atomic64_loader.zig`,
  `samples/zigux/runtime_bitmap_loader.zig`, and
  `samples/zigux/runtime_kretprobe_loader.zig`, so this packet still records a
  field contract rather than a live runtime command surface
- the landed kretprobe starter still keeps the current symbol surface bounded
  to `default_symbol_name = "kernel_clone"` plus pre-init retargeting, and the
  shared Phase 9 runtime packet still carries no `CONFIG_`, `Kconfig`,
  `EXPORT_SYMBOL`, or `symbol export` markers anywhere in this evidence family
- the shared loader-gap manifest also keeps the blocked module-metadata and depmod-publication boundary explicit: `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, and `scripts/depmod.sh` stay named only as blocked boundary surfaces until a real depmod bridge exists, so this packet does not imply published module catalog parity from the current starter evidence
- `zigux/helpers/allocator_policy.zig` already records the explicit
  caller-vs-fallback allocator posture that a future runtime loader must
  consume rather than bypass

What is now landed is the smallest shared consumer contract:

- `zigux/kernel/runtime_loader.zig` defines a common loader-stage vocabulary
  for shared runtime handoff
- `Documentation/zigux/phase9-runtime-loader-substrate-plan.md` keeps that
  shared loader-stage vocabulary reviewable beside the three sample-side loader
  plans that already bind into the shared request shape, while the newer
  trace-events scaffold remains an adjacent pre-execution note rather than part
  of the shared request union
- the shared request shape carries module identity, an optional shared `command_name` field, Linux anchor provenance, entry and exit symbol names, and a tagged payload for atomic64, bitmap, or kretprobe facts
- the shared request also consumes `zigux/helpers/allocator_policy.zig` through
  an explicit allocator-handoff record instead of leaving allocator posture in
  prose
- the shared request now also keeps the starter selftest-hook contract
  machine-checkable by rejecting nonzero `selftest_runs` whenever
  `provides_selftest_hook` is absent, so the three shared-request loader plans
  share one explicit review boundary instead of loader-local conventions
- the atomic64, bitmap, and kretprobe loader scaffolds can now emit that shared
  request shape while still stopping at `waiting_on_runtime_substrate`, while
  the trace-events scaffold records the same pre-execution lifecycle cues
  without yet claiming a shared-request binding

The current pilot-module evidence also carries an explicit
rollback-without-substrate path:

- each landed sample-side loader can release its pending shared request without
  claiming runtime execution
- each release path moves the shared handoff state from
  `waiting_on_runtime_substrate` to `released_without_substrate`
- this is the current fallback path for the pre-execution packet, so rollback
  stays explicit even though there is still no real runtime loader

The shared packet also needs one explicit sample-only boundary so repo reality
stays readable:

- `samples/zigux/runtime_trace_events.zig` is the fourth landed Phase 9 pilot sample, and `samples/zigux/runtime_trace_events_loader.zig` now records the same bounded init or exit handoff shape while preserving the sample-only blocked runtime pilot boundary
- that scaffold is intentional review-only progress rather than a solved
  runtime path, because `zigux/tests/runtime_trace_events_manifest.json` still
  records the `runtime-trace-events-substrate-handoff` blocker
- that blocker stays tied to runtime task ownership, polling and event-loop
  substrate, thread creation, and tracepoint-registration lifecycle wiring
- it also stays adjacent to `Documentation/zigux/freeze-map.md`, where
  `kernel/trace/ring_buffer.c` remains `Study / Boundary Only`
- this shared loader-gap packet therefore counts trace-events among the current
  loader-plan surfaces while still treating live runtime substrate ownership
  and tracepoint-registration execution as a sample-only blocked runtime pilot
  boundary

What is still missing is actual runtime execution behavior:

- no real runtime loader owns thread creation, task scheduling, polling, or
  event-loop behavior
- the shared request contract now records an optional shared `command_name` field, but no broader shared runtime command or environment control surface yet records argv policy or environment-derived activation cues
- `tools/lib/subcmd/exec-cmd.zig` owns the live Phase 8 command-name and path-shaping surfaces through `ExtractArgv0Result.command_name`, `Config.exec_path_env`, `PERF_EXEC_PATH`, and `PATH`
- `tools/lib/subcmd/help.zig` owns the live Phase 8 terminal-cue surfaces through `LINES`, `COLUMNS`, and the pretty-print terminal layout helpers
- no path here claims module registration parity, live init invocation, or live
  exit teardown
- no live `module_init()`, `module_exit()`, `register_kretprobe()`, or
  `unregister_kretprobe()` path is being claimed anywhere in this shared
  loader-gap packet
- no path here claims `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, or `scripts/depmod.sh` parity while the depmod bridge remains absent
- no path here claims workqueue parity, scheduler-facing runtime transport
  ownership, or a freeze-map status change for `kernel/workqueue.c` without an
  explicit Architecture Council decision

That means the current runtime surface is now a bounded shared request
contract, not a real loadable runtime path.

## Roadmap-Alignment Note

The roadmap boundary matters here:

- `Phase 6` is still a leaf-helper phase and should not absorb runtime
  allocator or boot/init work
- `Phase 8` owns the first repo-level command and environment plumbing surfaces
  under `tools/lib/subcmd/*.zig`, so this survey records the live
  `tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig` anchors and
  their continued absence from the runtime path instead of inventing a parallel
  control stack
- `Phase 9` is the first runtime-module phase, so this survey is recorded here
  even though the scheduled lane key is `P6-L01`

That same roadmap split also keeps earlier config and export ownership explicit.

`scripts/zigux/kconfig/conf_bridge.zig` and
`scripts/zigux/kconfig/confdata_bridge.zig` stay in the Phase 2 config-surface
bridge packet, while `rust/exports.c` and `zigux/kernel/export_shim.zig` stay
in the Phase 3 export-boundary packet. This Phase 9 survey records those files
only as boundary references instead of Phase 9 runtime evidence. That same
boundary discipline also keeps module metadata and depmod publication explicit.

`.modinfo`, `MODULE_ALIAS()`, `modules.alias`, and `scripts/depmod.sh` remain blocked boundary references in `zigux/tests/runtime_loader_gap_manifest.json` until a real depmod bridge exists, so this Phase 9 packet does not claim alias publication or module catalog output. This slice therefore stays deliberately pre-execution. It does not claim runtime scheduling, polling, or event-loop implementation and it does not move runtime allocator or init-flow ownership into Phase 6.

It also stays underneath the freeze-map study boundary for `kernel/workqueue.c`,
so the shared loader packet must keep workqueue parity and any scheduler-core
status change blocked until the Architecture Council explicitly reopens that
anchor with fresh evidence.

## Gates

1. run the validator self-test first
   - `python3 scripts/zigux/validate-phase9.py --self-test`
2. run the shared Phase 9 validation-flow self-test and the dedicated
   runtime-loader packet self-tests
   - `python3 scripts/zigux/check-phase9-validation-flow.py --self-test`
   - `python3 scripts/zigux/check-phase9-loader-substrate-plan.py --self-test`
   - `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`
   - `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test`
3. run the release-discipline validator and the dedicated runtime-loader packet
   checks
   - `python3 scripts/zigux/validate-phase9.py`
   - `python3 scripts/zigux/check-phase9-validation-flow.py`
   - `python3 scripts/zigux/check-phase9-loader-substrate-plan.py`
   - `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`
   - `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py`
4. run the shared Phase 9 runtime survey bundle
   - `zig build test --build-file zigux/tests/phase9_build.zig --summary all`
5. run the focused shared runtime-loader replay
   - `make -C zigux phase9-runtime-loader-shared-tests`
6. run the shared convenience targets
   - `make -C zigux phase9-test`
   - `make -C zigux phase9`

## Non-goals

This slice does not yet claim:

- a loadable runtime module path
- argv-policy or environment-derived activation controls
- allocator ownership changes beyond the shared handoff contract built from
  `zigux/helpers/allocator_policy.zig`
- rollback beyond the explicit without-substrate release path already recorded
  in the sample-side loaders and shared request contract
- parity or ownership for `kernel/workqueue.c`
- Phase 6 runtime implementation progress

## Next Bounded Step

If a future runtime lane reopens this blocker, keep the next step narrow:
extend the shared `zigux/kernel/runtime_loader.zig` request surface only where
a new runtime starter can reuse it, or add one explicit argv or environment
activation field once the separate Phase 8 tooling posture gives that control
surface a real owner, while keeping `kernel/workqueue.c` in study-only status
unless the Architecture Council explicitly reopens that boundary.