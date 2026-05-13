# Phase 13 Shared Helper Lane Sequencing

This note keeps the active Phase 13 shared-subsystems packet split into bounded owner lanes so contributor-facing guidance does not collapse `libfs`, `devres`, `landlock`, and adjacent notifier evidence into one noisy bucket.

Current Phase 13 repo reality now spans two naming layers: some shipped manifests and packet-local notes still carry the older repo packet ids on `master`, while scheduled coordination uses newer bounded aliases to keep verification-only, helper-local, and shared reminder work from colliding. This note exists to keep those two layers readable without turning either one into a duplicate owner map.

## Scope

Use this note when a Phase 13 change touches any part of the shipped shared-helper release packet:
- `fs/libfs.c` through the shipped `fs/libfs.zig`, `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`; if direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_libfs_addressability.zig`, or the older shared `zigux/tests/phase13_build.zig` route cannot be materialized on current `master`, keep that absence anchored to repo reality instead of assumed current-`master` evidence
- `lib/devres.c` through the shipped `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py`, while older broader `devres` reviewability wording and the absent `zigux/tests/phase13_devres_boundary_evidence.zig` companion should stay anchored to repo reality instead of assumed current-master evidence
- `security/landlock/ruleset.c` through `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, the shipped `Documentation/zigux/phase13-landlock-ruleset-slice.md`, the shipped `Documentation/zigux/phase13-landlock-ruleset-survey.md` note, the shipped `security/landlock/ruleset.zig` starter, the direct `zigux/tests/phase13_landlock_ruleset.zig` replay, the direct `zigux/tests/phase13_landlock_ruleset_manifest.json` companion, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py`; if the older shared `zigux/tests/phase13_build.zig` route cannot be materialized on current `master`, keep that absence anchored to repo reality instead of assumed current-master evidence
- `security/landlock/syscalls.c` through the shipped `Documentation/zigux/phase13-landlock-syscalls-governance.md`, the shipped `Documentation/zigux/phase13-landlock-syscalls-slice.md`, the shipped `Documentation/zigux/phase13-landlock-syscalls-survey.md` note, the shipped `security/landlock/syscalls.zig` starter, the direct `zigux/tests/phase13_landlock_syscalls.zig` replay, the direct `zigux/tests/phase13_landlock_syscalls_reviewability.zig` companion, and the direct `zigux/tests/phase13_landlock_syscalls_manifest.json` packet; if the older shared `zigux/tests/phase13_build.zig` route cannot be materialized on current `master`, keep that absence anchored to repo reality instead of assumed current-master evidence

Adjacent notifier evidence stays in scope for release-surface truthfulness, but it is still adjacent evidence rather than a fifth shared-helper anchor. Current `master` anchors that adjacent packet through:
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

If direct notifier companions such as `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, or `zigux/helpers/hlist_view.zig` cannot be materialized on current `master`, keep them recorded as adjacent repo-reality gaps instead of listing them here as independently shipped review evidence.

## Owner Split

Keep the current owner map explicit:
- `libfs` helper parity keeps the shipped helper packet explicit through manifest-backed repo packet id `P13-L04`, while scheduled coordination currently uses verification-only alias `P13-L03` for exact-content rereads of the already-landed packet: `fs/libfs.zig`, `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`; treat `P13-L03` as a verification alias for that same `libfs` packet rather than as a second helper-growth or shared-reminder lane
- `devres` helper parity keeps the shipped manifest-backed packet explicit through repo packet id `P13-L01`, but scheduled coordination is now split across `P13-L05` packet-truthfulness work and `P13-L06` bounded resource-lifetime helper follow-through: `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py`; treat `P13-L01` as the repo packet id, `P13-L05` as the survey-reviewability-manifest truthfulness lane for the current narrow DMA or scatterlist boundary, and `P13-L06` as the parked cleanup-side arch-memtype helper increment plus direct replay lane instead of letting those three labels act like separate helper families
- `landlock/ruleset` helper parity keeps the shipped manifest-backed packet explicit through repo packet id `P13-L09`, while scheduled coordination currently uses verification-only alias `P13-L11`: `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `security/landlock/ruleset.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py`; treat `P13-L11` as a verification alias for the same ruleset packet rather than as a second ruleset implementation lane
- `landlock/syscalls` helper truthfulness keeps the shipped manifest-backed packet explicit through repo packet id `P13-L17`, but scheduled coordination is currently split across `P13-Y04` governance-note follow-through and `P13-L13` survey-companion follow-through: `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`; treat `P13-L17` as the underlying repo packet id, `P13-Y04` as governance-note truthfulness, and `P13-L13` as survey-companion follow-through instead of treating those labels as three competing syscall owners
- shared contributor-surface truthfulness routes through `P13-Y08` only: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`; this broad reminder lane must not absorb helper-local verification, helper increments, or packet-local note repairs
- shared owner-map maintenance for this note itself routes through `P13-Y06` only: `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`; keep that sequencing lane narrower than the broader contributor-reminder lane `P13-Y08`, and do not use it to reopen helper-local packets unless the owner map itself cannot be made truthful without a directly coupled same-note reference
- adjacent notifier evidence owns `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig`, `include/zigux/abi.h`, `drivers/tty/hvc/hvc_console.h`, `zigux/Makefile`, `make -C zigux phase13-validate`, and `make -C zigux phase13`; if direct notifier companions such as `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, or `zigux/helpers/hlist_view.zig` cannot be materialized on current `master`, keep that absence recorded as an adjacent repo-reality gap instead of listing those paths here as shipped current-master evidence, and keep the landed nonincreasing-priority signal explicit through `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/validate-phase13-release.py`, `make -C zigux phase13-validate`, and `make -C zigux phase13`

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

Treat `make -C zigux phase13-validate` as the stable shared replay handle. If `scripts/zigux/validate-phase13-release.py` or the direct `zigux/tests/phase13_build.zig` build route cannot be materialized on current `master`, record those direct paths as repo reality instead of listing them here as independently shipped evidence.

## Sequencing Rules

Use this note to keep the bounded work order honest:
1. Prefer one helper lane at a time instead of batching `libfs`, `devres`, `landlock`, and notifier evidence into one mixed change.
2. Treat adjacent notifier evidence as release-surface support for the shared packet, not as an extra shared replay step.
3. Keep the validator-first route explicit through `make -C zigux phase13-validate`, then `make -C zigux phase13`; if a direct `zigux/tests/phase13_build.zig` build route can be materialized later, pair it with that stable make route instead of presenting the direct path as independently shipped evidence before readback confirms it.
4. If a broad reminder surface changes, keep the owner split visible instead of replacing it with a generic "Phase 13 helper packet" summary.
5. Do not imply a closed Phase 13 tranche or a fifth helper anchor while the packet still depends on bounded adjacent notifier evidence.
6. Keep the repo packet ids and the scheduled aliases distinct: `P13-L04` with verification alias `P13-L03` for `libfs`, `P13-L01` with scheduled follow-through split `P13-L05` plus `P13-L06` for `devres`, `P13-L09` with verification alias `P13-L11` for `landlock/ruleset`, `P13-L17` with scheduled follow-through split `P13-Y04` plus `P13-L13` for `landlock/syscalls`, `P13-Y08` for shared contributor reminders, and `P13-Y06` for this shared owner-map note.
7. Do not let verification aliases `P13-L03` and `P13-L11` absorb new helper growth, do not let `P13-L05` and `P13-L06` reopen each other without a directly coupled manifest or replay reason, do not let `P13-Y04` and `P13-L13` stand in for the underlying repo packet id `P13-L17`, and do not let `P13-Y06` or `P13-Y08` replace helper-local ownership.

## Non-Goals

This note does not widen Phase 13 into:
- a direct filesystem parity claim beyond the shipped `libfs` packet
- a separate shared replay step for notifier evidence
- broader security policy ownership outside the landed Landlock ruleset and syscall notes
- a claim that the Phase 13 packet is closed or frozen
