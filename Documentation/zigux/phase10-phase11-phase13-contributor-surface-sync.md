# Phase 10, 11, and 13 Contributor Surface Sync

Use this note when a change touches the active Phase 10 virtio packet, the active Phase 11 simple-driver packet, or the active Phase 13 shared-helper packet and the review needs one compact contributor-facing owner map.

## Purpose

Keep the broad contributor surfaces aligned so docs-root, scripts-root, tests-root, and checklist-facing reminders do not drift across the three still-active shared packets.

Shared surfaces to keep aligned:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

## Phase 10 contributor packet

Keep the bounded virtio packet explicit through:
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `Documentation/zigux/phase10-virtio-core-slice.md`
- `Documentation/zigux/phase10-virtio-core-survey.md`
- `Documentation/zigux/phase10-virtio-ring-slice.md`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `Documentation/zigux/phase10-virtio-input-slice.md`
- `Documentation/zigux/phase10-virtio-input-module-slice.md`
- `Documentation/zigux/phase10-virtio-input-survey.md`
- `Documentation/zigux/phase10-virtio-mmio-slice.md`
- `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `scripts/zigux/check-phase10-core-packet.py`
- `scripts/zigux/check-phase10-ring-packet.py`
- `scripts/zigux/check-phase10-input-packet.py`
- `scripts/zigux/check-phase10-mmio-packet.py`
- `scripts/zigux/check-phase10-mmio-freeze-boundary.py`
- `zigux/tests/phase10_build.zig`
- `zigux/Makefile`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Contributor reminder:
- keep the blocked risky-transport posture explicit
- keep the allowed `drivers/virtio/*.zig` destination family explicit
- treat Phase 5 reference samples and Phase 9 runtime starters as adjacent evidence, not extra Phase 10 closure proof

## Phase 11 contributor packet

Keep the shared-versus-dedicated simple-driver packet explicit through:
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-closure-note.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `scripts/zigux/check-phase11-shared-replay-contract.py`
- `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-packet.py`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `zigux/tests/phase11_build.zig`
- `zigux/Makefile`
- `make -C zigux phase11`
- `make -C zigux phase11-hvc-survey`

Contributor reminder:
- keep the shared replay split explicit instead of collapsing bcm2835, DesignWare, HVC, and header-boundary evidence into one generic driver note
- keep the bounded `hvc_cleanup()` teardown handoff and the dedicated DesignWare teardown companion explicit

## Phase 13 contributor packet

Keep the shared-subsystems packet explicit through the verified docs-root, validator-first, and contributor-facing replay surfaces:
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `security/landlock/ruleset.zig`
- `security/landlock/syscalls.zig`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/validate-phase13-release.py`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

Contributor reminder:
- keep the validator-first Phase 13 release route explicit through `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `make -C zigux phase13-validate`, and `make -C zigux phase13` while treating direct helper-local tests-root and notifier companions as repo-reality gaps until current-`master` readback proves them
- keep `libfs`, `devres` helper parity, `devres` packet truthfulness, `landlock`, and adjacent notifier evidence as separate owners
- keep direct helper-local tests-root paths and adjacent focused checker paths framed as repo reality rather than shipped evidence when current `master` still cannot materialize `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_landlock_*.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/helpers/notifier_chain_view.zig`, and `drivers/tty/hvc/hvc_console.h`, while the shipped `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet-alignment.py` guard, the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, `zigux/bindings/notifier_abi.zig`, and `include/zigux/abi.h` stay explicit
- if a broad reminder still spells the missing devres reviewability companion as `zigux/tests/phase13Devres_reviewability.zig`, treat that as stale wording for `zigux/tests/phase13_devres_reviewability.zig` rather than as a separate valid path
- treat notifier evidence as adjacent release-surface support rather than a fifth shared-helper anchor
- refresh this note only with surfaces verified on current `master`, not with hoped-for follow-up notes

## Sync Rules

1. When one of these packets changes, refresh the broad contributor surfaces before adding new packet-local wording.
2. Prefer one packet-local change at a time instead of batching Phase 10, 11, and 13 drift into a single mixed update.
3. Do not imply validator, checker, or replay surfaces that are not on current `master`.
4. Keep release-surface truthfulness explicit whenever a broad reminder references an adjacent evidence note or manifest.
5. Keep phase-local owner maps visible instead of replacing them with a generic cross-phase summary.
