# Phase 9 Runtime Focused Replay Matrix

This note keeps the current runtime-pilot packet reviewable through one bounded replay matrix instead of spreading the active checks across separate survey notes.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_PACKET=runtime-focused-replay-matrix`
- scope: shared runtime validation plus the focused replay routes for the current starter descriptors, loader-plan scaffolds, metadata packet, and trace-events boundary packet
- roadmap boundary: keep Phase 9 runtime work inside `zigux/tests/runtime_*` and `samples/zigux/runtime_*` without implying a ready loadable-module path

## Shared Runtime Route

Run these first when the runtime packet changes:

1. `python3 scripts/zigux/validate-phase9.py --self-test`
2. `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`
3. `python3 scripts/zigux/validate-phase9.py`
4. `python3 scripts/zigux/check-phase9-module-metadata-packet.py`
5. `make -C zigux phase9-validate`
6. `zig build test --build-file zigux/tests/phase9_build.zig --summary all`

## Focused Replays

| packet | primary files | focused replay | current boundary |
| --- | --- | --- | --- |
| runtime atomic64 | `samples/zigux/runtime_atomic64.zig`, `samples/zigux/runtime_atomic64_loader.zig`, `zigux/tests/runtime_atomic64_{module,diff,survey}.zig` | `zig build test --build-file zigux/tests/phase9_build.zig --summary all` | starter-laned and selftest-backed, but still blocked on real runtime substrate handoff |
| runtime bitmap | `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `zigux/tests/runtime_bitmap_{module,diff,survey}.zig` | `zig build test --build-file zigux/tests/phase9_build.zig --summary all` | starter-laned and bounded to helper-backed replay rather than live module delivery |
| runtime kretprobe | `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `zigux/tests/runtime_kretprobe_{module,diff,survey}.zig` | `make -C zigux phase9-kretprobe-survey` | keeps registration labels and release-without-substrate fallback explicit without claiming a live registration path |
| runtime loader gap | `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/kernel/runtime_loader.zig` | `make -C zigux phase9-loader-gap-survey` | shared `RuntimeLoadRequest` remains pre-execution and still blocks argv-policy plus environment-derived activation controls |
| runtime module metadata | `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`, `zigux/tests/runtime_module_metadata_manifest.json`, `zigux/tests/runtime_module_metadata_survey.zig`, `scripts/zigux/check-phase9-module-metadata-packet.py` | `make -C zigux phase9-module-metadata-survey` | four starter descriptors and four loader scaffolds are real, but `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, and `scripts/depmod.sh` parity remain absent |
| runtime trace-events | `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, `zigux/tests/runtime_trace_events_{manifest,module,diff,survey}.zig`, `samples/zigux/runtime_trace_events.zig` | `make -C zigux phase9-trace-events-survey` | keep `kernel/trace/ring_buffer.c` at `Study / Boundary Only` and keep the loader target absent from the shared Phase 9 bundle |

## Review Guardrails

- Keep the current runtime packet explicit about shipped selftest hooks and bounded lifecycle parity.
- Treat `samples/zigux/runtime_trace_events_loader.zig` as a blocked scaffold until shared runtime-substrate ownership is real.
- Keep `MODULE_INFO()`, `MODULE_ALIAS()`, `.modinfo`, `modules.alias`, `modules.order`, `modules.builtin`, `Module.symvers`, and `scripts/depmod.sh` explicit as missing depmod-facing surfaces rather than implied progress.
- Keep Phase 2 config-surface bridges and Phase 3 export-boundary files as non-owner references around the runtime packet.

## Next Bounded Step

If Phase 9 runtime work reopens from this note, the next high-value implementation step is to harden the shared validator so it fails closed on the dedicated runtime module-metadata packet and its focused replay route with the same strictness already used by the separate packet checker.
