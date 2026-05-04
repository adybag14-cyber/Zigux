# Phase 9 Module Metadata and Depmod Bridge Survey

This note records the current Phase 9 runtime module-metadata surface and the still-missing depmod-facing bridge around the shipped `samples/zigux/runtime_*` starter family.

## Status

- `PHASE9_STATUS=parked`
- `PHASE9_SLICE=runtime-module-metadata-depmod-bridge-survey`
- `PHASE9_SURVEYED_COMMIT=949994db4046ec70abf044d1b2ea874fde9bc4a6`
- scope: dedicated metadata survey note, manifest-backed survey gate, and a bounded review packet for the current runtime starter descriptors, four landed loader-side scaffolds, the shared runtime-loader metadata fields, and the still-absent depmod-facing surfaces
- product boundary:
  - `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`
  - `zigux/tests/runtime_module_metadata_manifest.json`
  - `zigux/tests/runtime_module_metadata_survey.zig`
  - `scripts/zigux/check-phase9-module-metadata-packet.py`
  - `zigux/Makefile`
  - `zigux/tests/phase9_build.zig`
  - `zigux/tests/README.md`
  - `zigux/kernel/runtime_loader.zig`
  - `samples/zigux/runtime_atomic64.zig`
  - `samples/zigux/runtime_bitmap.zig`
  - `samples/zigux/runtime_kretprobe.zig`
  - `samples/zigux/runtime_trace_events.zig`
  - `samples/zigux/runtime_atomic64_loader.zig`
  - `samples/zigux/runtime_bitmap_loader.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `samples/zigux/runtime_trace_events_loader.zig`

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

The same shared request also keeps a tagged `payload` union limited to the currently landed `atomic64`, `bitmap`, and `kretprobe` loader lanes.
The dedicated `samples/zigux/runtime_trace_events_loader.zig` scaffold is now landed too, but it still stops outside that shared `RuntimeLoadRequest` union while the broader trace-events runtime substrate and registration path remain blocked.

That is real metadata progress, but it is not yet loadable-module metadata parity.

The current survey packet is pinned to `master` commit `949994db4046ec70abf044d1b2ea874fde9bc4a6`.
This keeps later runtime metadata or depmod-boundary edits from silently drifting past the exact starter and loader-plan surface reviewed here.

## Current metadata surface

Repo reality today is still bounded and review-first:

- the four runtime starters each ship one explicit `ModuleDescriptor`
- the shared runtime loader currently exposes three tagged loader lanes: `atomic64`, `bitmap`, and `kretprobe`
- four landed loader-plan files now stay at `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, and `samples/zigux/runtime_trace_events_loader.zig`
- the first three landed loader-plan files currently project `command_name = null` into `RuntimeLoadRequest`, so the optional command-name field is still reserved for a future shared activation surface rather than exercised by the shipped starter packet
- those same three loaders now also expose `planForWithCommandName` or `prepareWithCommandName` review helpers, and their shared-request plus release-without-substrate replays preserve explicit `perf-runtime-*` command names when reviewers choose to exercise that optional field
- the landed trace-events loader keeps its own loader-side metadata explicit through entry and exit symbols, `register_api`, `unregister_api`, thread labels, bounded lifecycle stage, the current summary snapshot, and an optional review-only `command_name` that survives prepare, request, and release-without-substrate replays, but it does not yet emit the shared `RuntimeLoadRequest` contract

This means the current runtime family has enough metadata for surveyable starter descriptors, one shared metadata surface for three loader families, and one dedicated fourth loader-side scaffold, but not enough for a real module-install or depmod story.

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

Those surfaces are therefore still absent from the current runtime starter family. This survey records that absence directly so reviewers do not over-read the starter descriptors, the three shared `RuntimeLoadRequest` lanes, or the dedicated trace-events loader scaffold as if the repo had already landed a depmod bridge.

## Delivery ownership map

The shared replay route is part of this dedicated metadata packet too, because the note, focused replay, shared Phase 9 bundle, tests-root guide, fail-closed checker, and wrapper routes all need to describe the same bounded metadata story.

The dedicated metadata packet keeps one bounded ownership split:

- `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md` owns the written survey of the current descriptor surface, the fourth landed loader scaffold, and the depmod-facing gap
- `zigux/tests/runtime_module_metadata_manifest.json` owns the machine-readable counts, exact file list, metadata field inventory, and depmod-gap catalog
- `zigux/tests/runtime_module_metadata_survey.zig` owns the focused replay that proves the note, manifest, starter descriptors, shared loader metadata, and the dedicated trace-events loader scaffold still agree
- `scripts/zigux/check-phase9-module-metadata-packet.py` owns the fail-closed checker for this dedicated metadata packet, including the survey note, focused replay, shared Phase 9 bundle replay entrypoint, tests-root guidance, and the dedicated trace-events loader scaffold markers
- `zigux/Makefile` owns the focused `phase9-module-metadata-survey` wrapper plus the shared `phase9-validate` wrapper route that keep the dedicated metadata replay visible beside the broader Phase 9 runtime packet
- `zigux/tests/phase9_build.zig` owns the shared Phase 9 runtime bundle replay entrypoint that includes `phase9-runtime-module-metadata-survey-tests` beside the adjacent runtime packets
- `zigux/tests/README.md` owns the tests-root guidance that keeps the dedicated metadata checker and shared replay route explicit beside the broader Phase 9 runtime packet
- `zigux/kernel/runtime_loader.zig` owns the shared `RuntimeLoadRequest` metadata fields and the current three-lane loader union
- `samples/zigux/runtime_trace_events_loader.zig` owns the dedicated trace-events loader-side scaffold and preserves registration-label plus thread-label metadata until the shared `RuntimeLoadRequest` handoff grows a fourth lane

## Roadmap-alignment note

This packet stays inside the roadmap's Phase 9 boundary:

- it records the starter metadata that is already real in `samples/zigux/runtime_*` and `zigux/kernel/runtime_loader.zig`
- it records the fourth landed `samples/zigux/runtime_trace_events_loader.zig` scaffold without pretending that the shared loader union already carries a trace-events lane
- it does not claim live loadable-module parity
- it does not claim depmod bridge ownership
- it does not reopen the shared loader-behavior packet beyond the current metadata surface

That is more honest than counting starter descriptors or loader scaffolds as if they already closed `.modinfo` or depmod parity.

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
- `make -C zigux phase9-module-metadata-survey`

5. run the shared convenience target
- `make -C zigux phase9-validate`

The shared tests-root guidance should keep this dedicated metadata checker explicit beside `scripts/zigux/validate-phase9.py`, `zigux/tests/phase9_build.zig`, and `make -C zigux phase9-validate` so the bounded review route stays visible outside this note too.

## Non-goals

This slice does not claim:

- a live loadable-module install path
- `MODULE_INFO()` parity
- `MODULE_ALIAS()` parity
- generated `.modinfo` sections
- `modules.alias`, `modules.order`, or `modules.builtin` outputs
- `Module.symvers` ownership
- a working `scripts/depmod.sh` bridge
- a completed shared `RuntimeLoadRequest` trace-events lane

## Next bounded step

If a future Phase 9 lane reopens this metadata family, keep the next step narrow: the shared validator already mutates this dedicated packet through the manifest `surveyed_commit` proof and the focused survey gate's shared-validator route, so the next honest same-lane hardening is one more fail-closed self-test branch that proves `validate-phase9.py` also catches drift in the module-metadata survey note or dedicated checker markers themselves. Only after that lands should later work consider adding a real metadata-export surface or extending the shared handoff to the trace-events loader scaffold without overstating depmod parity.
