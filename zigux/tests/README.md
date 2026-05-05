# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose
- hold shared harness logic before subsystem-specific tests spread through the tree
- keep product-facing validation code separate from ad hoc experiments
- provide the checks for helper parity, ABI assertions, and rollback readiness

Key entrypoints
- `zigux/tests/build.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/bitmap_diff.zig`
- `zigux/tests/phase4_build.zig`
- `zigux/tests/phase5_build.zig`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_bench.zig`
- `zigux/tests/phase6_build.zig`
- `zigux/tests/phase6_checksum.zig`
- `zigux/tests/phase7_build.zig`
- `zigux/tests/phase7_string_helpers.zig`
- `zigux/tests/phase7_cmdline.zig`
- `zigux/tests/phase7_argv_split.zig`
- `zigux/tests/phase7_rbtree.zig`
- `zigux/tests/phase9_build.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/runtime_trace_events_survey.zig`
- `zigux/tests/runtime_kretprobe_survey.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase14_build.zig`
- `zigux/tests/phase14_ring_buffer_survey.zig`
- `zigux/tests/phase14_skbuff_bridge.zig`
- `zigux/tests/phase14_workqueue_bridge.zig`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/validate-phase4.py`
- `Documentation/zigux/phase4-validation-matrix.md`
- `scripts/zigux/phase3_catalog.py --self-test`
- `scripts/zigux/phase3_check_lib.py --self-test`
- `scripts/zigux/generate-phase3-check-wrappers.py --check`
- `scripts/zigux/run-phase3-checks.py --self-test`
- `scripts/zigux/run-phase3-checks.py`

Phase 3 fixtures
- each Phase 3 slice keeps its expected JSON and C harness under `zigux/tests/fixtures/phase3_*`
- manifests may live beside the fixture directory or inside it; the Phase 3 catalog selects the best valid manifest candidate
- the catalog also discovers the matching dump entrypoint under `zigux/tests/phase3_*_dump.zig`
- the shared runner now executes slices directly from catalog metadata, and slice docs may point their `PHASE3_INTEROP_GATE` marker at either `run-phase3-checks.py --slug <slug>` or the legacy wrapper command
- `python3 scripts/zigux/phase3_catalog.py --legacy-wrapper-docs` lists the slice docs that still rely on legacy wrapper markers so cleanup work can stay targeted
- `python3 scripts/zigux/phase3_catalog.py --legacy-wrapper-references` lists the remaining concrete wrapper-path mentions outside the slice docs so fixture and policy cleanup stays targeted too
- wrapper stubs are convenience entrypoints rather than the execution path and may be pruned when the underlying slice disappears

Guidance
- keep parity fixtures committed and readable
- prefer discovery-based validation over hard-coded file inventories when adding new Phase 3 slices
- keep the shared Phase 5 reference-sample checks wired through `zigux/tests/phase5_build.zig` so the four shipped sample-backed surveys stay reviewable without implying runtime-substrate closure
- keep the shared Phase 7 leaf-helper packet wired through `zigux/tests/phase7_build.zig` so the landed `string_helpers`, `cmdline`, `argv_split`, and `rbtree` bundle stays reviewable through one bounded runtime-safe entrypoint
- keep the bounded Phase 9 runtime surveys wired through `zigux/tests/phase9_build.zig` so the loader-handoff packet stays reviewable without implying shared runtime substrate closure
- keep new Phase 6 and Phase 7 leaf-helper tests small, explicit, and tied to the owning helper path when those helper lanes reopen
