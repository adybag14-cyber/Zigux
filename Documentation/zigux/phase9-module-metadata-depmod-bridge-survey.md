# Phase 9 Module Metadata and Depmod Bridge Survey

This note records the current Phase 9 runtime module-metadata surface and the still-missing depmod-facing bridge around the shipped `samples/zigux/runtime_*` starter family.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-module-metadata-depmod-bridge-survey`
- `PHASE9_SURVEYED_COMMIT=5a2398b1223d2c1e39c84c500f684244f4182eff`
- scope: dedicated metadata survey note, manifest-backed survey gate, and a bounded review packet for the current runtime starter descriptors, shared runtime-loader metadata fields, and still-absent depmod-facing surfaces
- product boundary:
  - `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`
  - `zigux/tests/runtime_module_metadata_manifest.json`
  - `zigux/tests/runtime_module_metadata_survey.zig`
  - `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
  - `zigux/kernel/runtime_loader.zig`
  - `samples/zigux/runtime_atomic64.zig`
  - `samples/zigux/runtime_bitmap.zig`
  - `samples/zigux/runtime_kretprobe.zig`
  - `samples/zigux/runtime_trace_events.zig`

## Why this slice exists

The roadmap's Phase 9 goal is the first loadable Zigux runtime-module family with selftest hooks and bounded lifecycle parity under `zigux/tests/runtime_*` and `samples/zigux/runtime_*`.

Live `master` already ships four runtime starter descriptors:

- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_kretprobe.zig`
- `samples/zigux/runtime_trace_events.zig`

Each of those starters exposes a reviewable `ModuleDescriptor` with the same four metadata fields:

- `name`
- `anchor`
- `requires_runtime_substrate`
- `provides_selftest_hook`

The shared handoff packet also exposes a narrower runtime-loader metadata surface in `zigux/kernel/runtime_loader.zig` through `RuntimeLoadRequest`:

- `module_name`
- `command_name`
- `anchor`
- `entry_symbol`
- `exit_symbol`
- `requires_runtime_substrate`
- `provides_selftest_hook`
- `handoff_stage`
- `allocator_handoff`

That is real metadata progress, but it is not yet loadable-module metadata parity.

The current survey packet is pinned to `master` commit `5a2398b1223d2c1e39c84c500f684244f4182eff`.
This keeps later runtime metadata or depmod-boundary edits from silently drifting past the exact starter surface reviewed here.

## Current metadata surface

Repo reality today is still bounded and review-first:

- the four runtime starters each ship one explicit `ModuleDescriptor`
- the shared runtime loader currently exposes three tagged loader lanes: `atomic64`, `bitmap`, and `kretprobe`
- the three landed loader-plan files stay at `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_kretprobe_loader.zig`
- `samples/zigux/runtime_trace_events.zig` remains intentionally sample-only, and `samples/zigux/runtime_trace_events_loader.zig` is still absent
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md` already keeps that missing trace-events loader sibling explicit as a blocked runtime-substrate boundary

This means the current runtime family has enough metadata for surveyable starter descriptors and shared request fields, but not enough for a real module-install or depmod story.

## Depmod-facing gap

The current Phase 9 packet still does not ship the Linux-facing metadata surfaces that a real loadable-module or depmod bridge would require:

- `MODULE_INFO()`
- `MODULE_ALIAS()`
- `.modinfo`
- `modules.alias`
- `modules.order`
- `modules.builtin`
- `Module.symvers`
- `scripts/depmod.sh`

Those surfaces are therefore still absent from the current runtime starter family. This survey records that absence directly so reviewers do not over-read the starter descriptors or shared `RuntimeLoadRequest` metadata as if the repo had already landed a depmod bridge.

## Delivery ownership map

The dedicated metadata packet keeps one bounded ownership split:

- `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md` owns the written survey of the current descriptor surface and the depmod-facing gap
- `zigux/tests/runtime_module_metadata_manifest.json` owns the machine-readable counts, exact file list, metadata field inventory, and absent depmod surface list
- `zigux/tests/runtime_module_metadata_survey.zig` owns the focused replay that proves the note, manifest, starter descriptors, and shared loader metadata still agree
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md` owns the shared loader-packet note that keeps the missing `samples/zigux/runtime_trace_events_loader.zig` sibling explicit
- `zigux/kernel/runtime_loader.zig` owns the shared `RuntimeLoadRequest` metadata fields and the current three-lane loader union

## Roadmap-alignment note

This packet stays inside the roadmap's Phase 9 boundary:

- it records the starter metadata that is already real in `samples/zigux/runtime_*` and `zigux/kernel/runtime_loader.zig`
- it does not claim live loadable-module parity
- it does not claim depmod bridge ownership
- it does not reopen the shared loader-behavior packet beyond the current metadata surface

That is more honest than counting starter descriptors as if they already closed `.modinfo` or depmod parity.

## Gates

1. run the shared validator self-test plus the dedicated metadata checker self-test
- `python3 scripts/zigux/validate-phase9.py --self-test`
- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`

2. run the shared validator and the dedicated metadata checker
- `python3 scripts/zigux/validate-phase9.py`
- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`

3. run the shared Phase 9 runtime bundle
- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`

4. run the focused metadata survey replay
- `zig test zigux/tests/runtime_module_metadata_survey.zig`

5. run the shared convenience target
- `make -C zigux phase9-validate`

The shared tests-root guidance should keep this dedicated metadata checker explicit beside `scripts/zigux/validate-phase9.py` and `make -C zigux phase9-validate` so the bounded review route stays visible outside this note too.

## Non-goals

This slice does not claim:

- a live loadable-module install path
- `MODULE_INFO()` parity
- `MODULE_ALIAS()` parity
- generated `.modinfo` sections
- `modules.alias`, `modules.order`, or `modules.builtin` outputs
- `Module.symvers` ownership
- a working `scripts/depmod.sh` bridge
- a new runtime trace-events loader implementation

## Next bounded step

If a future Phase 9 lane reopens this metadata family, keep the next step narrow: either add one real metadata-export surface that the current starter family can prove end-to-end, or extend the dedicated survey packet to cover one newly landed runtime loader sibling without overstating depmod parity.
