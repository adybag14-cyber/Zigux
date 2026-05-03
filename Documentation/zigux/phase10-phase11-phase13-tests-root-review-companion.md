# Phase 10, 11, and 13 Tests-Root Review Companion

Use this note when a change touches the active Phase 10 virtio lab packet, the active Phase 11 simple-driver packet, or the active Phase 13 shared-helper release packet and the review needs a compact tests-root checklist.

Keep `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, and `Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md` aligned with this note when they describe the same packet so the shared reviewer prompts do not drift across docs-root, tests-root, and checklist-facing guidance.

## Phase 10 tests-root packet

Keep the tests-root replay packet explicit:
- `zigux/tests/phase10_build.zig`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`
- `zigux/tests/phase10_virtio_mmio_queue_isolation.zig`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `zigux/tests/phase10_virtio_input_manifest.json`
- `zigux/tests/phase10_virtio_mmio_manifest.json`
- `scripts/zigux/check-phase10-harness-coverage.py`
- `scripts/zigux/validate-phase10.py`
- `scripts/zigux/validate-phase10-closure.py`

Tests-root reviewer prompt:
- Do the shared Phase 10 build, closure manifest, focused multitouch preflight, focused MMIO queue-isolation replay, and harness-coverage checker still describe the same validator-first lab bundle rather than a set of unrelated virtio starter files?

## Phase 11 tests-root packet

Keep the shared-versus-dedicated replay boundary explicit:
- `zigux/tests/phase11_build.zig`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-layout-assert-surface.py`
- `scripts/zigux/check-phase11-hvc-validation-flow.py`
- `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`
- `scripts/zigux/validate-phase11.py`

Tests-root reviewer prompts:
- Do the pre-replay Phase 11 checkers still describe the same delivery contract that `zigux/tests/phase11_build.zig` and `zigux/tests/fixtures/phase11_build_inventory.json` claim?
- Does `zigux/tests/phase11_hvc_console_survey.zig` still stay separate as the dedicated archival replay while the shared starter packet remains under `zigux/tests/phase11_build.zig`?

## Phase 13 tests-root packet

Keep the shared release replay packet explicit:
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `zigux/tests/phase13_devres_manifest.json`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `scripts/zigux/validate-phase13-release.py`

Tests-root reviewer prompt:
- Do the shared Phase 13 build, the four roadmap-anchor manifests, the Landlock syscall reviewability replay, and the adjacent notifier reviewability packet still name the same validator-first release path and evidence bundle instead of drifting into separate stories?

## Checklist carryover prompts

Keep these reviewer questions explicit when `zigux/tests/README.md` or other shared contributor-facing workflow notes are refreshed:
- Phase 10: do `Documentation/zigux/phase10-closure-evidence.md`, `zigux/tests/phase10_closure_manifest.json`, `scripts/zigux/check-phase10-harness-coverage.py`, `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`, and `zigux/tests/phase10_virtio_mmio_queue_isolation.zig` still describe the same validator-first lab bundle and focused harness evidence?
- Phase 11: do `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-layout-assert-surface.py`, `scripts/zigux/check-phase11-hvc-validation-flow.py`, `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, `zigux/tests/phase11_build.zig`, and `zigux/tests/phase11_hvc_console_survey.zig` still keep the pre-replay stack and shared-versus-dedicated `hvc_console` split aligned?
- Phase 13: do `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/README.md`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, and `zigux/helpers/notifier_chain_view.zig` still keep the validator-first release path and adjacent notifier evidence aligned?

## Shared rule

When one of these packets changes, keep the tests-root replay file, the packet-local manifest or focused reviewability shard, and the validator-first review surface reviewable together.