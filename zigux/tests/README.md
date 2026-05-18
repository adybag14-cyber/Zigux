# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose

  * hold shared harness logic before subsystem-specific tests spread through the tree
  * keep product-facing validation code separate from ad hoc experiments
  * provide the checks for helper parity, ABI assertions, and rollback readiness

Key entrypoints
  * `zigux/tests/build.zig`
  * roadmap-backed Phase 4 differential-gate destinations still missing on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`
  * current direct-readback Phase 4 rollback packet:
    `Documentation/zigux/phase4-reversible-delivery-evidence.md`
    `Documentation/zigux/review-checklist.md`
    `zigux/tests/README.md`
    `scripts/zigux/check-phase4-repo-reality-warning.py`
    `scripts/zigux/check-phase4-reversible-delivery-pins.py`
  * Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`
  * repo-reality warning for the broader Phase 4 validator, lab-matrix, and remaining local-only perf companions: authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig`
  * public current-`master` fallback rereads can still expose older broader Phase 4 companions, but keep that fallback visibility separate from authenticated direct-readback proof in this tests-root reminder until the same files return through direct contents reads
  * Phase 4 follow-through should treat the stale `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines in `Documentation/zigux/phase4-reversible-delivery-evidence.md` as historical provenance for that missing broader packet until fresh current-head evidence lands
  * The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open until that broader validator, lab-matrix, and remaining local-only perf companions are directly readable again
  * current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone
  * historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until the dedicated exact-pin refresh or a broader republish makes those companion blob values directly readable again
  * `Documentation/zigux/phase5-kfifo-sample-survey.md`
  * `samples/zigux/bytestream_fifo.zig`
  * `zigux/tests/phase5_bytestream_fifo_manifest.json`
  * current public-tree-backed Phase 5 bytestream companions: `zigux/tests/phase5_bytestream_fifo.zig` and `zigux/tests/phase5_bytestream_fifo_survey.zig`
  * `Documentation/zigux/phase5-kobject-sample-survey.md`
  * `samples/zigux/kobject_example.zig`
  * `zigux/tests/phase5_kobject_example.zig`
  * `zigux/tests/phase5_kobject_example_manifest.json`
  * current public-tree-backed Phase 5 kobject survey companion: `zigux/tests/phase5_kobject_example_survey.zig`
  * `Documentation/zigux/phase5-kretprobe-sample-survey.md`
  * `samples/zigux/kretprobe_example.zig`
  * `zigux/tests/phase5_kretprobe_example.zig`
  * `zigux/tests/phase5_kretprobe_example_manifest.json`
  * `zigux/tests/phase5_kretprobe_example_survey.zig`
  * current public-tree-backed Phase 5 kretprobe shared-build companion: `zigux/tests/phase5_build.zig`
  * keep this tests-root reminder aligned with the restored non-runtime kretprobe packet and keep `zigux/tests/phase5_build.zig` framed as companion evidence instead of direct authenticated-contents proof
  * `Documentation/zigux/phase5-trace-events-sample-survey.md`
  * `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
  * current repo-reality warning for the remaining trace-events sample-local companions: authenticated contents reads on current `master` now return missing for `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and `zigux/tests/phase5_build.zig`
  * keep this tests-root reminder aligned with those trace-events survey-note and approved-idiom-gap surfaces plus the shared Phase 5 review packet instead of treating those missing trace-events paths as direct tests-root proof until a fresh reread shows they returned
  * `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
  * `Documentation/zigux/phase1-closure.md`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/README.md`
  * `zigux/tests/fixtures/phase1_helper_manifest.json`
  * `zigux/tests/fixtures/phase1_helpers.json`
  * current direct-readback Phase 1 reminder packet: `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py`
  * repo-reality warning for the broader Phase 1 installer-backed closure-and-replay packet: repeated authenticated contents reads on current `master` now return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`
  * the restored `Documentation/zigux/phase1-closure.md` note and `scripts/zigux/validate-phase1-closure.py` now keep the current-master-safe closure packet explicit from the tests root, while `scripts/zigux/check-phase1-bench.py` remains the shipped bench-side checker for the remaining shared reminder wording
  * current `master` does ship `scripts/zigux/check-phase1-bench.py`, so keep the remaining shared reminder follow-through on the broader docs-root, checklist, and tests-root bench wording instead of treating the checker itself as a missing tests-root route
  * keep current Phase 1 follow-through tied to the live owner-map plus restored closure-side, string-review, and bench reminder packet instead of reconstructing the broader installer-backed closure-and-replay packet from those older missing installer, validator-first, closure-side, and replay files and routes alone
  * current direct-readback Phase 6 shared packet: `Documentation/zigux/phase6-helper-evidence-catalog.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/phase6_build.zig`, and `zigux/tests/phase6_helper_evidence_manifest.json`
  * repo-reality warning for the broader Phase 6 helper parity and perf packet: repeated authenticated contents reads on current `master` now return missing for `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`
  * keep current Phase 6 follow-through tied to those directly readable shared reminder surfaces plus the restored shared build and machine-readable evidence footholds instead of reconstructing the broader helper-local parity and perf packet from older route names alone

Phase 2 review packet
  * `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/check-zig-toolchain.py`
  * `scripts/zigux/check-phase2-kbuild-routes.py`
  * `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
  * `scripts/zigux/check-phase2-tests-readme-alignment.py`
  * `scripts/zigux/check-phase2-cross-selftest-alignment.py`
  * `scripts/zigux/check-phase2-toolchain-pinning.py`
  * `scripts/zigux/check-phase2-toolchain-pin-scope.py`
  * `scripts/zigux/check-phase2-docs-shared-reminder.py`
  * `scripts/zigux/check-phase2-required-make-routes.py`
  * `python3 scripts/zigux/check-zig-toolchain.py --self-test`
  * `scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
  * `scripts/zigux/kconfig/conf_bridge.zig`
  * `scripts/zigux/kconfig/confdata_bridge.zig`
  * `zigux/tests/fixtures/phase2_tool_manifest.json`
  * `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
  * `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
  * `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
  * `make -C zigux phase2-kconfig`
  * `zigux/tests/fixtures/kconfig_bridge/cases.json`
  * the current directly readable Phase 2 packet is the scripts-root kbuild, cross-selftest, docs-shared-reminder, required-make-route, and toolchain reminder set plus the live kconfig bridge helpers, the restored closure-side note and validator entrypoint, the shipped `zigux/Makefile` wrappers, and their fixture roster; keep this tests-root summary aligned to that narrower packet instead of rebuilding the older validator-first and direct cross-route stack from missing current-`master` paths
  * keep the pinned `x86_64-linux` bootstrap archive note and repo-local `.zig-toolchain` fallback reused by the surviving `scripts/zigux/check-zig-toolchain.py` and pin-scope guards explicit in this tests-root packet beside the live toolchain checker instead of widening back into missing validator-first or make-wrapper proof text
  * repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep those validator-first, installer, and direct cross-route names framed as historical packet members rather than direct tests-root evidence until the files or wrappers return on current `master`
  * keep the fixture-backed tool-manifest, artifact-tools, and kconfig bridge packet visible in the tests root without reviving missing validator-first or make-wrapper proof text

Phase 3 review packet
  * `Documentation/zigux/phase3-abi-slice.md`
  * `Documentation/zigux/phase3-errptr-xarray-slice.md`
  * `Documentation/zigux/phase3-policy-slice.md`
  * `Documentation/zigux/phase3-validator-support-surface.md`
  * `include/linux/zigux.h`
  * `include/zigux/dev_t.h`
  * `include/zigux/abi.h`
  * `zigux/uapi/version.zig`
  * `zigux/uapi/dev_t.zig`
  * `zigux/bindings/dev_t.zig`
  * `zigux/bindings/abi.zig`
  * `zigux/helpers/err_ptr.zig`
  * `zigux/helpers/xa_value.zig`
  * `zigux/helpers/panic_policy.zig`
  * `zigux/helpers/allocator_policy.zig`
  * `zigux/helpers/unsafe_policy.zig`
  * `zigux/tests/phase3_dev_t_starter_packet.zig`
  * `zigux/tests/phase3_dev_t_starter_packet_build.zig`
  * `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
  * `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
  * `zigux/tests/phase3_policy_starter_packet.zig`
  * `zigux/tests/phase3_policy_starter_packet_build.zig`
  * `zigux/tests/phase3_policy_starter_packet_manifest.json`
  * `scripts/zigux/check-phase3-dev-t-starter-packet.py`
  * `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
  * `scripts/zigux/check-phase3-policy-starter-packet.py`
  * `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test`
  * `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test`
  * `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
  * keep the current shared Phase 3 reminder anchored to the bounded `dev_t` starter packet, the helper-local `err_ptr` / `xarray` slice, and the focused policy slice already described in `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, and `Documentation/zigux/phase3-policy-slice.md`, instead of presenting the broader validator, export/UAPI layout, low-level-wrapper, IDR, or IDA packet as shipped tests-root evidence
  * treat broader routes such as `Documentation/zigux/phase3-abi-header-family-survey.md`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `scripts/zigux/validate-phase3.py`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, and `scripts/zigux/phase3_catalog.py` as repo-reality gaps until fresh current-tree proof lands
  * keep `Documentation/zigux/phase3-shared-reminder-gap.md` limited to tracking any future shared-surface drift or separate scripts-root inventory follow-through, because `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md` already carry the bounded three-slice posture and this tests-root packet should stay aligned with them
