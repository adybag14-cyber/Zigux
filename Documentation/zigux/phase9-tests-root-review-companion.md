# Phase 9 Tests-Root Review Companion

This note keeps the tests-root view of the active Phase 9 runtime-pilot packet reviewable without widening the shared runtime-loader evidence beyond its current bounded request surface.

## Shared reviewer surface

The active Phase 9 packet should continue to agree across these shared review surfaces:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
- `Documentation/zigux/phase9-runtime-loader-substrate-plan.md`
- `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`
- `Documentation/zigux/phase9-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

## Tests-root ownership

From the tests root, the bounded Phase 9 packet is carried by:
- `zigux/tests/phase9_build.zig`
- `zigux/tests/runtime_loader_gap_manifest.json`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/runtime_loader_non_owner_boundary_survey.zig`
- `zigux/tests/runtime_module_metadata_manifest.json`
- `zigux/tests/runtime_module_metadata_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_bitmap_manifest.json`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`
- `zigux/tests/runtime_kretprobe_manifest.json`
- `zigux/tests/runtime_kretprobe_survey.zig`
- `zigux/tests/runtime_kretprobe_module.zig`
- `zigux/tests/runtime_kretprobe_diff.zig`
- `zigux/tests/runtime_trace_events_manifest.json`
- `zigux/tests/runtime_trace_events_survey.zig`
- `zigux/tests/runtime_trace_events_module.zig`
- `zigux/tests/runtime_trace_events_diff.zig`

Those files should keep the manifest-backed catalog, shared replay entrypoint, module-metadata packet, non-owner boundary, and the current runtime starter surveys aligned with the docs-root and scripts-root packet.

## Shared request boundary

The tests-root packet should continue to keep the shared `RuntimeLoadRequest` boundary explicit:
- `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_kretprobe_loader.zig` should continue to route their bounded loader-plan evidence through `zigux/kernel/runtime_loader.zig` and its shared `RuntimeLoadRequest` surface.
- `samples/zigux/runtime_trace_events_loader.zig` remains an adjacent scaffold until the blocked trace-events substrate handoff can truthfully adopt that same request path.
- `zigux/tests/runtime_loader_gap_manifest.json` and `zigux/tests/runtime_loader_gap_survey.zig` should keep that shared-request boundary reviewable beside the same without-substrate fallback posture and the current sample-only blocked trace-events pilot.

## Validator-first route

The tests-root packet stays bounded behind the same validator-first route:
- `python3 scripts/zigux/validate-phase9.py --self-test`
- `python3 scripts/zigux/check-phase9-validation-flow.py --self-test`
- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py --self-test`
- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`
- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`
- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test`
- `python3 scripts/zigux/validate-phase9.py`
- `python3 scripts/zigux/check-phase9-validation-flow.py`
- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py`
- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`
- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`
- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py`
- `make -C zigux phase9-validate`
- `make -C zigux phase9-loader-gap-survey`
- `make -C zigux phase9-loader-commit-alignment-survey`
- `make -C zigux phase9-non-owner-boundary-survey`
- `make -C zigux phase9-module-metadata-survey`
- `make -C zigux phase9-kretprobe-survey`
- `make -C zigux phase9-trace-events-survey`
- `make -C zigux phase9`
- `zigux/tests/phase9_build.zig`

## Review rule

Update this companion only when the tests-root ownership view, the shared `RuntimeLoadRequest` boundary, or the validator-first Phase 9 route changes too. Do not treat a new helper, an implicit loadable-module claim, or a trace-events substrate reopening as Phase 9 maintenance unless the shared loader-gap packet is deliberately reopened with matching docs, tests, and review-surface evidence.