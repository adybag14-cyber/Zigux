# Contributing To Zigux

Use this guide for bounded product work in `adybag14-cyber/Zigux`.

## Start With Scope
- Name the roadmap phase, lane or workstream, and exact Linux anchor file or tree path before you change code or docs.
- Keep work bounded to one real packet: helper, validator, survey note, manifest, build entrypoint, or contributor-facing workflow surface.
- Avoid mirror-tree sprawl, wrapper churn, or speculative ports that are not backed by the roadmap.
- Respect freeze-map and study-only boundaries. Deep-core status changes still require Architecture Council evidence.

## Prefer Validator-First Delivery
- The default replay path in Zigux is validator first, then focused Zig or shared build replay.
- When a phase already has a published `make -C zigux phaseN-validate` or `python3 scripts/zigux/validate-phaseN.py` route, use that as the first command reviewers rerun.
- If you add a new checker or survey packet, wire it into the existing validator-first route instead of leaving it discoverable only from a one-off script or workflow step.
- If local Zig replay is blocked, say exactly what was unavailable and keep the narrowest honest Python, fixture, or self-test validation you can still run.

## Keep Shared Surfaces In Sync
When a change affects validation or replay wiring, check whether the same change also needs updates in these contributor-facing surfaces:
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
- the relevant `Documentation/zigux/*.md` review note, survey, closure record, or checklist
- `.github/PULL_REQUEST_TEMPLATE.md` when contributor prompts need to name the new route

A docs-only update is still expected when the repo already ships the validator, checker, or replay path but contributors cannot discover it from the shared guidance.

## Active Phase 10, 11, and 13 Packets
When a change touches the current active contributor packets, keep the shared guide plus the packet-local evidence aligned in the same review instead of updating only one note, one manifest, or one build file.

- Phase 10: keep `Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md`, `Documentation/zigux/phase10-closure-evidence.md`, `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned with the same `make -C zigux phase10-validate` then `make -C zigux phase10` route.
- Phase 11: keep `Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned with the same `make -C zigux phase11-validate`, `make -C zigux phase11`, and dedicated `make -C zigux phase11-hvc-survey` boundary.
- Phase 13: keep `Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned with the same `make -C zigux phase13-validate` then `make -C zigux phase13` route.

## Validation Notes To Record
Include these details in the pull request description:
- the validator-first command run
- any focused Zig replay or shared build replay run after the validator
- any checker self-tests or fixture checks run
- the exact blocker if local replay was not possible
- rollback owner, fallback path, and any open follow-up

## Publication Expectations
- Keep changes small and coherent.
- Prefer additive updates that make an existing packet more reviewable or less drift-prone.
- Do not treat repetitive helper-plan growth as product progress unless it closes a real roadmap-backed gap.
- If a packet is blocked, record the blocker plainly and leave the next bounded step inside the same lane.

## Good Contributor Pattern
1. Pick one roadmap-backed gap.
2. Update the code, manifest, or docs packet that actually closes it.
3. Run the validator-first command.
4. Run the narrowest honest focused replay you can support.
5. Sync the shared guidance surfaces if the contributor workflow changed.
6. Record the exact validation and blocker state in the PR.
