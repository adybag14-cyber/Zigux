# Zigux Documentation
This directory is the product documentation root for Zigux.
Scope
- product charter
- review rules
- freeze map
- phase closure records
- phase policy
- future porting guides
- validation and artifact-diff policy
Rules
- keep product commitments here, not in ad hoc issue threads
- keep deep-core freeze decisions explicit
- require validation and rollback language for every new active port target
- align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
Current closure records
- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase2-closure.md`
Phase 1 notes
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase1-closure.py`
- `scripts/zigux/check-phase1-string-review-packet.py`
- `scripts/zigux/check-phase1-direct-owner-markers.py`
- `scripts/zigux/check-phase1-shared-reminder-packet.py`
- `scripts/zigux/check-phase1-bench.py`
keep the live owner map, the restored closure note and closure validator, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.
  * repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12.
  * the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.
  * keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.
  * `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.
Phase 2 notes
- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`
- `scripts/zigux/README.md`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `zigux/Makefile`
keep the bounded Phase 2 docs-root packet explicit through the returned closure-side validator pair, the shipped installer and direct cross-route companions, the surviving toolchain and shared-reminder guards, the selected kconfig bridge helpers, the current manifests, and the shipped make-wrapper routes instead of treating that now-rematerialized tranche as historical-only evidence.
  * the current docs-root Phase 2 reminder packet should stay parked on `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, and `zigux/Makefile`, with `zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/phase2_cross_targets.json`, and the current kconfig bridge manifests keeping the same packet aligned across docs-root, scripts-root, and tests-root surfaces.
  * `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again, so keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, and make-wrapper surfaces instead of leaving them in historical-gap wording.
  * `python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side and make-wrapper packet without widening it back into older missing-route assumptions.
Phase 3 notes
- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `zigux/tests/fixtures/phase3_policy_dump_expected.txt`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/check-phase3-policy-starter-packet.py`
- `scripts/zigux/check-phase3-policy-dump.py`
- `scripts/zigux/phase3_catalog.py`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/validate-phase3-policy-unsafe-survey.py`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `include/linux/zigux.h`
- `include/zigux/abi.h`
- `include/zigux/dev_t.h`
- `zigux/kernel/export_shim.zig`
- `zigux/helpers/layout_assert.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/helpers/mmio.zig`
- `zigux/unsafe/narrow.zig`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/tests/phase3_policy_dump.zig`
- `zigux/tests/phase3_policy_dump_build.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
keep the bounded Phase 3 docs-root packet explicit through the ABI slice, the focused policy-and-unsafe survey pair, the directly coupled low-level-wrapper survey pair, the dedicated export/UAPI boundary survey, the returned linux-header governance note, the manifest-backed ABI and policy inventory, the validator set, the catalog helper, the direct layout replay route, and the starter export/UAPI plus policy surfaces instead of understating the current policy-and-unsafe packet as if it were only an implicit companion to the broader ABI substrate.
  * the current docs-root Phase 3 reminder packet should stay parked on `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase3_abi_manifest.json`, `zigux/tests/phase3_policy_starter_packet_manifest.json`, `zigux/tests/fixtures/phase3_policy_dump_expected.txt`, `scripts/zigux/README.md`, `scripts/zigux/check-phase3-abi.py`, `scripts/zigux/check-phase3-policy-starter-packet.py`, `scripts/zigux/check-phase3-policy-dump.py`, `scripts/zigux/phase3_catalog.py`, `scripts/zigux/validate-phase3.py`, `scripts/zigux/validate-phase3-policy-unsafe-survey.py`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `include/linux/zigux.h`, `include/zigux/abi.h`, `include/zigux/dev_t.h`, `zigux/kernel/export_shim.zig`, `zigux/helpers/layout_assert.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/helpers/mmio.zig`, `zigux/unsafe/narrow.zig`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `zigux/tests/phase3_policy_dump.zig`, `zigux/tests/phase3_policy_dump_build.zig`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, `zigux/tests/phase3_export_uapi_layout.zig` and `zigux/tests/phase3_export_uapi_layout_build.zig` so the docs root matches the same starter boundary packet already described by the dedicated surveys, the linux-header governance note, the shared manifests, and the scripts-root reminder surfaces.
  * current `master` directly serves the starter export shim, the version-only and `dev_t` starter UAPI companions, the linux-facing boundary relay, the dedicated export/UAPI survey validator, and the direct layout replay route `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`, so keep those surfaces explicit here instead of leaving the Phase 3 reminder packet understated.
  * current `master` also directly serves the helper-local policy packet through `Documentation/zigux/phase3-policy-slice.md`, `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`, `scripts/zigux/validate-phase3-policy-unsafe-survey.py`, `scripts/zigux/check-phase3-policy-starter-packet.py`, `scripts/zigux/check-phase3-policy-dump.py`, `zigux/tests/phase3_policy_starter_packet_manifest.json`, `zigux/tests/fixtures/phase3_policy_dump_expected.txt`, `zigux/helpers/layout_assert.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/unsafe_policy.zig`, and `zigux/unsafe/narrow.zig`, and it directly serves the adjacent MMIO-plus-narrow wrapper packet through `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/helpers/mmio.zig`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig`, so keep those policy-and-unsafe surfaces explicit here too instead of leaving them parked only in packet-local notes.
  * the remaining packet-local repo-reality gap is still the absent catalog-selftest guard `scripts/zigux/check-phase3-catalog-selftest.py`; keep that gap explicit without widening this docs-root reminder into claims about a larger returned UAPI family or newer export/UAPI-only replay routes than current `master` actually ships.
  * `python3 scripts/zigux/validate-phase3.py`, `python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py`, `python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `python3 scripts/zigux/validate-phase3-export-uapi-survey.py`, `zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig`, `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`, and `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig` replay the bounded current Phase 3 reminder packet without widening it into speculative helper or catalog-selftest follow-through.
Phase 5 notes
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/check-phase5-review-guide-surface.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
keep the current four-anchor non-runtime sample packet explicit from the docs root instead of letting the shared contributor reminder drift away from the live sample-root, scripts-root, guide, sequencing, checklist, and tests-root packet.
  * current `master` still directly exposes the restored bytestream packet through `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig`, and it still directly exposes the restored kretprobe packet through `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`, while `samples/zigux/trace_events_string_formatting_sample.zig` stays only the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample.
  * keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit here as the shipped shared guard for the direct bytestream and kretprobe proof markers, the bounded trace-events companion wording, and the no-extra-sample boundary instead of treating the docs-root Phase 5 packet as guide-only prose.
  * keep the no-extra-sample boundary explicit here too: there is no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep those helper families tied to their existing helper or later-phase packets instead of treating the sample root as proof they landed here.
  * keep `samples/zigux/runtime_*.zig` framed as separate Phase 9 runtime-pilot evidence rather than extra Phase 5 proof, and keep the `kobject` anchor in roadmap-backed shared-reminder or repo-reality-gap wording until a fresh reread restores its older sample-root and tests-root packet as direct authenticated proof.
  * keep the current `kobject` ownership-and-lifetime split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are current direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay public-tree-backed companion evidence until a fresh reread restores direct authenticated proof for those two routes.
Phase 9 notes
- Phase 9 notes - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`
- `Documentation/zigux/phase9-runtime-trace-events-survey.md`
- `zigux/tests/README.md`
- `zigux/tests/runtime_trace_events_manifest.json`
- `zigux/tests/runtime_trace_events_survey.zig`
- `samples/zigux/README.md`
- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_unregistered_gate.zig`
- `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
- `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`
- `scripts/zigux/check-phase9-trace-events-runtime-packet.py`
keep the live Phase 9 docs-root packet review-first and narrow: `samples/zigux/runtime_trace_events.zig` remains the surviving direct runtime-module sample and still exposes `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking, `samples/zigux/runtime_trace_events_unregistered_gate.zig` keeps unregistered function-thread failures fail-closed, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig` keeps failed-exit rollback explicit after reusable selftest replay, `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` keeps balanced function-thread registration reusable across the initialized and selftest_complete stages, and the returned family-local `zigux/tests/runtime_*` witness stays explicit without pretending the broader shared runtime-loader packet returned.
  * the current docs-root Phase 9 reminder packet should stay parked on `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `zigux/tests/README.md`, `zigux/tests/runtime_trace_events_manifest.json`, `zigux/tests/runtime_trace_events_survey.zig`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and the surviving trace-events sample family so the docs root matches the same narrow Phase 9 packet already described by the lane-sequencing note, checklist, scripts-root reminder, tests-root witness, and sample-root packet.
  * current `master` does not currently expose the broader shared runtime-loader packet, so `zigux/tests/phase9_build.zig`, the broader shared `zigux/tests/runtime_*` replay family beyond the returned trace-events survey witness, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, dedicated `phase9-*` routes in `zigux/Makefile`, and the older `samples/zigux/runtime_*_loader.zig` scaffolds stay backlog references unless a fresh repo reread proves they have returned.
  * keep the older cross-phase non-owner boundaries explicit here too: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence.
Phase 11 notes
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`
- `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`
- `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `Documentation/zigux/phase11-dw-wdt-slice.md`
- `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `drivers/watchdog/dw_wdt.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `drivers/tty/hvc/hvc_console.zig`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt.zig`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
keep the bounded Phase 11 docs-root packet explicit through the shared sequencing and matrix-gap notes, the directly readable gpio and HVC validation matrices, the current DesignWare owner packet, the narrower HVC current-head continuity packet, the coupled inventory and proof-backed adjunct builds, and the broad contributor and tests-root reminders instead of reviving the older shared replay-contract stack or absent Phase 11 build routes as if they were current `master` evidence.
  * the current docs-root Phase 11 reminder packet should stay parked on `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-validation-matrix-gap-survey.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`, `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-matrix-gap-survey.py`, `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`, `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/tty/hvc/hvc_console.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, and `zigux/tests/phase11_hvc_cleanup_packet_build.zig` so the docs root matches the same current-head simple-driver packet already described by the dedicated Phase 11 notes, the shared contributor sync note, and the tests-root companion.
  * current direct contents reads still do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-shared-summary-surfaces.py`, or `zigux/tests/phase11_build.zig`, while `zigux/Makefile` is current repo evidence again but still exposes no dedicated `make -C zigux phase11`, `make -C zigux phase11-validate`, or `make -C zigux phase11-contract` routes, so keep those matrix, shared-summary, shared-replay, and shared-route handles framed as repo-reality gaps or reminder vocabulary until a future reread proves they returned on current `master`.
  * `python3 scripts/zigux/check-phase11-build-inventory.py`, `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`, `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`, `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, and `zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig` replay the bounded current Phase 11 reminder packet without widening it into platform-backed watchdog registration, notifier execution, khvcd execution, live sysrq dispatch, live MMIO validation, or hardware-backed teardown claims.
Phase 12 notes
- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-release-readiness-survey.md`
- `Documentation/zigux/phase12-release-closure-checklist.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `Documentation/zigux/phase12-virtio-net-survey.md`
- `Documentation/zigux/phase12-virtio-scsi-slice.md`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
- `Documentation/zigux/phase12-nvme-pci-slice.md`
- `Documentation/zigux/phase12-nvme-pci-survey.md`
- `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-build-only-phase12-surface.py`
- `scripts/zigux/check-phase12-release-readiness-packet.py`
- `scripts/zigux/validate-phase12.py`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
keep the bounded Phase 12 docs-root packet explicit through the shared release-order, readiness, closure, coordination, fallback, and driver-local reminder notes plus the shipped validator-side support bundle instead of letting the docs root drift away from the active-not-closed release packet on current `master`.
  * the current docs-root Phase 12 reminder packet should stay parked on `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md`, with `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keeping the same shared packet aligned across docs-root, scripts-root, tests-root, workflow, and make-wrapper surfaces.
  * `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the docs root while current `zigux/Makefile` now exposes `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, and `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns on current `master`.
  * keep the degraded rerun order honest here too: rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile` before attached-Zig rerun vocabulary, and if that local fallback is absent keep `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` framed only as last-resort rerun vocabulary while `make -C zigux phase12-validate` remains reminder-only text.
  * keep the bounded packet split explicit here too: `virtio_net` stays starter-present reviewability, `virtio_scsi` stays the smoke-first and rollback-lab packet, `nvme_pci` stays driver-local outside the shared smoke-and-test route, and the Phase 12 libbpf packet stays parked behind survey, snapshot, and verify-shard reminder surfaces instead of widening the docs root into deeper DMA, queueing, throughput, or transport claims.
