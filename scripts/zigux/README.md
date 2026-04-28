# scripts/zigux

This directory holds Zigux-specific bootstrap and validation helpers.

Initial responsibilities
- Zig toolchain policy checks
- bootstrap validation
- committed parity fixture generation and checking
- future ABI/layout guards
- artifact diff helpers for host-side tools

Current bootstrap helpers
- `artifact_diff.py`
- `check-zig-toolchain.py`
- `validate-bootstrap.py`
- `install-zig.py`
- `validate-phase1.py`
- `check-phase1-bench.py`
- `validate-phase1-closure.py`
- `validate-phase2.py`
- `validate-phase2-closure.py`
- `validate-phase3.py`
- `validate-phase4.py`
- `validate-phase6.py`
- `validate-phase8.py`
- `validate-phase9.py`
- `validate-phase10-closure.py`
- `validate-phase11.py`
- `check-phase12-build-inventory.py`
- `validate-phase12.py`
- `validate-phase13-release.py`
- `validate-phase14.py`
- `validate-phase3-roadmap-gap-survey.py`
- `run-phase3-checks.py`
- `phase3_catalog.py`
- `check-phase1-parity.py`
- `check-fixdep-diff.py`
- `check-genksyms-bridge.py`
- `check-genksyms-crc-diff.py`
- `check-kconfig-bridge.py`
- `check-phase2-cross.py`
- `check-mk-elfconfig-diff.py`

Zig toolchain gate
- `check-zig-toolchain.py` verifies that the selected Zig binary exists and satisfies the configured minimum version.
- `check-zig-toolchain.py --self-test` runs built-in parser and version-ordering coverage without needing a local Zig install.

Phase 2 flow
- `artifact_diff.py --self-test` exercises the shared text, JSON, SHA-256, and missing-file comparison paths before the bounded Phase 2 artifact lanes run.
- `validate-phase2.py` checks that the bounded Phase 2 helper inventory, fixture set, workflow wiring, and docs markers stay in sync before the parity lanes run.
- `validate-phase2-closure.py` confirms the closed Phase 2 tranche still matches the workflow, the closure docs, and the Phase 2 manifests.
- `check-fixdep-diff.py` compares the bounded `fixdep.zig` output against the committed fixture set, including the multi-target, escaped-whitespace, comment-only no-target, and missing-dependency failure artifacts under `zigux/tests/fixtures/fixdep/`, and now also fails if any success-path fixdep case starts emitting unexpected stderr noise.
- `check-genksyms-bridge.py` exercises the bounded `genksyms.zig` bridge parity lane.
- `check-genksyms-crc-diff.py` checks the bounded `genksyms_crc.zig` artifact lane and now proves repeat-run JSON determinism for both the bounded C harness and Zig tool before fixture comparison.
- `check-kconfig-bridge.py` covers the bounded `kconfig/conf_bridge.zig` and `kconfig/confdata_bridge.zig` bridge lanes.
- `check-phase2-cross.py` runs the bounded Phase 2 cross-target compile checks.
- `check-mk-elfconfig-diff.py` covers the bounded `mk_elfconfig.zig` artifact parity lane.

Phase 3 flow
- `validate-phase3-roadmap-gap-survey.py` checks that `Documentation/zigux/phase3-roadmap-gap-survey.md` stays aligned with the live repo-backed Phase 3 substrate, the published README note, the current export shim and current `zigux/uapi/version.zig` boundary, and the current roadmap-backed `rbtree` gap.
- `validate-phase3-roadmap-gap-survey.py --self-test` exercises the survey-marker and README-hook checks without needing the full repo tree.
- `phase3_catalog.py` discovers Phase 3 slices from the docs, dump entrypoints, and fixture manifests instead of maintaining one giant hard-coded inventory, and now carries per-slice metadata such as display descriptions, build-step overrides, and the current `PHASE3_INTEROP_GATE` mode recorded in each slice doc.
- `phase3_catalog.py --self-test` exercises isolated slug discovery, manifest selection, and interop-gate classification across docs, dumps, and fixture candidates.
- `phase3_catalog.py --legacy-wrapper-docs` lists the discovered slice docs that still point at legacy `check-phase3-*.py` compatibility wrappers.
- `phase3_catalog.py --rewrite-shared-runner-docs` rewrites those legacy per-slice doc commands to the shared `run-phase3-checks.py --slug ...` form so wrapper-reference cleanup is scripted instead of manual.
- `phase3_catalog.py --legacy-wrapper-references` lists remaining discovered Phase 3 wrapper mentions in non-slice documentation, which keeps stray policy-doc references auditable now that the manifest cleanup is complete.
- `phase3_catalog.py --rewrite-legacy-wrapper-references` rewrites those non-slice documentation references to the shared runner form, leaving `artifact-diff.md` and similar policy docs on the same scripted cleanup path as the slice records.
- `phase3_catalog.py --rewrite-artifact-diff-phase3-section` regenerates the detailed `Documentation/zigux/artifact-diff.md` Phase 3 policy block from the discovered slice catalog.
- `phase3_catalog.py --audit-doc-sync` reports stale non-slice wrapper references plus a stale `artifact-diff.md` Phase 3 block, and bootstrap now runs it so documentation drift fails fast.
- `phase3_catalog.py --suggest-slug-renames` turns the slug sanity audit into concrete cleanup candidates by pairing each repetitively overgrown slug with the longest clean prefix already present in the catalog, while skipping slugs whose only issue is crossing the token-count threshold and suppressing prefix matches whose normalized fixture manifest or `expected.json` schema does not actually line up with the shorter slice.
- `phase3_catalog.py --suggest-slug-rename-paths` lists the core slice files and directories that each safe rename would retire.
- `phase3_catalog.py --suggest-slug-merge-prep` expands those safe rename candidates into a cleanup checklist by listing the retireable long-slug artifacts and the extra docs, workflow, script, or `zigux/tests/build.zig` lines that still mention the long slug elsewhere in the tree; `--suggest-slug-merge-plans` remains accepted as a compatibility alias.
- `phase3_check_lib.py` holds the shared Phase 3 parity execution logic used by every wrapper and the shared runner.

Phase 4 flow
- `artifact_diff.py --self-test` now runs as part of `make -C zigux phase4-validate` so the shared text, JSON, SHA-256, and missing-file comparison paths stay live before the rollback-readiness checks run.
- `validate-phase4.py` checks that the bounded Phase 4 differential gates, that shared artifact-diff self-test, their shared `zigux/tests/phase4_build.zig` entrypoint, and the directly coupled documentation and workflow markers stay aligned.
- `zigux/tests/phase4_build.zig` runs the live `runtime_atomic64_diff.zig` and `bitmap_diff.zig` rollback-readiness gates together instead of letting one of them drift out of the regular validation path.
- `Documentation/zigux/phase4-validation-matrix.md` keeps the current rollback owners, threshold posture, exact workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, the shared `phase4-runtime-atomic64-diff-tests` plus `phase4-bitmap-diff-tests` replay anchors, and the reversible-delivery evidence that ties each shipped Phase 4 gate back to its current C anchor if the shared entrypoint has to drop that Zig gate.

Phase 6 flow
- `validate-phase6.py` checks that the bounded Phase 6 leaf-helper bundle still keeps `zigux/tests/phase6_build.zig`, `make -C zigux phase6-validate`, the bootstrap workflow, and the published base64, bsearch, checksum, and hexdump slice notes aligned.
- `make -C zigux phase6-checksum-perf` replays the checksum-specific perf sanity harness so the current math-sensitive helper lane records representative per-call and per-byte cost without claiming a cross-machine threshold yet.
- `make -C zigux phase6-hexdump-perf` replays the hexdump-specific perf sanity harness so the current formatter-sensitive helper lane records representative dump cost for both plain and ASCII review paths without claiming a cross-machine threshold.
- the same Phase 6 gate now machine-checks that the current hexdump lane still carries its truncation and empty-buffer required-length evidence through `zigux/tests/phase6_hexdump.zig` and `Documentation/zigux/phase6-hexdump-slice.md`.

Phase 8 flow
- `validate-phase8.py` checks that the bounded Phase 8 tooling bundle still keeps `zigux/tests/phase8_build.zig`, `make -C zigux phase8-validate`, the bootstrap workflow, and the published userspace-adjacent slice notes aligned.
- the same Phase 8 gate now records the already-landed libbpf `cpu_mask.zig`, `logging.zig`, `pin_path.zig`, and `type_names.zig` bridge slices directly through `Documentation/zigux/phase8-libbpf-segment-survey.md` and the shared control-plane notes instead of leaving part of that helper bundle implicit in `phase8_build.zig` alone.

Phase 9 flow
- `validate-phase9.py` checks that the bounded Phase 9 runtime governance bundle still keeps `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, the shared README notes, the bootstrap workflow, `make -C zigux phase9-validate`, and `zigux/tests/phase9_build.zig` aligned.
- the same Phase 9 gate keeps the current loader-handoff release discipline explicit instead of leaving allocator ownership, `requires_runtime_substrate`, and the still-blocked command or environment control surface implied only by the survey note or checklist.
- the same validator now also keeps the manifest-backed catalog and ownership map explicit, so the survey note, review checklist, shared request contract, sample-side loader plans, and shared `phase9_build.zig` replay path stay assigned to one reviewable evidence packet.

Phase 10 flow
- `validate-phase10-closure.py` checks that the bounded Phase 10 virtio lab bundle still keeps `Documentation/zigux/phase10-closure-evidence.md`, the three manifest-backed survey records, the shared bootstrap workflow, `make -C zigux phase10-validate`, and `zigux/tests/phase10_build.zig` aligned.
- the same Phase 10 gate keeps the current virtio tranche honest about its blocker posture by requiring the published evidence bundle to say explicitly that `drivers/virtio/virtio_mmio.zig` remains intentionally absent while the MMIO work stays survey-backed.

Phase 11 flow
- `validate-phase11.py` checks that the bounded Phase 11 simple-driver bundle still keeps `make -C zigux phase11-validate`, the shared workflow path, `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_hvc_console_manifest.json`, and `zigux/tests/phase11_uapi_header_parity_manifest.json` aligned around the same watchdog plus hvc starter tranche.
- the same Phase 11 gate now also checks that each dedicated Phase 11 survey test stays pinned to its manifest's exact `surveyed_commit` and the same starter, ready-next, and blocked status totals before the slower Zig replay path runs.
- the same Phase 11 gate keeps the manifest bundle honest about its current follow-up posture by requiring the committed `phase11_build_inventory.json` fixture to match the exact shared `phase11_build.zig` test inventory and to keep `zigux/tests/phase11_hvc_console_survey.zig` as a dedicated survey replay while the shared path continues to cover the landed starter tests plus the watchdog and shared-header survey gates.
- the same Phase 11 gate now also keeps the dedicated hvc_console survey note and validation matrix aligned with the manifest-backed survey packet so the fast tooling path fails if those review notes drift away from the current commit pin, the split shared-versus-dedicated replay boundary, or the next bounded khvcd polling-contract follow-up.
- the same Phase 11 gate now also proves that the hvc validation matrix still records the exact shared-versus-dedicated replay commands and observed outcome lines for the current starter tranche, including the shared `Build Summary: 17/17 steps succeeded; 37/37 tests passed`, the included `phase11-hvc-console-tests` artifact line, and the separate dedicated survey `2/2 ... OK` result.

Phase 12 flow
- `check-phase12-build-inventory.py` regenerates the committed `zigux/tests/fixtures/phase12_build_inventory.json` build-derived fields from `zigux/tests/phase12_build.zig` and compares the result through `artifact_diff.py` so the shared replay inventory stays reproducible instead of living only in manually edited fixture text.
- `validate-phase12.py` checks that the bounded Phase 12 degraded-workflow bundle still keeps `make -C zigux phase12-validate`, the shared workflow path, `zigux/tests/phase12_build.zig`, `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_nvme_pci_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_libbpf_manifest.json` aligned around the same complex-driver and heavy-helper tranche.
- the same Phase 12 gate also checks that each dedicated Phase 12 survey test stays pinned to its manifest's exact `surveyed_commit` and the same starter, DMA-blocked, and object-model-blocked status totals before the slower Zig replay path runs.
- the same fast validator now also keeps the four Phase 12 survey notes pinned to each manifest's exact `surveyed_commit`, Linux anchor, and shared `make -C zigux phase12` replay contract instead of leaving that survey-evidence packet solely to the slower Zig test pass.
- the same validator keeps the degraded fallback contract explicit by requiring the workflow, README notes, review checklist, `zigux/Makefile`, and `zigux/tests/phase12_virtio_scsi_survey.zig` to agree that `make -C zigux phase12` runs the validator before the shared `phase12_build.zig` replay.
- the same validator now also snapshots the shared build inventory snapshot and expected shared replay summary in `zigux/tests/fixtures/phase12_build_inventory.json` so the exact replay shape and current `Build Summary: 17/17 steps succeeded; 34/34 tests passed` expectation stay committed instead of living only in ad hoc run logs.

Phase 13 flow
- `validate-phase13-release.py` checks that the bounded Phase 13 release-discipline packet still keeps `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, the shared workflow path, `make -C zigux phase13-validate`, and `zigux/tests/phase13_build.zig` aligned around the same active shared-helper tranche.
- the same Phase 13 gate keeps the release evidence explicit instead of leaving the validator-helper contract implicit by requiring the docs packet and helper index to say that Phase 13 is still active, `make -C zigux phase13` routes through the validator before the shared replay, and `lib/devres.c` remains the only roadmap anchor without a manifest-backed survey packet.

Phase 14 flow
- `validate-phase14.py` checks that the bounded Phase 14 shared smoke packet still keeps `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `scripts/zigux/README.md`, the shared workflow path, `make -C zigux phase14-validate`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/tests/phase14_build.zig` aligned around the same workqueue, skbuff, ring-buffer, and RCU stay-in-C boundary bundle.
- the same Phase 14 gate now also checks the focused smoke-shard replay contract, so `make -C zigux phase14-smoke`, the dedicated `phase14-smoke` build step, and the workflow smoke-shard job cannot drift away from the shared smoke manifest or survey note.
- the same Phase 14 gate keeps the productized smoke evidence explicit instead of leaving it to the slower Zig replay alone by requiring the docs packet and helper index to say that the shared Phase 14 smoke packet stays active, `make -C zigux phase14` routes through the validator before the shared replay, `make -C zigux phase14-smoke` remains the focused shard entrypoint, and the four anchor-local manifests plus survey notes still carry the same ready-next versus blocked posture under the stay-in-C boundary.
