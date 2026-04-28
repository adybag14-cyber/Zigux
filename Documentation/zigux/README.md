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

Phase 2 notes
- `python3 scripts/zigux/artifact_diff.py --self-test` is now part of the published Phase 2 closure path through `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/artifact-diff.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`, so shared comparison drift fails before the bounded host-tool parity lanes run.

Phase 3 notes
- `Documentation/zigux/phase3-roadmap-gap-survey.md` now maps the original Phase 3 roadmap anchors `rust/exports.c`, `lib/bitmap.c`, `lib/rbtree.c`, and `lib/cpumask.c` to the live ABI substrate, the current export shim and current `zigux/uapi/version.zig` boundary, and the current interop slices, so reviewers can see in one place which anchors are already covered, which adjacent helpers are real repo state, and which roadmap-backed gap is still open.
- `scripts/zigux/validate-phase3-roadmap-gap-survey.py`, `make -C zigux phase3-validate`, and the bootstrap workflow now keep that survey note explicit, including the narrow export shim and current `zigux/uapi/version.zig` boundary, the current `rbtree` gap, and the note that the longer `chrdev_*` planning ladder should not be mistaken for roadmap closure.
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md` now records the narrower export-shim and UAPI boundary reality inside the same Phase 3 substrate: `zigux/kernel/export_shim.zig` remains a narrow explicit-status helper with a shared boundary-header path, `zigux/uapi/` remains bounded to `zigux/uapi/version.zig`, and the broader curated UAPI surface is still intentionally deferred.
- `scripts/zigux/validate-phase3-export-uapi-survey.py` and `make -C zigux phase3-validate` now keep that dedicated export-shim and UAPI boundary survey packet explicit alongside the broader roadmap-gap note.
- `Documentation/zigux/phase3-abi-slice.md` now also records the published focused policy-and-unsafe substrate gate around `zigux/helpers/layout_assert.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, and `zigux/unsafe/narrow.zig`, including the explicit `raw_pointer_bridge` unsafe scope plus the dedicated `zigux/tests/phase3_policy_unsafe.zig` replay path.
- `scripts/zigux/validate-phase3.py`, `zigux/tests/fixtures/phase3_abi_manifest.json`, and `make -C zigux phase3-validate` now keep that focused Phase 3 policy-and-unsafe packet explicit instead of leaving the helper family implied only by the broader ABI substrate bundle.

Phase 5 notes
- `Documentation/zigux/phase5-kfifo-sample-survey.md` now records the landed `samples/zigux/bytestream_fifo.zig` reference sample, its exact replay, non-destructive snapshot, preview-truncation, fixed embedded backing, and lifecycle-boundary checks, and the remaining non-goals around procfs, user-copy, locking, and module registration parity.
- the same Phase 5 survey note now doubles as the sample-backed contributor guide for the landed bytestream FIFO slice by naming the descriptor, manifest, and shared build-entrypoint prompts that reviewers should keep in sync.
- `Documentation/zigux/phase5-kobject-sample-survey.md` now records the landed `samples/zigux/kobject_example.zig` reference sample, its exact registration, Linux `foo`/`baz`/`bar` attribute-order, and attribute-roundtrip checks, and the remaining non-goals around sysfs creation, `kernel_kobj`, uevents, and module registration.
- the same kobject survey note now doubles as the sample-backed contributor guide for the landed kobject slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync.
- `Documentation/zigux/phase5-kretprobe-sample-survey.md` now records the landed `samples/zigux/kretprobe_example.zig` reference sample, its exact skip, private-data-shape, return-value, duration, fixed `maxactive`, and `nmissed` replay checks, and the remaining non-goals around probe registration, `pt_regs`, and module wiring.
- the same kretprobe survey note now doubles as the sample-backed contributor guide for the landed non-runtime `kretprobe` slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync while staying distinct from the separate Phase 9 runtime starter.
- `Documentation/zigux/phase5-trace-events-sample-survey.md` now records the landed `samples/zigux/trace_events_sample.zig` reference sample, its exact payload, string-selection, main-path and callback-path iteration cues, formatted-message, event-family-count, vararg-payload, relative-location, callback-path, and callback-registration replay checks, and the remaining non-goals around tracepoint macros, kernel scheduling, and module wiring.
- the same trace-events survey note now doubles as the sample-backed contributor guide for the landed non-runtime `trace-events` slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync while staying distinct from the separate Phase 9 runtime pilot tranche.
- the Phase 5 notes now carry all four roadmap sample anchors as bounded `samples/zigux/` reference readings, while still keeping the separate Phase 9 runtime pilot tranche explicit for the same `trace-events` and `kretprobe` families.

Phase 4 notes
- `make -C zigux phase4-validate` runs `python3 scripts/zigux/artifact_diff.py --self-test` plus `python3 scripts/zigux/validate-phase4.py` before the shared Phase 4 Zig diff gates.
- `python3 scripts/zigux/check-artifact-diff-contract.py` now gives the same Phase 4 validation path one external replay of the actual `artifact_diff.py` CLI contract, covering one stable pass case plus one missing-file failure shape so the outward `ARTIFACT_DIFF=...` lines do not live only inside the helper's built-in self-test.
- `python3 scripts/zigux/validate-phase4.py` keeps the live `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, and `zigux/tests/bitmap_diff.zig` rollback gates plus survey evidence, the shared `zigux/tests/phase4_build.zig` entrypoint, the bootstrap workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, and the directly coupled Phase 4 notes aligned.
- `Documentation/zigux/phase4-validation-matrix.md` records the current Phase 4 rollback owners, threshold posture, the shared `phase4-runtime-atomic64-diff-tests`, `phase4-runtime-atomic64-diff-survey-tests`, and `phase4-bitmap-diff-tests` build entries plus the dedicated `phase4-runtime-atomic64-diff` and `phase4-bitmap-diff` local replay steps that keep each shipped gate measurable, and the reversible-delivery evidence that ties each shipped gate back to its current C anchor if the shared Phase 4 entrypoint has to drop that Zig gate.

Phase 6 notes
- `Documentation/zigux/phase6-helper-parity-catalog.md`
- `Documentation/zigux/phase6-base64-slice.md`
- `Documentation/zigux/phase6-bsearch-slice.md`
- `Documentation/zigux/phase6-checksum-slice.md`
- `Documentation/zigux/phase6-hexdump-slice.md`
- `python3 scripts/zigux/validate-phase6.py` and `make -C zigux phase6-validate` now fail fast if the shared Phase 6 leaf-helper bundle drifts out of sync across `Documentation/zigux/phase6-helper-parity-catalog.md`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, the bootstrap workflow, and the published slice notes.
- `zigux/tests/phase6_build.zig` and `make -C zigux phase6` now gate the current base64, bsearch, checksum, and hexdump helper bundle together, so new helper slices should only land when that shared lane stays green as one unit.
- `Documentation/zigux/phase6-helper-parity-catalog.md` is the shared inventory note for the current roadmap-backed leaf-helper packet and should move together with any helper, fixture, perf, or slice-note ownership change.
- `make -C zigux phase6-base64-perf` now replays the bounded base64 perf sanity harness so the current leaf-helper lane keeps its representative encode and decode timing step visible while the review packet decides whether the shared Zig fixture surface is enough to park `lib/base64.zig`.
- `python3 scripts/zigux/check-phase6-base64-c-parity.py` is the current external C-vs-Zig spot check for the bounded base64 slice and should move together with the same review packet when portability-sensitive drift is under review.
- `python3 scripts/zigux/check-phase6-bsearch-c-parity.py` is the current external C-vs-Zig spot check for the bounded bsearch slice and should move together with `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, and the same review packet when portability-sensitive drift is under review.
- `make -C zigux phase6-checksum-perf` now replays a checksum-specific perf sanity harness so the current math-sensitive helper lane records representative per-call and per-byte cost before Phase 6 claims it is ready to park.
- `make -C zigux phase6-hexdump-perf` now replays a hexdump-specific perf sanity harness so the current formatter-sensitive helper lane records representative dump cost for plain and ASCII paths before Phase 6 treats that slice as fully parked.
- the current bounded base64 decision is no longer whether reverse-map parity is wired at all; it is whether the current reverse-map coverage plus the perf-sanity replay is sufficient to leave the helper parked or whether one small external C-vs-Zig fixture is still worth carrying.
- if the current spot check stops being worth the maintenance cost, replace it with a generated fixture flow rather than widening the lane into a broader new helper family.
- the current bounded Phase 6 decision is no longer whether the hexdump fixture wiring works in CI; it is whether the current bsearch, checksum, and hexdump parity evidence is sufficient to park the leaf-helper lane or whether one more tiny external fixture is still worth carrying.

Phase 7 notes
- `Documentation/zigux/phase7-string-helpers-slice.md`
- `Documentation/zigux/phase7-cmdline-slice.md`
- `Documentation/zigux/phase7-argv-split-slice.md`
- `Documentation/zigux/phase7-rbtree-slice.md`
- `python3 scripts/zigux/validate-phase7.py` and `make -C zigux phase7-validate` now fail fast if the shared Phase 7 runtime-helper bundle drifts out of sync across `zigux/tests/phase7_build.zig`, `zigux/Makefile`, the bootstrap workflow, the shared README notes, the four published slice docs, and the current external `rbtree` parity hook.
- `make -C zigux phase7-test` is the local wrapper for the shared `zigux/tests/phase7_build.zig` replay, and the workflow intentionally drives that same build file directly through `zig build test --build-file zigux/tests/phase7_build.zig --summary all` so CI keeps per-step summaries without changing the exercised Phase 7 helper bundle.
- `zigux/tests/phase7_build.zig` and `make -C zigux phase7` now gate the current string-helpers, cmdline, argv-split, and rbtree helper bundle together, so Phase 7 helper work should stay reviewable through that shared lane instead of adding ad hoc per-slice CI steps.
- the current Phase 7 build handoff is intentionally split: helper tests import `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, and `lib/rbtree.zig` through explicit `addImport(...)` aliases in `zigux/tests/phase7_build.zig`, while the two survey tests keep their own repo-root manifest reads through `zigux/tests/phase7_argv_split_manifest.json` and `zigux/tests/phase7_rbtree_manifest.json`.
- `python3 scripts/zigux/check-phase7-rbtree-parity.py` remains the current representative external C-vs-Zig spot check for the parked Phase 7 packet and should move together with the same review bundle when the `rbtree` slice changes.
- the Phase 7 helper bundle is now parked end-to-end: cmdline, argv-split, rbtree, and the bounded string-helpers slice all carry their current dedicated proofs through the shared `phase7_build.zig` gate, so future work here should reopen only for a concrete newly observed parity gap rather than for more speculative fixture expansion.
- the Phase 7 string-helpers slice is intentionally helper-only under `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`; current `master` ships no `samples/zigux/*string*` reference sample, so sample-root follow-up should not treat that absence as a missing Phase 5 port.

Phase 8 notes
- `Documentation/zigux/phase8-exec-cmd-slice.md`
- `Documentation/zigux/phase8-help-slice.md`
- `Documentation/zigux/phase8-kallsyms-slice.md`
- `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md`
- `Documentation/zigux/phase8-bpf-type-names-slice.md`
- `Documentation/zigux/phase8-libbpf-segment-survey.md`
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
- `python3 scripts/zigux/validate-phase8.py` and `make -C zigux phase8-validate` now fail fast if the shared Phase 8 tooling bundle drifts out of sync across `zigux/tests/phase8_build.zig`, `zigux/Makefile`, the bootstrap workflow, the shared README notes, and the current libbpf helper-family survey around `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, `tools/lib/bpf/zigux_segments/type_names.zig`, and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, while keeping the deferred `file-path-and-handle-bridge` and `perf-buffer-online-cpu-routing` boundaries explicit.
- the same shared README packet now also exposes `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, so the parked command-preparation and libbpf handle-boundary contract stays reviewable from the top-level docs index instead of hiding only inside the validator and the deeper survey note.
- `zigux/tests/phase8_build.zig` and `make -C zigux phase8` now gate the current exec-cmd, help, kallsyms, libbpf cpu-mask, libbpf logging, libbpf pin-path, libbpf type-name, libbpf fdinfo-map-info, bridge-boundary-survey, and segment-survey bundle together, so new Phase 8 tooling work should stay reviewable through that shared lane instead of widening into ad hoc per-slice checks.
- the current bounded Phase 8 decision is no longer whether `exec-cmd` still needs its pure `execl_cmd()` parity helper, whether `kallsyms.zig` still needs a direct parse wrapper, or whether `help.zig` still needs its pure pretty-print emission surface; those slices are now parked, so the next follow-up should come from the next helper-first libbpf segment or another still-active Phase 8 tooling slice.

Phase 9 notes
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`
- `Documentation/zigux/phase9-runtime-kretprobe-survey.md`
- `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`
- `Documentation/zigux/phase9-runtime-trace-events-survey.md`
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md` and `Documentation/zigux/review-checklist.md` now carry the shared loader-handoff release-discipline evidence for the current runtime bundle, so the bounded Phase 9 lane stays explicit about allocator ownership, `requires_runtime_substrate`, handoff stage, and the still-blocked command or environment control surface.
- the same Phase 9 governance packet now also keeps the roadmap's shipped selftest-hook markers and bounded lifecycle-parity posture explicit across the current runtime starter surveys, manifests, and shared `zigux/tests/phase9_build.zig` replay, so review notes do not overstate the still-blocked loadable-module path.
- the same Phase 9 loader-gap bundle now keeps a manifest-backed catalog and ownership map in `zigux/tests/runtime_loader_gap_manifest.json`, so reviewers can see which file owns the survey note, checklist, shared request contract, sample-side loader plans, and shared `phase9_build.zig` replay path before the lane widens again.
- the `Documentation/zigux/phase9-runtime-trace-events-{survey,module-slice}.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` bundle now keeps the `Documentation/zigux/freeze-map.md` boundary explicit, so `kernel/trace/ring_buffer.c` stays `Study / Boundary Only` and any trace-core status change still requires an Architecture Council decision.
- `python3 scripts/zigux/validate-phase9.py` and `make -C zigux phase9-validate` now fail fast if the shared Phase 9 checklist, loader-gap survey, trace-events freeze-map boundary packet, README notes, workflow wiring, and `zigux/tests/phase9_build.zig` entrypoint drift apart.
- `zigux/tests/phase9_build.zig` and `make -C zigux phase9` now gate the current runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle together, so new Phase 9 runtime work should stay reviewable through that shared lane instead of widening into ad hoc per-slice checks.
- the current bounded Phase 9 decision is no longer whether the kretprobe lane still needs a starter, a survey gate, or shared build wiring; those pieces and the newer loader-handoff scaffold are now landed, so the next follow-up should be whichever small shared runtime loader substrate step can honestly consume the existing atomic64, bitmap, or kretprobe loader plans without widening into a larger runtime-module implementation.

Phase 10 notes
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-virtio-core-slice.md`
- `Documentation/zigux/phase10-virtio-core-survey.md`
- `Documentation/zigux/phase10-virtio-ring-slice.md`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `Documentation/zigux/phase10-virtio-input-slice.md`
- `Documentation/zigux/phase10-virtio-input-module-slice.md`
- `Documentation/zigux/phase10-virtio-input-survey.md`
- `Documentation/zigux/phase10-virtio-mmio-slice.md`
- `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `Documentation/zigux/README.md` now exposes the same nine published Phase 10 docs named by the shared closure packet, including `Documentation/zigux/phase10-virtio-core-survey.md` and `Documentation/zigux/phase10-virtio-mmio-slice.md`, so the top-level docs index does not undercount the live parity-evidence bundle.
- `Documentation/zigux/phase10-closure-evidence.md` now records the exact current roadmap-aligned virtio lab bundle and keeps Phase 10 explicit as active rather than prematurely closed while `drivers/virtio/virtio_mmio.zig`, its bounded MMIO starter test, and the remaining risky transport gaps stay visible together.
- `python3 scripts/zigux/validate-phase10.py` now keeps the narrower virtio_input packet aligned, so the Phase 10 docs, helper, tests, and survey manifest all keep the same landed registration-preflight helper summary, ready-next queue-callback preflight helper, and registration-lifecycle blocker posture.
- `python3 scripts/zigux/validate-phase10-closure.py` and `make -C zigux phase10-validate` now fail fast if the shared closure note, the four Phase 10 survey manifests, the bootstrap workflow, and `zigux/tests/phase10_build.zig` drift apart.
- `zigux/tests/phase10_build.zig` and `make -C zigux phase10` now gate the current virtio core, ring, input, and MMIO-survey evidence bundle together, so new Phase 10 work stays reviewable as one bounded lab tranche instead of widening into ad hoc transport claims.

Phase 12 notes
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
- `Documentation/zigux/phase12-virtio-scsi-slice.md`
- `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- `Documentation/zigux/phase12-libbpf-segment-survey.md`
- the active Phase 12 storage-driver survey packet now keeps the bounded `drivers/scsi/virtio_scsi.zig` queue-layout, recovery, probe snapshot, host-limit summary, and io-queue-map starters visible from the top-level docs index without overstating the still-blocked DMA-backed queue ownership, `Scsi_Host` lifecycle, or blk-mq follow-up.
- `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`, and `make -C zigux phase12` now keep that same storage-driver survey packet reviewable through the shared Phase 12 tranche instead of leaving it discoverable only through the deeper survey note.
- the same top-level Phase 12 packet now also needs to keep the libbpf rollback and reversible-delivery lab visible: `Documentation/zigux/phase12-libbpf-segment-survey.md` records the bounded survey gate, reviewability gate, rollback owner, fallback path, and reversible-delivery drill around the helper-first `tools/lib/bpf/zigux_segments/` footing without overstating the still-blocked skeleton, object-loader, relocation, or syscall-backed surfaces.
- the current shared rollback-lab replay has already advanced beyond the committed fast-inventory snapshot: the live `zig build test --build-file zigux/tests/phase12_build.zig --summary all` replay now reaches `Build Summary: 17/17 steps succeeded; 47/47 tests passed`, while `zigux/tests/fixtures/phase12_build_inventory.json` still records `35/35`, so this docs index keeps the new lab state explicit without reopening the shared fixture or validator lane here.

Phase 13 notes
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-libfs-slice.md`
- `Documentation/zigux/phase13-libfs-survey.md`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- the active Phase 13 shared-helper packet now keeps the roadmap-to-repo path for `fs/libfs.c`, `lib/devres.c`, `security/landlock/ruleset.c`, and `security/landlock/syscalls.c` visible from the top-level docs index instead of leaving the shared traceability and release-discipline reading buried only in the deeper notes.
- `zigux/tests/phase13_build.zig`, `make -C zigux phase13`, `Documentation/zigux/phase13-roadmap-traceability.md`, and `Documentation/zigux/phase13-release-notes-survey.md` now expose the same shared tranche entrypoints and release-facing readout, so this docs index stays aligned with the validator-first replay path already used elsewhere in the Phase 13 packet.
- all four roadmap anchors now carry manifest-backed survey packets, while the adjacent notifier-list reviewability packet stays explicit as supporting shared-helper evidence rather than a fifth roadmap anchor.
- the same top-level Phase 13 packet still keeps the helper-only `devres` boundary honest: live MMIO side effects, live DMA-backed mappings, live scatterlist ownership, live device-tree walking, and live arch memtype state remain intentionally blocked even though `lib/devres.c` is now manifest-backed.
