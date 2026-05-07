# Phase 10, 11, and 13 Contributor Surface Sync

Use this note when a contributor-facing wording change touches the active Phase 10, Phase 11, or Phase 13 packet and the same idea needs to stay aligned across docs-root, tests-root, checklist-facing, and validator-first guidance.

## Why this note exists

These three active packets already have strong packet-local evidence notes and checker stacks, but the broad contributor prompts can still drift when a wording refresh lands in one surface and not the others.

Treat the files below as one shared workflow bundle whenever a prompt, checklist sentence, or summary sentence changes.

## Shared surfaces

Update these surfaces together when they describe the same active contributor packet:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

For Phase 13 wording, keep the shared validator-first replay route separate from the broader shipped adjacent release-surface evidence so review prompts do not quietly turn those adjacent files into extra replay steps.

Also refresh the packet-local docs-root or scripts-root note when the wording change depends on a newly named replay, checker, manifest, or survey file.

## Update order

1. Start from the packet-local source of truth.
2. Refresh `Documentation/zigux/README.md` so the exact checker stack, replay route, and evidence names stay visible from the top-level product index.
3. Refresh `Documentation/zigux/phase13-contributor-workflow-guide.md` and `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` when the change sharpens the shared validator-first replay route, the owner-map split, or the broader shipped adjacent release-surface evidence for Phase 13 contributors.
4. Refresh the compact tests-root companion so the same packet stays reviewable in the short form.
5. Refresh `scripts/zigux/README.md` when the wording change affects the scripts-root validator-first replay summary, checker inventory, or Linux-style command wording.
6. Refresh `Documentation/zigux/review-checklist.md` if the change alters a shared reviewer prompt or release-discipline question.
7. Refresh `zigux/tests/README.md` last so the broad tests-root carryover prompt matches the already-tightened packet notes.
8. Re-read the six shared surfaces and confirm they use the same nouns for the same packet rather than mixing shorthand and explicit wording.

## Phase 10 anchors

For the active virtio contributor packet, confirm wording still matches the current build-backed Phase 10 surface on `master`:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-virtio-core-slice.md`
- `Documentation/zigux/phase10-virtio-core-survey.md`
- `Documentation/zigux/phase10-virtio-ring-slice.md`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `Documentation/zigux/phase10-virtio-input-slice.md`
- `Documentation/zigux/phase10-virtio-input-module-slice.md`
- `Documentation/zigux/phase10-virtio-input-survey.md`
- `Documentation/zigux/phase10-virtio-mmio-slice.md`
- `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase10_build.zig`
- `zigux/tests/phase10_virtio_core_reset_queue.zig`
- `zigux/tests/phase10_virtio_driver_id.zig`
- `zigux/tests/phase10_virtio_input_status_drain.zig`
- `scripts/zigux/check-phase10-core-packet.py`
- `scripts/zigux/check-phase10-ring-packet.py`
- `scripts/zigux/check-phase10-input-packet.py`
- `scripts/zigux/check-phase10-mmio-packet.py`
- `zigux/Makefile`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Keep the shared wording honest about what is not shipped on `master`: there is still no dedicated shared `validate-phase10.py`, `check-phase10-harness-coverage.py`, `phase10_closure_manifest.json`, or closure-ledger-backed replay route.

## Phase 11 anchors

For the active simple-driver contributor packet, confirm wording still matches:
- `Documentation/zigux/README.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `zigux/tests/phase11_build.zig`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/Makefile`

## Phase 13 anchors

For the active shared-helper release packet, keep the shared validator-first replay route and the broader shipped adjacent release-surface evidence described separately but truthfully. Confirm wording still matches:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-libfs-slice.md`
- `Documentation/zigux/phase13-libfs-survey.md`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/tests/README.md`
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_manifest.json`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/notifier_chain_view.zig`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase13-devres-packet.py`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

## Drift checks

Before closing a contributor-guidance change, ask:
- Did the compact tests-root companion now explicitly keep `Documentation/zigux/README.md` in its opening shared-surface sentence while this sync note or another shared contributor prompt still leaves the docs-root README implicit?
- Did a short-form companion note gain wording that the broad tests-root prompt still skips?
- Did a shared scripts-root Phase 13 summary keep `zigux/tests/phase13_landlock_syscalls_reviewability.zig` implicit after the contributor guide, compact tests-root companion, or review checklist made that focused landlock reviewability shard explicit as direct evidence beside `zigux/tests/phase13_landlock_syscalls.zig`?
- Did a checklist prompt keep an old replay count after the docs-root summary changed?
- Did docs-root or scripts-root add a new replay, checker, manifest, or survey file that the shared contributor prompts still compress into older shorthand?
- Did one shared Phase 10 prompt collapse the shipped `scripts/zigux/check-phase10-ring-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, or `scripts/zigux/check-phase10-mmio-packet.py` guards back into core-only shorthand, leave the scripts-root Phase 10 flow talking as if only the core and input packet guards exist, or drop `Documentation/zigux/phase10-virtio-mmio-slice.md`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, or `zigux/tests/phase10_virtio_input_status_drain.zig` after the packet-local evidence named them explicitly?
- Did one shared Phase 13 prompt turn shipped adjacent release-surface evidence such as `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, or `zigux/helpers/notifier_chain_view.zig` into extra replay steps, drop `make -C zigux phase13-validate` or `make -C zigux phase13`, or add the unshipped `scripts/zigux/check-phase13-notifier-packet.py` route?
- Do any shared Phase 13 prompts still imply `scripts/zigux/check-phase13-release-replay-exact-counts.py` as a shipped surface even though that exact-count checker does not currently round-trip on `master`?

If the answer is yes, finish the shared-surface sync before treating the packet as review-ready.
