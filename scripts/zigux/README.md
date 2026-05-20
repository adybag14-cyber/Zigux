# scripts/zigux

This directory holds shipped Zigux validation helpers and compact reminder surfaces.

## Phase 1

- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes
- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route
- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that packet
- `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` are back on current `master`, so bitmap-side follow-through can use that restored closure packet as live reminder evidence instead of replaying older missing validator-first or make-route names by default
- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence
- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here
- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts

## Phase 2

- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of replaying older missing-route assumptions inside that now-rematerialized toolchain packet
- `scripts/zigux/kconfig/conf_bridge.zig` keeps the shipped sixteen-mode request-plan bridge explicit from the scripts root, including the `helpnewconfig` `silent` option handling and the same `randconfig`, `defconfig`, `savedefconfig`, and `syncconfig` argument surfaces that the Phase 2 wrapper-first roadmap tranche expects
- `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` keep the current conf-side and confdata-side bridge evidence packet explicit from the scripts root without pretending the broader closure packet is still directly readable
- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/check-phase2-required-make-routes.py` remain the shipped Phase 2 toolchain, reminder, alignment, artifact-support, fixdep, genksyms-bridge, and required-make-route guards that survive on current `master`
- `.github/workflows/zigux-bootstrap.yml`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` keep the shipped pinned Zig toolchain guard explicit in the live bootstrap action path before the surviving Phase 2 bridge and pinning checks
- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set
- `scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards
- `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` keep the shipped artifact-support and fixdep packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards
- `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording
- keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet
- if future work widens the installer or direct cross-route packet, update this reminder packet only after rereading those direct current-`master` surfaces together with the live toolchain policy, manifest-backed kconfig fixture roster, the fixture-backed Phase 2 tool packet, and shipped make-wrapper packet so the scripts-root summary stays aligned with the now-returned Phase 2 evidence

## Phase 3

## Phase 4

## Phase 5

## Phase 6

## Phase 8

## Phase 9

## Phase 10

## Phase 11

## Phase 12

## Phase 13

## Phase 14

## Phase 15

- Phase 15 flow - the current scripts-root governance reminder packet stays in maintenance-mode truthfulness work, keeping the landed freeze-map, readiness, handoff, parity, stay-in-C, study-only, and shared-summary surfaces aligned without implying Architecture Council approval or a deep-core port-readiness decision
- `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-shared-summary-gap.py`, and `scripts/zigux/check-phase15-readiness-gate-packet.py` keep the shipped docs-root, scripts-root, tests-root, handoff, shared-summary, and readiness packet guards explicit from the scripts root
- `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-parity-scorecard-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_architecture_council_review_process_build.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_readiness_gate_manifest.json`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, and `.github/workflows/zigux-bootstrap.yml` keep the current directly readable governance packet explicit from the scripts root
- repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`, so keep those broader validator-first and build companions framed as repo-reality gaps instead of shipped scripts-root evidence while `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig` stays part of the directly readable governance packet
- although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names as blocked route vocabulary rather than directly readable replay paths
- `.github/workflows/zigux-bootstrap.yml` is present on current `master`, but it still carries no dedicated Phase 15 validate, test, or aggregate route, so keep that workflow surface framed as shared-summary gap vocabulary rather than shipped Phase 15 replay evidence
- no Architecture Council approval is currently recorded for a freeze-map status change, and any future follow-through should tighten the smallest truthful reminder surface first instead of widening into a status-change claim
