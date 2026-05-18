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
  * repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again even though its live body still exposes only the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes.
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
- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`
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
  * keep the pinned archive-integrity replay explicit without reviving missing closure, cross-target, or installer proof text.
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
now keep the current Phase 3 reminder surface anchored to one bounded `dev_t` starter packet with its directly readable export shim companion, one focused helper-local `err_ptr` / `xarray` slice, one focused helper-local policy slice, and the now-shipped export/UAPI boundary reminder packet, instead of presenting broader catalog, low-level-wrapper, or shared replay surfaces as the whole docs-root Phase 3 story on current `master`.
  * the docs-root Phase 3 summary should keep the current starter packet explicit through `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `include/linux/zigux.h`, `include/zigux/dev_t.h`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `zigux/bindings/abi.zig`, `zigux/bindings/dev_t.zig`, `zigux/bindings/version.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_dev_t_starter_packet.zig`, `zigux/tests/phase3_dev_t_starter_packet_build.zig`, `zigux/tests/phase3_dev_t_starter_packet_manifest.json`, and the dedicated `scripts/zigux/check-phase3-dev-t-starter-packet.py` checker, while the helper-local interop slice stays explicit through `Documentation/zigux/phase3-errptr-xarray-slice.md`, `zigux/helpers/err_ptr.zig`, `zigux/helpers/xa_value.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`, and `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`, and the focused policy slice stays explicit through `Documentation/zigux/phase3-policy-slice.md`, `include/zigux/abi.h`, `zigux/bindings/abi.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/tests/phase3_policy_starter_packet.zig`, `zigux/tests/phase3_policy_starter_packet_build.zig`, `zigux/tests/phase3_policy_starter_packet_manifest.json`, and `scripts/zigux/check-phase3-policy-starter-packet.py`.
  * keep the docs-root Phase 3 export boundary wording limited to what the current direct-readback path actually proves: `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, and the direct `make -C zigux phase3-export-uapi-layout-test` convenience route keep the returned kernel-facing export note, notifier-binding companion, and focused layout replay explicit from the docs root, while `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, and `zigux/tests/fixtures/phase3_abi_manifest.json` should stay framed as repo-reality gaps until authenticated direct readback returns them again; `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/unsafe/narrow.zig`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, and `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig` keep the current bounded atomic, barrier, and MMIO wrapper reminder packet explicit; keep `Documentation/zigux/phase3-shared-reminder-gap.md` explicit as the tracker for the remaining tests-root reminder follow-through rather than reopening broader saved Phase 3 publication packets.
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
- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `zigux/tests/README.md`
now keep the current shared Phase 5 reminder packet explicit from the docs root so contributor guidance still matches the four approved non-runtime sample anchors without inventing new sample behavior or runtime proof.
  * the docs-root Phase 5 summary should stay aligned with `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, and `zigux/tests/README.md`, and it should keep the same four roadmap-backed anchors explicit: `samples/kfifo/bytestream-example.c`, `samples/kobject/kobject-example.c`, `samples/kprobes/kretprobe_example.c`, and `samples/trace_events/trace-events-sample.c`.
  * keep the current shared packet truthful here too: `Documentation/zigux/phase5-kfifo-sample-survey.md` plus `samples/zigux/bytestream_fifo.zig` keep the restored direct bytestream note-and-sample proof explicit, `samples/zigux/kretprobe_example.zig` is the directly readable non-runtime sample-root proof for the restored kretprobe packet, and `samples/zigux/trace_events_string_formatting_sample.zig` remains the bounded direct trace-events formatting companion rather than a returned full trace-events port or a fifth sample; keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` framed as current public-tree-backed trace-events companion evidence, while `samples/zigux/kobject_example.zig` and the shared `zigux/tests/phase5_build.zig` route stay in split-readback companion or repo-reality-gap wording until a fresh reread proves broader direct authenticated proof again.
  * keep the no-extra-sample boundaries explicit from this docs root too: there is no standalone Phase 5 `samples/zigux/*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` reference sample on current `master`, and the bounded `*string*` companion stays tied to the non-runtime trace-events anchor rather than helper-local delivery.
  * keep the Phase 5 versus Phase 9 boundary explicit: do not count `samples/zigux/runtime_*.zig` files as extra Phase 5 evidence, and do not widen this docs-root reminder into runtime-loader, module-registration, procfs, sysfs, workqueue, or ring-buffer claims while the freeze map keeps those later lanes separate.
Phase 6 notes