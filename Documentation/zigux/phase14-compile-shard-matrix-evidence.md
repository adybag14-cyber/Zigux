# Phase 14 Compile Shard Matrix Evidence

This note records the exact current readback evidence for the shared Phase 14 compile-shard matrix.

## Exact current readback

- Readback date: `2026-05-27`
- Roadmap posture: Phase 14 remains a bounded core-adjacent study and freeze-in-C packet, so this lane records reviewability evidence only.
- Current readable machine-readable source: `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- Current readable route wrapper: `make -C zigux phase14-validate`
- Current readable workflow route: `.github/workflows/zigux-bootstrap.yml` still reruns `make -C zigux phase14-validate`
- Current readable compile-shard survey: `Documentation/zigux/phase14-compile-shard-matrix-survey.md`
- Current readable shared smoke note: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`

## Verified counts

- `PHASE14_COMPILE_SHARD_TOTAL=6`
- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`
- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`
- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`
- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`

## Exact coverage interpretation

- The readable manifest still carries six compile-shard rows.
- The readable manifest still records one focused shard command: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`.
- The readable Makefile still exposes `phase14-validate` and still omits `phase14-smoke`, `phase14-test`, and `phase14`.
- The readable workflow still reruns `make -C zigux phase14-validate` and still does not rerun a dedicated Phase 14 smoke or build step.
- The readable shared smoke note still lists `zigux/tests/phase14_build.zig` under executable packet members that remain unrecovered through the exact contents path.
- Direct current-master contents readback for `zigux/tests/phase14_build.zig` still returns `404 Not Found`.

## Product reading

Current repo evidence supports a narrow claim:

- the compile-shard matrix is still present as manifest-backed and reminder-backed reviewability evidence
- the focused shard still exists as declared route vocabulary in readable current-master surfaces
- the focused shard is not currently backed by a directly readable `zigux/tests/phase14_build.zig` body through the same exact contents path

That means the honest current packet is:

- six declared compile-shard rows
- one focused shard claim
- five full-bundle-only rows
- one shared Makefile gate
- zero readable dedicated Makefile smoke wrappers
- zero direct contents-path proof for the focused build-file body itself

## Next bounded step

If the current repo state changes again, repair only the smallest compile-matrix reminder or checker surface that drifts away from this exact evidence split before widening into anchor-local Phase 14 work.
