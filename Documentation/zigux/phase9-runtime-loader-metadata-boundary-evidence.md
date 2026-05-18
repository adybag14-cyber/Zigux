# Phase 9 Runtime Loader Metadata Boundary Evidence

- lane: `P9-L09`
- recorded: `2026-05-18`
- scope: current metadata behavior for the shared runtime-loader packet and the still-blocked depmod-publication bridge

## Why this note exists

Phase 9 still targets first runtime pilot modules, selftest hooks, and runtime module lifecycle parity under `zigux/tests/runtime_*` and `samples/zigux/runtime_*`. This note records the current repo-first evidence for the shared metadata boundary without reviving the removed dedicated module-metadata packet.

## Current shared contract evidence

`zigux/kernel/runtime_loader_contract.zig` keeps the shared `LoadPlan` limited to:

- `module_name`
- `anchor`
- `entry_symbol`
- `exit_symbol`
- `requires_runtime_substrate`
- `provides_selftest_hook`
- `allocator_handoff`
- `init_flow`

The same contract keeps publication and depmod-facing metadata outside the shared request packet.

Blocked publication-side field names in the live contract:

- `modinfo`
- `module_alias`
- `module_aliases`
- `modules_alias_path`
- `module_install_root`
- `modules_order_path`
- `modules_builtin_path`
- `module_symvers_path`

Blocked depmod-facing field names in the live contract:

- `depmod_script`
- `depmod_manifest`
- `depmod_aliases`

The live contract tests still assert that registration-summary, publication, and depmod surfaces stay outside the shared request contract.

## Loader bridge evidence

The current loader scaffolds bridge family-local plans into the shared `runtime_loader.LoadPlan` through `toSharedLoadPlan(...)` helpers in:

- `samples/zigux/runtime_atomic64_loader.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`
- `samples/zigux/runtime_trace_events_loader.zig`

Across those bridges, the shared packet stays limited to the shared plan fields above plus family-appropriate allocator handoff and staged init-flow data.

Family-local metadata still exists, but it remains outside the shared publication packet:

- `samples/zigux/runtime_kretprobe_loader.zig` keeps `register_api`, `unregister_api`, `symbol_name`, `maxactive`, `private_data_bytes`, and `summary` on the local `RuntimeKretprobeLoadPlan`, then strips that detail before `runtime_loader.prepareRequest(toSharedLoadPlan(plan))`.
- `samples/zigux/runtime_trace_events_loader.zig` keeps `register_api`, `unregister_api`, and `summary` local, and exposes `registrationSnapshot(...)` as a family-local helper rather than shared request metadata.

## Shared build and checker evidence

`zigux/tests/phase9_build.zig` still imports the shared runtime-loader facade and contract for the current shared runtime-loader test family.

`scripts/zigux/check-phase9-build-only-surface.py` still treats the older dedicated metadata packet as removed surfaces rather than current Phase 9 proof. The checker forbids:

- `scripts/zigux/validate-phase9.py`
- `scripts/zigux/check-phase9-validation-flow.py`
- `scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`
- `scripts/zigux/check-phase9-loader-substrate-plan.py`

That same checker also requires the live shared packet files, including:

- `zigux/tests/phase9_build.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/runtime_loader_gap_manifest.json`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`
- the four `samples/zigux/runtime_*_loader.zig` scaffolds

## Conclusion

The current Phase 9 metadata bridge is still review-first rather than publication-complete.

The live shared runtime-loader packet carries loader identity, lifecycle, substrate, allocator-handoff, and staged init-flow facts, but it does not currently ship `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root, or `depmod` script or manifest state as shared publication behavior.

This note is evidence-only. It should not be treated as a revived dedicated module-metadata owner map or as proof of a live depmod bridge.
