# Phase 10, 11, and 13 Contributor Surface Sync

Use this note when a contributor-facing wording change touches the active Phase 10, Phase 11, or Phase 13 packet and the same idea needs to stay aligned across docs-root, tests-root, checklist-facing, and validator-first guidance.

## Why this note exists

These three active packets already have strong packet-local evidence notes and checker stacks, but the broad contributor prompts can still drift when a wording refresh lands in one surface and not the others.

Treat the files below as one shared workflow bundle whenever a prompt, checklist sentence, or summary sentence changes.

## Shared surfaces

Update these surfaces together when they describe the same active contributor packet:
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `zigux/tests/README.md`

Also refresh the packet-local docs-root or scripts-root note when the wording change depends on a newly named replay, checker, manifest, or survey file.

## Update order

1. Start from the packet-local source of truth.
2. Refresh the validator-first review guide with the exact checker stack, replay route, and evidence names.
3. Refresh the compact tests-root companion so the same packet stays reviewable in the short form.
4. Refresh `Documentation/zigux/review-checklist.md` if the change alters a shared reviewer prompt or release-discipline question.
5. Refresh `zigux/tests/README.md` last so the broad tests-root carryover prompt matches the already-tightened packet notes.
6. Re-read the four shared surfaces and confirm they use the same nouns for the same packet rather than mixing shorthand and explicit wording.

## Phase 10 anchors

For the active virtio contributor packet, confirm wording still matches:
- `Documentation/zigux/phase10-closure-evidence.md`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`
- `scripts/zigux/check-phase10-closure-inventory.py`
- `scripts/zigux/check-phase10-core-packet.py`
- `scripts/zigux/check-phase10-harness-coverage.py`

## Phase 11 anchors

For the active simple-driver contributor packet, confirm wording still matches:
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-shared-replay-contract.py`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `zigux/tests/phase11_hvc_console_survey.zig`

## Phase 13 anchors

For the active shared-helper release packet, confirm wording still matches:
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `Documentation/zigux/phase13-devres-scatterlist-slice.md`
- `scripts/zigux/check-phase13-libfs-packet.py`
- `scripts/zigux/check-phase13-devres-packet.py`
- `scripts/zigux/check-phase13-devres-inventory-contract.py`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `scripts/zigux/check-phase13-release-replay-exact-counts.py`

## Drift checks

Before closing a contributor-guidance change, ask:
- Did a short-form companion note gain wording that the broad tests-root prompt still skips?
- Did a checklist prompt keep an old replay count after the validator-first guide changed?
- Did docs-root or scripts-root add a new replay, checker, manifest, or survey file that the shared contributor prompts still compress into older shorthand?

If the answer is yes, finish the shared-surface sync before treating the packet as review-ready.
