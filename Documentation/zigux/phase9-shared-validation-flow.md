# Phase 9 Shared Validation Flow

This note records the current shared validation-first route for the active Phase 9 runtime pilot packet.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=shared-runtime-validation-flow`
- `PHASE9_LANE_KEY=runtime-pilot`
- scope: shared validator route, focused checker stack, shared Phase 9 build replay, and the bounded survey replays that keep the runtime pilot packet reviewable without implying a loadable module path
- evidence basis: current `master` readback inspected on 2026-05-03 across the shared Phase 9 validator, Makefile, workflow, survey notes, and runtime test bundle
- product boundary:
  - `scripts/zigux/validate-phase9.py`
  - `scripts/zigux/check-phase9-validation-flow.py`
  - `scripts/zigux/check-phase9-loader-substrate-plan.py`
  - `scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`
  - `scripts/zigux/check-phase9-loader-non-owner-boundary.py`
  - `scripts/zigux/check-phase9-module-metadata-packet.py`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
  - `zigux/tests/phase9_build.zig`
  - `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
  - `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`
  - `Documentation/zigux/phase9-runtime-kretprobe-survey.md`
  - `Documentation/zigux/phase9-runtime-trace-events-survey.md`
  - `Documentation/zigux/phase9-runtime-loader-substrate-plan.md`
  - `zigux/tests/runtime_loader_non_owner_boundary_survey.zig`

## Why this note exists

The runtime pilot packet already has real shared validation surfaces on `master`, but they were split across several survey notes, one shared validator, one shared validation-flow checker, several focused packet checkers, the Makefile, the bootstrap workflow, and the shared `zigux/tests/phase9_build.zig` replay bundle.

That is healthy runtime-pilot evidence, but it is easy for the shared route to disappear into file-local context. This note keeps one bounded handoff in the runtime lane itself so future Phase 9 maintenance can see the exact shared replay contract before widening any runtime surface.

## Shared validator-first route

Run the current packet in this order:

1. shared validator self-test
- `python3 scripts/zigux/validate-phase9.py --self-test`

2. focused checker self-tests
- `python3 scripts/zigux/check-phase9-validation-flow.py --self-test`
- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py --self-test`
- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`
- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test`
- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`

3. shared live validator and focused packet checks
- `python3 scripts/zigux/validate-phase9.py`
- `python3 scripts/zigux/check-phase9-validation-flow.py`
- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py`
- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`
- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py`
- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`

4. shared convenience entrypoint
- `make -C zigux phase9-validate`

5. shared replay bundle
- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`
- `make -C zigux phase9`

## Focused survey replays

Keep the narrower packet legs explicit too:

- `make -C zigux phase9-loader-gap-survey` replays the shared loader-gap packet around the bounded `RuntimeLoadRequest` handoff, the allocator handoff contract, the blocked command or environment control surface, and the study-only `kernel/workqueue.c` boundary.
- `make -C zigux phase9-non-owner-boundary-survey` replays the focused Phase 2 plus Phase 3 non-owner boundary note so `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `rust/exports.c`, and `zigux/kernel/export_shim.zig` stay explicit as boundary references instead of being counted as Phase 9 runtime evidence.
- `make -C zigux phase9-module-metadata-survey` replays the dedicated module-metadata and depmod-gap packet so the four starter descriptors, the shared `RuntimeLoadRequest` metadata fields, the current three-lane loader union, the fourth landed trace-events loader scaffold, and the still-absent depmod-facing surfaces remain reviewable together.
- `make -C zigux phase9-kretprobe-survey` replays the bounded kretprobe runtime packet inside the same shared build family.
- `make -C zigux phase9-trace-events-survey` replays the dedicated trace-events survey packet while keeping the loader target absent from the shared build and the `kernel/trace/ring_buffer.c` freeze boundary explicit.

## Ownership split

The shared flow stays honest because each packet still has a narrow owner:

- `scripts/zigux/validate-phase9.py` owns the broad Phase 9 runtime packet alignment across the shared docs, tests, Makefile, workflow, and runtime starter families.
- `scripts/zigux/check-phase9-validation-flow.py` owns the published validator-first route itself, including the Makefile hooks, workflow entrypoint, loader-gap survey gates, module-metadata survey gates, trace-events survey gates, and shared build legs.
- `scripts/zigux/check-phase9-loader-substrate-plan.py` owns the shared runtime-loader substrate-plan packet and its bounded handoff vocabulary.
- `scripts/zigux/check-phase9-runtime-loader-commit-alignment.py` owns the shared surveyed-commit alignment around the loader-gap family.
- `scripts/zigux/check-phase9-loader-non-owner-boundary.py` owns the focused Phase 2 plus Phase 3 non-owner boundary packet inside the runtime lane.
- `scripts/zigux/check-phase9-module-metadata-packet.py` owns the dedicated module-metadata plus depmod-gap packet.
- `zigux/tests/phase9_build.zig` owns the shared replay bundle and keeps the survey legs explicit in one bounded runtime-pilot packet.
- `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` own the published convenience route that contributors and CI can replay without reassembling the packet manually.

## Non-goals

This shared validation-flow note does not claim:

- a live loadable runtime module path
- `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, or `scripts/depmod.sh` parity
- a shared trace-events loader lane inside `RuntimeLoadRequest`
- runtime task ownership, polling, or event-loop substrate parity
- any freeze-map status change for `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`

## Next bounded step

If the runtime-pilot lane reopens this packet, keep the next step narrow: thread this shared validation-flow note into one existing discovery surface such as `Documentation/zigux/README.md` or `Documentation/zigux/review-checklist.md` so the shared Phase 9 route is easier to find without widening the runtime substrate itself.
