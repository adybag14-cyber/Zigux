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
  * repo-reality warning for the broader historical Phase 1 validator-first, bench, and replay stack: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, and `zigux/Makefile`
  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`
  * current direct-readback Phase 2 kconfig bridge packet:
    `Documentation/zigux/review-checklist.md`
    `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
    `scripts/zigux/kconfig/conf_bridge.zig`
    `scripts/zigux/kconfig/confdata_bridge.zig`
    `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
    `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
  * current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`
  * roadmap-backed Phase 4 differential-gate destinations directly readable on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`
  * current direct-readback Phase 4 rollback packet:
    `Documentation/zigux/phase4-reversible-delivery-evidence.md`
    `Documentation/zigux/review-checklist.md`
    `zigux/tests/README.md`
    `scripts/zigux/check-phase4-repo-reality-warning.py`
    `scripts/zigux/check-phase4-reversible-delivery-pins.py`
  * Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`
  * Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`
  * repo-reality warning for the broader Phase 4 validator, lab-matrix, and bitmap-diff packet: authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`
  * public current-`master` fallback rereads can still expose older broader Phase 4 companions, but keep that fallback visibility separate from authenticated direct-readback proof in this tests-root reminder until the same files return through direct contents reads
  * Phase 4 follow-through should treat the stale `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines in `Documentation/zigux/phase4-reversible-delivery-evidence.md` as historical provenance for that missing broader packet until fresh current-head evidence lands
  * The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open until that broader validator, lab-matrix, or bitmap-diff packet is directly readable again
  * current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone
  * historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until the dedicated exact-pin refresh or a broader republish makes those companion blob values directly readable again

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
- `Documentation/zigux/phase13-devres-survey.md`
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
- `lib/devres.zig`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_boundary_evidence.zig`
- `zigux/tests/phase13_devres_manifest.json`
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
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`

Keep the shared contributor-facing release handle anchored to current repo reality: current `master` now materializes the bounded `fs/libfs.zig` foothold together with `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`.

It also materializes the devres helper packet through `lib/devres.zig`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, and `zigux/tests/phase13_devres_manifest.json`, so broader contributor wording should keep that direct boundary-evidence replay explicit beside the shared devres packet instead of treating it as a missing companion.

Current `master` also materializes the helper-owned Landlock ownership and syscall-governance notes plus the shipped `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` notes, the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, the direct ruleset replay pair `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json`, and the direct syscall replay packet `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, so contributor workflow wording should keep those shipped helper anchors explicit beside `Documentation/zigux/phase13-landlock-ruleset-ownership.md` and `Documentation/zigux/phase13-landlock-syscalls-governance.md` instead of treating Landlock as docs-only ownership metadata.

Current `master` still does not materialize `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, or `scripts/zigux/check-phase13-notifier-priority-signal.py`, so keep those validator-first and checker names framed as repo-reality gaps rather than shipped tests-root evidence.

Current `master` does materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep that guard explicit as shipped shared-summary evidence aligned with the contributor workflow guide and roadmap-traceability note instead of repeating it as a missing tests-root gap.

Current `master` also materializes the adjacent notifier survey plus the direct-evidence shards `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those six paths explicit as shipped adjacent evidence without counting them as extra shared replay steps.

Current `master` still does not materialize `zigux/helpers/notifier_chain_view.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, or `include/zigux/notifier_abi.h`, so keep those companion paths framed as adjacent repo-reality gaps rather than shipped tests-root evidence.

If direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/helpers/notifier_chain_view.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, or the older `scripts/zigux/check-phase13-devres-packet.py` cannot be materialized on current `master`, record them as repo-reality gaps instead of presenting them here as independently shipped review evidence.

Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep `zigux/Makefile` distinct from those route names and keep only the route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.

Current `master` also materializes the dedicated Phase 13 packet summary in `zigux/tests/README.md`, so keep that broader tests-root guide aligned with the contributor workflow guide and shared-helper sequencing note as shipped Phase 13 review evidence instead of framing it as a pending shared-surface follow-up.

Tests-root reviewer prompt:
- Do the contributor workflow guide, shared-helper sequencing note, release-coordination-matrix, release-notes and roadmap-traceability notes, the shipped shared-summary guard `scripts/zigux/check-phase13-shared-summary-surfaces.py`, the shipped `Documentation/zigux/phase13-libfs-survey.md` note plus `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`, the shipped devres slice and survey plus `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, and `zigux/tests/phase13_devres_manifest.json`, the helper-owned Landlock ownership and syscall-governance notes plus the shipped `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` notes, the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, the direct ruleset replay pair `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json`, the direct syscall replay packet `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, the shared contributor-facing reminder handle through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, plus the explicit repo-reality gap notes for `zigux/helpers/notifier_chain_view.zig`, `make -C zigux phase13-validate`, `make -C zigux phase13`, `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/check-phase13-notifier-packet.py`, and `include/zigux/notifier_abi.h`, while keeping `zigux/Makefile` distinct from those still-missing route names, the shared contributor-surface sync note, the shared review checklist, and the shipped adjacent notifier evidence `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and the Linux-side `drivers/tty/hvc/hvc_console.h` header explicit without counting them as extra shared replay steps, while treating missing direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/helpers/notifier_chain_view.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, and the older `scripts/zigux/check-phase13-devres-packet.py` as repo-reality gaps rather than shipped evidence?
