# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose

  * hold shared harness logic before subsystem-specific tests spread through the tree
  * keep product-facing validation code separate from ad hoc experiments
  * provide the checks for helper parity, ABI assertions, and rollback readiness

Key entrypoints
  * `zigux/tests/build.zig`
  * current direct-readback Phase 1 reminder packet:
    `Documentation/zigux/phase1-closure.md`
    `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
    `Documentation/zigux/review-checklist.md`
    `scripts/zigux/README.md`
    `scripts/zigux/validate-phase1-closure.py`
    `scripts/zigux/check-phase1-string-review-packet.py`
    `scripts/zigux/check-phase1-direct-owner-markers.py`
    `scripts/zigux/check-phase1-bench.py`
    `zigux/tests/fixtures/phase1_helper_manifest.json`
  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
  * repo-reality warning for the broader historical Phase 1 validator-first, bench, and replay stack: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`
  * current `master` does materialize `zigux/Makefile` again, but its live body exposes only the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof
  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`
  * current direct-readback Phase 2 kconfig bridge packet:
    `Documentation/zigux/review-checklist.md`
    `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
    `scripts/zigux/kconfig/conf_bridge.zig`
    `scripts/zigux/kconfig/confdata_bridge.zig`
    `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
    `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
  * current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`
  * Phase 2 review packet:
    `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
    `Documentation/zigux/phase2-closure.md`
    `Documentation/zigux/review-checklist.md`
    `scripts/zigux/README.md`
    `scripts/zigux/validate-phase2.py`
    `scripts/zigux/check-zig-toolchain.py`
    `scripts/zigux/check-phase2-kbuild-routes.py`
    `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
    `scripts/zigux/check-phase2-tests-readme-alignment.py`
    `scripts/zigux/check-phase2-cross-selftest-alignment.py`
    `scripts/zigux/check-phase2-toolchain-pinning.py`
    `scripts/zigux/check-phase2-toolchain-pin-scope.py`
    `scripts/zigux/check-phase2-docs-shared-reminder.py`
    `scripts/zigux/check-phase2-required-make-routes.py`
    `python3 scripts/zigux/check-zig-toolchain.py --self-test`
    `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`
    `scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
    `scripts/zigux/kconfig/conf_bridge.zig`
    `scripts/zigux/kconfig/confdata_bridge.zig`
    `zigux/Makefile`
    `zigux/tests/fixtures/phase2_tool_manifest.json`
    `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
    `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
    `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
    `make -C zigux phase2-toolchain`
    `make -C zigux phase2-tools`
    `make -C zigux phase2-kconfig`
    `make -C zigux phase2-cross`
    `make -C zigux phase2-validate`
    `make -C zigux phase2`
    `zigux/tests/fixtures/kconfig_bridge/cases.json`
  * the current directly readable Phase 2 packet is the scripts-root kbuild, cross-selftest, docs-shared-reminder, required-make-route, and toolchain reminder set plus the live kconfig bridge helpers, the restored closure-side note and validator entrypoint, the shipped `zigux/Makefile` wrappers, and their fixture roster
  * keep the pinned `x86_64-linux` bootstrap archive note, the live `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replay, and the repo-local `.zig-toolchain` fallback reused by the surviving `scripts/zigux/check-zig-toolchain.py` and pin-scope guards explicit in this tests-root packet
  * repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep those older validator-first, installer, and direct cross-route names framed as historical packet members rather than direct tests-root evidence
  * keep the fixture-backed tool-manifest, artifact-tools, and kconfig bridge packet visible in the tests root without reviving missing validator-first or make-wrapper proof text
  * current direct-readback Phase 3 shared reminder packet:
    `Documentation/zigux/phase3-abi-slice.md`
    `Documentation/zigux/phase3-errptr-xarray-slice.md`
    `Documentation/zigux/phase3-policy-slice.md`
    `Documentation/zigux/phase3-validator-support-surface.md`
    `include/linux/zigux.h`
    `include/zigux/dev_t.h`
    `include/zigux/abi.h`
    `zigux/uapi/version.zig`
    `zigux/uapi/dev_t.zig`
    `zigux/bindings/dev_t.zig`
    `zigux/bindings/abi.zig`
    `zigux/helpers/err_ptr.zig`
    `zigux/helpers/xa_value.zig`
    `zigux/helpers/panic_policy.zig`
    `zigux/helpers/allocator_policy.zig`
    `zigux/helpers/unsafe_policy.zig`
    `zigux/tests/phase3_dev_t_starter_packet.zig`
    `zigux/tests/phase3_dev_t_starter_packet_build.zig`
    `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
    `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
    `zigux/tests/phase3_policy_starter_packet.zig`
    `zigux/tests/phase3_policy_starter_packet_build.zig`
    `zigux/tests/phase3_policy_starter_packet_manifest.json`
    `scripts/zigux/check-phase3-dev-t-starter-packet.py`
    `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
    `scripts/zigux/check-phase3-policy-starter-packet.py`
    `scripts/zigux/validate-phase3.py`
  * keep the current bounded Phase 3 packet explicit in the tests root: the directly readable starter packet, focused helper-local `err_ptr` / `xarray` slice, focused policy slice, and separately readable shared validator entrypoint are shipped current-`master` evidence here
  * keep the returned notifier-binding and focused export/UAPI layout replay pair explicit here instead of leaving `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and `zigux/tests/phase3_export_uapi_layout_build.zig` framed as broader repo-reality gaps
  * current bounded low-level-wrapper reminder packet: `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig`
  * keep the separately readable shared validator entrypoint explicit here too: `scripts/zigux/validate-phase3.py` is direct current-`master` evidence, but that single entrypoint should not be used to imply that the broader export/UAPI survey, catalog, or shared replay packet has returned
  * instead of presenting the broader export/UAPI survey, catalog, IDR, or IDA packet as shipped tests-root evidence
  * repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `scripts/zigux/phase3_catalog.py`, and `zigux/tests/fixtures/phase3_abi_manifest.json`, so keep those broader export/UAPI survey, catalog, and manifest-root routes framed as repo-reality gaps rather than direct tests-root evidence
  * roadmap-backed Phase 4 differential-gate destinations directly readable on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`
  * current direct-readback Phase 4 rollback packet:
    `Documentation/zigux/phase4-reversible-delivery-evidence.md`
    `Documentation/zigux/review-checklist.md`
    `zigux/tests/README.md`
    `scripts/zigux/check-phase4-repo-reality-warning.py`
    `scripts/zigux/check-phase4-reversible-delivery-pins.py`
  * Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`
  * Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`
  * recovered current-head broader Phase 4 note companions: `Documentation/zigux/phase4-gate-evidence.md` and `Documentation/zigux/phase4-validation-matrix.md`
  * repo-reality warning for the still-unreadable broader Phase 4 validator, checker, and bitmap-diff packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`
  * public current-`master` fallback rereads can still expose older broader Phase 4 companions, but keep that fallback visibility separate from authenticated direct-readback proof in this tests-root reminder until the same files return through direct contents reads
  * Phase 4 follow-through should treat the stale `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines in `Documentation/zigux/phase4-reversible-delivery-evidence.md` as historical provenance for that missing broader packet until fresh current-head evidence lands
  * The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open until that broader validator, lab-matrix, or bitmap-diff packet is directly readable again
  * current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone
  * historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until the dedicated exact-pin refresh or a broader republish makes those companion blob values directly readable again
## Phase 5 review packet

Keep the current shared Phase 5 reminder packet explicit through `Documentation/zigux/README.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.

Keep the current direct sample-root proof truthful here too: `samples/zigux/bytestream_fifo.zig` and `samples/zigux/kretprobe_example.zig` are the directly readable non-runtime sample-root ports on current `master`, while `samples/zigux/trace_events_string_formatting_sample.zig` is the bounded trace-events formatting companion rather than a returned full trace-events port, a standalone string-helper delivery, or a fifth Phase 5 sample. Keep `zigux/tests/phase5_build.zig` framed only as current public-tree-backed companion evidence until a fresh reread restores direct authenticated proof.

Keep the string-sample boundary explicit in the tests root too: there is still no standalone Phase 5 `samples/zigux/*string*` reference sample on current `master` outside the bounded trace-events formatting companion and the shared reminder packet. Keep that bounded string cue tied to the roadmap-backed `samples/trace_events/trace-events-sample.c` anchor instead of treating it as helper-local delivery or as proof that a separate string sample landed under `samples/zigux`.

Keep the same no-extra-sample boundaries explicit here: there is no standalone Phase 5 `samples/zigux/*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` reference sample on current `master`. Keep `samples/zigux/runtime_*.zig` framed as separate Phase 9 runtime-pilot evidence rather than extra Phase 5 proof.

## Phase 13 review packet

Keep the stable contributor-facing reminder handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `Documentation/zigux/review-checklist.md` and `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md` aligned with that stable handle as supporting shared reminder surfaces rather than treating the missing Makefile-backed route family as the shared entrypoint.

Keep the broader current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `Documentation/zigux/phase13-libfs-survey.md`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
- `Documentation/zigux/phase13-devres-scatterlist-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `fs/libfs.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `scripts/zigux/check-phase13-devres-dma-boundary.py`
- `scripts/zigux/check-phase13-devres-mmio-packet.py`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`
- `lib/devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist_build.zig`
- `security/landlock/ruleset.zig`
- `security/landlock/syscalls.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `zigux/tests/README.md`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`

Keep the shared contributor-facing release handle anchored to current repo reality: current `master` now materializes the bounded `fs/libfs.zig` foothold together with `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`.

Current `master` instead materializes the narrower devres helper packet through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`, so broader contributor wording should keep that direct planner and scatterlist packet explicit instead of rebuilding the older missing direct `lib/devres.zig` helper packet.

Current `master` also materializes the helper-owned Landlock ownership and syscall-governance notes plus the shipped `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` notes, the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, the direct ruleset replay pair `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json`, and the direct syscall replay packet `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, so contributor workflow wording should keep those shipped helper anchors explicit beside `Documentation/zigux/phase13-landlock-ruleset-ownership.md` and `Documentation/zigux/phase13-landlock-syscalls-governance.md` instead of treating Landlock as docs-only ownership metadata.

Current `master` still does not materialize `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, or `scripts/zigux/check-phase13-notifier-priority-signal.py`, so keep those validator-first, broader devres, and checker names framed as repo-reality gaps rather than shipped tests-root evidence.

Current `master` does materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep that guard explicit as shipped shared-summary evidence aligned with the contributor workflow guide and roadmap-traceability note instead of repeating it as a missing tests-root gap.

Current `master` also materializes the adjacent notifier survey plus the direct-evidence shards `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those six paths explicit as shipped adjacent evidence without counting them as extra shared replay steps.

Current `master` still does not materialize `zigux/helpers/notifier_chain_view.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, or `include/zigux/notifier_abi.h`, so keep those companion paths framed as adjacent repo-reality gaps rather than shipped tests-root evidence.

If direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/helpers/notifier_chain_view.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, or the older `scripts/zigux/check-phase13-devres-packet.py` cannot be materialized on current `master`, record them as repo-reality gaps instead of presenting them here as independently shipped review evidence.

Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.

Current `master` also materializes the dedicated Phase 13 packet summary in `zigux/tests/README.md`, so keep that broader tests-root guide aligned with the contributor workflow guide and shared-helper sequencing note as shipped Phase 13 review evidence instead of framing it as a pending shared-surface follow-up.

Tests-root reviewer prompt:
- Do the contributor workflow guide, shared-helper sequencing note, release-coordination matrix, release-notes and roadmap-traceability notes, the shipped shared-summary guard `scripts/zigux/check-phase13-shared-summary-surfaces.py`, the shipped `Documentation/zigux/phase13-libfs-survey.md` note plus `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`, the narrower current-master devres planner and scatterlist packet through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`, the helper-owned Landlock ownership and syscall-governance notes plus the shipped `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` notes, the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, the direct ruleset replay pair `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json`, the direct syscall replay packet `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, the shared contributor-facing reminder handle through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, plus the explicit repo-reality gap notes for `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `zigux/helpers/notifier_chain_view.zig`, `make -C zigux phase13-validate`, `make -C zigux phase13`, `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/check-phase13-notifier-packet.py`, and `include/zigux/notifier_abi.h`, while keeping `zigux/Makefile` distinct from those still-missing route names, the shared contributor-surface sync note, the shared review checklist, and the shipped adjacent notifier evidence `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and the Linux-side `drivers/tty/hvc/hvc_console.h` header explicit without counting them as extra shared replay steps, while treating missing direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/helpers/notifier_chain_view.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, and the older `scripts/zigux/check-phase13-devres-packet.py` as repo-reality gaps rather than shipped evidence?

## Phase 14 shared smoke packet

Keep the current tests-root Phase 14 reminder packet explicit through `Documentation/zigux/phase14-productization-gap-survey.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. The tests root should mirror the recovered study-only packet on current `master` instead of repeating the older assumption that the broader shared-smoke bundle is simply unreadable.

Keep the directly recoverable shared-smoke layer explicit here too: fresh current-`master` rereads recover `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, and the validator body through pinned blob readback for `scripts/zigux/validate-phase14.py`, so the tests-root reminder should point first at that recovered study-only packet and its named readback gaps.

Keep the current Makefile posture explicit instead of reviving stale route claims: `zigux/Makefile` is readable again on current `master`, but its live body exposes only the Phase 2 toolchain and kbuild routes and no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets. Keep `zigux/Makefile` distinct from those older route names and treat the route names as packet-local or repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves they returned.

Keep the broader executable packet framed as the current repo-reality gap in this tests-root reminder: `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_ring_buffer_survey.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, and `net/core/skbuff_bridge.zig` should stay framed as the still-unrecovered executable layer rather than direct current-`master` tests-root proof.

Keep the four roadmap-owned anchors explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay in the study-only boundary bucket, while `net/core/skbuff.c` and `kernel/rcu/tree.c` stay freeze-in-C anchors until the Architecture Council records a status change with parity-scorecard evidence. This tests-root reminder should keep those anchors visible without implying Phase 14 parity delivery.

Tests-root reviewer prompt:
- Do `Documentation/zigux/phase14-productization-gap-survey.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` keep the recovered study-only Phase 14 packet explicit, keep the pinned-blob validator readback for `scripts/zigux/validate-phase14.py` visible, keep the readable current `zigux/Makefile` framed as Phase-2-only rather than live `phase14-*` route proof, keep `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_ring_buffer_survey.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, and `net/core/skbuff_bridge.zig` framed as repo-reality gaps rather than shipped tests-root evidence, and keep `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, `net/core/skbuff.c`, and `kernel/rcu/tree.c` explicit as study-only or freeze-in-C anchors instead of reopened Phase 14 ownership claims?
