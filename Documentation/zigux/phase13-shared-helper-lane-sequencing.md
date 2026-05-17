# Phase 13 Shared Helper Lane Sequencing

This note keeps the active Phase 13 shared-helper packet split into bounded owner lanes so contributor-facing guidance does not collapse `libfs`, `devres`, `landlock`, and adjacent notifier evidence into one noisy bucket.

Current Phase 13 repo reality now spans two naming layers: some shipped manifests and packet-local notes still carry the older repo packet ids on `master`, while scheduled coordination uses newer bounded aliases to keep verification-only, helper-local, and shared reminder work from colliding. This note exists to keep those two layers readable without turning either one into a duplicate owner map.

## Scope

Use this note when a Phase 13 change touches any part of the shipped shared-helper release packet:

- `fs/libfs.c` through the shipped `fs/libfs.zig`, `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`; if direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_libfs_addressability.zig`, or the older shared `zigux/tests/phase13_build.zig` route cannot be materialized on current `master`, keep that absence anchored to repo reality instead of assumed current-`master` evidence.
- `lib/devres.c` through the shipped `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_manifest.json`; keep missing checker-side names such as `scripts/zigux/check-phase13-devres-packet-alignment.py` and the older `scripts/zigux/check-phase13-devres-packet.py` anchored to repo reality instead of assumed current-`master` evidence.
- `security/landlock/ruleset.c` through `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, the shipped `Documentation/zigux/phase13-landlock-ruleset-slice.md`, the shipped `Documentation/zigux/phase13-landlock-ruleset-survey.md` note, the shipped `security/landlock/ruleset.zig` starter, the direct `zigux/tests/phase13_landlock_ruleset.zig` replay, and the direct `zigux/tests/phase13_landlock_ruleset_manifest.json` companion; if checker-side reminders such as `scripts/zigux/check-phase13-landlock-ruleset-packet.py` or the older shared `zigux/tests/phase13_build.zig` route cannot be materialized on current `master`, keep those absences anchored to repo reality instead of assumed current-`master` evidence.
- `security/landlock/syscalls.c` through the shipped `Documentation/zigux/phase13-landlock-syscalls-governance.md`, the shipped `Documentation/zigux/phase13-landlock-syscalls-slice.md`, the shipped `Documentation/zigux/phase13-landlock-syscalls-survey.md` note, the shipped `security/landlock/syscalls.zig` starter, the direct `zigux/tests/phase13_landlock_syscalls.zig` replay, the direct `zigux/tests/phase13_landlock_syscalls_reviewability.zig` companion, and the direct `zigux/tests/phase13_landlock_syscalls_manifest.json` packet; if the older shared `zigux/tests/phase13_build.zig` route cannot be materialized on current `master`, keep that absence anchored to repo reality instead of assumed current-`master` evidence.

Adjacent notifier evidence stays in scope for release-surface truthfulness, but it is still adjacent evidence rather than a fifth shared-helper anchor.

Current `master` anchors that adjacent packet through:

- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`

Current `master` still does not materialize `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, `make -C zigux phase13-validate`, blocked convenience route `make -C zigux phase13`, or `Documentation/zigux/phase13-notifier-list-survey.md`, so keep those paths recorded as adjacent repo-reality gaps rather than current anchors.

If direct notifier companions such as `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, or `zigux/helpers/hlist_view.zig` cannot be materialized on current `master`, keep them recorded as adjacent repo-reality gaps instead of listing them as independently shipped review evidence.

## Owner Split

Keep the current owner map explicit:

- `libfs` helper parity keeps the shipped helper packet explicit through manifest-backed repo packet id `P13-L04`, while scheduled coordination currently splits that same packet across helper-local governance alias `P13-Y01` and verification-only alias `P13-L03`: `fs/libfs.zig`, `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`. Treat `P13-Y01` as the helper-local governance lane for that same `libfs` packet, treat `P13-L03` as its verification alias, and do not let either alias act like a second helper-growth or shared-reminder lane.
- `devres` helper parity keeps the shipped manifest-backed packet explicit through repo packet id `P13-L01`, but scheduled coordination is now split across `P13-L05` packet-truthfulness work, `P13-L06` bounded resource-lifetime helper follow-through, and verification-only alias `P13-L07`: `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_manifest.json`. Keep missing checker-side names such as `scripts/zigux/check-phase13-devres-packet-alignment.py` and the older `scripts/zigux/check-phase13-devres-packet.py` recorded as repo-reality gaps rather than shipped packet evidence. Treat `P13-L01` as the repo packet id, `P13-L05` as the survey-reviewability-manifest truthfulness lane for the current boundary-evidence plus narrow DMA or scatterlist boundary, `P13-L06` as the parked cleanup-side arch-memtype helper increment plus direct replay lane, and `P13-L07` as the verification-only alias for the already-published non-posted wrapper packet instead of letting those four labels act like separate helper families.
- `landlock/ruleset` helper parity keeps the shipped manifest-backed packet explicit through current repo packet id `P13-Y03`, while scheduled coordination currently uses verification-only alias `P13-L11`: `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `security/landlock/ruleset.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, and `zigux/tests/phase13_landlock_ruleset_manifest.json`. Keep `scripts/zigux/check-phase13-landlock-ruleset-packet.py` recorded as a repo-reality gap rather than shipped packet evidence. Treat `P13-Y03` as the helper-local ruleset packet id on current `master`, treat `P13-L11` as its verification alias, and do not let either label act like a second ruleset implementation or shared-reminder lane.
- `landlock/syscalls` helper truthfulness keeps the shipped manifest-backed packet explicit through repo packet id `P13-L17`, but scheduled coordination is currently split across `P13-Y04` governance-note follow-through and `P13-L13` survey-companion follow-through: `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`. Treat `P13-L17` as the underlying repo packet id, `P13-Y04` as governance-note truthfulness, and `P13-L13` as survey-companion follow-through instead of treating those labels as three competing syscall owners.
- Shared contributor-surface truthfulness routes through `P13-Y08` only: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `scripts/zigux/check-phase13-shared-summary-surfaces.py` recorded as the current repo-reality gap for that lane until `master` materializes it again. This broad reminder lane must not absorb helper-local verification, helper increments, or packet-local note repairs.
- Shared owner-map maintenance for this note itself routes through `P13-Y05` only: `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`. Keep that sequencing lane narrower than the broader contributor-reminder lane `P13-Y08`, and do not use it to reopen helper-local packets unless the owner map itself cannot be made truthful without a directly coupled same-note reference.
- Adjacent notifier evidence owns `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig`, `include/zigux/abi.h`, and `drivers/tty/hvc/hvc_console.h`. Keep `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, `make -C zigux phase13-validate`, blocked convenience route `make -C zigux phase13`, `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, and `zigux/helpers/hlist_view.zig` recorded as adjacent repo-reality gaps until current `master` materializes them again rather than listing those paths as shipped current-`master` evidence.

## Shared Packet Surfaces

When a real Phase 13 change lands, keep these shared surfaces aligned:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Treat the shared documentation-and-reminder packet as the current replay handle, keep `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/Makefile`, `make -C zigux phase13-validate`, blocked convenience route `make -C zigux phase13`, and `zigux/tests/phase13_build.zig` recorded as repo-reality gaps until current `master` materializes them again, and avoid presenting the direct build path or the older Makefile-backed routes as independently shipped evidence before readback confirms they returned.

If the direct `zigux/tests/phase13_build.zig` build route still cannot be materialized on current `master`, keep that build path and the older validator-first helper names such as `scripts/zigux/validate-phase13-release.py` recorded as repo-reality gaps instead of presenting them as shipped shared review evidence.

## Sequencing Rules

Use this note to keep the bounded work order honest:

1. Prefer one helper lane at a time instead of batching `libfs`, `devres`, `landlock`, and notifier evidence into one mixed change.
2. Treat adjacent notifier evidence as release-surface support for the shared packet, not as an extra shared replay step.
3. Keep the shared review wording anchored to `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, and `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`; keep `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/Makefile`, `make -C zigux phase13-validate`, blocked convenience route `make -C zigux phase13`, `zigux/tests/phase13_build.zig`, and the older notifier-side or validator-first helper names recorded as repo-reality gaps until current `master` materializes them again, and if a direct shared build route can be materialized later, pair it with fresh readback instead of presenting it as independently shipped evidence before that reread happens.
4. If a broad reminder surface changes, keep the owner split visible instead of replacing it with a generic "Phase 13 helper packet" summary.
5. Do not imply a closed Phase 13 tranche or a fifth helper anchor while the packet still depends on bounded adjacent notifier evidence.
6. Keep the repo packet ids and the scheduled aliases distinct: `P13-L04` with helper-governance alias `P13-Y01` and verification alias `P13-L03` for `libfs`, `P13-L01` with scheduled follow-through split `P13-L05` plus `P13-L06` and verification alias `P13-L07` for `devres`, `P13-Y03` with verification alias `P13-L11` for `landlock/ruleset`, `P13-L17` with scheduled follow-through split `P13-Y04` plus `P13-L13` for `landlock/syscalls`, `P13-Y08` for shared contributor reminders, and `P13-Y05` for this shared owner-map note.
7. Do not let `P13-Y01` or verification alias `P13-L03` stand in for the underlying `libfs` repo packet `P13-L04` or absorb shared-reminder work, do not let `P13-Y03` or verification alias `P13-L11` stand in for the neighboring syscall packet or broader shared-reminder work, do not let `P13-L05`, `P13-L06`, and verification alias `P13-L07` reopen each other without a directly coupled truthfulness, replay, or verification reason, do not let `P13-Y04` and `P13-L13` stand in for the underlying repo packet id `P13-L17`, and do not let `P13-Y05` or `P13-Y08` replace helper-local ownership.

## Non-Goals

This note does not widen Phase 13 into:

- a direct filesystem parity claim beyond the shipped `libfs` packet
- a separate shared replay step for notifier evidence
- broader security policy ownership outside the landed Landlock ruleset and syscall notes
- a claim that the Phase 13 packet is closed or frozen