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
- `scripts/zigux/check-phase1-bench.py`
keep the live owner map, the restored closure note and closure validator, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.
  * repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence.
  * the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.
  * keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.
  * `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.
Phase 2 notes
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `python3 scripts/zigux/check-zig-toolchain.py --self-test`
- `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `scripts/zigux/zig-toolchain-policy.json`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`
now keep the current directly readable Phase 2 toolchain, kbuild, kconfig bridge, make-wrapper, and artifact-support packet visible from the docs root instead of rebuilding the older closure-side validator stack from missing current-`master` paths.
  * repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so treat those validator-first follow-through, installer, and direct cross-route names as historical packet members until same-lane work rematerializes them on `master`.
  * keep the docs-root Phase 2 summary aligned to the shipped toolchain checker, the docs-shared-reminder checker, the required-make-route guard, the pinned Zig toolchain policy, the surviving kbuild and alignment guards, the live `conf_bridge` plus `confdata_bridge` helpers, `zigux/Makefile`, the current artifact-support manifest, the current kconfig fixture roster, and the current reminder routes `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.
  * without reviving missing closure, cross-target, or installer proof text.
Phase 3 notes
- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `Documentation/zigux/phase3-shared-reminder-gap.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `include/zigux/abi.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/abi.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/version.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_dev_t_starter_packet_manifest.json`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
now keep the current Phase 3 reminder surface anchored to one bounded `dev_t` starter packet with its directly readable export shim companion, one focused helper-local `err_ptr` / `xarray` slice, and one focused helper-local policy slice, instead of presenting the older broader validator, export/UAPI layout, catalog, low-level-wrapper, or shared replay packet as shipped docs-root evidence on current `master`.
  * the docs-root Phase 3 summary should keep the current starter packet explicit through `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `include/linux/zigux.h`, `include/zigux/dev_t.h`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `zigux/bindings/abi.zig`, `zigux/bindings/dev_t.zig`, `zigux/bindings/version.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_dev_t_starter_packet.zig`, `zigux/tests/phase3_dev_t_starter_packet_build.zig`, `zigux/tests/phase3_dev_t_starter_packet_manifest.json`, and the dedicated `scripts/zigux/check-phase3-dev-t-starter-packet.py` checker, while the helper-local interop slice stays explicit through `Documentation/zigux/phase3-errptr-xarray-slice.md`, `zigux/helpers/err_ptr.zig`, `zigux/helpers/xa_value.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`, and `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`, and the focused policy slice stays explicit through `Documentation/zigux/phase3-policy-slice.md`, `include/zigux/abi.h`, `zigux/bindings/abi.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/tests/phase3_policy_starter_packet.zig`, `zigux/tests/phase3_policy_starter_packet_build.zig`, `zigux/tests/phase3_policy_starter_packet_manifest.json`, and `scripts/zigux/check-phase3-policy-starter-packet.py`.
  * keep broader routes such as `Documentation/zigux/phase3-abi-header-family-survey.md`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `zigux/bindings/notifier_abi.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `scripts/zigux/validate-phase3.py`, and `scripts/zigux/phase3_catalog.py` framed as repo-reality gaps until fresh current-tree proof lands, while `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/unsafe/narrow.zig`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, and `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig` keep the current bounded atomic, barrier, and MMIO wrapper reminder packet explicit; keep `Documentation/zigux/phase3-shared-reminder-gap.md` explicit as the tracker for any remaining docs-root or tests-root reminder drift rather than reopening the stale saved Phase 3 publication packets.
Phase 4 notes
- `Documentation/zigux/phase4-reversible-delivery-evidence.md`
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase4-repo-reality-warning.py`
- `scripts/zigux/check-phase4-reversible-delivery-pins.py`
Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` now keep the current direct-readback rollback packet reviewable from the docs root while the broader validator, lab-matrix, local-only perf, and bitmap-diff companions remain repo-reality gaps on current `master`.
  * keep the broader Phase 4 repo-reality gaps explicit from the docs root too: `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` should stay framed as broader missing-current-head companions until fresh authenticated readback restores them.
  * keep the pending shared-CI perf-promotion posture explicit instead of implying those broader Phase 4 routes are live current-head evidence.
Phase 5 notes
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `zigux/tests/README.md`
now keep the current shared Phase 5 reminder packet explicit from the docs root so contributor guidance still matches the four approved non-runtime sample anchors without inventing new sample behavior or runtime proof.
  * the docs-root Phase 5 summary should stay aligned with `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, and `zigux/tests/README.md`, and it should keep the same four roadmap-backed anchors explicit: `samples/kfifo/bytestream-example.c`, `samples/kobject/kobject-example.c`, `samples/kprobes/kretprobe_example.c`, and `samples/trace_events/trace-events-sample.c`.
  * keep the current sample-root proof truthful here too: `samples/zigux/kretprobe_example.zig` is the directly readable non-runtime sample-root port on current `master`, while `samples/zigux/trace_events_string_formatting_sample.zig` is the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample; keep `samples/zigux/bytestream_fifo.zig`, `samples/zigux/kobject_example.zig`, the older direct trace-events sample-local companions, and the shared `zigux/tests/phase5_build.zig` route framed only as repo-reality gaps or current public-tree-backed companion evidence until a fresh reread proves direct authenticated proof again.
  * keep the no-extra-sample boundaries explicit from this docs root too: there is no standalone Phase 5 `samples/zigux/*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` reference sample on current `master`, and the bounded `*string*` companion stays tied to the non-runtime trace-events anchor rather than helper-local delivery.
  * keep the Phase 5 versus Phase 9 boundary explicit: do not count `samples/zigux/runtime_*.zig` files as extra Phase 5 evidence, and do not widen this docs-root reminder into runtime-loader, module-registration, procfs, sysfs, workqueue, or ring-buffer claims while the freeze map keeps those later lanes separate.
Phase 6 notes
- `Documentation/zigux/phase6-helper-evidence-catalog.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase6_build.zig`
- `zigux/tests/phase6_helper_evidence_manifest.json`
- `scripts/zigux/check-phase6-shared-surface.py`
- `scripts/zigux/check-phase6-present-entrypoints.py`
now keep the current Phase 6 docs-root reminder packet explicit from the documentation root so current helper parity and perf follow-through stays bounded to the directly readable shared evidence packet without widening into new helper semantics.
  * repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`, so treat those broader parity and perf reminder paths as historical packet members that need fresh reread or re-materialization before they are reused here as direct current-`master` docs-root evidence.
  * keep the docs-root Phase 6 summary aligned with `Documentation/zigux/phase6-helper-evidence-catalog.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_helper_evidence_manifest.json`, `scripts/zigux/check-phase6-shared-surface.py`, and `scripts/zigux/check-phase6-present-entrypoints.py`, so the shared helper packet keeps the bounded base64, bsearch, checksum, and hexdump evidence rows truthful without widening into missing helper-local parity or perf surfaces.
  * keep the roadmap-backed leaf-helper anchors explicit here too: `lib/base64.c`, `lib/bsearch.c`, `lib/checksum.c`, and `lib/hexdump.c` stay the Phase 6 scope, and follow-through should remain limited to reminder-surface truthfulness, helper-local parity, or perf-gate drift inside that bounded packet rather than runtime-core or freeze-map targets.
Phase 9 notes
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`
- `scripts/zigux/check-phase9-trace-events-runtime-packet.py`
- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_unregistered_gate.zig`
- `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
now keep the current docs-root Phase 9 reminder packet explicit from the documentation root so contributor guidance matches the surviving narrow trace-events runtime sample family without reviving the removed shared runtime-loader packet by implication.
  * keep the docs-root Phase 9 summary aligned with `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, so the docs root mirrors the same narrow runtime selftest-hook, lifecycle, fail-closed, and balanced registration-reentry packet that current `master` still exposes.
  * keep the current direct runtime-module evidence explicit here too: `samples/zigux/runtime_trace_events.zig` still exposes `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking, while `samples/zigux/runtime_trace_events_unregistered_gate.zig` keeps the same narrow packet's unregistered function-thread failures fail-closed plus its initialized-before/after, selftest_complete-before/after, and exited-before/after summary-stability checks, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` keeps balanced function-thread registration reusable across the initialized and selftest_complete stages instead of implying the broader shared runtime-loader family returned.
  * current `master` does not currently expose the broader shared runtime-loader packet, so `zigux/tests/phase9_build.zig`, the shared `zigux/tests/runtime_*` replay family, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the older `samples/zigux/runtime_*_loader.zig` scaffolds should stay framed as backlog references unless a fresh repo reread proves they have returned.
  * keep the older non-owner boundaries explicit here too: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence, and keep `kernel/workqueue.c` plus `kernel/trace/ring_buffer.c` framed only through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` instead of as runtime-pilot bridge-readiness cues.
Phase 13 notes
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
now keep the current docs-root Phase 13 reminder packet explicit from the documentation root so contributor guidance stays tied to the shipped shared-summary guard, notifier gap note, tests-root alignment check, and the four roadmap-owned helper anchors instead of the older missing validator-first or Makefile-backed handle.
  * keep the shared contributor-facing handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, keep the shipped shared-summary guard `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py` explicit beside `Documentation/zigux/phase13-shared-summary-guard-gap.md`, `Documentation/zigux/phase13-notifier-summary-gap.md`, and `scripts/zigux/check-phase13-tests-readme-alignment.py`, and keep the active helper-local packet bounded to `fs/libfs.c`, `lib/devres.c`, `security/landlock/ruleset.c`, and `security/landlock/syscalls.c`.
  * keep the shipped helper-local evidence explicit here too: `Documentation/zigux/phase13-libfs-survey.md`, `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_libfs_manifest.json`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/ruleset.zig`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, and `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls.zig`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` explicit, while `zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig`, `include/zigux/abi.h`, and `drivers/tty/hvc/hvc_console.h` stay adjacent notifier evidence rather than a fifth helper family.
  * current `master` still does not materialize `zigux/Makefile`, `make -C zigux phase13-validate`, `make -C zigux phase13`, `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, and `include/zigux/notifier_abi.h`, so keep those routes and companions framed as repo-reality gaps instead of direct current-`master` docs-root evidence. Keep `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/helpers/list_view.zig`, and `zigux/helpers/hlist_view.zig` explicit as returned shared-summary and adjacent notifier evidence on current `master` instead of leaving them in the repo-reality-gap list.
Phase 14 notes
- `Documentation/zigux/phase14-productization-gap-survey.md`
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`
- `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
now keep the current docs-root Phase 14 reminder packet honest from the documentation root so direct current-`master` readback in this lane is anchored to the directly recoverable shared-smoke survey, the current gap notes, and the readable-but-Phase-2-only `zigux/Makefile` surface instead of repeating the older story that the broader shared-smoke packet is simply missing.
  * keep the current docs-root Phase 14 summary aligned with `Documentation/zigux/phase14-productization-gap-survey.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, so the documentation root points first at the recovered study-only packet and its recorded readback gaps rather than at stale reminder text.
  * keep the directly recoverable shared-smoke layer explicit here too: fresh current-`master` rereads now recover `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, and the validator body through pinned blob readback for `scripts/zigux/validate-phase14.py`.
  * keep the current Makefile posture explicit instead of reviving stale route claims: `zigux/Makefile` is readable again on current `master`, but its live body now exposes only the Phase 2 toolchain and kbuild routes and no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets, so the docs-root reminder should not treat those older Phase 14 rerun routes as current shipped evidence from the Makefile.
  * keep the broader executable packet framed as the live repo-reality gap until fresh exact readback restores it: `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_ring_buffer_survey.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, and `net/core/skbuff_bridge.zig` should stay framed as the still-unrecovered executable layer rather than as direct current-`master` docs-root evidence.
  * keep the four roadmap-owned anchors explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay in the study-only boundary bucket, while `net/core/skbuff.c` and `kernel/rcu/tree.c` stay freeze-in-C anchors until the Architecture Council records a status change with parity-scorecard evidence. This docs-root reminder should keep those anchors visible without implying direct Phase 14 parity delivery.
  * keep the next honest follow-through narrow and notes-first: tighten any remaining shared reminder surfaces that still treat the older Makefile-backed `phase14-*` routes as current proof, or re-evaluate the parked validator-local handoff only if a later run restores a matching validator-and-build packet instead of widening this docs-root note into a new replay route or anchor-local status change.
Phase 15 notes
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-parity-scorecard-survey.md`
- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `Documentation/zigux/phase15-governance-lane-sequencing.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
- `scripts/zigux/check-phase15-docs-readme-alignment.py`
- `scripts/zigux/check-phase15-scripts-readme-alignment.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `zigux/tests/phase15_readiness_gate_manifest.json`
- `zigux/tests/phase15_architecture_council_review_process.zig`
- `zigux/tests/phase15_indefinite_c_policy.json`
- `zigux/tests/phase15_indefinite_c_policy.zig`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
now keep the current docs-root Phase 15 handoff packet explicit from the documentation root without implying any Architecture Council approval for a freeze-map status change.
  * the shared Phase 15 docs-root handoff should also keep the named reopen trigger, any deep-core blocker-posture change, and the current governance reminder split explicit through the freeze-map governance note, the Architecture Council review-process note, the dedicated decision-record template, the indefinite-C policy note, the parity scorecard plus roadmap-facing survey, the readiness and handoff surveys, the governance sequencing note, the study-only anchor accounting note, the shared-summary gap note, the docs-root and scripts-root alignment checkers, the shared-summary gap checker, the focused review-process handoff checker, and the dedicated `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_readiness_gate_manifest.json`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, and `zigux/tests/phase15_indefinite_c_policy.zig` companions while the four freeze-in-C anchors and two study-only anchors stay parked.
  * treat `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, and the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes as broader repo-reality gap vocabulary here until direct current-`master` readback proves they have returned as landed evidence, and keep the current docs-root reminder narrowed to truthfulness maintenance rather than a fresh freeze-map status change claim.