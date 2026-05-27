# Phase 9 Module Metadata and Depmod Bridge Survey

This note records the current `master` gap between the Phase 9 runtime-pilot roadmap and the surviving shared runtime-loader packet for module metadata and depmod-facing publication surfaces.

## Readback date

Current repository state was reread on 2026-05-27 against `master`.

## Roadmap anchor

Phase 9 is still the runtime pilot tranche.

- primary Linux anchors:
  - `lib/atomic64_test.c`
  - `lib/test_bitmap.c`
  - `samples/trace_events/trace-events-sample.c`
  - `samples/kprobes/kretprobe_example.c`
- required Zigux features:
  - first loadable Zigux runtime modules
  - selftest hooks
  - runtime module lifecycle parity
- recommended Zigux destinations:
  - `zigux/tests/runtime_*`
  - `samples/zigux/runtime_*`

The roadmap allows bounded runtime-pilot packets, but it does not let reminder surfaces pretend that metadata publication or depmod-facing delivery already landed.

## Current shared-owner evidence

Trusted current-`master` rereads on 2026-05-27 still recover the narrower shared runtime-loader packet through:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/phase9_build.zig`
- `zigux/tests/runtime_pilot_manifest.json`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `Documentation/zigux/phase9-runtime-pilot-ownership-map.md`

That packet proves a metadata-only runtime-loader contract, not module publication.

`zigux/kernel/runtime_loader_contract.zig` currently keeps these shared request fields explicit inside `LoadPlan`:

- `module_name`
- `anchor`
- `entry_symbol`
- `exit_symbol`
- `requires_runtime_substrate`
- `provides_selftest_hook`
- `allocator_handoff`
- `init_flow`

Those fields are enough to keep staged runtime-loader planning reviewable across the current atomic64, bitmap, trace-events, and kretprobe pilot packets.

## Current gap versus module-metadata and depmod delivery

The same live contract also proves that the broader publication packet is still blocked on current `master`.

`zigux/kernel/runtime_loader_contract.zig` carries an explicit blocked-publication test that keeps these fields out of `LoadPlan` today:

- `modinfo`
- `module_alias`
- `module_aliases`
- `modules_alias_path`
- `module_install_root`
- `modules_order_path`
- `modules_builtin_path`
- `module_symvers_path`
- `depmod_script`
- `depmod_manifest`
- `depmod_aliases`

That means the current Phase 9 runtime packet still does not provide direct current-`master` proof for:

- `.modinfo` publication ownership
- `MODULE_ALIAS()` or `modules.alias` generation
- depmod-facing alias output
- `modules.order`, `modules.builtin`, or `Module.symvers` publication wiring
- install-root or depmod bridge execution

The surviving `phase9-runtime-loader-shared-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, and neighboring runtime-pilot rerun handles are bounded review routes only. They are not proof that metadata publication or depmod bridge delivery has returned.

## Survey conclusion

Against the Phase 9 roadmap, current `master` is in a mixed state:

- runtime pilot packets do exist and still prove selftest-hook and lifecycle-parity behavior inside bounded sample and test families
- the shared runtime-loader packet does preserve module-name, anchor, entry, exit, allocator, and init-flow planning metadata
- the module-metadata and depmod-publication bridge remains a real roadmap gap rather than a shipped shared-owner surface

The honest Phase 9 reading is therefore: first loadable runtime-pilot evidence exists, but the metadata-publication boundary that would carry `.modinfo`, alias, install-root, and depmod-facing outputs is still blocked historical vocabulary on current `master`.

## Next bounded step

If a later same-lane pass needs follow-through, keep it narrow:

1. tighten one shared reminder or manifest surface at a time so it names the blocked module-metadata and depmod bridge explicitly
2. do not widen into runtime behavior, loader semantics, or family-local sample changes from this survey lane alone
3. only add checker growth if a specific shared summary drifts away from the blocked boundary recorded here
