# Phase 9 Module Metadata And Depmod Bridge Survey

This note records the current Phase 9 runtime-module metadata shape on `master` and captures the exact evidence that the repo still has no depmod-facing bridge for those starters.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=module-metadata-depmod-bridge-survey`
- lane: `P9-L09`
- surveyed commit: `bc6ede334f83820e5d0aa4f509aba5f5ba41accf`
- scope: bounded evidence note plus a standalone manifest-backed survey gate for the current runtime metadata surface and the still-missing depmod bridge

## Why this slice exists

Phase 9 is the first roadmap phase that allows runtime pilot modules under `zigux/tests/runtime_*` and `samples/zigux/runtime_*`.

The current repo already has runtime starter metadata, but that metadata still stops at Zigux-local descriptors and shared handoff structs. This lane therefore records the exact current behavior instead of implying Linux module metadata or depmod integration that the repo has not landed.

## Exact current behavior

The live Phase 9 runtime starters already expose bounded descriptor metadata:

- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_kretprobe.zig`

Each of those files keeps the same starter descriptor fields explicit:

- `.name`
- `.anchor`
- `.requires_runtime_substrate`
- `.provides_selftest_hook`

Three loader-plan files also expose bounded handoff metadata:

- `samples/zigux/runtime_atomic64_loader.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`

Those loaders all keep these handoff fields explicit:

- `.module_name`
- `.command_name`
- `.entry_symbol`
- `.exit_symbol`

The shared handoff contract under `zigux/kernel/runtime_loader.zig` keeps the same metadata machine-checkable at the shared request level:

- `.module_name`
- `.command_name`
- `.anchor`
- `.entry_symbol`
- `.exit_symbol`

The current Phase 9 starter family therefore has reviewable internal metadata, but it is still Zigux-local metadata rather than depmod-facing metadata.

## Exact depmod-bridge evidence

The current Phase 9 runtime packet still has no depmod-oriented bridge surface:

- no `depmod`
- no `modinfo`
- no `modules.dep`
- no `modules.alias`
- no `modules.symbols`
- no `modules.builtin.modinfo`

The current runtime metadata packet also does not expose Linux module-info style fields inside these runtime starter and loader surfaces:

- no `MODULE_LICENSE`
- no `MODULE_DESCRIPTION`
- no `MODULE_AUTHOR`
- no `MODULE_ALIAS`
- no `MODULE_FIRMWARE`
- no `MODULE_SOFTDEP`

That means the current runtime metadata is sufficient for bounded Zigux review and shared handoff tests, but not for module-install metadata export, modinfo replay, or depmod indexing.

## Exact shape gap

The current Phase 9 starter family is also intentionally uneven:

- four runtime starter samples exist
- three loader-plan files exist
- `samples/zigux/runtime_trace_events.zig` does not yet have a sibling loader-plan file

That asymmetry is still honest for current `master`: the repo has starter-module metadata and three bounded loader handoff surfaces, but no universal runtime metadata bridge and no depmod-facing export path.

## Evidence catalog

- `samples/zigux/runtime_atomic64.zig` proves starter descriptor metadata for the atomic64 pilot
- `samples/zigux/runtime_bitmap.zig` proves starter descriptor metadata for the bitmap pilot
- `samples/zigux/runtime_trace_events.zig` proves starter descriptor metadata for the trace-events pilot
- `samples/zigux/runtime_kretprobe.zig` proves starter descriptor metadata for the kretprobe pilot
- `samples/zigux/runtime_atomic64_loader.zig` proves bounded loader metadata for the atomic64 handoff path
- `samples/zigux/runtime_bitmap_loader.zig` proves bounded loader metadata for the bitmap handoff path
- `samples/zigux/runtime_kretprobe_loader.zig` proves bounded loader metadata for the kretprobe handoff path
- `zigux/kernel/runtime_loader.zig` proves the shared request contract and also proves that the metadata still stays inside Zigux-local handoff structs
- `zigux/tests/runtime_module_metadata_manifest.json` records the exact file set and the absent depmod markers
- `zigux/tests/runtime_module_metadata_survey.zig` replays the same evidence as a standalone check
- `scripts/zigux/check-phase9-module-metadata-packet.py` keeps this dedicated note, the manifest-backed file inventory, the standalone survey gate, and the README hooks aligned as one fail-closed review packet

## Non-goals

This slice does not claim:

- loadable-module metadata parity
- `modinfo` output parity
- `depmod` integration
- `modules.dep` or `modules.alias` generation
- runtime trace-events loader parity

## Next bounded step

If this lane reopens, keep it narrow: either add one explicit Phase 9 loader-plan surface for trace-events so the current metadata family is structurally complete, or introduce one deliberately small exported module-info record that can be reviewed without claiming a full depmod bridge.
