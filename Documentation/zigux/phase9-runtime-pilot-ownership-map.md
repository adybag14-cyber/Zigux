# Phase 9 Runtime Pilot Ownership Map

This note records the current ownership map for the bounded Phase 9 runtime pilot packet on `master`.

It is intentionally narrower than a new validator or closure note.
Its job is to keep the shipped runtime pilot evidence easy to review without implying a broader runtime-substrate delivery claim.

## Roadmap Anchor

Phase 9 in the product roadmap is the runtime pilot stage:
- primary goal: enter runtime kernels through tests and samples, not production pressure
- primary Linux anchors: `lib/atomic64_test.c`, `lib/test_bitmap.c`, `samples/trace_events/trace-events-sample.c`, and `samples/kprobes/kretprobe_example.c`
- recommended Zigux destinations: `zigux/tests/runtime_*` plus `samples/zigux/runtime_*`

That means the truthful Phase 9 packet is owned by the runtime sample, survey, loader, and shared runtime-loader surfaces already landed in-tree.

## Shared Delivery Surfaces

Treat these files as the shared delivery packet for the current Phase 9 runtime pilot family:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase9-build-only-surface.py`
- `zigux/tests/phase9_build.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/Makefile`

The shipped replay route remains:
- `python3 scripts/zigux/check-phase9-build-only-surface.py`
- `zig build test --build-file zigux/tests/phase9_build.zig`
- `make -C zigux phase9`

The focused shared runtime-loader shard remains:
- `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`

There is still no dedicated shared `validate-phase9.py` route on `master`.

## Runtime Pilot Catalog

The current Phase 9 runtime pilot family breaks down like this:

### `runtime_atomic64`
- roadmap anchor: `lib/atomic64_test.c`
- runtime sample: `samples/zigux/runtime_atomic64.zig`
- loader handoff: `samples/zigux/runtime_atomic64_loader.zig`
- survey gate: `zigux/tests/runtime_atomic64_survey.zig`
- shared build wiring: `zigux/tests/phase9_build.zig`

### `runtime_bitmap`
- roadmap anchor: `lib/test_bitmap.c`
- runtime sample: `samples/zigux/runtime_bitmap.zig`
- loader handoff: `samples/zigux/runtime_bitmap_loader.zig`
- focused companion replay: `samples/zigux/runtime_bitmap_top_bit_build.zig` and `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- survey gate: `zigux/tests/runtime_bitmap_survey.zig`
- shared build wiring: `zigux/tests/phase9_build.zig`

### `runtime_trace_events`
- roadmap anchor: `samples/trace_events/trace-events-sample.c`
- runtime sample: `samples/zigux/runtime_trace_events.zig`
- loader handoff: `samples/zigux/runtime_trace_events_loader.zig`
- survey gate: `zigux/tests/runtime_trace_events_survey.zig`
- shared build wiring: `zigux/tests/phase9_build.zig`

### `runtime_kretprobe`
- roadmap anchor: `samples/kprobes/kretprobe_example.c`
- runtime sample: `samples/zigux/runtime_kretprobe.zig`
- loader handoff: `samples/zigux/runtime_kretprobe_loader.zig`
- survey gate: `zigux/tests/runtime_kretprobe_survey.zig`
- shared build wiring: `zigux/tests/phase9_build.zig`

## Ownership Boundaries

Keep these boundaries explicit when Phase 9 moves:
- `samples/zigux/README.md` owns the sample-root distinction between the four approved Phase 5 reference samples and the separate Phase 9 runtime pilot family.
- `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` own the shared delivery summary for the runtime pilot packet.
- `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/tests/runtime_loader_allocator_init_flow.zig` own the current runtime-loader handoff, contract, and allocator/init-flow evidence.
- `scripts/zigux/check-phase9-build-only-surface.py` owns the fail-closed shared packet check for the Phase 9 build-only route.
- `zigux/tests/phase9_build.zig` owns the shared replay wiring for the runtime pilot family and the focused `phase9-runtime-loader-shared-tests` shard.

## Non-Owner Surfaces

These files may be mentioned by the Phase 9 packet, but they are not owned by the runtime pilot lane itself:
- `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references.
- `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.
- `tools/lib/subcmd/exec-cmd.zig` still owns deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` tooling cues.
- `tools/lib/subcmd/help.zig` still owns the `LINES` and `COLUMNS` terminal-formatting cues.
- The freeze-map anchors under `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain study-only or blocked boundaries rather than active runtime-loader delivery targets.

## Current Product Posture

The truthful current claim for Phase 9 is:
- Zigux ships a bounded runtime pilot packet with runtime samples, loader handoff scaffolds, survey gates, a shared runtime-loader facade and contract, and a workflow-backed build-only replay route.
- Zigux does not yet ship a broader runtime-substrate closure, a standalone runtime activation-control surface, or a separate `validate-phase9.py` validator path.
- The runtime pilot packet should keep tightening reviewability through small ownership-map, survey, contract, and shared-build truthfulness repairs before it widens into larger runtime-module implementation work.
