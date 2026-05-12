# Phase 13 Shared Helper Lane Sequencing

This note keeps the active Phase 13 shared-subsystems packet split into bounded owner lanes so contributor-facing guidance does not collapse `libfs`, `devres`, `landlock`, and adjacent notifier evidence into one noisy bucket.

## Scope

Use this note when a Phase 13 change touches any part of the shipped shared-helper release packet:
- `fs/libfs.c` through the shipped `fs/libfs.zig` plus `zigux/tests/phase13_libfs.zig` foothold together with the shipped `zigux/tests/phase13_libfs_reviewability.zig` companion; if direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs_addressability.zig`, or `zigux/tests/phase13_libfs_manifest.json` cannot be materialized on current `master`, keep that absence anchored to repo reality instead of assumed current-`master` evidence
- `lib/devres.c` through the shipped `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py`, while older `scripts/zigux/check-phase13-devres-packet.py` wording and the absent `zigux/tests/phase13_devres_boundary_evidence.zig` companion should stay anchored to repo reality instead of assumed current-master evidence
- `security/landlock/ruleset.c` through `Documentation/zigux/phase13-landlock-ruleset-ownership.md` plus the shipped `security/landlock/ruleset.zig` starter
- `security/landlock/syscalls.c` through `Documentation/zigux/phase13-landlock-syscalls-governance.md` plus the shipped `security/landlock/syscalls.zig` starter

Adjacent notifier evidence stays in scope for release-surface truthfulness, but it is still adjacent evidence rather than a fifth shared-helper anchor. Current `master` anchors that adjacent packet through:
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/abi.h`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

If direct notifier companions such as `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/helpers/notifier_chain_view.zig`, or `drivers/tty/hvc/hvc_console.h` cannot be materialized on current `master`, keep them recorded as adjacent repo-reality gaps instead of listing them here as independently shipped review evidence.

## Owner Split

Keep the current owner map explicit:
- `libfs` owns the shipped `fs/libfs.zig` plus `zigux/tests/phase13_libfs.zig` foothold together with the shipped `zigux/tests/phase13_libfs_reviewability.zig` companion; if direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs_addressability.zig`, or `zigux/tests/phase13_libfs_manifest.json` cannot be materialized on current `master`, keep that absence recorded as repo reality instead of listing those paths here as shipped helper-parity evidence
- `devres` helper parity owns the shipped `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_manifest.json`; keep older `scripts/zigux/check-phase13-devres-packet.py` wording and the absent `zigux/tests/phase13_devres_boundary_evidence.zig` companion anchored to repo reality instead of presenting them as shipped helper-parity evidence
- `devres` packet truthfulness owns the docs-side packet wording plus the shipped `scripts/zigux/check-phase13-devres-packet-alignment.py`; if the older `scripts/zigux/check-phase13-devres-packet.py` or `zigux/tests/phase13_devres_boundary_evidence.zig` are absent, treat that as a repo-reality blocker rather than as shipped current-master evidence
- `landlock/ruleset` owns `Documentation/zigux/phase13-landlock-ruleset-ownership.md` plus the shipped `security/landlock/ruleset.zig` starter; if direct companions such as `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, or `scripts/zigux/check-phase13-landlock-ruleset-packet.py` cannot be materialized on current `master`, keep that absence recorded as repo reality instead of listing those paths here as shipped helper-parity evidence
- `landlock/syscalls` owns `Documentation/zigux/phase13-landlock-syscalls-governance.md` plus the shipped `security/landlock/syscalls.zig` starter; if direct companions such as `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, or `zigux/tests/phase13_landlock_syscalls_manifest.json` cannot be materialized on current `master`, keep that absence recorded as repo reality instead of listing those paths here as shipped helper-parity evidence
- adjacent notifier evidence owns `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/Makefile`, `make -C zigux phase13-validate`, and `make -C zigux phase13`; if direct notifier companions such as `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/helpers/notifier_chain_view.zig`, or `drivers/tty/hvc/hvc_console.h` cannot be materialized on current `master`, keep that absence recorded as an adjacent repo-reality gap instead of listing those paths here as shipped current-master evidence, and keep the landed nonincreasing-priority signal explicit through `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/validate-phase13-release.py`, `make -C zigux phase13-validate`, and `make -C zigux phase13`

## Shared Packet Surfaces

When a real Phase 13 change lands, keep these shared surfaces aligned:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

Treat `make -C zigux phase13-validate` as the stable shared replay handle. If `scripts/zigux/validate-phase13-release.py`, `zigux/tests/phase13_build.zig`, or the direct `zig build test --build-file zigux/tests/phase13_build.zig --summary all` route cannot be materialized on current `master`, record those direct paths as repo reality instead of listing them here as shipped evidence.

## Sequencing Rules

Use this note to keep the bounded work order honest:
1. Prefer one helper lane at a time instead of batching `libfs`, `devres`, `landlock`, and notifier evidence into one mixed change.
2. Treat adjacent notifier evidence as release-surface support for the shared packet, not as an extra shared replay step.
3. Keep the validator-first route explicit through `make -C zigux phase13-validate`, then `make -C zigux phase13`; if a direct `zigux/tests/phase13_build.zig` build route or `scripts/zigux/validate-phase13-release.py` can be materialized later, pair it with that stable make route instead of presenting the direct path as independently shipped evidence before readback confirms it.
4. If a broad reminder surface changes, keep the owner split visible instead of replacing it with a generic "Phase 13 helper packet" summary.
5. Do not imply a closed Phase 13 tranche or a fifth helper anchor while the packet still depends on bounded adjacent notifier evidence.

## Non-Goals

This note does not widen Phase 13 into:
- a direct filesystem parity claim beyond the shipped `libfs` packet
- a separate shared replay step for notifier evidence
- broader security policy ownership outside the landed Landlock ruleset and syscall notes
- a claim that the Phase 13 packet is closed or frozen
